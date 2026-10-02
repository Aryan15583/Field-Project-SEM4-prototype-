"""WebAuthn passkeys: register on a signed-in account, then sign in with Face ID / fingerprint / PIN / security key.

User verification is required, so a passkey is two factors in one (the device + the biometric or PIN that unlocks
it) and signing in with one skips the emailed code. Challenges are random, stored server-side, expire after five
minutes and are deleted when used, so a captured response can't be replayed.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.exceptions import InvalidAuthenticationResponse, InvalidRegistrationResponse
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    AuthenticatorTransport,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from ..config import get_settings
from ..models import Passkey, User, WebAuthnChallenge
from .tokens import aware

CHALLENGE_COOKIE = "cg_webauthn"
CHALLENGE_MINUTES = 5
MAX_PASSKEYS = 10


def rp() -> tuple[str, str]:
    """(relying-party id, expected origin) - both derived from PUBLIC_URL."""
    url = urlparse(get_settings().public_url)
    return url.hostname or "localhost", f"{url.scheme}://{url.netloc}"


def user_handle(user: User) -> bytes:
    """Stable, opaque WebAuthn user id - no email or database id is stored on the authenticator."""
    return hmac.new(get_settings().secret_key.encode(), f"webauthn:{user.id}".encode(), hashlib.sha256).digest()[:16]


def _store_challenge(db: Session, response: Response, challenge: bytes, purpose: str, user: User | None) -> None:
    now = datetime.now(timezone.utc)
    db.execute(delete(WebAuthnChallenge).where(WebAuthnChallenge.expires_at < now))
    row = WebAuthnChallenge(
        challenge=bytes_to_base64url(challenge), purpose=purpose, user_id=user.id if user else None,
        expires_at=now + timedelta(minutes=CHALLENGE_MINUTES),
    )
    db.add(row)
    db.commit()
    response.set_cookie(
        CHALLENGE_COOKIE, row.id, max_age=CHALLENGE_MINUTES * 60, path="/api/auth/passkeys",
        httponly=True, secure=get_settings().cookie_secure, samesite="strict",
    )


def _take_challenge(db: Session, request: Request, response: Response, purpose: str, user: User | None) -> bytes:
    """Fetch and delete the pending challenge - every challenge works at most once."""
    response.delete_cookie(CHALLENGE_COOKIE, path="/api/auth/passkeys")
    cid = request.cookies.get(CHALLENGE_COOKIE, "")
    row = db.get(WebAuthnChallenge, cid) if cid else None
    if row is not None:
        db.delete(row)
        db.commit()
    if (
        row is None
        or row.purpose != purpose
        or aware(row.expires_at) < datetime.now(timezone.utc)
        or (user is not None and row.user_id != user.id)
    ):
        raise HTTPException(400, "This passkey request expired. Please try again.")
    return base64url_to_bytes(row.challenge)


def registration_options(db: Session, response: Response, user: User) -> str:
    rp_id, _ = rp()
    existing = db.scalars(select(Passkey).where(Passkey.user_id == user.id)).all()
    if len(existing) >= MAX_PASSKEYS:
        raise HTTPException(400, f"You can have up to {MAX_PASSKEYS} passkeys. Remove one first.")
    challenge = secrets.token_bytes(32)
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="Codeingo",
        user_id=user_handle(user),
        user_name=user.email,
        user_display_name=user.name,
        challenge=challenge,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,  # discoverable: sign in without typing an email
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        exclude_credentials=[PublicKeyCredentialDescriptor(id=base64url_to_bytes(p.credential_id)) for p in existing],
    )
    _store_challenge(db, response, challenge, "register", user)
    return options_to_json(options)


def register(db: Session, request: Request, response: Response, user: User, credential: dict, name: str) -> Passkey:
    rp_id, origin = rp()
    challenge = _take_challenge(db, request, response, "register", user)
    try:
        v = verify_registration_response(
            credential=credential, expected_challenge=challenge, expected_rp_id=rp_id, expected_origin=origin,
            require_user_verification=True,
        )
    except (InvalidRegistrationResponse, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(400, "That passkey couldn't be verified.") from exc
    cred_id = bytes_to_base64url(v.credential_id)
    if db.scalar(select(Passkey.id).where(Passkey.credential_id == cred_id)):
        raise HTTPException(400, "That passkey is already registered.")
    transports = [t for t in (credential.get("response", {}).get("transports") or []) if t in {x.value for x in AuthenticatorTransport}]
    pk = Passkey(
        user_id=user.id, credential_id=cred_id, public_key=bytes_to_base64url(v.credential_public_key),
        sign_count=v.sign_count, transports=transports[:6], name=name, backed_up=bool(v.credential_backed_up),
    )
    db.add(pk)
    db.commit()
    return pk


def login_options(db: Session, response: Response) -> str:
    rp_id, _ = rp()
    challenge = secrets.token_bytes(32)
    # no allow-list: the browser offers whichever passkeys this device has for the site
    options = generate_authentication_options(rp_id=rp_id, challenge=challenge, user_verification=UserVerificationRequirement.REQUIRED)
    _store_challenge(db, response, challenge, "login", None)
    return options_to_json(options)


def authenticate(db: Session, request: Request, response: Response, credential: dict) -> User:
    rp_id, origin = rp()
    challenge = _take_challenge(db, request, response, "login", None)
    fail = HTTPException(400, "That passkey isn't registered here. Sign in another way, then add it in your profile.")
    raw_id = credential.get("rawId") or credential.get("id")
    if not isinstance(raw_id, str) or len(raw_id) > 1400:
        raise fail
    pk = db.scalar(select(Passkey).where(Passkey.credential_id == raw_id.rstrip("=")))
    if pk is None:
        raise fail
    user = db.get(User, pk.user_id)
    if user is None or not user.is_active:
        raise HTTPException(403, "This account is disabled.")
    handle = (credential.get("response") or {}).get("userHandle")
    if handle and handle.rstrip("=") != bytes_to_base64url(user_handle(user)):
        raise fail
    try:
        v = verify_authentication_response(
            credential=credential, expected_challenge=challenge, expected_rp_id=rp_id, expected_origin=origin,
            credential_public_key=base64url_to_bytes(pk.public_key), credential_current_sign_count=pk.sign_count,
            require_user_verification=True,
        )
    except (InvalidAuthenticationResponse, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(400, "That passkey couldn't be verified.") from exc
    pk.sign_count = v.new_sign_count
    pk.last_used_at = datetime.now(timezone.utc)
    return user


def public(pk: Passkey) -> dict:
    return {
        "id": pk.id,
        "name": pk.name,
        "synced": pk.backed_up,
        "created_at": aware(pk.created_at).isoformat(),
        "last_used_at": aware(pk.last_used_at).isoformat() if pk.last_used_at else None,
    }
