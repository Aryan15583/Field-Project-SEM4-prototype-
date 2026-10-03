from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import AuditLog, Certificate, Follow, ReviewItem, User, UserBadge, UserLesson, XpEvent

from .conftest import enroll, future_code
from .test_checkpoints import _path, _play_lesson


def _count(model, uid, col="user_id"):
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(model).where(getattr(model, col) == uid))


def _uid(email):
    with SessionLocal() as db:
        return db.scalar(select(User.id).where(User.email == email))


def test_export_has_my_data_and_no_secrets(client):
    enroll(client, "ada@example.com", "Ada")  # an owner, to make sure export works for everyone
    client.post("/api/auth/logout")
    totp = enroll(client, "bob@example.com", "Bob")
    _play_lesson(client, _path(client)["units"][0]["lessons"][0]["id"])
    r = client.get("/api/account/export")
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"] and r.headers["cache-control"] == "no-store"
    data = r.json()
    assert data["account"]["email"] == "bob@example.com" and data["progress"]["xp_total"] > 0
    assert data["progress"]["lessons"] and data["progress"]["badges"]
    text = r.text.lower()
    for secret in ("totp_secret", "code_hash", "token", "password", "ada@example.com"):
        assert secret not in text
    assert totp  # (signed in with the authenticator)
    client.post("/api/auth/logout")
    assert client.get("/api/account/export").status_code == 401


def test_delete_account_removes_everything(client):
    enroll(client, "ada@example.com", "Ada")
    ada_code = client.get("/api/auth/me").json()["friend_code"]
    client.post("/api/auth/logout")
    totp = enroll(client, "bob@example.com", "Bob")
    _play_lesson(client, _path(client)["units"][0]["lessons"][0]["id"])
    client.post("/api/friends", json={"code": ada_code})
    bob = _uid("bob@example.com")
    assert _count(ReviewItem, bob) and _count(UserLesson, bob) and _count(XpEvent, bob) and _count(UserBadge, bob) and _count(Follow, bob, "follower_id")

    assert client.post("/api/account/delete", json={"code": "000000"}).status_code == 400  # wrong code
    assert client.get("/api/auth/me").status_code == 200  # still there
    r = client.post("/api/account/delete", json={"code": future_code(totp)})
    assert r.status_code == 200 and r.json() == {"ok": True}

    assert client.get("/api/auth/me").status_code == 401  # signed out
    assert _uid("bob@example.com") is None
    for model in (UserLesson, XpEvent, UserBadge, ReviewItem):
        assert _count(model, bob) == 0, model
    assert _count(Follow, bob, "follower_id") == 0 and _count(Certificate, bob) == 0
    with SessionLocal() as db:
        # a trace that a deletion happened, with nothing that identifies the person
        events = db.scalars(select(AuditLog).where(AuditLog.event == "account_deleted")).all()
        assert len(events) == 1 and events[0].user_id is None
        assert not db.scalars(select(AuditLog).where(AuditLog.user_id == bob)).all()
    # the same email can sign up again from scratch
    client.get("/api/auth/csrf")
    assert client.post("/api/auth/dev-login", json={"email": "bob@example.com", "name": "Bob"}).json() == {"stage": "setup"}


def test_owner_cannot_delete_their_account(client):
    totp = enroll(client, "admin@example.com", "Owner")
    assert client.post("/api/account/delete", json={"code": future_code(totp)}).status_code == 403
    assert _uid("admin@example.com") is not None
