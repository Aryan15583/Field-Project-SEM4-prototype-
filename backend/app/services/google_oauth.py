"""Google sign-in via OpenID Connect authorization-code flow with PKCE, state and nonce."""
import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from ..config import get_settings

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def new_flow() -> dict:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return {"state": secrets.token_urlsafe(24), "nonce": secrets.token_urlsafe(24), "verifier": verifier, "challenge": challenge}


def authorization_url(flow: dict) -> str:
    s = get_settings()
    params = {
        "client_id": s.google_client_id,
        "redirect_uri": s.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": flow["state"],
        "nonce": flow["nonce"],
        "code_challenge": flow["challenge"],
        "code_challenge_method": "S256",
        "prompt": "select_account",
        "access_type": "online",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


async def exchange_code(code: str, verifier: str) -> str:
    s = get_settings()
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": s.google_client_id,
                "client_secret": s.google_client_secret,
                "redirect_uri": s.google_redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": verifier,
            },
        )
    resp.raise_for_status()
    return resp.json()["id_token"]


def verify_id_token(token: str, nonce: str) -> dict:
    """Verifies signature (Google JWKS), audience, issuer, expiry, nonce and email verification."""
    s = get_settings()
    claims = id_token.verify_oauth2_token(token, google_requests.Request(), s.google_client_id, clock_skew_in_seconds=10)
    if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise ValueError("bad issuer")
    if not secrets.compare_digest(str(claims.get("nonce", "")), nonce):
        raise ValueError("bad nonce")
    if not claims.get("email_verified"):
        raise ValueError("email not verified")
    email = claims["email"].lower()
    if s.allowed_email_domains and email.rsplit("@", 1)[-1] not in s.allowed_email_domains:
        raise ValueError("email domain not allowed")
    return claims
