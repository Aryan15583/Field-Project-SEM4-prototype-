import pyotp
from sqlalchemy import select

from app.db import SessionLocal
from app.models import AuditLog, User
from app.security import mfa

from .conftest import enroll, future_code


def _id(email):
    with SessionLocal() as db:
        return db.scalar(select(User.id).where(User.email == email))


def _setup(client):
    """bob is a learner; the signed-in account is the owner admin@example.com (from ADMIN_EMAILS)."""
    enroll(client, "bob@example.com", "Bob")
    assert client.get("/api/admin/users").status_code == 404  # hidden from learners
    client.post("/api/auth/logout")
    return enroll(client, "admin@example.com", "Owner")


def test_admin_grants_and_removes_admin_with_a_2fa_code(client):
    totp = _setup(client)
    bob = _id("bob@example.com")
    users = {u["email"]: u for u in client.get("/api/admin/users").json()}
    assert users["admin@example.com"]["owner"] and not users["bob@example.com"]["owner"]
    assert client.get("/api/admin/users", params={"q": "BOB"}).json()[0]["email"] == "bob@example.com"

    assert client.post(f"/api/admin/users/{bob}/role", json={"role": "admin", "code": "000000"}).status_code == 400
    assert client.post(f"/api/admin/users/{bob}/role", json={"role": "admin", "code": future_code(totp)}).json() == {"ok": True, "role": "admin"}
    with SessionLocal() as db:
        events = [e for (e,) in db.execute(select(AuditLog.event))]
    assert "admin_role_confirm_failed" in events and "admin_role_change" in events

    # bob is now an admin, but not an owner
    client.post("/api/auth/logout")
    client.post("/api/auth/dev-login", json={"email": "bob@example.com", "name": "Bob"})
    with SessionLocal() as db:
        bob_totp = pyotp.TOTP(mfa.decrypt(db.get(User, bob).totp_secret_enc))
    assert client.post("/api/auth/2fa/verify", json={"code": future_code(bob_totp)}).status_code == 200
    assert client.get("/api/auth/me").json()["role"] == "admin"
    assert client.get("/api/admin/tree").status_code == 200
    owner = _id("admin@example.com")
    assert client.post(f"/api/admin/users/{owner}/role", json={"role": "learner", "code": "123456"}).status_code == 403
    assert client.post(f"/api/admin/users/{owner}/active", json={"active": False}).status_code == 403
    assert client.post(f"/api/admin/users/{bob}/role", json={"role": "learner", "code": "123456"}).status_code == 400  # not yourself


def test_owner_removes_admin_access_immediately(client):
    totp = _setup(client)
    bob = _id("bob@example.com")
    with SessionLocal() as db:
        db.get(User, bob).role = "admin"
        db.commit()
    assert client.post(f"/api/admin/users/{bob}/role", json={"role": "learner", "code": future_code(totp)}).json()["role"] == "learner"
    with SessionLocal() as db:
        assert db.get(User, bob).role == "learner"


def test_promotion_needs_a_finished_signup(client):
    totp = _setup(client)
    with SessionLocal() as db:
        u = User(email="new@example.com", name="New")
        db.add(u)
        db.commit()
        new = u.id
    assert client.post(f"/api/admin/users/{new}/role", json={"role": "admin", "code": future_code(totp)}).status_code == 400
