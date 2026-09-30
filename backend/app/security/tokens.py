"""JWT access tokens, short-lived MFA tokens, rotating refresh tokens and auth cookies."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import RefreshToken, User, new_id

ALGORITHM = "HS256"
ISSUER = "codeingo"

ACCESS_COOKIE = "cg_access"
REFRESH_COOKIE = "cg_refresh"
MFA_COOKIE = "cg_mfa"
CSRF_COOKIE = "cg_csrf"
REFRESH_PATH = "/api/auth"


def aware(dt: datetime | None) -> datetime | None:
    """SQLite drops tzinfo; treat stored naive datetimes as UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _encode(claims: dict, minutes: int) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {**claims, "iss": ISSUER, "iat": now, "nbf": now, "exp": now + timedelta(minutes=minutes), "jti": new_id()}
    return jwt.encode(payload, s.secret_key, algorithm=ALGORITHM)


def decode(token: str, typ: str) -> dict | None:
    """Return claims if the token is valid AND of the expected type, else None."""
    try:
        claims = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[ALGORITHM],  # pinned: prevents alg=none / algorithm confusion
            issuer=ISSUER,
            options={"require": ["exp", "iat", "iss", "sub", "typ"]},
        )
    except jwt.PyJWTError:
        return None
    return claims if claims.get("typ") == typ else None


def create_access_token(user: User) -> str:
    s = get_settings()
    return _encode({"sub": str(user.id), "typ": "access", "ver": user.token_version, "role": user.role}, s.access_token_minutes)


def create_mfa_token(user: User, stage: str) -> str:
    """Issued after Google sign-in, before 2-step verification. stage: 'setup' | 'verify'."""
    return _encode({"sub": str(user.id), "typ": "mfa", "stage": stage}, get_settings().mfa_token_minutes)


# ---------------------------------------------------------------- refresh tokens
def issue_refresh_token(db: Session, user: User, family_id: str | None = None, ua: str = "", ip: str = "") -> str:
    raw = secrets.token_urlsafe(48)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=sha256(raw),
            family_id=family_id or new_id(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=get_settings().refresh_token_days),
            user_agent=ua[:256],
            ip=ip[:64],
        )
    )
    return raw


def rotate_refresh_token(db: Session, raw: str, ua: str = "", ip: str = "") -> tuple[User, str] | tuple[None, str]:
    """Returns (user, new_raw_token) on success, or (None, reason)."""
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == sha256(raw)))
    if row is None:
        return None, "unknown"
    now = datetime.now(timezone.utc)
    if row.revoked_at is not None:
        # A rotated token was presented again -> likely stolen. Kill the whole family.
        revoke_family(db, row.family_id)
        db.commit()
        return None, "reuse"
    if aware(row.expires_at) < now:
        return None, "expired"
    user = db.get(User, row.user_id)
    if user is None or not user.is_active or not user.mfa_enabled:
        return None, "inactive"
    row.revoked_at = now
    new_raw = issue_refresh_token(db, user, row.family_id, ua, ip)
    db.commit()
    return user, new_raw


def revoke_family(db: Session, family_id: str) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc))
    )


def revoke_all_for_user(db: Session, user_id: int) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc))
    )


def revoke_raw(db: Session, raw: str) -> None:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == sha256(raw)))
    if row:
        revoke_family(db, row.family_id)


# ---------------------------------------------------------------- cookies
def _cookie_kwargs() -> dict:
    return {"httponly": True, "secure": get_settings().cookie_secure, "samesite": "strict"}


def set_csrf_cookie(response: Response) -> str:
    token = secrets.token_urlsafe(32)
    # Readable by JS on purpose (double-submit pattern); useless to an attacker on another origin.
    response.set_cookie(CSRF_COOKIE, token, httponly=False, secure=get_settings().cookie_secure, samesite="strict", path="/")
    return token


def set_session_cookies(response: Response, user: User, refresh_raw: str, rotate_csrf: bool = True) -> None:
    s = get_settings()
    response.set_cookie(ACCESS_COOKIE, create_access_token(user), max_age=s.access_token_minutes * 60, path="/", **_cookie_kwargs())
    response.set_cookie(REFRESH_COOKIE, refresh_raw, max_age=s.refresh_token_days * 86400, path=REFRESH_PATH, **_cookie_kwargs())
    response.delete_cookie(MFA_COOKIE, path="/")
    if rotate_csrf:  # new token at login (prevents fixation); kept on refresh so in-flight requests don't break
        set_csrf_cookie(response)


def set_mfa_cookie(response: Response, user: User, stage: str) -> None:
    s = get_settings()
    # Lax: this cookie is set on the redirect back from Google (a cross-site navigation).
    response.set_cookie(
        MFA_COOKIE, create_mfa_token(user, stage), max_age=s.mfa_token_minutes * 60, path="/",
        httponly=True, secure=s.cookie_secure, samesite="lax",
    )


def clear_session_cookies(response: Response) -> None:
    for name, path in ((ACCESS_COOKIE, "/"), (REFRESH_COOKIE, REFRESH_PATH), (MFA_COOKIE, "/")):
        response.delete_cookie(name, path=path)
