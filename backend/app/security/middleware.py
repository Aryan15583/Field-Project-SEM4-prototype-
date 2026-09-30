"""HTTP-level protections applied to every request."""
import hmac
from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ..config import get_settings
from . import ratelimit
from .tokens import CSRF_COOKIE

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

CSP = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https://lh3.googleusercontent.com",
        "font-src 'self'",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "form-action 'self' https://accounts.google.com",
        "base-uri 'none'",
        "object-src 'none'",
    ]
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        h = response.headers
        h.setdefault("Content-Security-Policy", CSP)
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        h.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        h.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        if get_settings().cookie_secure:
            h.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        if request.url.path.startswith("/api/"):
            h.setdefault("Cache-Control", "no-store")
        if "server" in h:
            del h["server"]
        return response


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """Coarse per-IP limit on all API traffic (application-layer flood protection).
    Volumetric DDoS must be absorbed upstream (CDN / nginx limit_req) - see deploy/nginx.conf."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/") and request.url.path != "/api/health":
            limit = get_settings().rate_limit_global_per_minute
            allowed, retry = ratelimit.check(f"global:{ratelimit.client_ip(request)}", limit, 60)
            if not allowed:
                return JSONResponse({"detail": "Too many requests"}, status_code=429, headers={"Retry-After": str(retry)})
        return await call_next(request)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Double-submit cookie + Origin check for every state-changing API request.
    (Auth cookies are also SameSite=Strict, so this is defence in depth.)"""

    async def dispatch(self, request: Request, call_next):
        if request.method in UNSAFE_METHODS and request.url.path.startswith("/api/"):
            origin = request.headers.get("origin")
            if origin and not _same_origin(origin):
                return JSONResponse({"detail": "Cross-origin request blocked"}, status_code=403)
            cookie = request.cookies.get(CSRF_COOKIE, "")
            header = request.headers.get("x-csrf-token", "")
            if not cookie or not hmac.compare_digest(cookie, header):
                return JSONResponse({"detail": "CSRF token missing or invalid"}, status_code=403)
        return await call_next(request)


def _same_origin(origin: str) -> bool:
    allowed = urlparse(get_settings().public_url)
    got = urlparse(origin)
    return (got.scheme, got.netloc) == (allowed.scheme, allowed.netloc)


class BodySizeLimitMiddleware:
    """Rejects oversized bodies, including chunked uploads that lie about / omit Content-Length."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        max_bytes = get_settings().max_request_bytes
        for name, value in scope.get("headers", []):
            if name == b"content-length" and value.isdigit() and int(value) > max_bytes:
                return await _too_large(scope, receive, send)
        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > max_bytes:
                    raise _BodyTooLarge()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            await _too_large(scope, receive, send)


class _BodyTooLarge(Exception):
    pass


async def _too_large(scope: Scope, receive: Receive, send: Send) -> None:
    await JSONResponse({"detail": "Request body too large"}, status_code=413)(scope, receive, send)
