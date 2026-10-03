import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=s.allowed_hosts)
    app.add_middleware(SecurityHeadersMiddleware)
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
