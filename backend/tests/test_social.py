from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Follow, User
from app.services import mailer, reminders, social

from .conftest import enroll
from .test_checkpoints import _path, _play_lesson


def _user(email):
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.email == email))


def _two_learners(client):
    """Ada signs up and plays a lesson; then Bob signs up (and stays signed in)."""
    enroll(client, "ada@example.com", "Ada")
    _play_lesson(client, _path(client)["units"][0]["lessons"][0]["id"])
    ada_code = client.get("/api/auth/me").json()["friend_code"]
    client.post("/api/auth/logout")
    enroll(client, "bob@example.com", "Bob")
    return ada_code


def test_follow_by_friend_code_and_friends_league(client):
    ada_code = _two_learners(client)
    me = client.get("/api/auth/me").json()
    assert len(ada_code) == 8 and len(me["friend_code"]) == 8 and ada_code != me["friend_code"]

    assert client.get("/api/leaderboard", params={"scope": "friends"}).json()["entries"] == [
        {"rank": 1, "name": "Bob", "avatar_url": None, "code": me["friend_code"], "xp": 0, "streak": 0, "me": True, "following": False}
    ]
    # codes are forgiving about case, spaces and dashes
    loose = f"{ada_code[:4].lower()}-{ada_code[4:]}"
    assert client.get("/api/friends/lookup", params={"code": loose}).json() == {"code": ada_code, "name": "Ada", "avatar_url": None, "following": False}
    r = client.post("/api/friends", json={"code": loose})
    assert r.status_code == 200, r.text
    assert r.json()["friend"]["name"] == "Ada" and r.json()["friend"]["xp_week"] > 0 and r.json()["new_badges"] == ["friend"]
    assert client.post("/api/friends", json={"code": ada_code}).json()["new_badges"] == []  # following twice is a no-op

    friends = client.get("/api/friends").json()
    assert friends["code"] == me["friend_code"] and friends["followers"] == 0
    assert [(f["name"], f["follows_you"]) for f in friends["following"]] == [("Ada", False)]

    board = client.get("/api/leaderboard", params={"scope": "friends"}).json()["entries"]
    assert [(e["name"], e["me"], e["following"]) for e in board] == [("Ada", False, True), ("Bob", True, False)]
    glob = client.get("/api/leaderboard").json()["entries"]
    assert [e["name"] for e in glob] == ["Ada"] and glob[0]["following"]
    assert all("email" not in e for e in board + glob)

    assert client.delete(f"/api/friends/{ada_code}").json() == {"ok": True}
    assert client.get("/api/friends").json()["following"] == []
    with SessionLocal() as db:
        assert db.scalars(select(Follow)).all() == []


def test_follow_errors(client):
    _two_learners(client)
    me = client.get("/api/auth/me").json()["friend_code"]
    assert client.post("/api/friends", json={"code": me}).status_code == 400
    assert client.post("/api/friends", json={"code": "ZZZZZZZZ"}).status_code == 404
    assert client.post("/api/friends", json={"code": "<script>"}).status_code == 422
    assert client.get("/api/leaderboard", params={"scope": "everyone"}).status_code == 422
    with SessionLocal() as db:  # disabled accounts can't be found
        db.scalar(select(User).where(User.email == "ada@example.com")).is_active = False
        db.commit()
        code = db.scalar(select(User.friend_code).where(User.email == "ada@example.com"))
    assert client.post("/api/friends", json={"code": code}).status_code == 404


EVENING = datetime(2030, 5, 10, 19, 0, tzinfo=timezone.utc)


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(mailer, "send", lambda to, subject, text, html=None, headers=None: sent.append((to, subject, text, headers)))
    return sent


def _streak(email, *, last_active: date, streak=4, **extra):
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.email == email))
        u.streak_current, u.last_active_date = streak, last_active
        for k, v in extra.items():
            setattr(u, k, v)
        db.commit()


def test_streak_reminder_is_sent_once_on_the_evening_it_would_end(client, outbox):
    enroll(client)
    yesterday = EVENING.date() - timedelta(days=1)
    _streak("learner@example.com", last_active=yesterday)

    assert reminders.run_once(EVENING.replace(hour=9)) == 0  # too early in the day
    assert reminders.run_once(EVENING) == 1
    to, subject, text, headers = outbox[0]
    assert to == "learner@example.com" and "4-day streak" in subject and "http://testserver/learn" in text
    assert headers["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    assert headers["List-Unsubscribe"].startswith("<http://testserver/api/public/unsubscribe?u=")
    assert reminders.run_once(EVENING + timedelta(hours=2)) == 0  # once a day
    assert reminders.run_once(EVENING + timedelta(days=1)) == 0  # streak already lost by then


@pytest.mark.parametrize(
    "setup",
    [
        {"last_active": EVENING.date()},  # already practised today
        {"last_active": EVENING.date() - timedelta(days=3)},  # streak already gone
        {"last_active": EVENING.date() - timedelta(days=1), "streak": 0},
        {"last_active": EVENING.date() - timedelta(days=1), "reminder_emails": False},
        {"last_active": EVENING.date() - timedelta(days=1), "is_active": False},
    ],
)
def test_no_reminder_when_not_needed(client, outbox, setup):
    enroll(client)
    _streak("learner@example.com", **setup)
    assert reminders.run_once(EVENING) == 0 and outbox == []


def test_failed_send_is_retried_later(client, monkeypatch):
    enroll(client)
    _streak("learner@example.com", last_active=EVENING.date() - timedelta(days=1))

    def broken(*a, **k):
        raise mailer.MailError("down")

    monkeypatch.setattr(mailer, "send", broken)
    assert reminders.run_once(EVENING) == 0
    assert _user("learner@example.com").last_reminder_on is None
    monkeypatch.setattr(mailer, "send", lambda *a, **k: None)
    assert reminders.run_once(EVENING + timedelta(minutes=15)) == 1


def test_unsubscribe_link_and_settings_toggle(client):
    enroll(client)
    uid = _user("learner@example.com").id
    assert client.get("/api/auth/me").json()["reminder_emails"] is True

    # mail clients post the one-click link without cookies or a CSRF token; the signature is what counts
    url = "/api/public/unsubscribe"
    assert client.post(url, params={"u": uid, "t": "0" * 32}, headers={"x-csrf-token": ""}).status_code == 400
    assert client.post(url, params={"u": uid + 1, "t": reminders.unsubscribe_token(uid)}, headers={"x-csrf-token": ""}).status_code == 400
    r = client.post(url, params={"u": uid, "t": reminders.unsubscribe_token(uid)}, headers={"x-csrf-token": ""})
    assert r.status_code == 200 and r.json() == {"ok": True}
    assert client.get("/api/auth/me").json()["reminder_emails"] is False

    # other endpoints still require the CSRF token
    assert client.patch("/api/profile", json={"reminder_emails": True}, headers={"x-csrf-token": ""}).status_code == 403
    assert client.patch("/api/profile", json={"reminder_emails": True}).json()["reminder_emails"] is True


def test_friend_codes_are_unique_and_readable(client):
    with SessionLocal() as db:
        users = [User(email=f"u{i}@example.com", name=f"U{i}") for i in range(50)]
        db.add_all(users)
        db.commit()
        codes = {social.ensure_code(db, u) for u in users}
    assert len(codes) == 50 and all(len(c) == 8 and not set(c) & set("01OIL") for c in codes)
