from app.security import tokens

from .conftest import enroll, future_code


def test_security_headers(client):
    r = client.get("/api/health")
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert "server" not in r.headers


def test_protected_routes_require_login(client):
    for path in ("/api/auth/me", "/api/courses", "/api/stats", "/api/leaderboard", "/api/admin/tree"):
        assert client.get(path).status_code == 401, path


def test_csrf_required_for_state_changes(client):
    r = client.post("/api/auth/dev-login", json={"email": "a@example.com", "name": "A"}, headers={"X-CSRF-Token": "forged"})
    assert r.status_code == 403


def test_cross_origin_post_blocked(client):
    r = client.post("/api/auth/dev-login", json={"email": "a@example.com", "name": "A"}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403


def test_untrusted_host_rejected(client):
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 400


def test_body_size_limit(client):
    r = client.post("/api/ai/hint", content=b"x" * 70_000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_login_requires_2fa_before_session(client):
    client.post("/api/auth/dev-login", json={"email": "a@example.com", "name": "A"})
    # Signed in with the identity provider but NOT yet 2FA-verified: no access.
    assert client.get("/api/courses").status_code == 401
    assert client.post("/api/auth/2fa/verify", json={"code": "123456"}).status_code == 401  # wrong stage


def test_full_2fa_flow_and_replay_protection(client):
    totp = enroll(client)
    assert client.get("/api/auth/me").json()["email"] == "learner@example.com"
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401

    assert client.post("/api/auth/dev-login", json={"email": "learner@example.com", "name": "L"}).json() == {"stage": "verify"}
    code = future_code(totp)
    assert client.post("/api/auth/2fa/verify", json={"code": code}).status_code == 200
    client.post("/api/auth/logout")
    client.post("/api/auth/dev-login", json={"email": "learner@example.com", "name": "L"})
    # Same code again -> rejected (replay)
    assert client.post("/api/auth/2fa/verify", json={"code": code}).status_code == 400


def test_mfa_lockout_after_repeated_failures(client):
    totp = enroll(client)
    client.post("/api/auth/logout")
    client.post("/api/auth/dev-login", json={"email": "learner@example.com", "name": "L"})
    for _ in range(5):
        assert client.post("/api/auth/2fa/verify", json={"code": "000000"}).status_code == 400
    # Even the right code is refused while locked.
    assert client.post("/api/auth/2fa/verify", json={"code": future_code(totp)}).status_code == 429


def test_recovery_code_is_single_use(client):
    enroll(client)
    client.post("/api/auth/logout")
    # regenerate isn't reachable when logged out; grab codes by re-enrolling a fresh user instead
    client.post("/api/auth/dev-login", json={"email": "r@example.com", "name": "R"})
    import pyotp

    totp = pyotp.TOTP(client.post("/api/auth/2fa/setup").json()["secret"])
    codes = client.post("/api/auth/2fa/enable", json={"code": totp.now()}).json()["recovery_codes"]
    client.post("/api/auth/logout")
    client.post("/api/auth/dev-login", json={"email": "r@example.com", "name": "R"})
    assert client.post("/api/auth/2fa/verify", json={"recovery_code": codes[0]}).status_code == 200
    client.post("/api/auth/logout")
    client.post("/api/auth/dev-login", json={"email": "r@example.com", "name": "R"})
    assert client.post("/api/auth/2fa/verify", json={"recovery_code": codes[0]}).status_code == 400


def test_refresh_rotation_and_reuse_detection(client):
    enroll(client)
    old = client.cookies.get(tokens.REFRESH_COOKIE)
    assert client.post("/api/auth/refresh").status_code == 200
    new = client.cookies.get(tokens.REFRESH_COOKIE)
    assert new and new != old
    # Replaying the old token a few seconds later (two tabs at once) is tolerated and does not log anyone out.
    client.cookies.set(tokens.REFRESH_COOKIE, old, path=tokens.REFRESH_PATH)
    assert client.post("/api/auth/refresh").status_code == 200
    # An attacker replaying it well after rotation -> whole family revoked.
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import update
    from app.db import SessionLocal
    from app.models import RefreshToken
    with SessionLocal() as db:
        db.execute(update(RefreshToken).values(revoked_at=datetime.now(timezone.utc) - timedelta(minutes=5)))
        db.commit()
    client.cookies.set(tokens.REFRESH_COOKIE, old, path=tokens.REFRESH_PATH)
    assert client.post("/api/auth/refresh").status_code == 401
    client.cookies.set(tokens.REFRESH_COOKIE, new, path=tokens.REFRESH_PATH)
    assert client.post("/api/auth/refresh").status_code == 401


def test_logout_all_invalidates_access_tokens(client):
    enroll(client)
    access = client.cookies.get(tokens.ACCESS_COOKIE)
    assert client.post("/api/auth/logout-all").status_code == 200
    client.cookies.set(tokens.ACCESS_COOKIE, access)
    assert client.get("/api/auth/me").status_code == 401


def test_forged_and_wrong_type_tokens_rejected(client):
    import jwt

    enroll(client)
    forged = jwt.encode({"sub": "1", "typ": "access", "ver": 0, "iss": "codeingo", "iat": 0, "exp": 9999999999}, "wrong-key", algorithm="HS256")
    client.cookies.set(tokens.ACCESS_COOKIE, forged)
    assert client.get("/api/auth/me").status_code == 401
    none_alg = jwt.encode({"sub": "1", "typ": "access", "ver": 0, "iss": "codeingo", "iat": 0, "exp": 9999999999}, None, algorithm="none")
    client.cookies.set(tokens.ACCESS_COOKIE, none_alg)
    assert client.get("/api/auth/me").status_code == 401


def test_auth_rate_limit(client):
    statuses = [client.post("/api/auth/dev-login", json={"email": "x@example.com", "name": "X"}).status_code for _ in range(25)]
    assert 429 in statuses


def test_non_admin_cannot_use_admin_api(client):
    enroll(client)
    assert client.get("/api/admin/tree").status_code == 404  # hidden: learners can't tell it exists
    assert client.get("/api/admin/audit").status_code == 404


def test_admin_can_manage_content_and_it_is_audited(client):
    enroll(client, "admin@example.com", "Admin")
    tree = client.get("/api/admin/tree").json()
    unit_id = tree[0]["units"][0]["id"]
    lesson = {
        "unit_id": unit_id, "title": "New", "intro": "", "xp_reward": 10,
        "exercises": [{"kind": "mcq", "prompt": "1+1?", "data": {"options": ["1", "2"]}, "solution": {"index": 1}}],
    }
    assert client.post("/api/admin/lessons", json=lesson).status_code == 201
    bad = {**lesson, "exercises": [{"kind": "code", "prompt": "x", "solution": {"patterns": ["(unclosed"]}}]}
    assert client.post("/api/admin/lessons", json=bad).status_code == 422
    events = [e["event"] for e in client.get("/api/admin/audit").json()]
    assert "admin_lesson_create" in events and "mfa_enabled" in events


def test_render_own_hostname_is_always_accepted(monkeypatch):
    import os

    from fastapi.testclient import TestClient

    from app.main import create_app

    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", "my-api.onrender.com")
    with TestClient(create_app(), base_url="https://my-api.onrender.com") as c:
        assert c.get("/api/health").status_code == 200
    with TestClient(create_app(), base_url="https://evil.example.com") as c:
        assert c.get("/api/health").status_code == 400
