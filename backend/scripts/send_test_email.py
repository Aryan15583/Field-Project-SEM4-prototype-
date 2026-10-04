"""Sends one test email with the SMTP settings from .env, to check them before going live.

    python scripts/send_test_email.py you@gmail.com
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.services import mailer  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2 or "@" not in sys.argv[1]:
        print("usage: python scripts/send_test_email.py you@gmail.com")
        return 2
    s = get_settings()
    if not s.email_configured:
        print("SMTP_HOST is empty - fill in the SMTP_* settings in backend/.env first.")
        return 1
    print(f"Sending through {s.smtp_host}:{s.smtp_port} ({s.smtp_security}) as {s.smtp_from or s.smtp_username} ...")
    try:
        mailer.send(sys.argv[1], "Codeingo test email", "If you can read this, Codeingo can email sign-in codes.")
    except mailer.MailError as exc:
        print(f"FAILED: {exc}. Check the username, App Password, port and security setting (see the log above).")
        return 1
    print(f"Sent. Check the inbox (and spam) of {sys.argv[1]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
