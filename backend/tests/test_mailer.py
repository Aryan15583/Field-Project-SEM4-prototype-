"""Email delivery: SMTP and the Brevo HTTPS API (used where SMTP ports are blocked)."""
import httpx
import pytest

from app.config import get_settings
from app.services import mailer


class _Resp:
    def __init__(self, status_code=201, text="{}"):
        self.status_code, self.text = status_code, text


def _brevo(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "brevo_api_key", "key-123")
    monkeypatch.setattr(s, "mail_from", "Codeingo <sender@example.com>")
    monkeypatch.setattr(s, "smtp_host", "")


def test_brevo_request_shape(monkeypatch):
    _brevo(monkeypatch)
    seen = {}

    def fake_post(url, json, headers, timeout):
        seen.update(url=url, json=json, headers=headers)
        return _Resp()

    monkeypatch.setattr(mailer.httpx, "post", fake_post)
    mailer.send("user@example.com", "123456 is your code", "Your code is 123456", "<b>123456</b>")
    assert seen["url"] == "https://api.brevo.com/v3/smtp/email"
    assert seen["headers"]["api-key"] == "key-123"
    assert seen["json"]["sender"] == {"email": "sender@example.com", "name": "Codeingo"}
    assert seen["json"]["to"] == [{"email": "user@example.com"}]
    assert seen["json"]["subject"] == "123456 is your code"


def test_brevo_rejection_and_network_errors_raise(monkeypatch):
    _brevo(monkeypatch)
    monkeypatch.setattr(mailer.httpx, "post", lambda *a, **k: _Resp(401, "unauthorized"))
    with pytest.raises(mailer.MailError):
        mailer.send("user@example.com", "s", "t")

    def boom(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(mailer.httpx, "post", boom)
    with pytest.raises(mailer.MailError):
        mailer.send("user@example.com", "s", "t")


def test_brevo_counts_as_configured(monkeypatch):
    _brevo(monkeypatch)
    assert get_settings().email_configured
