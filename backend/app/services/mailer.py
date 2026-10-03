"""Outgoing email over SMTP (TLS required). Used for sign-in codes and streak reminders."""
import json
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid

from ..config import get_settings

log = logging.getLogger("codeingo.mail")


class MailError(Exception):
    pass


def send(to: str, subject: str, text: str, html: str | None = None, headers: dict[str, str] | None = None) -> None:
    s = get_settings()
    if not s.email_configured:
        if s.is_production:
            raise MailError("email is not configured")
        # Development only: no mail server, so show the message in the API console instead.
        log.warning("EMAIL (dev, not sent) to=%s subject=%r\n%s", to, subject, text)
        if s.mail_outbox_file:
            with open(s.mail_outbox_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({"to": to, "subject": subject, "text": text}) + "\n")
        return

    sender = s.smtp_from or s.smtp_username
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to  # EmailMessage rejects CR/LF in headers, so no header injection
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=sender.rsplit("@", 1)[-1].strip(">") or None)
    for name, value in (headers or {}).items():
        msg[name] = value
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    ctx = ssl.create_default_context()  # verifies the server certificate and hostname
    try:
        if s.smtp_security == "ssl":
            server = smtplib.SMTP_SSL(s.smtp_host, s.smtp_port, timeout=s.smtp_timeout_seconds, context=ctx)
        else:
            server = smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=s.smtp_timeout_seconds)
        with server:
            if s.smtp_security != "ssl":
                server.starttls(context=ctx)  # never send credentials or codes in clear text
            if s.smtp_username:
                server.login(s.smtp_username, s.smtp_password)
            server.send_message(msg)
    except (OSError, smtplib.SMTPException) as exc:
        log.error("sending email failed: %s", exc)
        raise MailError("could not send email") from exc
