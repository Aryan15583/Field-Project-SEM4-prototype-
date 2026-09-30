"""Content management and moderation - admin role only, every change is audit-logged."""
from typing import Annotated, Literal

import regex
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import AuditLog, Course, Exercise, Lesson, Unit, User
from ..security import tokens
from ..security.deps import audit, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

Admin = Annotated[User, Depends(require_admin)]
DB = Annotated[Session, Depends(get_db)]

Short = Annotated[str, Field(min_length=1, max_length=200)]


class ExerciseIn(BaseModel):
    kind: Literal["mcq", "fill", "order", "code"]
    prompt: str = Field(min_length=1, max_length=1000)
    code: str | None = Field(None, max_length=2000)
    data: dict = Field(default_factory=dict)
    solution: dict = Field(default_factory=dict)
    explanation: str = Field("", max_length=1000)
    hint: str = Field("", max_length=500)

    @model_validator(mode="after")
    def check_shape(self):
        d, s = self.data, self.solution
        if self.kind == "mcq":
            opts = d.get("options")
            if not (isinstance(opts, list) and 2 <= len(opts) <= 6 and all(isinstance(o, str) and len(o) <= 200 for o in opts)):
                raise ValueError("mcq needs 2-6 string options")
            if not (isinstance(s.get("index"), int) and 0 <= s["index"] < len(opts)):
                raise ValueError("mcq solution.index out of range")
        elif self.kind == "fill":
            acc = s.get("accepted")
            if not (isinstance(acc, list) and 1 <= len(acc) <= 10 and all(isinstance(a, str) and a for a in acc)):
                raise ValueError("fill needs solution.accepted (1-10 strings)")
        elif self.kind == "order":
            lines = d.get("lines")
            if not (isinstance(lines, list) and 2 <= len(lines) <= 12 and all(isinstance(l, str) and len(l) <= 200 for l in lines)):
                raise ValueError("order needs 2-12 lines, in the correct order")
        elif self.kind == "code":
            pats = s.get("patterns")
            if not (isinstance(pats, list) and 1 <= len(pats) <= 10):
                raise ValueError("code needs solution.patterns (1-10 regexes)")
            for p in pats + list(s.get("forbid", [])):
                if not isinstance(p, str) or len(p) > 300:
                    raise ValueError("pattern too long")
                try:
                    regex.compile(p)
                except regex.error as exc:
                    raise ValueError(f"invalid regex {p!r}: {exc}") from exc
        return self


class LessonIn(BaseModel):
    unit_id: int
    title: Short
    intro: str = Field("", max_length=4000)
    xp_reward: int = Field(10, ge=1, le=50)
    exercises: list[ExerciseIn] = Field(min_length=1, max_length=20)


class CourseIn(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9-]{2,40}$")
    title: Short
    description: str = Field("", max_length=400)
    icon: str = Field("{}", max_length=8)


class UnitIn(BaseModel):
    course_id: int
    title: Short


class ActiveIn(BaseModel):
    active: bool


@router.get("/tree")
def tree(_: Admin, db: DB):
    courses = db.scalars(select(Course).order_by(Course.position).options(selectinload(Course.units).selectinload(Unit.lessons))).all()
    return [
        {"id": c.id, "slug": c.slug, "title": c.title,
         "units": [{"id": u.id, "title": u.title, "lessons": [{"id": l.id, "title": l.title} for l in u.lessons]} for u in c.units]}
        for c in courses
    ]


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, _: Admin, db: DB):
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(404, "Lesson not found")
    return {
        "id": lesson.id, "unit_id": lesson.unit_id, "title": lesson.title, "intro": lesson.intro, "xp_reward": lesson.xp_reward,
        "exercises": [
            {"kind": e.kind, "prompt": e.prompt, "code": e.code, "data": e.data, "solution": e.solution,
             "explanation": e.explanation, "hint": e.hint}
            for e in lesson.exercises
        ],
    }


