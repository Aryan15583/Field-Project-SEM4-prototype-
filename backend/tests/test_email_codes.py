import re
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.config import Settings
from app.db import SessionLocal
from app.models import User
from app.services import mailer


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(mailer, "send", lambda to, subject, text, html=None: sent.append({"to": to, "subject": subject, "text": text}))
    return sent


def _code(mail) -> str:
    return re.search(r"\b(\d{6})\b", mail["text"]).group(1)


def _user(email="mail@example.com") -> User:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.email == email))


def _age_last_send(email="mail@example.com", seconds=120):
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.email == email))
        u.email_code_sent_at = datetime.now(timezone.utc) - timedelta(seconds=seconds)
        db.commit()


def _login(client, email="mail@example.com"):
    return client.post("/api/auth/dev-login", json={"email": email, "name": "Mail"}).json()["stage"]


def _enroll_by_email(client, outbox, email="mail@example.com"):
    assert _login(client, email) == "setup"
    r = client.post("/api/auth/2fa/email/send")
    assert r.status_code == 200 and r.json()["sent_to"].endswith("@example.com")
    r = client.post("/api/auth/2fa/email/enable", json={"code": _code(outbox[-1])})
    assert r.status_code == 200, r.text
    return r


def test_email_setup_signs_in_without_an_authenticator(client, outbox):
    r = _enroll_by_email(client, outbox)
    assert r.json()["user"]["mfa_method"] == "email"
    assert "recovery_codes" not in r.json()
    assert outbox[0]["to"] == "mail@example.com" and outbox[0]["subject"].startswith(_code(outbox[0]))
    assert client.get("/api/auth/me").status_code == 200
    u = _user()
    assert u.mfa_enabled and u.mfa_method == "email" and u.email_code_hash is None  # code used up
    assert _code(outbox[0]) not in (u.email_code_hash or "")


def test_next_sign_in_needs_a_fresh_emailed_code(client, outbox):
    _enroll_by_email(client, outbox)
    old = _code(outbox[-1])
    client.post("/api/auth/logout")
    assert _login(client) == "verify"
    status = client.get("/api/auth/2fa/status").json()
    assert status["method"] == "email" and status["email_masked"] == "ma•••••@example.com"
    assert client.post("/api/auth/2fa/verify", json={"code": old}).status_code == 400  # old code is single-use
    _age_last_send()
    client.post("/api/auth/2fa/email/send")
    assert client.post("/api/auth/2fa/verify", json={"code": _code(outbox[-1])}).status_code == 200
    assert client.get("/api/auth/me").status_code == 200


def test_expired_codes_are_rejected(client, outbox):
    _login(client)
    client.post("/api/auth/2fa/email/send")
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.email == "mail@example.com"))
        u.email_code_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.post("/api/auth/2fa/email/enable", json={"code": _code(outbox[-1])}).status_code == 400


def test_a_code_dies_after_too_many_wrong_guesses(client, outbox):
    _login(client)
    client.post("/api/auth/2fa/email/send")
    good = _code(outbox[-1])
    wrong = "000000" if good != "000000" else "111111"
    for _ in range(4):
        assert client.post("/api/auth/2fa/email/enable", json={"code": wrong}).status_code == 400
    # 5th attempt locks the account (shared failure counter) and the code is already burned
    assert client.post("/api/auth/2fa/email/enable", json={"code": wrong}).status_code == 400
    assert client.post("/api/auth/2fa/email/enable", json={"code": good}).status_code == 429
    assert _user().email_code_hash is None


def test_resend_cooldown_and_hourly_cap(client, outbox):
    _login(client)
    first = client.post("/api/auth/2fa/email/send").json()
    again = client.post("/api/auth/2fa/email/send").json()  # e.g. a double click or page reload
    assert len(outbox) == 1 and again["resend_in"] > 0 and first["resend_in"] > 0
    for _ in range(5):
        _age_last_send()
        assert client.post("/api/auth/2fa/email/send", json={"resend": True}).status_code == 200
    assert len(outbox) == 6
    _age_last_send()
    r = client.post("/api/auth/2fa/email/send", json={"resend": True})
    assert r.status_code == 429 and len(outbox) == 6


