from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


def _make_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    # Bounded pool + statement timeout so a flood of slow queries can't exhaust the database.
    return create_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=10,
        pool_pre_ping=True,
        connect_args={"options": "-c statement_timeout=5000"},
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
    "lessons": {"key": "VARCHAR(80)", "content_hash": "VARCHAR(64)"},
    # existing accounts were all enrolled with an authenticator app
    "users": {
        "mfa_method": "VARCHAR(10) DEFAULT 'totp'",
        "email_code_hash": "VARCHAR(64)",
        "email_code_expires_at": "TIMESTAMP WITH TIME ZONE",
        "email_code_sent_at": "TIMESTAMP WITH TIME ZONE",
        "email_code_attempts": "INTEGER DEFAULT 0",
        "email_code_window_start": "TIMESTAMP WITH TIME ZONE",
        "email_code_window_count": "INTEGER DEFAULT 0",
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
                    if name == "key":
                        conn.execute(text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{table}_key_u ON {table} (key)"))