def _apply_exercises(lesson: Lesson, items: list[ExerciseIn]) -> None:
    lesson.exercises.clear()
    for i, e in enumerate(items):
        lesson.exercises.append(Exercise(position=i, **e.model_dump()))


@router.post("/courses", status_code=201)
def create_course(body: CourseIn, request: Request, admin: Admin, db: DB):
    if db.scalar(select(Course.id).where(Course.slug == body.slug)):
        raise HTTPException(409, "Slug already exists")
    pos = (db.scalar(select(func.max(Course.position))) or 0) + 1
    course = Course(position=pos, **body.model_dump())
    db.add(course)
    db.flush()
    audit(db, request, "admin_course_create", admin.id, body.slug)
    db.commit()
    return {"id": course.id}


@router.post("/units", status_code=201)
def create_unit(body: UnitIn, request: Request, admin: Admin, db: DB):
    if db.get(Course, body.course_id) is None:
        raise HTTPException(404, "Course not found")
    pos = (db.scalar(select(func.max(Unit.position)).where(Unit.course_id == body.course_id)) or 0) + 1
    unit = Unit(course_id=body.course_id, title=body.title, position=pos)
    db.add(unit)
    db.flush()
    audit(db, request, "admin_unit_create", admin.id, body.title)
    db.commit()
    return {"id": unit.id}


@router.post("/lessons", status_code=201)
def create_lesson(body: LessonIn, request: Request, admin: Admin, db: DB):
    if db.get(Unit, body.unit_id) is None:
        raise HTTPException(404, "Unit not found")
    pos = (db.scalar(select(func.max(Lesson.position)).where(Lesson.unit_id == body.unit_id)) or 0) + 1
    lesson = Lesson(unit_id=body.unit_id, title=body.title, intro=body.intro, xp_reward=body.xp_reward, position=pos)
    _apply_exercises(lesson, body.exercises)
    db.add(lesson)
    db.flush()
    audit(db, request, "admin_lesson_create", admin.id, f"{lesson.id}:{body.title}")
    db.commit()
    return {"id": lesson.id}


@router.put("/lessons/{lesson_id}")
def update_lesson(lesson_id: int, body: LessonIn, request: Request, admin: Admin, db: DB):
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(404, "Lesson not found")
    lesson.title, lesson.intro, lesson.xp_reward = body.title, body.intro, body.xp_reward
    _apply_exercises(lesson, body.exercises)
    audit(db, request, "admin_lesson_update", admin.id, str(lesson_id))
    db.commit()
    return {"id": lesson.id}


@router.delete("/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, request: Request, admin: Admin, db: DB):
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(404, "Lesson not found")
    db.delete(lesson)
    audit(db, request, "admin_lesson_delete", admin.id, f"{lesson_id}:{lesson.title}")
    db.commit()
    return {"ok": True}


@router.get("/users")
def users(_: Admin, db: DB, limit: int = Query(100, ge=1, le=500)):
    rows = db.scalars(select(User).order_by(User.created_at.desc()).limit(limit)).all()
    return [
        {"id": u.id, "email": u.email, "name": u.name, "role": u.role, "active": u.is_active, "mfa": u.mfa_enabled,
         "xp": u.xp_total, "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None}
        for u in rows
    ]


@router.post("/users/{user_id}/active")
def set_active(user_id: int, body: ActiveIn, request: Request, admin: Admin, db: DB):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    if user.id == admin.id:
        raise HTTPException(400, "You can't disable your own account")
    user.is_active = body.active
    if not body.active:
        user.token_version += 1  # kill access tokens immediately
        tokens.revoke_all_for_user(db, user.id)
    audit(db, request, "admin_user_active", admin.id, f"user={user_id} active={body.active}")
    db.commit()
    return {"ok": True}


@router.get("/audit")
def audit_log(_: Admin, db: DB, limit: int = Query(100, ge=1, le=500)):
    rows = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all()
    return [
        {"id": r.id, "user_id": r.user_id, "event": r.event, "ip": r.ip, "detail": r.detail, "at": r.created_at.isoformat()}
        for r in rows
    ]
