"""TOTP 2-step verification (RFC 6238) with replay protection, lockout and recovery codes."""
import base64
import hmac
import io
import secrets
import time
from datetime import datetime, timedelta, timezone

import pyotp
import qrcode
import qrcode.image.svg
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import RecoveryCode, User
from .tokens import aware, sha256

RECOVERY_CODE_COUNT = 10


def encrypt(secret: str) -> str:
    return get_settings().fernet.encrypt(secret.encode()).decode()


def decrypt(token: str) -> str:
    return get_settings().fernet.decrypt(token.encode()).decode()


def start_enrollment(user: User) -> tuple[str, str]:
    """Creates a pending secret. Returns (otpauth_uri, qr_svg_data_uri)."""
    secret = pyotp.random_base32(32)
    user.totp_pending_enc = encrypt(secret)
    uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=get_settings().app_name)
    img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage, box_size=8)
    buf = io.BytesIO()
    img.save(buf)
    return uri, "data:image/svg+xml;base64," + base64.b64encode(buf.getvalue()).decode()


def is_locked(user: User) -> bool:
    locked = aware(user.mfa_locked_until)
    return locked is not None and locked > datetime.now(timezone.utc)


def register_failure(user: User) -> None:
    s = get_settings()
    user.mfa_failed_count += 1
    if user.mfa_failed_count >= s.mfa_max_failures:
        user.mfa_locked_until = datetime.now(timezone.utc) + timedelta(minutes=s.mfa_lockout_minutes)
        user.mfa_failed_count = 0


def _clean(code: str) -> str:
    return "".join(ch for ch in code if ch.isalnum()).upper()


def verify_totp(user: User, code: str, *, pending: bool = False) -> bool:
    enc = user.totp_pending_enc if pending else user.totp_secret_enc
    code = _clean(code)
    if not enc or len(code) != 6 or not code.isdigit():
        return False
    totp = pyotp.TOTP(decrypt(enc))
    now_step = int(time.time()) // 30
    for step in (now_step - 1, now_step, now_step + 1):  # +/- 30s clock drift
        if hmac.compare_digest(totp.at(step * 30), code):
            if step <= user.totp_last_step:  # code already used -> replay
                return False
            user.totp_last_step = step
            return True
    return False


def new_recovery_codes(db: Session, user: User) -> list[str]:
    for old in db.scalars(select(RecoveryCode).where(RecoveryCode.user_id == user.id)):
        db.delete(old)
    codes = [f"{secrets.token_hex(4)}-{secrets.token_hex(4)}".upper() for _ in range(RECOVERY_CODE_COUNT)]
    for c in codes:
        db.add(RecoveryCode(user_id=user.id, code_hash=sha256(_clean(c))))
    return codes


def use_recovery_code(db: Session, user: User, code: str) -> bool:
    h = sha256(_clean(code))
    row = db.scalar(
        select(RecoveryCode).where(RecoveryCode.user_id == user.id, RecoveryCode.code_hash == h, RecoveryCode.used_at.is_(None))
    )
    if row is None:
        return False
    row.used_at = datetime.now(timezone.utc)
    return True


def remaining_recovery_codes(db: Session, user: User) -> int:
    return len(list(db.scalars(select(RecoveryCode.id).where(RecoveryCode.user_id == user.id, RecoveryCode.used_at.is_(None)))))


# ------------------------------------------------------------------ emailed sign-in codes
class EmailCodeThrottled(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after


def _email_code_hash(user: User, code: str) -> str:
    # Keyed with the server secret: a leaked database alone can't be brute-forced back into codes.
    key = get_settings().secret_key.encode()
    return hmac.new(key, f"email-code:{user.id}:{user.email}:{code}".encode(), "sha256").hexdigest()


def _live_email_code(user: User) -> bool:
    expires = aware(user.email_code_expires_at)
    return bool(user.email_code_hash) and expires is not None and expires > datetime.now(timezone.utc)


def email_code_resend_in(user: User) -> int:
    """Seconds until another code may be sent. Only an unused, unexpired code holds a resend back -
    once a code is used up (e.g. signing out and straight back in) a new one goes out immediately."""
    sent = aware(user.email_code_sent_at)
    if sent is None or not _live_email_code(user):
        return 0
    wait = get_settings().email_code_resend_seconds - (datetime.now(timezone.utc) - sent).total_seconds()
    return max(0, int(wait + 0.999))


def issue_email_code(user: User, *, resend: bool = False) -> str | None:
    """Creates a fresh 6-digit code, or returns None when the code already sent should be used:
    - without `resend` (e.g. the sign-in page loading or reloading) whenever a code is still valid,
      so a reload never silently replaces the code the learner is about to type;
    - with `resend` (the learner asked for a new code) only during the short cooldown.
    Raises EmailCodeThrottled when the hourly limit is reached."""
    s = get_settings()
    now = datetime.now(timezone.utc)
    if email_code_resend_in(user) > 0 or (not resend and _live_email_code(user)):
        return None
    window = aware(user.email_code_window_start)
    if window is None or now - window >= timedelta(hours=1):
        user.email_code_window_start, user.email_code_window_count = now, 0
    if user.email_code_window_count >= s.email_code_max_per_hour:
        raise EmailCodeThrottled(int((aware(user.email_code_window_start) + timedelta(hours=1) - now).total_seconds()) + 1)
    code = f"{secrets.randbelow(1_000_000):06d}"
    user.email_code_hash = _email_code_hash(user, code)
    user.email_code_expires_at = now + timedelta(minutes=s.email_code_minutes)
    user.email_code_sent_at = now
    user.email_code_attempts = 0
    user.email_code_window_count += 1
    return code


def verify_email_code(user: User, code: str) -> bool:
    """Single use, expires, and only a few guesses per code."""
    code = _clean(code)
    if not _live_email_code(user):
        return False
    user.email_code_attempts += 1
    ok = len(code) == 6 and code.isdigit() and hmac.compare_digest(user.email_code_hash, _email_code_hash(user, code))
    if ok or user.email_code_attempts >= get_settings().email_code_max_attempts:
        user.email_code_hash = user.email_code_expires_at = None  # used up (or too many guesses)
    return ok


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    shown = local[:2] if len(local) > 3 else local[:1]
    return f"{shown}•••••@{domain}"  # fixed width: doesn't reveal the address length
