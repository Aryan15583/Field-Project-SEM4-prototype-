"""In-memory snapshots of the course structure (courses -> units -> lessons: ids, titles, order).

The structure only changes when the curriculum is synced or an admin edits it, but almost every request used to
reload it from the database. Now it is kept in memory for TTL seconds (admin edits call invalidate() so they show up
at once on this server process), and - new - PER COURSE:
  - overview(): the course list with lesson counts and which lesson belongs to which course: a few cheap rows, no
    objects per lesson. Enough for the course picker.
  - by_slug(): the full tree of ONE course, loaded only when someone opens that course. A Python learner makes the
    server build the Python tree, not all ten; a course nobody opens is never built (a cold server starts faster and
    each refresh does a tenth of the work).
Lesson TEXT and exercises are never cached here - only what is needed to lay out the path and check locking."""
import threading
import time
from dataclasses import dataclass, field
from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Course, Exercise, Lesson, Unit

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


@dataclass(frozen=True)
class CourseOverview:
    slug: str
    title: str
    description: str
    icon: str
    lesson_ids: frozenset[int]  # every lesson of the course (for "x of y completed")


_lock = threading.Lock()
_overview: dict = {"at": 0.0, "list": [], "lesson_slug": {}}
_trees: dict[str, tuple[float, CourseInfo]] = {}  # slug -> (loaded at, full tree): only courses someone opened
_exercises: dict[int, tuple[float, SimpleNamespace]] = {}


def invalidate() -> None:
    with _lock:
        _overview["at"] = 0.0
        _trees.clear()
        _exercises.clear()


def _load_overview(db: Session) -> None:
    # plain rows, not ORM objects: ~1,000 (lesson id, course) pairs cost almost nothing to fetch and keep
    rows = db.execute(select(Course.id, Course.slug, Course.title, Course.description, Course.icon).order_by(Course.position)).all()
    pairs = db.execute(select(Lesson.id, Course.slug).select_from(Lesson).join(Unit, Lesson.unit_id == Unit.id).join(Course, Unit.course_id == Course.id)).all()
    ids: dict[str, set[int]] = {r.slug: set() for r in rows}
    lesson_slug: dict[int, str] = {}
    for lesson_id, slug in pairs:
        ids.setdefault(slug, set()).add(lesson_id)
        lesson_slug[lesson_id] = slug
    listing = [CourseOverview(r.slug, r.title, r.description, r.icon, frozenset(ids.get(r.slug, ()))) for r in rows]
    _overview.update(at=time.monotonic(), list=listing, lesson_slug=lesson_slug)


def _fresh_overview(db: Session) -> dict:
    if time.monotonic() - _overview["at"] > TTL:
        with _lock:
            if time.monotonic() - _overview["at"] > TTL:
                _load_overview(db)
    return _overview


def overview(db: Session) -> list[CourseOverview]:
    return _fresh_overview(db)["list"]


def by_slug(db: Session, slug: str) -> CourseInfo | None:
    """The full tree of one course (loaded on first use, then reused for TTL seconds)."""
    hit = _trees.get(slug)
    if hit and time.monotonic() - hit[0] <= TTL:
        return hit[1]
    with _lock:
        hit = _trees.get(slug)
        if hit and time.monotonic() - hit[0] <= TTL:
            return hit[1]
        c = db.scalar(select(Course).where(Course.slug == slug).options(selectinload(Course.units).selectinload(Unit.lessons)))
        if c is None:
            _trees.pop(slug, None)
            return None
        info = CourseInfo(c.id, c.slug, c.title, c.description, c.icon)
        for u in c.units:
            ui = UnitInfo(u.id, u.title, u.section)
            for l in u.lessons:
                ui.lessons.append(LessonInfo(l.id, l.title, l.xp_reward, bool(l.is_project)))
            info.units.append(ui)
        _trees[slug] = (time.monotonic(), info)
        return info


def course_of_lesson(db: Session, lesson_id: int) -> CourseInfo | None:
    slug = _fresh_overview(db)["lesson_slug"].get(lesson_id)
    return by_slug(db, slug) if slug else None


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
