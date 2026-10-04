"""Path progression: which lessons are unlocked, chapter (unit) tests and section readiness tests.

Rules
- Lessons unlock one after another.
- The first lesson of a unit also needs the previous unit's chapter test to be passed. Learners who
  already completed lessons further along (before chapter tests existed) keep their access.
- A section readiness test (15 questions on everything before that section) lets a learner jump
  ahead: passing it marks the earlier lessons as "tested out" and their chapter tests as passed.
"""
import math
import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Course, Exercise, Unit, User, UserLesson, UserTest

UNIT_TEST_QUESTIONS = 8
SECTION_TEST_QUESTIONS = 15
PASS_RATIO = 0.75
QUIZ_KINDS = ("mcq", "fill", "order", "code")  # quick questions; writing whole programs stays in lessons
UNIT_TEST_XP = 20
SECTION_TEST_XP = 50


def unit_target(unit_id: int) -> str:
    return f"unit:{unit_id}"


def section_target(course_id: int, name: str) -> str:
    return f"section:{course_id}:{name}"


def pass_mark(questions: int) -> int:
    return math.ceil(questions * PASS_RATIO)


def section_name(unit: Unit) -> str:
    return unit.section or "Beginner"


def sections(course: Course) -> list[tuple[str, list[Unit]]]:
    out: list[tuple[str, list[Unit]]] = []
    for u in course.units:
        if out and out[-1][0] == section_name(u):
            out[-1][1].append(u)
        else:
            out.append((section_name(u), [u]))
    return out


def completed_ids(db: Session, user: User) -> set[int]:
    return set(db.scalars(select(UserLesson.lesson_id).where(UserLesson.user_id == user.id)))


def passed_targets(db: Session, user: User) -> set[str]:
    return set(db.scalars(select(UserTest.target).where(UserTest.user_id == user.id, UserTest.passed_at.is_not(None))))


def lesson_statuses(course: Course, done: set[int], passed: set[str], debug: bool = False) -> dict[int, str]:
    units = course.units
    if debug:  # admin debug mode: everything is open and shown as completed
        return {l.id: "completed" for u in units for l in u.lessons}
    # does the learner have any completed lesson in unit i or later? (grandfathers old progress)
    reached = [False] * (len(units) + 1)
    for i in range(len(units) - 1, -1, -1):
        reached[i] = reached[i + 1] or any(l.id in done for l in units[i].lessons)

    status: dict[int, str] = {}
    first, prev_done = True, True
    for i, unit in enumerate(units):
        gate = i == 0 or unit_target(units[i - 1].id) in passed or reached[i]
        for j, lesson in enumerate(unit.lessons):
            if lesson.id in done:
                status[lesson.id] = "completed"
            elif first or (prev_done and (j > 0 or gate)):
                status[lesson.id] = "unlocked"
            else:
                status[lesson.id] = "locked"
            prev_done, first = lesson.id in done, False
    return status


def unit_test_status(unit: Unit, status: dict[int, str], passed: set[str]) -> str:
    if unit_target(unit.id) in passed:
        return "passed"
    if unit.lessons and all(status.get(l.id) == "completed" for l in unit.lessons):
        return "unlocked"
    return "locked"


def section_test_status(course: Course, name: str, status: dict[int, str], passed: set[str]) -> str | None:
    """'available' while the section hasn't been reached yet, 'passed' once jumped, else None."""
    secs = sections(course)
    idx = next((i for i, (n, _) in enumerate(secs) if n == name), None)
    if not idx:  # unknown, or the first section (nothing to test out of)
        return None
    if section_target(course.id, name) in passed:
        return "passed"
    first_lesson = next((l for u in secs[idx][1] for l in u.lessons), None)
    return "available" if first_lesson is not None and status.get(first_lesson.id) == "locked" else None


def units_before_section(course: Course, name: str) -> list[Unit]:
    out: list[Unit] = []
    for n, units in sections(course):
        if n == name:
            return out
        out.extend(units)
    return []


def pick_questions(units: list[Unit], n: int) -> list[Exercise]:
    """Up to n quiz questions spread evenly over the units, most recent units first."""
    rng = random.SystemRandom()
    pools = []
    for unit in reversed(units):
        pool = [e for l in unit.lessons for e in l.exercises if e.kind in QUIZ_KINDS]
        rng.shuffle(pool)
        if pool:
            pools.append(pool)
    picked: list[Exercise] = []
    while len(picked) < n and any(pools):
        for pool in pools:
            if pool and len(picked) < n:
                picked.append(pool.pop())
    rng.shuffle(picked)
    return picked
