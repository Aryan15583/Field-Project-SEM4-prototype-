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
    public_url: str = "http://localhost:5173"  # where the SPA is served (used for redirects + CORS)
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
    google_redirect_uri: str = "http://localhost:5173/api/auth/google/callback"
    # Optionally restrict sign-in to Google Workspace domains, e.g. ["myschool.edu"]
    allowed_email_domains: list[str] = []
    admin_emails: list[str] = []

    # --- local development only: password-less login, still followed by 2FA ---
    dev_login_enabled: bool = False

    # --- tokens / cookies ---
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    mfa_token_minutes: int = 5
    cookie_secure: bool = True  # browsers treat http://localhost as secure, so this works in dev too

    # --- abuse protection ---
    rate_limit_global_per_minute: int = 240
    rate_limit_auth_per_minute: int = 20
    rate_limit_ai_per_hour: int = 30
    max_request_bytes: int = 64 * 1024
    mfa_max_failures: int = 5
    mfa_lockout_minutes: int = 15

    # --- AI tutor (any OpenAI-compatible endpoint: OpenAI, Mistral, Llama 3 via Ollama/vLLM...) ---
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = ""
    ai_timeout_seconds: float = 15.0

    # --- gamification ---
    max_hearts: int = 5
    heart_refill_minutes: int = 30

    @property
    def is_production(self) -> bool:
        return self.env == "production"

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
