"""Chapter (unit) tests and section readiness tests.

Questions are drawn from the lessons' quick exercises and graded on the server exactly like lesson
answers; each question can be answered once per sitting and answers are revealed only afterwards.
Tests never cost hearts.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Course, Exercise, Lesson, TestAttempt, Unit, User, UserLesson, UserTest
from ..schemas import public_exercise
from ..security.deps import get_current_user
from ..security.ratelimit import limit
from ..services import certificates, gamification, grading, progress, review
from .learn import AnswerIn

router = APIRouter(prefix="/api/tests", tags=["tests"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]

ATTEMPT_TTL = timedelta(hours=2)
MIN_SECONDS_PER_QUESTION = 2  # anti-automation, same idea as lessons


class StartIn(BaseModel):
    course: str = Field(max_length=40)
    unit_id: int | None = None
    section: str | None = Field(None, max_length=40)


def _course(db: Session, slug: str) -> Course:
    course = db.scalar(
        select(Course)
        .where(Course.slug == slug)
        .options(selectinload(Course.units).selectinload(Unit.lessons).selectinload(Lesson.exercises))
    )
    if course is None:
        raise HTTPException(404, "Course not found")
    return course


@router.post("/start", dependencies=[Depends(limit("test_start", 20))])
def start(body: StartIn, user: CurrentUser, db: DB):
    course = _course(db, body.course)
    done = progress.completed_ids(db, user)
    passed = progress.passed_targets(db, user)
    status = progress.lesson_statuses(course, done, passed, gamification.debug_active(user))

    if body.unit_id is not None:
        unit = next((u for u in course.units if u.id == body.unit_id), None)
        if unit is None:
            raise HTTPException(404, "Unit not found")
        if progress.unit_test_status(unit, status, passed) == "locked":
            raise HTTPException(403, "Finish this unit's lessons to unlock its test")
        kind, target, units, n = "unit", progress.unit_target(unit.id), [unit], progress.UNIT_TEST_QUESTIONS
        title = f"{unit.title.split(' · ', 1)[-1]} · Chapter test"
    elif body.section:
        units = progress.units_before_section(course, body.section)
        if not units:
            raise HTTPException(404, "There's no readiness test for that section")
        kind, target, n = "section", progress.section_target(course.id, body.section), progress.SECTION_TEST_QUESTIONS
        title = f"Ready for {body.section}?"
    else:
        raise HTTPException(400, "Choose a unit or a section")

    questions = progress.pick_questions(units, n)
    if not questions:
        raise HTTPException(404, "No questions available for this test")
    attempt = TestAttempt(
        user_id=user.id, course_id=course.id, kind=kind, target=target,
        exercise_ids=[q.id for q in questions], results={}, pass_mark=progress.pass_mark(len(questions)),
    )
    db.add(attempt)
    db.commit()
    return {
        "attempt_id": attempt.id, "kind": kind, "title": title, "course": course.slug, "course_title": course.title,
        "pass_mark": attempt.pass_mark, "xp": progress.UNIT_TEST_XP if kind == "unit" else progress.SECTION_TEST_XP,
        "questions": [public_exercise(q) for q in questions],
    }


def _attempt(db: Session, user: User, attempt_id: str) -> TestAttempt:
    attempt = db.get(TestAttempt, attempt_id[:32], with_for_update=True)  # serialises parallel calls
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(404, "Test not found")
    if attempt.completed_at is not None:
        raise HTTPException(409, "This test is already finished")
    if gamification.aware(attempt.started_at) + ATTEMPT_TTL < datetime.now(timezone.utc):
        raise HTTPException(410, "This test expired. Start it again.")
    return attempt


@router.post("/{attempt_id}/answer", dependencies=[Depends(limit("test_answer", 60))])
def answer(attempt_id: str, body: AnswerIn, user: CurrentUser, db: DB):
    attempt = _attempt(db, user, attempt_id)
    if body.exercise_id not in attempt.exercise_ids:
        raise HTTPException(404, "Question not found")
    key = str(body.exercise_id)
    if key in attempt.results:
        raise HTTPException(409, "You've already answered this question")
    ex = db.get(Exercise, body.exercise_id)
    correct = grading.grade(ex, body.value())
    review.record(db, user, ex, correct)
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
        raise HTTPException(400, "Answer every question to finish the test")
    elapsed = datetime.now(timezone.utc) - gamification.aware(attempt.started_at)
    if elapsed.total_seconds() < MIN_SECONDS_PER_QUESTION * total:
        raise HTTPException(400, "That was suspiciously fast. Take your time!")

    attempt.score = sum(1 for v in attempt.results.values() if v)
    attempt.passed = attempt.score >= attempt.pass_mark
    attempt.completed_at = datetime.now(timezone.utc)

    record = db.scalar(select(UserTest).where(UserTest.user_id == user.id, UserTest.target == attempt.target))
    if record is None:
        record = UserTest(user_id=user.id, target=attempt.target, best_score=0, attempts=0)
        db.add(record)
    first_pass = attempt.passed and record.passed_at is None
    record.attempts += 1
    record.best_score = max(record.best_score, attempt.score)

    skipped = 0
    new_badges: list[str] = []
    if attempt.passed:
        if first_pass:
            record.passed_at = attempt.completed_at
            attempt.xp_awarded = progress.UNIT_TEST_XP if attempt.kind == "unit" else progress.SECTION_TEST_XP
            gamification.award_xp(db, user, attempt.xp_awarded, f"{attempt.kind}_test")
        if attempt.kind == "section":
            skipped = _test_out(db, user, attempt)
        new_badges = gamification.check_badges(db, user, test=attempt.kind)
    cert = certificates.maybe_issue(db, user, attempt.course_id) if attempt.passed else None
    db.commit()
    return {
        "certificate": certificates.public(cert) if cert else None,
        "passed": attempt.passed, "score": attempt.score, "total": total, "pass_mark": attempt.pass_mark,
        "xp_awarded": attempt.xp_awarded, "lessons_skipped": skipped, "best_score": record.best_score,
        "new_badges": [{"key": k, **gamification.BADGES[k]} for k in new_badges],
        "streak": gamification.current_streak(user), "xp_total": user.xp_total,
    }


def _test_out(db: Session, user: User, attempt: TestAttempt) -> int:
    """Mark everything before the section as tested out, and its chapter tests as passed."""
    course = db.get(Course, attempt.course_id)
    name = attempt.target.split(":", 2)[2]
    units = progress.units_before_section(course, name)
    done = progress.completed_ids(db, user)
    passed = progress.passed_targets(db, user)
    now = datetime.now(timezone.utc)
    skipped = 0
    for unit in units:
        for lesson in unit.lessons:
            if lesson.id not in done:
                db.add(UserLesson(user_id=user.id, lesson_id=lesson.id, completed_count=0, tested_out=True))
                skipped += 1
        target = progress.unit_target(unit.id)
        if target not in passed:
            row = db.scalar(select(UserTest).where(UserTest.user_id == user.id, UserTest.target == target))
            if row is None:
                db.add(UserTest(user_id=user.id, target=target, best_score=0, attempts=0, passed_at=now))
            else:
                row.passed_at = now
    return skipped
