"""Authentication: Google sign-in -> mandatory 2-step verification (emailed code or authenticator app) -> session cookies."""
import hmac
import logging
import re
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import User
from ..schemas import MeOut, me_out
from ..security import mfa, tokens
from ..security.deps import audit, get_current_user, get_mfa_user
from ..security.ratelimit import client_ip, limit
from ..services import google_oauth, mailer

log = logging.getLogger("codeingo.auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

OAUTH_COOKIE = "cg_oauth"


def auth_limit():
    return limit("auth", get_settings().rate_limit_auth_per_minute)


class CodeIn(BaseModel):
    code: str = Field(min_length=6, max_length=32)


class VerifyIn(BaseModel):
    code: str | None = Field(None, max_length=12)
    recovery_code: str | None = Field(None, max_length=32)


class DevLoginIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=60)


@router.get("/csrf")
def csrf(response: Response):
    return {"csrf": tokens.set_csrf_cookie(response)}


@router.get("/config")
def auth_config():
    s = get_settings()
    return {"google": bool(s.google_client_id), "devLogin": s.dev_login_enabled, "emailDelivery": s.email_configured}


# ------------------------------------------------------------------ Google sign-in
@router.get("/google/login", dependencies=[Depends(auth_limit())])
def google_login():
    s = get_settings()
    if not s.google_client_id:
        raise HTTPException(503, "Google sign-in is not configured")
    flow = google_oauth.new_flow()
    signed = jwt.encode(
        {"typ": "oauth", "state": flow["state"], "nonce": flow["nonce"], "verifier": flow["verifier"],
         "exp": int(datetime.now(timezone.utc).timestamp()) + 600},
        s.secret_key, algorithm=tokens.ALGORITHM,
    )
    resp = RedirectResponse(google_oauth.authorization_url(flow), status_code=302)
    # Lax so it is sent on Google's top-level redirect back to us.
    resp.set_cookie(OAUTH_COOKIE, signed, max_age=600, httponly=True, secure=s.cookie_secure, samesite="lax", path="/api/auth/google")
    return resp


@router.get("/google/callback", dependencies=[Depends(auth_limit())])
async def google_callback(request: Request, code: str = "", state: str = "", db: Session = Depends(get_db)):
    s = get_settings()
    fail = RedirectResponse(f"{s.public_url}/?error=signin_failed", status_code=302)
    fail.delete_cookie(OAUTH_COOKIE, path="/api/auth/google")
    try:
        flow = jwt.decode(request.cookies.get(OAUTH_COOKIE, ""), s.secret_key, algorithms=[tokens.ALGORITHM])
        if flow.get("typ") != "oauth" or not code or len(code) > 512 or not state:
            raise ValueError("missing params")
        if not hmac.compare_digest(flow["state"], state):
            raise ValueError("state mismatch")  # CSRF on the OAuth flow
        claims = google_oauth.verify_id_token(await google_oauth.exchange_code(code, flow["verifier"]), flow["nonce"])
    except Exception as exc:  # never leak details to the browser
        log.warning("google sign-in failed: %s", exc)
        audit(db, request, "login_failed", detail=str(exc)[:200])
        db.commit()
        return fail

    user = _upsert_google_user(db, claims)
    if not user.is_active:
        audit(db, request, "login_blocked", user.id)
        db.commit()
        return fail
    stage = "verify" if user.mfa_enabled else "setup"
    audit(db, request, "google_ok", user.id)
    db.commit()
    resp = RedirectResponse(f"{s.public_url}/2fa/{stage}", status_code=302)
    resp.delete_cookie(OAUTH_COOKIE, path="/api/auth/google")
    tokens.set_mfa_cookie(resp, user, stage)
    return resp


def _upsert_google_user(db: Session, claims: dict) -> User:
    s = get_settings()
    email = claims["email"].lower()
    user = db.scalar(select(User).where(User.google_sub == claims["sub"]))
    if user is None:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, name=(claims.get("name") or email.split("@")[0])[:120], hearts=s.max_hearts)
            db.add(user)
        user.google_sub = claims["sub"]
    user.email = email
    pic = claims.get("picture") or ""
    # Google serves a 96px thumbnail by default; ask for 256px so avatars stay sharp on hi-res screens
    pic = re.sub(r"=s\d+(-c)?$", "=s256-c", pic)
    user.avatar_url = pic[:512] if pic.startswith("https://lh3.googleusercontent.com/") else None
    if email in [e.lower() for e in s.admin_emails]:
        user.role = "admin"
    db.flush()
    return user


# ------------------------------------------------------------------ dev-only login
@router.post("/dev-login", dependencies=[Depends(auth_limit())])
def dev_login(body: DevLoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    s = get_settings()
    if not s.dev_login_enabled or s.is_production:
        raise HTTPException(404, "Not found")
    email = body.email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, name=body.name, hearts=s.max_hearts)
        db.add(user)
    if email in [e.lower() for e in s.admin_emails]:
        user.role = "admin"
    db.flush()
    stage = "verify" if user.mfa_enabled else "setup"
    audit(db, request, "dev_login", user.id)
    db.commit()
    tokens.set_mfa_cookie(response, user, stage)
    return {"stage": stage}


