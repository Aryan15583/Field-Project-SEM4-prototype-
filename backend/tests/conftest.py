import os
import tempfile
import time

_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ.update(
    ENV="test",
    DATABASE_URL=f"sqlite:///{_db}",
    DEV_LOGIN_ENABLED="true",
    ADMIN_EMAILS='["admin@example.com"]',
    COOKIE_SECURE="false",  # TestClient talks plain http://testserver
    PUBLIC_URL="http://testserver",
    REDIS_URL="",
    AI_API_KEY="",
    STREAK_REMINDERS="false",  # tests call reminders.run_once() directly
)

import pyotp  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.security import ratelimit  # noqa: E402
from app.seed import seed_if_empty  # noqa: E402


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_if_empty(db)
    ratelimit.store().reset()
    with TestClient(app) as c:
        c.get("/api/auth/csrf")

        def add_csrf(request):  # mimic the SPA: echo the current CSRF cookie on every request
            if "x-csrf-token" not in request.headers and c.cookies.get("cg_csrf"):
                request.headers["X-CSRF-Token"] = c.cookies.get("cg_csrf")

        c.event_hooks["request"] = [add_csrf]
        yield c


def enroll(client: TestClient, email: str = "learner@example.com", name: str = "Learner") -> pyotp.TOTP:
    """Dev-login + complete mandatory 2FA enrollment. Returns the user's TOTP generator."""
    assert client.post("/api/auth/dev-login", json={"email": email, "name": name}).json() == {"stage": "setup"}
    setup = client.post("/api/auth/2fa/setup").json()
    totp = pyotp.TOTP(setup["secret"])
    r = client.post("/api/auth/2fa/enable", json={"code": totp.now()})
    assert r.status_code == 200, r.text
    assert len(r.json()["recovery_codes"]) == 10
    return totp


def future_code(totp: pyotp.TOTP) -> str:
    """A code for the next 30s window (codes can't be replayed within the same window)."""
    return totp.at(time.time() + 30)
