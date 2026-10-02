"""Courses, the learning path, lesson attempts and the daily challenge."""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Course, DailyChallengeClaim, Exercise, Lesson, LessonAttempt, Unit, User, UserLesson
from ..schemas import public_exercise
from ..security.deps import get_current_user
from ..security.ratelimit import limit
from ..config import get_settings
from ..security.ratelimit import check
from ..services import code_runner, gamification, grading, progress, review

router = APIRouter(prefix="/api", tags=["learn"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]

ATTEMPT_TTL = timedelta(hours=2)
MIN_SECONDS_PER_EXERCISE = 2  # anti-automation: a lesson can't be "completed" instantly
DAILY_BONUS_XP = 20


class RunAnswer(BaseModel):
    """A `run` exercise answer: the learner's code plus (browser languages) what each test printed."""

    code: str = Field(max_length=grading.MAX_CODE_CHARS)
    outputs: list[Annotated[str, Field(max_length=code_runner.MAX_OUTPUT)]] | None = Field(None, max_length=grading.MAX_TESTS)


class AnswerIn(BaseModel):
    exercise_id: int
    # int (mcq) | str (fill / code) | list[int] (order) | RunAnswer (run); size-limited here and in grading
    answer: int | Annotated[str, Field(max_length=2000)] | Annotated[list[int], Field(max_length=50)] | RunAnswer

    def value(self):
        return self.answer.model_dump() if isinstance(self.answer, RunAnswer) else self.answer


class RunIn(BaseModel):
    exercise_id: int
    code: str = Field(max_length=grading.MAX_CODE_CHARS)


def _ordered_lessons(course: Course) -> list[Lesson]:
    return [lesson for unit in course.units for lesson in unit.lessons]


def _completed_ids(db: Session, user: User) -> set[int]:
    return progress.completed_ids(db, user)


def _load_course(db: Session, course_id: int) -> Course:
    return db.scalar(
        select(Course).where(Course.id == course_id).options(selectinload(Course.units).selectinload(Unit.lessons))
    )


@router.get("/courses")
def list_courses(user: CurrentUser, db: DB):
    done = _completed_ids(db, user)
    courses = db.scalars(
        select(Course).order_by(Course.position).options(selectinload(Course.units).selectinload(Unit.lessons))
    ).all()
    out = []
    for c in courses:
        lessons = _ordered_lessons(c)
        out.append({
            "slug": c.slug, "title": c.title, "description": c.description, "icon": c.icon,
            "lessons": len(lessons), "completed": sum(1 for l in lessons if l.id in done),
        })
    return out


@router.get("/courses/{slug}")
def course_path(slug: Annotated[str, Field(max_length=40)], user: CurrentUser, db: DB):
    course = db.scalar(
        select(Course).where(Course.slug == slug).options(selectinload(Course.units).selectinload(Unit.lessons))
    )
    if course is None:
        raise HTTPException(404, "Course not found")
    done = _completed_ids(db, user)
    passed = progress.passed_targets(db, user)
    status = progress.lesson_statuses(course, done, passed)
    unit_q = progress.UNIT_TEST_QUESTIONS
    section_q = progress.SECTION_TEST_QUESTIONS
    return {
        "slug": course.slug, "title": course.title, "icon": course.icon, "description": course.description,
        "units": [
            {
                "id": u.id, "title": u.title, "section": progress.section_name(u),
                "lessons": [{"id": l.id, "title": l.title, "xp": l.xp_reward, "status": status[l.id]} for l in u.lessons],
                "test": {"status": progress.unit_test_status(u, status, passed), "questions": unit_q,
                         "pass_mark": progress.pass_mark(unit_q), "xp": progress.UNIT_TEST_XP},
            }
            for u in course.units
        ],
        "section_tests": {
            name: {"status": st, "questions": section_q, "pass_mark": progress.pass_mark(section_q), "xp": progress.SECTION_TEST_XP}
            for name, _ in progress.sections(course)
            if (st := progress.section_test_status(course, name, status, passed))
        },
    }


@router.post("/lessons/{lesson_id}/start", dependencies=[Depends(limit("lesson_start", 30))])
def start_lesson(lesson_id: int, user: CurrentUser, db: DB):
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(404, "Lesson not found")
    course = _load_course(db, lesson.unit.course_id)
    done = _completed_ids(db, user)
    if progress.lesson_statuses(course, done, progress.passed_targets(db, user)).get(lesson.id) == "locked":
        raise HTTPException(403, "Finish the previous lesson (and the chapter test) first")
    gamification.refill_hearts(user)
    if user.hearts <= 0 and lesson.id not in done:
        db.commit()
        raise HTTPException(409, "You're out of hearts. They refill over time, or practise a completed lesson.")
    attempt = LessonAttempt(user_id=user.id, lesson_id=lesson.id)
    db.add(attempt)
    db.commit()
    return {
        "attempt_id": attempt.id,
        "lesson": {"id": lesson.id, "title": lesson.title, "intro": lesson.intro, "course": course.slug, "course_title": course.title},
        "exercises": [public_exercise(e) for e in lesson.exercises],
        "hearts": user.hearts,
    }


def _get_attempt(db: Session, user: User, attempt_id: str) -> LessonAttempt:
    # Row lock serialises concurrent answer/complete calls (no double XP from parallel requests).
    attempt = db.get(LessonAttempt, attempt_id[:32], with_for_update=True)
    if attempt is None or attempt.user_id != user.id:  # never reveal other users' attempts
        raise HTTPException(404, "Attempt not found")
    if attempt.completed_at is not None:
        raise HTTPException(409, "Lesson already completed")
    if gamification.aware(attempt.started_at) + ATTEMPT_TTL < datetime.now(timezone.utc):
        raise HTTPException(410, "This lesson session expired. Start again.")
    return attempt


@router.post("/attempts/{attempt_id}/answer", dependencies=[Depends(limit("answer", 60))])
def answer(attempt_id: str, body: AnswerIn, user: CurrentUser, db: DB):
    attempt = _get_attempt(db, user, attempt_id)
    ex = db.get(Exercise, body.exercise_id)
    if ex is None or ex.lesson_id != attempt.lesson_id:
        raise HTTPException(404, "Exercise not found")
    correct = grading.grade(ex, body.value())
    review.record(db, user, ex, correct)
    # Replaying a finished lesson is free practice: mistakes there don't cost hearts.
    practice = db.scalar(select(UserLesson.id).where(UserLesson.user_id == user.id, UserLesson.lesson_id == ex.lesson_id)) is not None
    if correct:
        if ex.id not in attempt.correct_ids:
            attempt.correct_ids = [*attempt.correct_ids, ex.id]
    else:
        attempt.mistakes += 1
        if not practice:
            gamification.lose_heart(user)
    db.commit()
    return {
        "correct": correct,
        "correct_answer": grading.reveal(ex),
        "explanation": ex.explanation,
        "hearts": user.hearts,
        "out_of_hearts": user.hearts <= 0 and not practice,
    }


@router.post("/attempts/{attempt_id}/complete")
def complete(attempt_id: str, user: CurrentUser, db: DB):
    attempt = _get_attempt(db, user, attempt_id)
    lesson = db.get(Lesson, attempt.lesson_id)
    required = {e.id for e in lesson.exercises}
    if not required.issubset(set(attempt.correct_ids)):
        raise HTTPException(400, "Answer every exercise correctly to finish the lesson")
    elapsed = datetime.now(timezone.utc) - gamification.aware(attempt.started_at)
    if elapsed.total_seconds() < MIN_SECONDS_PER_EXERCISE * len(required):
        raise HTTPException(400, "That was suspiciously fast. Take your time!")

    perfect = attempt.mistakes == 0
    record = db.scalar(select(UserLesson).where(UserLesson.user_id == user.id, UserLesson.lesson_id == lesson.id))
    if record is None:
        xp = lesson.xp_reward + (5 if perfect else 0)
        db.add(UserLesson(user_id=user.id, lesson_id=lesson.id, completed_count=1, perfect=perfect))
    else:
        xp = 5 if record.completed_count < 20 else 0  # practice XP, capped to stop farming
        record.completed_count += 1
        record.perfect = record.perfect or perfect
    attempt.completed_at = datetime.now(timezone.utc)
    attempt.xp_awarded = xp
    gamification.award_xp(db, user, xp, "lesson")
    new_badges = gamification.check_badges(db, user, perfect=perfect)
    db.commit()
    return {
        "xp_awarded": xp, "perfect": perfect, "mistakes": attempt.mistakes,
        "new_badges": [{"key": k, **gamification.BADGES[k]} for k in new_badges],
        "streak": gamification.current_streak(user), "xp_total": user.xp_total,
    }


# ------------------------------------------------------------------ daily challenge
def _daily_exercise(db: Session) -> Exercise | None:
    ids = sorted(db.scalars(select(Exercise.id).where(Exercise.kind.in_(["mcq", "fill"]))))
    if not ids:
        return None
    seed = int(hashlib.sha256(gamification.today().isoformat().encode()).hexdigest(), 16)
    return db.get(Exercise, ids[seed % len(ids)])


@router.get("/daily")
def daily(user: CurrentUser, db: DB):
    ex = _daily_exercise(db)
    if ex is None:
        return {"exercise": None}
    claim = db.scalar(select(DailyChallengeClaim).where(DailyChallengeClaim.user_id == user.id, DailyChallengeClaim.day == gamification.today()))
    course = ex.lesson.unit.course
    return {
        "exercise": public_exercise(ex), "course": course.title, "bonus_xp": DAILY_BONUS_XP,
        "answered": claim is not None, "correct": bool(claim and claim.correct),
    }


@router.post("/daily/answer", dependencies=[Depends(limit("daily", 10))])
def daily_answer(body: AnswerIn, user: CurrentUser, db: DB):
    ex = _daily_exercise(db)
    if ex is None or ex.id != body.exercise_id:
        raise HTTPException(404, "Not today's challenge")
    today = gamification.today()
    if db.scalar(select(DailyChallengeClaim.id).where(DailyChallengeClaim.user_id == user.id, DailyChallengeClaim.day == today)):
        raise HTTPException(409, "You've already answered today's challenge")
    correct = grading.grade(ex, body.value())
    review.record(db, user, ex, correct)
    db.add(DailyChallengeClaim(user_id=user.id, day=today, correct=correct))
    try:
        db.flush()  # unique (user, day) constraint stops double-claims from parallel requests
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "You've already answered today's challenge")
    new_badges: list[str] = []
    if correct:
        gamification.award_xp(db, user, DAILY_BONUS_XP, "daily")
        new_badges = gamification.check_badges(db, user, daily=True)
    db.commit()
    return {
        "correct": correct, "correct_answer": grading.reveal(ex), "explanation": ex.explanation,
        "xp_awarded": DAILY_BONUS_XP if correct else 0,
        "new_badges": [{"key": k, **gamification.BADGES[k]} for k in new_badges],
    }



