"""Course certificates: issued automatically once every lesson (projects included) is complete and
every chapter test is passed. The certificate id is an unguessable public verification code."""
import secrets
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Certificate, Course, Unit, User
from . import progress


def eligible(db: Session, user: User, course: Course) -> bool:
    done = progress.completed_ids(db, user)
    passed = progress.passed_targets(db, user)
    lessons = [l for u in course.units for l in u.lessons]
    return bool(lessons) and all(l.id in done for l in lessons) and all(progress.unit_target(u.id) in passed for u in course.units)


def maybe_issue(db: Session, user: User, course_id: int) -> Certificate | None:
    """Issue the course certificate if it's now earned. Returns it only when newly issued."""
    if db.scalar(select(Certificate.id).where(Certificate.user_id == user.id, Certificate.course_id == course_id)):
        return None
    course = db.scalar(select(Course).where(Course.id == course_id).options(selectinload(Course.units).selectinload(Unit.lessons)))
    if course is None or not eligible(db, user, course):
        return None
    cert = Certificate(
        id=secrets.token_urlsafe(12), user_id=user.id, course_id=course.id, holder_name=user.name,
        course_title=course.title, lessons=sum(len(u.lessons) for u in course.units),
    )
    db.add(cert)
    db.flush()
    return cert


def issue_all_debug(db: Session, user: User) -> None:
    """Admin debug mode: make sure the admin holds a certificate for every course, marked as TEST certificates."""
    have = set(db.scalars(select(Certificate.course_id).where(Certificate.user_id == user.id)))
    for course in db.scalars(select(Course).options(selectinload(Course.units).selectinload(Unit.lessons))):
        if course.id in have:
            continue
        db.add(Certificate(
            id=secrets.token_urlsafe(12), user_id=user.id, course_id=course.id, holder_name=user.name, course_title=course.title,
            lessons=sum(len(u.lessons) for u in course.units), debug=True,
        ))
    db.flush()


def drop_debug(db: Session, user: User) -> None:
    for cert in db.scalars(select(Certificate).where(Certificate.user_id == user.id, Certificate.debug.is_(True))):
        db.delete(cert)


def public(cert: Certificate) -> dict:
    return {"code": cert.id, "name": cert.holder_name, "course": cert.course_title, "lessons": cert.lessons,
            "issued_at": _utc(cert.issued_at).isoformat(), "debug": bool(cert.debug)}


def _utc(dt):
    """SQLite returns naive datetimes; they're stored as UTC."""
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
