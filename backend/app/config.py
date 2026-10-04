"""Application settings, loaded from environment variables (see .env.example).

Production refuses to start with insecure settings - see `validate_for_production`.
"""
import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- general ---
    env: str = Field("development", description="development | test | production")
    app_name: str = "Codeingo"
    public_url: str = "http://localhost:3000"  # where the SPA is served (used for redirects + CORS)
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]

    # --- secrets ---
    secret_key: str = "dev-insecure-secret-change-me-dev-insecure-secret"
    # Fernet key used to encrypt TOTP secrets at rest. Generate with:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = ""

    # --- database / cache ---
    database_url: str = "sqlite:///./codeingo.db"
    redis_url: str = ""  # empty -> in-memory rate limiting (single process only)

    # --- Google OAuth (OpenID Connect) ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:3000/api/auth/google/callback"
    # Optionally restrict sign-in to Google Workspace domains, e.g. ["myschool.edu"]
    allowed_email_domains: list[str] = []
    admin_emails: list[str] = []

    # --- local development only: password-less login, still followed by 2FA ---
    dev_login_enabled: bool = False

    # --- tokens / cookies ---
    access_token_minutes: int = 15
    # "Stay signed in on this device until you log out": the refresh cookie lasts as long as browsers allow
    # (~400 days) and is renewed on every use, so an active or returning device never has to sign in again.
    refresh_token_days: int = 400
    refresh_grace_seconds: int = 10  # a just-rotated token is tolerated briefly (two tabs refreshing at once)
    mfa_token_minutes: int = 5
    cookie_secure: bool = True  # browsers treat http://localhost as secure, so this works in dev too

    # --- abuse protection ---
    rate_limit_global_per_minute: int = 240
    rate_limit_auth_per_minute: int = 20
    rate_limit_ai_per_hour: int = 30
    max_request_bytes: int = 64 * 1024
    mfa_max_failures: int = 5
    mfa_lockout_minutes: int = 15
    # emailed sign-in codes
    email_code_minutes: int = 10
    email_code_resend_seconds: int = 60
    email_code_max_per_hour: int = 6
    email_code_max_attempts: int = 5

    # --- outgoing email (sign-in codes). Gmail: smtp.gmail.com, port 587, an App Password. ---
    # Empty SMTP_HOST in development -> codes are printed to the API console instead of sent.
    # Development/test only: also append every email the app would send to this file (one JSON object per line),
    # so automated browser tests can read sign-in codes. Rejected in production.
    mail_outbox_file: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""  # e.g. "Codeingo <no-reply@codeingo.dev>"; defaults to SMTP_USERNAME
    smtp_security: str = "starttls"  # starttls (port 587) | ssl (port 465)
    smtp_timeout_seconds: float = 10.0
    # Alternative to SMTP: send through Brevo's HTTPS API (needed on hosts that block SMTP ports, such as Render's
    # free plan). Create a key at brevo.com -> SMTP & API -> API keys, and verify the sender address there.
    # The sender is MAIL_FROM (falls back to SMTP_FROM), e.g. "Codeingo <you@gmail.com>".
    brevo_api_key: str = ""
    mail_from: str = ""

    # --- AI tutor (any OpenAI-compatible endpoint: OpenAI, Mistral, Llama 3 via Ollama/vLLM...) ---
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = ""
    ai_timeout_seconds: float = 15.0

    # --- optional sandboxed code runner for Java/C/C++ (self-hosted Piston, private network only) ---
    code_runner_url: str = ""
    rate_limit_run_per_minute: int = 12

    # --- gamification ---
    max_hearts: int = 5
    heart_refill_minutes: int = 30

    # --- streak reminder emails (sent to learners whose streak would end tonight) ---
    streak_reminders: bool = True
    streak_reminder_hour_utc: int = Field(17, ge=0, le=23)  # don't send before this hour (UTC)
    streak_reminder_check_minutes: int = Field(15, ge=1)

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def email_configured(self) -> bool:
        return bool(self.smtp_host or self.brevo_api_key)

    @property
    def fernet(self) -> Fernet:
        return Fernet(self.encryption_key.encode())

    def validate_for_production(self) -> None:
        problems = []
        if len(self.secret_key) < 32 or "insecure" in self.secret_key:
            problems.append("SECRET_KEY must be a random value of at least 32 characters")
        try:
            Fernet(self.encryption_key.encode())
        except Exception:
            problems.append("ENCRYPTION_KEY must be a valid Fernet key")
        if not (self.google_client_id and self.google_client_secret):
            problems.append("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required")
        if self.dev_login_enabled:
            problems.append("DEV_LOGIN_ENABLED must be false in production")
        if not self.cookie_secure:
            problems.append("COOKIE_SECURE must be true in production")
        if not self.public_url.startswith("https://"):
            problems.append("PUBLIC_URL must use https:// in production")
        if self.brevo_api_key:
            if not (self.mail_from or self.smtp_from):
                problems.append("MAIL_FROM is required with BREVO_API_KEY")
        elif not self.smtp_host or not (self.smtp_from or self.smtp_username):
            problems.append("BREVO_API_KEY + MAIL_FROM, or SMTP_HOST + SMTP_FROM (or SMTP_USERNAME), are required to email sign-in codes")
        if self.mail_outbox_file:
            problems.append("MAIL_OUTBOX_FILE is for development and tests only")
        if self.smtp_security not in ("starttls", "ssl"):
            problems.append("SMTP_SECURITY must be starttls or ssl")
        if not self.redis_url:
            problems.append("REDIS_URL is required in production (shared rate limiting)")
        if self.database_url.startswith("sqlite"):
            problems.append("Use PostgreSQL (DATABASE_URL) in production")
        if problems:
            raise RuntimeError("Insecure production configuration:\n - " + "\n - ".join(problems))


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if not s.encryption_key and not s.is_production:
        # Dev convenience only: derive a stable key from SECRET_KEY. Production requires a real one.
        s.encryption_key = base64.urlsafe_b64encode(hashlib.sha256(s.secret_key.encode()).digest()).decode()
    if s.is_production:
        s.validate_for_production()
    if s.dev_login_enabled and s.env not in ("development", "test"):
        raise RuntimeError("dev login is only allowed in development/test")
    return s