# ------------------------------------------------------------------ 2-step verification
@router.get("/2fa/status")
def mfa_status(request: Request, db: Session = Depends(get_db)):
    for stage in ("setup", "verify"):
        try:
            user = get_mfa_user(request, db, stage)
            return {
                "stage": stage,
                "email": user.email,
                "email_masked": mfa.mask_email(user.email),
                "method": user.mfa_method if user.mfa_enabled else None,
                "has_recovery_codes": user.mfa_enabled and mfa.remaining_recovery_codes(db, user) > 0,
                "locked": mfa.is_locked(user),
                "resend_in": mfa.email_code_resend_in(user),
                # local development without a mail server prints codes to the API console
                "codes_in_console": get_settings().dev_login_enabled and not get_settings().email_configured,
            }
        except HTTPException:
            continue
    raise HTTPException(401, "Sign-in session expired. Please sign in again.")


@router.post("/2fa/setup", dependencies=[Depends(auth_limit())])
def mfa_setup(request: Request, db: Session = Depends(get_db)):
    user = get_mfa_user(request, db, "setup")
    if user.mfa_enabled:
        raise HTTPException(409, "2-step verification already enabled")
    uri, qr = mfa.start_enrollment(user)
    db.commit()
    secret = uri.split("secret=")[1].split("&")[0]
    return {"otpauth_uri": uri, "qr": qr, "secret": secret}


