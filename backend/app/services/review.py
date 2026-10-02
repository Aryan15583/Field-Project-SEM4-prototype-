"""Spaced repetition (Leitner system).

Every quick exercise a learner meets gets a review item:
- answered right the first time in a lesson -> box 1, due again in 1 day;
- answered wrong anywhere (lesson, test, daily, practice) -> box 0, due now, one more lapse;
- answered right in practice -> one box up, due after a growing interval (1, 3, 7, 16, 35 days).
Practice sessions serve what's due first, then the weakest items.
"""
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Exercise, Lesson, ReviewItem, Unit, User, UserLesson
from .progress import QUIZ_KINDS

INTERVAL_DAYS = [0, 1, 3, 7, 16, 35]  # by box
MAX_BOX = len(INTERVAL_DAYS) - 1
SESSION_SIZE = 10
MIN_SESSION = 3


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _item(db: Session, user: User, ex: Exercise) -> ReviewItem | None:
    return db.scalar(select(ReviewItem).where(ReviewItem.user_id == user.id, ReviewItem.exercise_id == ex.id))


def record(db: Session, user: User, ex: Exercise, correct: bool, *, practice: bool = False) -> None:
    """Update the schedule after any answer. Program-writing exercises aren't reviewed."""
    if ex.kind not in QUIZ_KINDS:
        return
    item = _item(db, user, ex)
    now = _now()
    if item is None:
        item = ReviewItem(user_id=user.id, exercise_id=ex.id, box=0, lapses=0, reviews=0)
        db.add(item)
        if correct:  # first meeting, got it right: check back tomorrow
            item.box, item.due_at, item.updated_at = 1, now + timedelta(days=INTERVAL_DAYS[1]), now
            return
    if practice:
        item.reviews += 1
    if not correct:
        item.box, item.due_at = 0, now
        item.lapses += 1
    elif practice:
        item.box = min(MAX_BOX, item.box + 1)
        item.due_at = now + timedelta(days=INTERVAL_DAYS[item.box])
    # a correct retry inside a lesson doesn't count as "learned" - practice decides that
    item.updated_at = now


def _scoped(stmt, course_id: int | None):
    stmt = stmt.join(Exercise, Exercise.id == ReviewItem.exercise_id)
    if course_id is not None:
        stmt = stmt.join(Lesson, Lesson.id == Exercise.lesson_id).join(Unit, Unit.id == Lesson.unit_id).where(Unit.course_id == course_id)
    return stmt


def summary(db: Session, user: User, course_id: int | None = None) -> dict:
    base = select(func.count(ReviewItem.id)).where(ReviewItem.user_id == user.id)
    now = _now()
    due = db.scalar(_scoped(base.where(ReviewItem.due_at <= now), course_id)) or 0
    mistakes = db.scalar(_scoped(base.where(ReviewItem.box == 0), course_id)) or 0
    total = db.scalar(_scoped(base, course_id)) or 0
    strong = db.scalar(_scoped(base.where(ReviewItem.box >= 3), course_id)) or 0
    next_due = db.scalar(_scoped(select(func.min(ReviewItem.due_at)).where(ReviewItem.user_id == user.id, ReviewItem.due_at > now), course_id))
    return {"due": due, "mistakes": mistakes, "total": total, "strong": strong, "next_due_at": next_due.isoformat() if next_due else None}


def pick(db: Session, user: User, course_id: int | None = None, n: int = SESSION_SIZE) -> list[Exercise]:
    """Due items (most overdue first), then the weakest ones, then anything from completed lessons."""
    rng = random.SystemRandom()
    chosen: list[int] = []
    now = _now()
    rows = db.execute(
        _scoped(select(ReviewItem.exercise_id, ReviewItem.due_at, ReviewItem.box, ReviewItem.lapses).where(ReviewItem.user_id == user.id), course_id)
    ).all()
    due = sorted((r for r in rows if _aware(r.due_at) <= now), key=lambda r: _aware(r.due_at))
    chosen += [r.exercise_id for r in due[:n]]
    if len(chosen) < n:
        weak = sorted((r for r in rows if r.exercise_id not in chosen), key=lambda r: (r.box, -r.lapses, rng.random()))
        chosen += [r.exercise_id for r in weak[: n - len(chosen)]]
    if len(chosen) < n:  # e.g. lessons finished before practice existed
        stmt = (
            select(Exercise.id)
            .join(Lesson, Lesson.id == Exercise.lesson_id)
            .join(UserLesson, (UserLesson.lesson_id == Lesson.id) & (UserLesson.user_id == user.id))
            .where(Exercise.kind.in_(QUIZ_KINDS))
        )
        if course_id is not None:
            stmt = stmt.join(Unit, Unit.id == Lesson.unit_id).where(Unit.course_id == course_id)
        extra = [i for i in db.scalars(stmt) if i not in chosen]
        rng.shuffle(extra)
        chosen += extra[: n - len(chosen)]
    exercises = [db.get(Exercise, i) for i in chosen]
    rng.shuffle(exercises)
    return [e for e in exercises if e is not None]


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
