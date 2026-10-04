"""An in-memory snapshot of the course structure (courses -> units -> lessons: ids, titles, order).

The structure only changes when the curriculum is synced or an admin edits it, but almost every request used to
reload it from the database - 3-5 network round trips each time. Here it is loaded once and reused for
TTL seconds; admin edits call invalidate() so they show up at once on this server process.
Lesson TEXT and exercises are never cached here - only what is needed to lay out the path and check locking."""
import threading
import time
from dataclasses import dataclass, field
from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Course, Exercise, Unit

TTL = 60.0


@dataclass(frozen=True)
class LessonInfo:
    id: int
    title: str
    xp_reward: int
    is_project: bool


@dataclass
class UnitInfo:
    id: int
    title: str
    section: str | None
    lessons: list[LessonInfo] = field(default_factory=list)


@dataclass
class CourseInfo:
    id: int
    slug: str
    title: str
    description: str
    icon: str
    units: list[UnitInfo] = field(default_factory=list)


_lock = threading.Lock()
_state: dict = {"at": 0.0, "courses": [], "by_slug": {}, "by_lesson": {}}
_exercises: dict[int, tuple[float, SimpleNamespace]] = {}


def invalidate() -> None:
    with _lock:
        _state["at"] = 0.0
        _exercises.clear()


def _load(db: Session) -> None:
    rows = db.scalars(select(Course).order_by(Course.position).options(selectinload(Course.units).selectinload(Unit.lessons))).all()
    courses, by_slug, by_lesson = [], {}, {}
    for c in rows:
        info = CourseInfo(c.id, c.slug, c.title, c.description, c.icon)
        for u in c.units:
            ui = UnitInfo(u.id, u.title, u.section)
            for l in u.lessons:
                ui.lessons.append(LessonInfo(l.id, l.title, l.xp_reward, bool(l.is_project)))
                by_lesson[l.id] = info
            info.units.append(ui)
        courses.append(info)
        by_slug[c.slug] = info
    _state.update(at=time.monotonic(), courses=courses, by_slug=by_slug, by_lesson=by_lesson)


def _fresh(db: Session) -> dict:
    if time.monotonic() - _state["at"] > TTL:
        with _lock:
            if time.monotonic() - _state["at"] > TTL:
                _load(db)
    return _state


def courses(db: Session) -> list[CourseInfo]:
    return _fresh(db)["courses"]


def by_slug(db: Session, slug: str) -> CourseInfo | None:
    return _fresh(db)["by_slug"].get(slug)


def course_of_lesson(db: Session, lesson_id: int) -> CourseInfo | None:
    return _fresh(db)["by_lesson"].get(lesson_id)


def exercise(db: Session, exercise_id: int) -> SimpleNamespace | None:
    """A read-only snapshot of one exercise (what grading and hints need), cached - answering a question no longer
    costs a database round trip for the exercise itself."""
    hit = _exercises.get(exercise_id)
    if hit and time.monotonic() - hit[0] < TTL * 5:
        return hit[1]
    ex = db.get(Exercise, exercise_id)
    if ex is None:
        return None
    snap = SimpleNamespace(
        id=ex.id, lesson_id=ex.lesson_id, kind=ex.kind, prompt=ex.prompt, code=ex.code, data=ex.data or {},
        solution=ex.solution or {}, explanation=ex.explanation or "", hint=ex.hint or "",
    )
    if len(_exercises) > 6000:
        _exercises.clear()
    _exercises[exercise_id] = (time.monotonic(), snap)
    return snap