@router.post("/2fa/enable", dependencies=[Depends(auth_limit())])
def mfa_enable(body: CodeIn, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_mfa_user(request, db, "setup")
    if mfa.is_locked(user):
        raise HTTPException(429, "Too many failed attempts. Try again later.")
    if not mfa.verify_totp(user, body.code, pending=True):
        mfa.register_failure(user)
        audit(db, request, "mfa_setup_failed", user.id)
        db.commit()
        raise HTTPException(400, "That code didn't match. Check your authenticator app and try again.")
    user.totp_secret_enc, user.totp_pending_enc = user.totp_pending_enc, None
    user.mfa_enabled, user.mfa_method = True, "totp"
    user.mfa_failed_count = 0
    codes = mfa.new_recovery_codes(db, user)
    _start_session(db, request, response, user)
    audit(db, request, "mfa_enabled", user.id)
    db.commit()
    return {"recovery_codes": codes, "user": me_out(db, user)}


def _send_email_code(db: Session, request: Request, user: User) -> dict:
    """Emails a fresh code unless one went out moments ago (then the earlier code stays valid)."""
    try:
        code = mfa.issue_email_code(user)
    except mfa.EmailCodeThrottled as exc:
        db.commit()
        raise HTTPException(429, f"Too many codes requested. Try again in {exc.retry_after // 60 + 1} minutes.")
    if code is not None:
        minutes = get_settings().email_code_minutes
        app = get_settings().app_name
        try:
            mailer.send(
                user.email,
                f"{code} is your {app} verification code",
                f"Your {app} verification code is: {code}\n\n"
                f"It expires in {minutes} minutes and can be used once.\n"
                "If you didn't try to sign in, ignore this email - and consider signing out of all devices.",
                _code_email_html(app, code, minutes),
            )
        except mailer.MailError:
            user.email_code_hash = user.email_code_expires_at = user.email_code_sent_at = None
            db.commit()
            raise HTTPException(503, "We couldn't send the email right now. Please try again in a minute.")
        audit(db, request, "email_code_sent", user.id)
    db.commit()
    return {"sent_to": mfa.mask_email(user.email), "resend_in": mfa.email_code_resend_in(user)}


def _code_email_html(app: str, code: str, minutes: int) -> str:
    # Only fixed text and a 6-digit number go in here - no user-controlled content.
    return f"""<!doctype html><html><body style="margin:0;background:#f5f7fb;font-family:Arial,Helvetica,sans-serif;color:#111">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px">
<table role="presentation" width="100%" style="max-width:440px;background:#fff;border-radius:16px;padding:32px;border:1px solid #e3e8f0">
<tr><td style="font-size:22px;font-weight:800;color:#1d4ed8">{app}</td></tr>
<tr><td style="padding-top:20px;font-size:16px">Your verification code is:</td></tr>
<tr><td style="padding:16px 0;font-size:36px;font-weight:800;letter-spacing:8px;font-family:Consolas,Menlo,monospace">{code}</td></tr>
<tr><td style="font-size:14px;color:#555">It expires in {minutes} minutes and can be used once.<br><br>
If you didn't try to sign in, you can ignore this email.</td></tr>
</table></td></tr></table></body></html>"""


@router.post("/2fa/email/send", dependencies=[Depends(auth_limit())])
def mfa_email_send(request: Request, db: Session = Depends(get_db)):
    """Send (or resend) an emailed code - during first-time setup or at sign-in."""
    for stage in ("setup", "verify"):
        try:
            user = get_mfa_user(request, db, stage)
            break
        except HTTPException:
            continue
    else:
        raise HTTPException(401, "Sign-in session expired. Please sign in again.")
    if stage == "verify" and user.mfa_method != "email":
        raise HTTPException(400, "This account uses an authenticator app")
    if mfa.is_locked(user):
        raise HTTPException(429, "Too many failed attempts. Try again later.")
    return _send_email_code(db, request, user)


@router.post("/2fa/email/enable", dependencies=[Depends(auth_limit())])
def mfa_email_enable(body: CodeIn, request: Request, response: Response, db: Session = Depends(get_db)):
    """First-time setup with emailed codes: proving you can read your inbox turns it on."""
    user = get_mfa_user(request, db, "setup")
    if user.mfa_enabled:
        raise HTTPException(409, "2-step verification already enabled")
    if mfa.is_locked(user):
        raise HTTPException(429, "Too many failed attempts. Try again later.")
    if not mfa.verify_email_code(user, body.code):
        mfa.register_failure(user)
        audit(db, request, "mfa_setup_failed", user.id)
        db.commit()
        raise HTTPException(400, "That code didn't match or has expired. Check your email or send a new code.")
    user.mfa_enabled, user.mfa_method, user.mfa_failed_count = True, "email", 0
    user.totp_pending_enc = None
    _start_session(db, request, response, user)
    audit(db, request, "mfa_enabled", user.id, "email")
    db.commit()
    return {"user": me_out(db, user)}


@router.post("/2fa/verify", dependencies=[Depends(auth_limit())])
def mfa_verify(body: VerifyIn, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_mfa_user(request, db, "verify")
    if mfa.is_locked(user):
        audit(db, request, "mfa_locked", user.id)
        db.commit()
        raise HTTPException(429, "Too many failed attempts. Try again later.")
    ok = False
    if body.code:
        ok = mfa.verify_email_code(user, body.code) if user.mfa_method == "email" else mfa.verify_totp(user, body.code)
    elif body.recovery_code:
        ok = mfa.use_recovery_code(db, user, body.recovery_code)
        if ok:
            audit(db, request, "recovery_code_used", user.id)
    if not ok:
        mfa.register_failure(user)
        audit(db, request, "mfa_failed", user.id)
        db.commit()
        raise HTTPException(400, "Invalid verification code")
    user.mfa_failed_count = 0
    _start_session(db, request, response, user)
    audit(db, request, "login", user.id)
    db.commit()
    return {"user": me_out(db, user)}


def _start_session(db: Session, request: Request, response: Response, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)
    raw = tokens.issue_refresh_token(db, user, ua=request.headers.get("user-agent", ""), ip=client_ip(request))
    tokens.set_session_cookies(response, user, raw)


# ------------------------------------------------------------------ session management
@router.post("/refresh", dependencies=[Depends(auth_limit())])
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    raw = request.cookies.get(tokens.REFRESH_COOKIE)
    if not raw:
        raise HTTPException(401, "Not authenticated")
    user, new_raw = tokens.rotate_refresh_token(db, raw, request.headers.get("user-agent", ""), client_ip(request))
    if user is None:
        if new_raw == "reuse":
            audit(db, request, "refresh_reuse_detected")
            db.commit()
        expired = JSONResponse({"detail": "Session expired"}, status_code=401)
        tokens.clear_session_cookies(expired)
        return expired
    tokens.set_session_cookies(response, user, new_raw, rotate_csrf=False)
    return {"ok": True}


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    raw = request.cookies.get(tokens.REFRESH_COOKIE)
    if raw:
        tokens.revoke_raw(db, raw)
        db.commit()
    tokens.clear_session_cookies(response)
    return {"ok": True}


@router.post("/logout-all")
def logout_all(request: Request, response: Response, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.token_version += 1
    tokens.revoke_all_for_user(db, user.id)
    audit(db, request, "logout_all", user.id)
    db.commit()
    tokens.clear_session_cookies(response)
    return {"ok": True}


@router.post("/recovery-codes", dependencies=[Depends(auth_limit())])
def regenerate_recovery_codes(body: CodeIn, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Re-authenticate with a fresh TOTP code before issuing new recovery codes."""
    if user.mfa_method != "totp":
        raise HTTPException(400, "Recovery codes are only used with an authenticator app")
    if mfa.is_locked(user) or not mfa.verify_totp(user, body.code):
        mfa.register_failure(user)
        db.commit()
        raise HTTPException(400, "Invalid verification code")
    codes = mfa.new_recovery_codes(db, user)
    audit(db, request, "recovery_codes_regenerated", user.id)
    db.commit()
    return {"recovery_codes": codes}


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return me_out(db, user)
