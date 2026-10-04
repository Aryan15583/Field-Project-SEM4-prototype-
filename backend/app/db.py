from collections.abc import Iterator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


def normalise_url(url: str) -> str:
    """Hosted Postgres (Neon, Render, Supabase...) hands out postgres:// or postgresql:// URLs; use the psycopg 3
    driver we install rather than SQLAlchemy's default psycopg2."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def _is_pooled(url: str) -> bool:
    """Neon's pooled endpoint (host contains -pooler) runs through PgBouncer in transaction mode."""
    host = url.split("@", 1)[-1].split("/", 1)[0]
    return "-pooler" in host


def _drop_param(url: str, name: str) -> str:
    """Removes one query parameter (e.g. channel_binding, which PgBouncer poolers don't support)."""
    if "?" not in url:
        return url
    base, query = url.split("?", 1)
    kept = [p for p in query.split("&") if p and p.split("=", 1)[0] != name]
    return base + ("?" + "&".join(kept) if kept else "")


def _make_engine(url: str):
    url = normalise_url(url)
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def _foreign_keys(dbapi_conn, _):
            # SQLite ignores ON DELETE CASCADE unless this is on (PostgreSQL always enforces it)
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

        return engine
    # Bounded pool + statement timeout so a flood of slow queries can't exhaust the database.
    connect_args: dict = {"options": "-c statement_timeout=5000"}
    if _is_pooled(url):
        # A PgBouncer pooler rejects startup options and shares connections between sessions, so don't
        # send the timeout as an option and don't use server-side prepared statements. (Use the direct
        # Neon string if you want the 5 s statement timeout.)
        url = _drop_param(url, "channel_binding")
        connect_args = {"prepare_threshold": None}
    return create_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=10,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _make_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Columns added after the first release. create_all() only creates missing tables, so add missing
# columns to existing ones (tiny forward-only migration; use Alembic if the schema grows further).
_ADDED_COLUMNS = {
    "units": {"key": "VARCHAR(80)", "section": "VARCHAR(40) DEFAULT 'Beginner'"},
    "lessons": {"key": "VARCHAR(80)", "content_hash": "VARCHAR(64)", "is_project": "BOOLEAN DEFAULT FALSE"},
    "user_lessons": {"tested_out": "BOOLEAN DEFAULT FALSE"},
    "lesson_attempts": {"chances": "JSON"},
    "certificates": {"debug": "BOOLEAN DEFAULT FALSE"},
    # existing accounts were all enrolled with an authenticator app
    "users": {
        "mfa_method": "VARCHAR(10) DEFAULT 'totp'",
        "email_code_hash": "VARCHAR(64)",
        "email_code_expires_at": "TIMESTAMP WITH TIME ZONE",
        "email_code_sent_at": "TIMESTAMP WITH TIME ZONE",
        "email_code_attempts": "INTEGER DEFAULT 0",
        "email_code_window_start": "TIMESTAMP WITH TIME ZONE",
        "email_code_window_count": "INTEGER DEFAULT 0",
        "friend_code": "VARCHAR(12)",
        "reminder_emails": "BOOLEAN DEFAULT TRUE",
        "last_reminder_on": "DATE",
        "debug_mode": "BOOLEAN DEFAULT FALSE",
    },
}


def ensure_columns() -> None:
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, cols in _ADDED_COLUMNS.items():
            if not insp.has_table(table):
                continue
            have = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in cols.items():
                if name not in have:
                    # identifiers come from the constant above, never from user input
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
                    if name == "friend_code":
                        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_friend_code ON users (friend_code)"))
                    if name == "key":
                        conn.execute(text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{table}_key_u ON {table} (key)"))
