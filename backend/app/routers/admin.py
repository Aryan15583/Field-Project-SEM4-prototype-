"""Content management and moderation - admin role only, every change is audit-logged."""
from typing import Annotated, Literal

import regex
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import AuditLog, Course, Exercise, Lesson, Unit, User
from ..security import mfa, tokens
from ..security.deps import audit, is_owner, require_admin
from ..security.ratelimit import limit
from ..services import grading

router = APIRouter(prefix="/api/admin", tags=["admin"])


Admin = Annotated[User, Depends(require_admin)]
DB = Annotated[Session, Depends(get_db)]


class DebugIn(BaseModel):
    on: bool


@router.post("/debug")
def set_debug_mode(body: DebugIn, request: Request, user: Admin, db: DB):
    """Admin-only debug mode: every lesson open and shown completed, unlimited hearts, ∞ XP / streak (display only -
    nothing is saved), and a TEST certificate for every course. Turning it off removes those test certificates."""
    from ..schemas import me_out
    from ..services import certificates

    user.debug_mode = body.on
    if body.on:
        certificates.issue_all_debug(db, user)
    else:
        certificates.drop_debug(db, user)
    audit(db, request, "admin_debug_on" if body.on else "admin_debug_off", user_id=user.id)
    db.commit()
    return me_out(db, user)

Short = Annotated[str, Field(min_length=1, max_length=200)]


class ExerciseIn(BaseModel):
    kind: Literal["mcq", "fill", "order", "code", "run"]
    prompt: str = Field(min_length=1, max_length=1000)
    code: str | None = Field(None, max_length=4000)
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
        elif self.kind == "run":
            _check_run(d, s)
        return self


RUN_LANGS = {"python", "javascript", "typescript", "git", "sql", "html", "java", "c", "cpp"}
TEST_KEYS = {"name", "stdin", "append", "selector", "prop"}


def _check_run(d: dict, s: dict) -> None:
    if d.get("language") not in RUN_LANGS:
        raise ValueError(f"run.language must be one of {sorted(RUN_LANGS)}")
    tests = d.get("tests")
    if not (isinstance(tests, list) and 1 <= len(tests) <= grading.MAX_TESTS):
        raise ValueError(f"run needs 1-{grading.MAX_TESTS} tests")
    for t in tests:
        if not isinstance(t, dict) or not set(t) <= TEST_KEYS or not all(isinstance(v, str) and len(v) <= 2000 for v in t.values()):
            raise ValueError(f"each test is an object with string keys from {sorted(TEST_KEYS)}")
        if d["language"] == "html" and not (t.get("selector") and t.get("prop")):
            raise ValueError("html tests need selector and prop")
    expected = s.get("expected")
    if not (isinstance(expected, list) and len(expected) == len(tests) and all(isinstance(e, str) for e in expected)):
        raise ValueError("run solution.expected must list one output string per test")
    for key in ("require", "forbid", "fallback"):
        for p in s.get(key, []):
            if not isinstance(p, str) or len(p) > 300:
                raise ValueError(f"{key} patterns must be strings under 300 chars")
            try:
                regex.compile(p)
            except regex.error as exc:
                raise ValueError(f"invalid regex {p!r}: {exc}") from exc
    if d["language"] in {"java", "c", "cpp"} and not s.get("fallback"):
        raise ValueError("java/c/cpp run exercises need solution.fallback patterns (used when no sandbox runner)")
    if not isinstance(d.get("setup", ""), str) or len(d.get("setup", "")) > 4000:
        raise ValueError("setup must be a string under 4000 chars")


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
    lesson.content_hash = None  # customised: curriculum sync will no longer overwrite it
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
def users(_: Admin, db: DB, limit: int = Query(100, ge=1, le=500), q: str = Query("", max_length=120)):
    query = select(User).order_by((User.role == "admin").desc(), User.created_at.desc()).limit(limit)
    if q.strip():
        like = f"%{q.strip().lower()}%"
        query = query.where(func.lower(User.email).like(like) | func.lower(User.name).like(like))
    return [
        {"id": u.id, "email": u.email, "name": u.name, "role": u.role, "owner": is_owner(u), "active": u.is_active,
         "mfa": u.mfa_enabled, "xp": u.xp_total, "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None}
        for u in db.scalars(query).all()
    ]


class RoleIn(BaseModel):
    role: Literal["admin", "learner"]
    code: str = Field(min_length=6, max_length=12)  # the acting admin's current 2-step code (re-confirmation)


@router.post("/confirm-code", dependencies=[Depends(limit("admin_confirm", 5))])
def send_confirm_code(request: Request, admin: Admin, db: DB):
    """Email a fresh code to an admin who confirms with emailed codes (authenticator users just open their app)."""
    if admin.mfa_method != "email":
        return {"method": "totp"}
    from .auth import _send_email_code

    return {"method": "email", **_send_email_code(db, request, admin, resend=True)}


@router.post("/users/{user_id}/role", dependencies=[Depends(limit("admin_role", 10))])
def set_role(user_id: int, body: RoleIn, request: Request, admin: Admin, db: DB):
    """Grant or remove admin access. Only admins can do this, and they must re-enter a 2-step code."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    if user.id == admin.id:
        raise HTTPException(400, "You can't change your own role")
    if is_owner(user):
        raise HTTPException(403, "Owner accounts (ADMIN_EMAILS) are always admins")
    if body.role == "admin" and not (user.is_active and user.mfa_enabled):
        raise HTTPException(400, "Only active accounts with 2-step verification set up can become admins")
    if mfa.is_locked(admin):
        raise HTTPException(429, "Too many failed attempts. Try again later.")
    ok = mfa.verify_email_code(admin, body.code) if admin.mfa_method == "email" else mfa.verify_totp(admin, body.code)
    if not ok:
        mfa.register_failure(admin)
        audit(db, request, "admin_role_confirm_failed", admin.id, f"user={user_id}")
        db.commit()
        raise HTTPException(400, "That code didn't match. Check it and try again.")
    admin.mfa_failed_count = 0
    if user.role != body.role:
        user.role = body.role  # checked on every request, so a removed admin loses access immediately
        audit(db, request, "admin_role_change", admin.id, f"user={user_id} {user.email} role={body.role}")
    db.commit()
    return {"ok": True, "role": user.role}


@router.post("/users/{user_id}/active")
def set_active(user_id: int, body: ActiveIn, request: Request, admin: Admin, db: DB):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    if user.id == admin.id:
        raise HTTPException(400, "You can't disable your own account")
    if is_owner(user):
        raise HTTPException(403, "Owner accounts can't be disabled here")
    if user.role == "admin" and not is_owner(admin):
        raise HTTPException(403, "Only an owner can disable another admin")
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
