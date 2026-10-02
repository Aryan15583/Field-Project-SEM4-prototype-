import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_sub: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(16), default="learner")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Bumping this invalidates every access token issued to the user ("log out everywhere").
    token_version: Mapped[int] = mapped_column(Integer, default=0)

    # --- 2-step verification: an emailed code (default) or an authenticator app (TOTP). ---
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_method: Mapped[str] = mapped_column(String(10), default="email")  # email | totp
    totp_secret_enc: Mapped[str | None] = mapped_column(Text)
    totp_pending_enc: Mapped[str | None] = mapped_column(Text)
    totp_last_step: Mapped[int] = mapped_column(Integer, default=0)  # replay protection
    mfa_failed_count: Mapped[int] = mapped_column(Integer, default=0)
    mfa_locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # The current emailed code: only a keyed hash is stored, never the code itself.
    email_code_hash: Mapped[str | None] = mapped_column(String(64))
    email_code_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_code_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_code_attempts: Mapped[int] = mapped_column(Integer, default=0)
    email_code_window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_code_window_count: Mapped[int] = mapped_column(Integer, default=0)

    # --- gamification ---
    xp_total: Mapped[int] = mapped_column(Integer, default=0)
    streak_current: Mapped[int] = mapped_column(Integer, default=0)
    streak_best: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date)
    hearts: Mapped[int] = mapped_column(Integer, default=5)
    hearts_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    daily_goal: Mapped[int] = mapped_column(Integer, default=30)

    badges: Mapped[list["UserBadge"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class RecoveryCode(Base):
    __tablename__ = "recovery_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RefreshToken(Base):
    """Opaque refresh tokens, stored only as SHA-256 hashes. Rotated on every use;
    re-use of a rotated token revokes the whole family (token theft detection)."""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    family_id: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_agent: Mapped[str | None] = mapped_column(String(256))
    ip: Mapped[str | None] = mapped_column(String(64))


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    title: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(400), default="")
    icon: Mapped[str] = mapped_column(String(8), default="{}")
    position: Mapped[int] = mapped_column(Integer, default=0)

    units: Mapped[list["Unit"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="Unit.position"
    )


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    key: Mapped[str | None] = mapped_column(String(80), unique=True)  # stable id for built-in curriculum
    section: Mapped[str] = mapped_column(String(40), default="Beginner")  # Beginner / Intermediate / Advanced
    title: Mapped[str] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(Integer, default=0)

    course: Mapped[Course] = relationship(back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", order_by="Lesson.position"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    key: Mapped[str | None] = mapped_column(String(80), unique=True)  # stable id for built-in curriculum
    # hash of the built-in content this lesson was seeded from; None once an admin customises it
    content_hash: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(120))
    intro: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    xp_reward: Mapped[int] = mapped_column(Integer, default=10)

    unit: Mapped[Unit] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan", order_by="Exercise.position"
    )


class Exercise(Base):
    """kind: mcq | fill | order | code | run.  `solution` never leaves the server before answering."""

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    kind: Mapped[str] = mapped_column(String(16))
    prompt: Mapped[str] = mapped_column(Text)
    code: Mapped[str | None] = mapped_column(Text)
    data: Mapped[dict] = mapped_column(JSON, default=dict)  # public: options / lines / starter
    solution: Mapped[dict] = mapped_column(JSON, default=dict)  # private
    explanation: Mapped[str] = mapped_column(Text, default="")
    hint: Mapped[str] = mapped_column(Text, default="")

    lesson: Mapped[Lesson] = relationship(back_populates="exercises")


class LessonAttempt(Base):
    __tablename__ = "lesson_attempts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    mistakes: Mapped[int] = mapped_column(Integer, default=0)
    correct_ids: Mapped[list] = mapped_column(JSON, default=list)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)


class UserLesson(Base):
    __tablename__ = "user_lessons"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    perfect: Mapped[bool] = mapped_column(Boolean, default=False)
    first_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # skipped by passing a section readiness test (completed_count stays 0 until really played)
    tested_out: Mapped[bool] = mapped_column(Boolean, default=False)


class TestAttempt(Base):
    """One sitting of a chapter (unit) test or a section readiness test."""

    __tablename__ = "test_attempts"
    __test__ = False  # not a pytest test class

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(10))  # unit | section
    target: Mapped[str] = mapped_column(String(80))  # "unit:<id>" | "section:<course id>:<name>"
    exercise_ids: Mapped[list] = mapped_column(JSON, default=list)
    results: Mapped[dict] = mapped_column(JSON, default=dict)  # {exercise id: correct}
    pass_mark: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)


class ReviewItem(Base):
    """Spaced-repetition state of one exercise for one learner (Leitner boxes 0-5)."""

    __tablename__ = "review_items"
    __table_args__ = (UniqueConstraint("user_id", "exercise_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    box: Mapped[int] = mapped_column(Integer, default=0)  # 0 = just missed ... 5 = well known
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    lapses: Mapped[int] = mapped_column(Integer, default=0)  # times answered wrong
    reviews: Mapped[int] = mapped_column(Integer, default=0)  # times practised
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    exercise_ids: Mapped[list] = mapped_column(JSON, default=list)
    results: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)
    heart_awarded: Mapped[bool] = mapped_column(Boolean, default=False)


class UserTest(Base):
    """Best result per test - a passed unit test unlocks the next unit."""

    __tablename__ = "user_tests"
    __table_args__ = (UniqueConstraint("user_id", "target"),)
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    target: Mapped[str] = mapped_column(String(80))
    best_score: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    passed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class XpEvent(Base):
    __tablename__ = "xp_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    badge: Mapped[str] = mapped_column(String(40))
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="badges")


class DailyChallengeClaim(Base):
    __tablename__ = "daily_claims"
    __table_args__ = (UniqueConstraint("user_id", "day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[date] = mapped_column(Date)
    correct: Mapped[bool] = mapped_column(Boolean, default=False)  # first answer is final


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    event: Mapped[str] = mapped_column(String(48), index=True)
    ip: Mapped[str | None] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
