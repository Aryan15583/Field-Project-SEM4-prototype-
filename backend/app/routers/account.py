"""Your data, your call: download everything we hold about you, or delete the account for good."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    AuditLog,
    Certificate,
    ContestEntry,
    Follow,
    Passkey,
    PracticeAttempt,
    ReviewItem,
    User,
    UserBadge,
    UserLesson,
    UserTest,
    XpEvent,
)
from ..security import mfa, tokens
from ..security.deps import audit, get_current_user, is_owner
from ..security.ratelimit import limit

router = APIRouter(prefix="/api/account", tags=["account"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


class DeleteIn(BaseModel):
    code: str = Field(min_length=6, max_length=12)  # the current 2-step code, re-confirming it's really you


def _iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).isoformat() if dt else None


@router.get("/export", dependencies=[Depends(limit("account_export", 5))])
def export(user: CurrentUser, db: DB, response: Response):
    """Everything tied to your account as one JSON file (never includes secrets, hashes or other people's data)."""
    response.headers["Content-Disposition"] = 'attachment; filename="codeingo-my-data.json"'
    response.headers["Cache-Control"] = "no-store"
    rows = lambda model: list(db.scalars(select(model).where(model.user_id == user.id)))  # noqa: E731
    return {
        "exported_at": _iso(datetime.now(timezone.utc)),
        "account": {
            "email": user.email, "name": user.name, "role": user.role, "created_at": _iso(user.created_at),
            "last_login_at": _iso(user.last_login_at), "two_step_method": user.mfa_method, "friend_code": user.friend_code,
            "streak_emails": user.reminder_emails, "daily_goal": user.daily_goal,
        },
        "progress": {
            "xp_total": user.xp_total, "streak_current": user.streak_current, "streak_best": user.streak_best, "hearts": user.hearts,
            "badges": [{"badge": b.badge, "earned_at": _iso(b.earned_at)} for b in rows(UserBadge)],
            "lessons": [{"lesson_id": r.lesson_id, "completed": r.completed_count, "perfect": r.perfect, "tested_out": r.tested_out} for r in rows(UserLesson)],
            "tests": [{"target": r.target, "best_score": r.best_score, "attempts": r.attempts, "passed_at": _iso(r.passed_at)} for r in rows(UserTest)],
            "xp_events": [{"amount": r.amount, "reason": r.reason, "at": _iso(r.created_at)} for r in rows(XpEvent)],
            "review_items": [{"exercise_id": r.exercise_id, "box": r.box, "lapses": r.lapses, "reviews": r.reviews} for r in rows(ReviewItem)],
            "practice_sessions": len(rows(PracticeAttempt)),
            "contests": [{"contest_id": r.contest_id, "score": r.score, "time_ms": r.time_ms} for r in rows(ContestEntry)],
        },
        "certificates": [{"code": c.id, "course": c.course_title, "name": c.holder_name, "issued_at": _iso(c.issued_at)} for c in rows(Certificate)],
        "passkeys": [{"name": p.name, "created_at": _iso(p.created_at), "last_used_at": _iso(p.last_used_at)} for p in rows(Passkey)],
        "following": [f.followee_id for f in db.scalars(select(Follow).where(Follow.follower_id == user.id))],
    }


@router.post("/confirm-code", dependencies=[Depends(limit("account_confirm", 5))])
def send_confirm_code(request: Request, user: CurrentUser, db: DB):
    """Email a fresh code (authenticator users just open their app) before a destructive action."""
    if user.mfa_method != "email":
        return {"method": "totp"}
    from .auth import _send_email_code

    return {"method": "email", **_send_email_code(db, request, user, resend=True)}


@router.post("/delete", dependencies=[Depends(limit("account_delete", 5))])
def delete_account(body: DeleteIn, request: Request, response: Response, user: CurrentUser, db: DB):
    """Permanently delete the account and everything linked to it. Needs a fresh 2-step code."""
    if is_owner(user):
        raise HTTPException(403, "Owner accounts (listed in ADMIN_EMAILS) can't be deleted here - remove the email from ADMIN_EMAILS first.")
    if mfa.is_locked(user):
        raise HTTPException(429, "Too many failed attempts. Try again later.")
    ok = mfa.verify_email_code(user, body.code) if user.mfa_method == "email" else mfa.verify_totp(user, body.code)
    if not ok:
        mfa.register_failure(user)
        audit(db, request, "account_delete_failed", user.id)
        db.commit()
        raise HTTPException(400, "That code didn't match. Check it and try again.")
    # keep a trace that a deletion happened, but nothing that identifies the person
    db.execute(update(AuditLog).where(AuditLog.user_id == user.id).values(ip=None, detail=""))
    audit(db, request, "account_deleted", None)
    tokens.revoke_all_for_user(db, user.id)
    db.delete(user)  # every table that points at users cascades
    db.commit()
    tokens.clear_session_cookies(response)
    return {"ok": True}
