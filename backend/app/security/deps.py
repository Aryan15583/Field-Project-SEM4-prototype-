from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AuditLog, User
from .ratelimit import client_ip
from .tokens import ACCESS_COOKIE, MFA_COOKIE, decode

UNAUTHORIZED = HTTPException(401, "Not authenticated")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(ACCESS_COOKIE)
    claims = decode(token, "access") if token else None
    if not claims:
        raise UNAUTHORIZED
    user = db.get(User, int(claims["sub"]))
    # token_version check makes "log out of all devices" and account disabling take effect instantly.
    if user is None or not user.is_active or not user.mfa_enabled or claims.get("ver") != user.token_version:
        raise UNAUTHORIZED
    request.state.user_id = user.id
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    # 404, not 403: to anyone who isn't an admin the admin API simply doesn't exist
    if user.role != "admin":
        raise HTTPException(404, "Not found")
    return user


def is_owner(user: User) -> bool:
    """Owners are the accounts listed in ADMIN_EMAILS: always admins, and no other admin can demote or disable them."""
    from ..config import get_settings

    return user.email.lower() in {e.lower() for e in get_settings().admin_emails}


def get_mfa_user(request: Request, db: Session, stage: str) -> User:
    token = request.cookies.get(MFA_COOKIE)
    claims = decode(token, "mfa") if token else None
    if not claims or claims.get("stage") != stage:
        raise HTTPException(401, "Sign-in session expired. Please sign in with Google again.")
    user = db.get(User, int(claims["sub"]))
    if user is None or not user.is_active:
        raise UNAUTHORIZED
    request.state.user_id = user.id
    return user


def audit(db: Session, request: Request | None, event: str, user_id: int | None = None, detail: str = "") -> None:
    db.add(AuditLog(user_id=user_id, event=event, ip=client_ip(request) if request else None, detail=detail[:500]))
