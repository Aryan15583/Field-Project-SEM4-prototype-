"""Streak reminder emails: one gentle nudge on the evening a learner's streak is about to end.

Sent at most once a day per learner (an atomic claim on `last_reminder_on` makes that hold even with
several API workers), only to people who practised yesterday but not yet today, and never to anyone
who switched reminders off. Every email carries a signed one-click unsubscribe link (RFC 8058).

Runs inside the API on a timer (see main.py); `python -m app.services.reminders` runs one pass by hand.
"""
import asyncio
import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import urlencode

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import SessionLocal
from ..models import User
from . import mailer

log = logging.getLogger("codeingo.reminders")


def unsubscribe_token(user_id: int) -> str:
    key = get_settings().secret_key.encode()
    return hmac.new(key, f"unsubscribe:{user_id}".encode(), hashlib.sha256).hexdigest()[:32]


def valid_token(user_id: int, token: str) -> bool:
    return hmac.compare_digest(unsubscribe_token(user_id), token or "")


def unsubscribe_query(user_id: int) -> str:
    return urlencode({"u": user_id, "t": unsubscribe_token(user_id)})


def due(db: Session, now: datetime) -> list[User]:
    """Learners whose streak ends tonight: active yesterday, not yet today, and not reminded today."""
    s = get_settings()
    if now.hour < s.streak_reminder_hour_utc:
        return []
    today = now.date()
    return list(
        db.scalars(
            select(User).where(
                User.is_active.is_(True),
                User.mfa_enabled.is_(True),  # finished signing up
                User.reminder_emails.is_(True),
                User.streak_current > 0,
                User.last_active_date == today - timedelta(days=1),
                or_(User.last_reminder_on.is_(None), User.last_reminder_on < today),
            )
        )
    )


def _claim(db: Session, user: User, today) -> bool:
    """Atomically mark today's reminder as taken - only one worker can win it."""
    res = db.execute(
        update(User)
        .where(User.id == user.id, or_(User.last_reminder_on.is_(None), User.last_reminder_on < today))
        .values(last_reminder_on=today)
    )
    db.commit()
    return res.rowcount == 1


def _message(user: User) -> tuple[str, str, str, dict[str, str]]:
    base = get_settings().public_url.rstrip("/")
    days = user.streak_current
    unsub_page = f"{base}/unsubscribe?{unsubscribe_query(user.id)}"
    one_click = f"{base}/api/public/unsubscribe?{unsubscribe_query(user.id)}"
    subject = f"Your {days}-day streak ends tonight 🔥"
    text = (
        f"Hi {user.name},\n\n"
        f"You're on a {days}-day coding streak - one short lesson today keeps it alive.\n\n"
        f"Keep it going: {base}/learn\n\n"
        f"Don't want these reminders? Turn them off: {unsub_page}\n"
    )
    html = (
        f"<p>Hi {escape(user.name)},</p>"
        f"<p>You're on a <strong>{days}-day</strong> coding streak - one short lesson today keeps it alive.</p>"
        f'<p><a href="{escape(base)}/learn">Keep my streak going</a></p>'
        f'<p style="color:#666;font-size:12px">Don\'t want these reminders? <a href="{escape(unsub_page)}">Turn them off</a>.</p>'
    )
    headers = {"List-Unsubscribe": f"<{one_click}>", "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}
    return subject, text, html, headers


def run_once(now: datetime | None = None) -> int:
    """Send every reminder that is due right now. Returns how many were sent."""
    now = now or datetime.now(timezone.utc)
    sent = 0
    with SessionLocal() as db:
        for user in due(db, now):
            if not _claim(db, user, now.date()):
                continue
            subject, text, html, headers = _message(user)
            try:
                mailer.send(user.email, subject, text, html, headers=headers)
                sent += 1
            except mailer.MailError:
                # give the next pass another chance today
                db.execute(update(User).where(User.id == user.id).values(last_reminder_on=None))
                db.commit()
    if sent:
        log.info("sent %d streak reminder(s)", sent)
    return sent


async def loop() -> None:
    """Background timer started by the API."""
    minutes = get_settings().streak_reminder_check_minutes
    while True:
        await asyncio.sleep(minutes * 60)
        try:
            await asyncio.to_thread(run_once)
        except Exception:  # never let one bad pass stop the timer
            log.exception("streak reminder pass failed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"sent {run_once()} reminder(s)")
