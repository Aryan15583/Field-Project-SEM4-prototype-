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
