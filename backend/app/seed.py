"""Keeps the database in step with the built-in curriculum (runs at start-up, idempotent).

- New courses/units/lessons are added.
- Built-in lessons whose content changed are updated in place (same lesson id, so learners keep
  their progress).
- Lessons an admin has edited (content_hash = None) are never overwritten.
Units are keyed "<course>/<n>" (or an explicit key such as "<course>/start1"); lessons "<course>/<unit#>/<lesson#>" unless a lesson sets an explicit `key`, so add new
lessons at the end of a unit (or give them a key) to keep existing keys stable.
"""
import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .curriculum import CURRICULUM
from .models import AppMeta, Course, Exercise, Lesson, Unit


def _hash(lesson: dict) -> str:
    return hashlib.sha256(json.dumps(lesson, sort_keys=True).encode()).hexdigest()


def _fill(lesson: Lesson, spec: dict) -> None:
    lesson.title = spec["title"]
    lesson.intro = spec["intro"]
    lesson.xp_reward = spec.get("xp", 10)
    lesson.is_project = bool(spec.get("project"))
    lesson.exercises.clear()
    for i, e in enumerate(spec["exercises"]):
        lesson.exercises.append(Exercise(position=i, **e))
    lesson.content_hash = _hash(spec)


# Bump when the sync rules below change, so every database is synced once with the new rules.
SYNC_VERSION = "1"
_DIGEST_KEY = "curriculum_digest"


def curriculum_digest() -> str:
    """Fingerprint of the built-in curriculum (plus the sync rules). ~0.02 s for the whole thing."""
    blob = json.dumps(CURRICULUM, sort_keys=True) + SYNC_VERSION
    return hashlib.sha256(blob.encode()).hexdigest()


def sync_curriculum(db: Session) -> None:
    # The sync below asks the database one question per lesson (~950 round trips). When the curriculum is exactly the
    # one we synced last time there is nothing to do, so a cold start (a free host waking up) skips all of it.
    digest = curriculum_digest()
    meta = db.get(AppMeta, _DIGEST_KEY)
    if meta is not None and meta.value == digest:
        return
    _sync(db)
    if meta is None:
        meta = AppMeta(key=_DIGEST_KEY)
        db.add(meta)
    meta.value = digest
    db.commit()


def _sync(db: Session) -> None:
    for ci, spec in enumerate(CURRICULUM):
        course = db.scalar(select(Course).where(Course.slug == spec["slug"]))
        if course is None:
            course = Course(slug=spec["slug"])
            db.add(course)
        course.title, course.description, course.icon, course.position = spec["title"], spec["description"], spec["icon"], ci
        db.flush()
        numbered = 0  # units with an explicit "key" (the Start-here units) don't consume a number
        for ui, uspec in enumerate(spec["units"]):
            if uspec.get("key"):
                ukey = f"{spec['slug']}/{uspec['key']}"
            else:
                numbered += 1
                ukey = f"{spec['slug']}/{numbered}"
            unit = db.scalar(select(Unit).where(Unit.key == ukey))
            if unit is None:
                unit = Unit(course_id=course.id, key=ukey)
                db.add(unit)
            unit.title, unit.position, unit.section = uspec["title"], ui, uspec.get("section", "Beginner")
            db.flush()
            for li, lspec in enumerate(uspec["lessons"]):
                lkey = lspec.get("key") or f"{ukey}/{li + 1}"
                lesson = db.scalar(select(Lesson).where(Lesson.key == lkey))
                if lesson is None:
                    lesson = Lesson(unit_id=unit.id, key=lkey, position=li)
                    _fill(lesson, lspec)
                    db.add(lesson)
                elif lesson.content_hash is not None and lesson.content_hash != _hash(lspec):
                    _fill(lesson, lspec)
                lesson.position = li
    db.commit()


# backwards-compatible name
seed_if_empty = sync_curriculum