# ------------------------------------------------------------------ sandboxed runs (Java / C / C++)
@router.post("/run")
def run_code(body: RunIn, user: CurrentUser, db: DB):
    """Compile + run learner code in the isolated sandbox and report pass/fail per test.
    Expected outputs are never returned - only whether each test passed."""
    allowed, retry = check(f"run:u{user.id}", get_settings().rate_limit_run_per_minute, 60)
    if not allowed:
        raise HTTPException(429, "You're running code very fast - wait a few seconds.", headers={"Retry-After": str(retry)})
    ex = db.get(Exercise, body.exercise_id)
    lang = (ex.data or {}).get("language") if ex else None
    if ex is None or ex.kind != "run" or lang not in code_runner.SERVER_LANGS:
        raise HTTPException(404, "Exercise not found")
    tests = ex.data.get("tests", [])
    expected = [grading.norm_output(e) for e in (ex.solution or {}).get("expected", [])]
    try:
        results = code_runner.run_tests(lang, body.code, tests)
    except code_runner.RunnerUnavailable:
        raise HTTPException(503, "The code runner isn't available right now. You can still check your answer.")
    return {
        "results": [
            {"name": t.get("name", f"Test {i + 1}"), "stdout": r["stdout"], "stderr": r["stderr"],
             "passed": r["ok"] and i < len(expected) and grading.norm_output(r["stdout"]) == expected[i]}
            for i, (t, r) in enumerate(zip(tests, results))
        ]
    }
