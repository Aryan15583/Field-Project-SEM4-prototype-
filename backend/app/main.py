import asyncio
import contextlib
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import get_settings
from .db import Base, SessionLocal, engine, ensure_columns
from .routers import account, admin, ai, auth, checkpoints, contests, learn, passkeys, practice, social, stats
from .security.middleware import (
    BodySizeLimitMiddleware,
    CSRFMiddleware,
    GlobalRateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from .seed import sync_curriculum
from .services import reminders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("codeingo")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    ensure_columns()
    with SessionLocal() as db:
        sync_curriculum(db)
    if get_settings().is_production and not get_settings().proxy_secret:
        log.warning("PROXY_SECRET is not set: client IPs for rate limiting can be forged with an X-Forwarded-For header")
    task = asyncio.create_task(reminders.loop()) if get_settings().streak_reminders else None
    yield
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title="Codeingo API",
        lifespan=lifespan,
        # Don't publish the API map in production.
        docs_url=None if s.is_production else "/api/docs",
        redoc_url=None,
        openapi_url=None if s.is_production else "/api/openapi.json",
    )

    # Starlette runs the LAST added middleware first (outermost).
    app.add_middleware(CSRFMiddleware)

    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(GlobalRateLimitMiddleware)
    # Render tells every web service its own public hostname; always accept it (plus the local addresses its health
    # checks use), so a mistyped ALLOWED_HOSTS can't lock the service out of its own address.
    hosts = list(s.allowed_hosts)
    own = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
    for extra in (own, "127.0.0.1", "localhost"):
        if extra and extra not in hosts:
            hosts.append(extra)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=800)  # the course path JSON is ~13 kB: send it compressed
    # No CORSMiddleware on purpose: the SPA is served from the same origin, so browsers
    # block every cross-origin read of the API by default.

    for r in (account.router, auth.router, passkeys.router, learn.router, checkpoints.router, contests.router, practice.router, social.router, stats.router, ai.router, admin.router):
        app.include_router(r)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        # Report which fields failed without echoing the submitted values back.
        errors = [{"loc": e.get("loc"), "msg": e.get("msg")} for e in exc.errors()][:10]
        return JSONResponse({"detail": "Invalid request", "errors": errors}, status_code=422)

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception):
        log.exception("unhandled error", exc_info=exc)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)  # never leak stack traces

    return app


app = create_app()
