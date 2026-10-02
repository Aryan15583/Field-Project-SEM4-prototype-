"""Practice sessions: spaced-repetition review of exercises the learner has already met.

Practice never costs hearts - it's how hearts are earned back - and gives a little XP, capped per day
so it can't be farmed. Answers are graded on the server and revealed only after answering.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Course, Exercise, PracticeAttempt, ReviewItem, User, XpEvent
from ..schemas import public_exercise
from ..security.deps import get_current_user
from ..security.ratelimit import limit
from ..services import gamification, grading, review
from .learn import AnswerIn

router = APIRouter(prefix="/api/practice", tags=["practice"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]

ATTEMPT_TTL = timedelta(hours=2)
MIN_SECONDS_PER_QUESTION = 2
PRACTICE_XP = 10
PRACTICE_XP_SESSIONS_PER_DAY = 5


class StartIn(BaseModel):
    course: str | None = Field(None, max_length=40)


def _course_id(db: Session, slug: str | None) -> int | None:
    if not slug:
        return None
    cid = db.scalar(select(Course.id).where(Course.slug == slug))
    if cid is None:
        raise HTTPException(404, "Course not found")
    return cid


@router.get("/summary")
def summary(user: CurrentUser, db: DB, course: Annotated[str | None, Query(max_length=40)] = None):
    return {**review.summary(db, user, _course_id(db, course)), "xp": PRACTICE_XP, "session_size": review.SESSION_SIZE}


@router.get("/overview")
def overview(user: CurrentUser, db: DB):
    """Review counts overall and for every course (for the Practice hub)."""
    courses = db.execute(select(Course.id, Course.slug, Course.title, Course.icon).order_by(Course.position)).all()
    return {
        "all": review.summary(db, user),
        "courses": [{"slug": c.slug, "title": c.title, "icon": c.icon, **review.summary(db, user, c.id)} for c in courses],
        "xp": PRACTICE_XP,
        "session_size": review.SESSION_SIZE,
        "min_items": review.MIN_SESSION,
    }


@router.post("/start", dependencies=[Depends(limit("practice_start", 20))])
def start(body: StartIn, user: CurrentUser, db: DB):
    course_id = _course_id(db, body.course)
    questions = review.pick(db, user, course_id)
    if len(questions) < review.MIN_SESSION:
        raise HTTPException(409, "Nothing to practise yet - finish a lesson first, and your mistakes will show up here.")
    due = {e.id for e in questions} & set(
        db.scalars(select(ReviewItem.exercise_id).where(ReviewItem.user_id == user.id, ReviewItem.due_at <= datetime.now(timezone.utc)))
    )
    attempt = PracticeAttempt(user_id=user.id, course_id=course_id, exercise_ids=[q.id for q in questions], results={})
    db.add(attempt)
    db.commit()
    return {
        "attempt_id": attempt.id,
        "title": "Practice" if course_id is None else f"{db.get(Course, course_id).title} practice",
        "questions": [{**public_exercise(q), "review": q.id in due} for q in questions],
        "xp": PRACTICE_XP,
    }


def _attempt(db: Session, user: User, attempt_id: str) -> PracticeAttempt:
    attempt = db.get(PracticeAttempt, attempt_id[:32], with_for_update=True)
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(404, "Practice session not found")
    if attempt.completed_at is not None:
        raise HTTPException(409, "This practice session is already finished")
    if gamification.aware(attempt.started_at) + ATTEMPT_TTL < datetime.now(timezone.utc):
        raise HTTPException(410, "This practice session expired. Start a new one.")
    return attempt


@router.post("/{attempt_id}/answer", dependencies=[Depends(limit("practice_answer", 60))])
def answer(attempt_id: str, body: AnswerIn, user: CurrentUser, db: DB):
    attempt = _attempt(db, user, attempt_id)
    if body.exercise_id not in attempt.exercise_ids:
        raise HTTPException(404, "Question not found")
    key = str(body.exercise_id)
    if key in attempt.results:
        raise HTTPException(409, "You've already answered this question")
    ex = db.get(Exercise, body.exercise_id)
    correct = grading.grade(ex, body.value())
    review.record(db, user, ex, correct, practice=True)
    attempt.results = {**attempt.results, key: correct}
    db.commit()
    return {
        "correct": correct, "correct_answer": grading.reveal(ex), "explanation": ex.explanation,
        "answered": len(attempt.results), "score": sum(attempt.results.values()),
    }


@router.post("/{attempt_id}/complete")
def complete(attempt_id: str, user: CurrentUser, db: DB):
    attempt = _attempt(db, user, attempt_id)
    total = len(attempt.exercise_ids)
    if len(attempt.results) < total:
        raise HTTPException(400, "Answer every question to finish the session")
    if (datetime.now(timezone.utc) - gamification.aware(attempt.started_at)).total_seconds() < MIN_SECONDS_PER_QUESTION * total:
        raise HTTPException(400, "That was suspiciously fast. Take your time!")
    attempt.completed_at = datetime.now(timezone.utc)
    score = sum(1 for v in attempt.results.values() if v)

    start_of_day = datetime.combine(gamification.today(), datetime.min.time(), tzinfo=timezone.utc)
    sessions_today = db.scalar(
        select(func.count(XpEvent.id)).where(XpEvent.user_id == user.id, XpEvent.reason == "practice", XpEvent.created_at >= start_of_day)
    ) or 0
    if sessions_today < PRACTICE_XP_SESSIONS_PER_DAY:
        attempt.xp_awarded = PRACTICE_XP
        gamification.award_xp(db, user, PRACTICE_XP, "practice")

    gamification.refill_hearts(user)
    if user.hearts < get_settings().max_hearts:
        user.hearts += 1  # practice is how you earn hearts back
        attempt.heart_awarded = True
    new_badges = gamification.check_badges(db, user, practice=True)
    db.commit()
    return {
        "score": score, "total": total, "xp_awarded": attempt.xp_awarded, "heart_awarded": attempt.heart_awarded,
        "hearts": user.hearts, "xp_capped": attempt.xp_awarded == 0,
        "new_badges": [{"key": k, **gamification.BADGES[k]} for k in new_badges],
        "summary": review.summary(db, user, attempt.course_id),
        "streak": gamification.current_streak(user), "xp_total": user.xp_total,
    }