def test_send_requires_a_sign_in_session(client, outbox):
    assert client.post("/api/auth/2fa/email/send").status_code == 401
    assert outbox == []


def test_authenticator_accounts_cannot_be_downgraded_to_email(client, outbox):
    from .conftest import enroll

    enroll(client, "app@example.com")
    client.post("/api/auth/logout")
    assert _login(client, "app@example.com") == "verify"
    assert client.post("/api/auth/2fa/email/send").status_code == 400
    assert outbox == []


def test_mail_failure_does_not_leave_a_usable_code(client, monkeypatch):
    def boom(*a, **k):
        raise mailer.MailError("smtp down")

    monkeypatch.setattr(mailer, "send", boom)
    _login(client)
    assert client.post("/api/auth/2fa/email/send").status_code == 503
    u = _user()
    assert u.email_code_hash is None and u.email_code_sent_at is None


def test_production_requires_smtp():
    s = Settings(env="production", smtp_host="")
    with pytest.raises(RuntimeError, match="SMTP_HOST"):
        s.validate_for_production()


def test_signing_straight_back_in_gets_a_new_code_immediately(client, outbox):
    _enroll_by_email(client, outbox)  # uses up the code that was just sent
    client.post("/api/auth/logout")
    assert _login(client) == "verify"
    r = client.post("/api/auth/2fa/email/send")  # well inside the 60s resend cooldown
    assert r.status_code == 200 and len(outbox) == 2
    assert client.post("/api/auth/2fa/verify", json={"code": _code(outbox[-1])}).status_code == 200


def test_mailer_upgrades_to_tls_before_sending(monkeypatch):
    from app import config

    calls = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            calls.append(("connect", host, port))

        def __enter__(self):
            return self

        def __exit__(self, *a):
            calls.append(("quit",))

        def starttls(self, context):
            calls.append(("starttls", context.check_hostname))

        def login(self, user, password):
            calls.append(("login", user))

        def send_message(self, msg):
            calls.append(("send", msg["To"], msg["Subject"], msg["From"]))

    s = config.get_settings()
    monkeypatch.setattr(s, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(s, "smtp_username", "bot@example.com")
    monkeypatch.setattr(s, "smtp_from", "Codeingo <bot@example.com>")
    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    mailer.send("to@example.com", "123456 is your code", "body", "<p>body</p>")
    assert [c[0] for c in calls] == ["connect", "starttls", "login", "send", "quit"]
    assert calls[1] == ("starttls", True)  # certificate hostname is verified
    assert calls[3] == ("send", "to@example.com", "123456 is your code", "Codeingo <bot@example.com>")


def test_mailer_rejects_header_injection(monkeypatch):
    from app import config

    s = config.get_settings()
    monkeypatch.setattr(s, "smtp_host", "smtp.example.com")
    with pytest.raises(ValueError):
        mailer.send("victim@example.com\r\nBcc: everyone@example.com", "x", "y")


def test_reloading_the_page_keeps_the_code_already_sent(client, outbox):
    _login(client)
    client.post("/api/auth/2fa/email/send")
    first = _code(outbox[-1])
    _age_last_send(seconds=120)  # learner spent two minutes finding the email, then the page reloaded
    r = client.post("/api/auth/2fa/email/send")
    assert r.status_code == 200 and len(outbox) == 1  # no new code replaced the one they're typing
    assert client.post("/api/auth/2fa/email/enable", json={"code": first}).status_code == 200


def test_asking_for_a_new_code_replaces_the_old_one(client, outbox):
    _login(client)
    client.post("/api/auth/2fa/email/send")
    old = _code(outbox[-1])
    _age_last_send()
    client.post("/api/auth/2fa/email/send", json={"resend": True})
    new = _code(outbox[-1])
    assert len(outbox) == 2
    if old != new:
        assert client.post("/api/auth/2fa/email/enable", json={"code": old}).status_code == 400
    assert client.post("/api/auth/2fa/email/enable", json={"code": new}).status_code == 200
