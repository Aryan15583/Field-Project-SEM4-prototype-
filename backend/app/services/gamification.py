"""XP, streaks, hearts and badges. All awarding happens server-side only."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Course, Lesson, Unit, User, UserBadge, UserLesson, XpEvent
from ..security.tokens import aware

BADGES: dict[str, dict] = {
    "first_lesson": {"name": "Hello, World!", "icon": "👋", "desc": "Complete your first lesson"},
    "perfect": {"name": "Flawless", "icon": "💎", "desc": "Finish a lesson without mistakes"},
    "streak_3": {"name": "On Fire", "icon": "🔥", "desc": "Reach a 3-day streak"},
    "streak_7": {"name": "Week Warrior", "icon": "⚡", "desc": "Reach a 7-day streak"},
    "xp_100": {"name": "Centurion", "icon": "💯", "desc": "Earn 100 XP"},
    "xp_500": {"name": "XP Hoarder", "icon": "🏆", "desc": "Earn 500 XP"},
    "polyglot": {"name": "Polyglot", "icon": "🌐", "desc": "Complete lessons in 3 languages"},
    "daily": {"name": "Challenger", "icon": "🎯", "desc": "Solve a daily challenge"},
    "checkpoint": {"name": "Checkpoint", "icon": "🏁", "desc": "Pass a chapter test"},
    "jumper": {"name": "Fast Track", "icon": "🚀", "desc": "Pass a readiness test to jump ahead"},
    "practice": {"name": "Sharpened", "icon": "🧠", "desc": "Finish a practice session"},
    "friend": {"name": "Friendly", "icon": "🤝", "desc": "Follow a friend"},
}


def today() -> date:
    return datetime.now(timezone.utc).date()


def refill_hearts(user: User) -> None:
    s = get_settings()
    if user.hearts >= s.max_hearts:
        user.hearts_updated_at = datetime.now(timezone.utc)
        return
    elapsed = datetime.now(timezone.utc) - aware(user.hearts_updated_at)
    gained = int(elapsed.total_seconds() // (s.heart_refill_minutes * 60))
    if gained > 0:
        user.hearts = min(s.max_hearts, user.hearts + gained)
        user.hearts_updated_at = aware(user.hearts_updated_at) + timedelta(minutes=gained * s.heart_refill_minutes)


def lose_heart(user: User) -> None:
    refill_hearts(user)
    if user.hearts >= get_settings().max_hearts:
        user.hearts_updated_at = datetime.now(timezone.utc)
    user.hearts = max(0, user.hearts - 1)


def current_streak(user: User) -> int:
    if user.last_active_date is None or user.last_active_date < today() - timedelta(days=1):
        return 0
    return user.streak_current


def award_xp(db: Session, user: User, amount: int, reason: str) -> None:
    if amount <= 0:
        return
    db.add(XpEvent(user_id=user.id, amount=amount, reason=reason))
    user.xp_total += amount
    d = today()
    if user.last_active_date != d:
        user.streak_current = user.streak_current + 1 if user.last_active_date == d - timedelta(days=1) else 1
        user.last_active_date = d
    user.streak_best = max(user.streak_best, user.streak_current)


def grant_badge(db: Session, user: User, key: str, earned: list[str]) -> None:
    if not db.scalar(select(UserBadge.id).where(UserBadge.user_id == user.id, UserBadge.badge == key)):
        db.add(UserBadge(user_id=user.id, badge=key))
        earned.append(key)


def check_badges(
    db: Session, user: User, *, perfect: bool = False, daily: bool = False, test: str | None = None, practice: bool = False
) -> list[str]:
    earned: list[str] = []
    db.flush()
    # lessons actually played (rows from testing out have completed_count 0)
    played = (UserLesson.user_id == user.id) & (UserLesson.completed_count > 0)
    lessons_done = db.scalar(select(func.count()).select_from(UserLesson).where(played)) or 0
    if lessons_done >= 1:
        grant_badge(db, user, "first_lesson", earned)
    if perfect:
        grant_badge(db, user, "perfect", earned)
    if daily:
        grant_badge(db, user, "daily", earned)
    if test == "unit":
        grant_badge(db, user, "checkpoint", earned)
    if test == "section":
        grant_badge(db, user, "jumper", earned)
    if practice:
        grant_badge(db, user, "practice", earned)
    if user.streak_current >= 3:
        grant_badge(db, user, "streak_3", earned)
    if user.streak_current >= 7:
        grant_badge(db, user, "streak_7", earned)
    if user.xp_total >= 100:
        grant_badge(db, user, "xp_100", earned)
    if user.xp_total >= 500:
        grant_badge(db, user, "xp_500", earned)
    languages = db.scalar(
        select(func.count(func.distinct(Course.id)))
        .select_from(UserLesson)
        .join(Lesson, Lesson.id == UserLesson.lesson_id)
        .join(Unit, Unit.id == Lesson.unit_id)
        .join(Course, Course.id == Unit.course_id)
        .where(played)
    ) or 0
    if languages >= 3:
        grant_badge(db, user, "polyglot", earned)
    return earned


def xp_today(db: Session, user: User) -> int:
    start = datetime.combine(today(), datetime.min.time(), tzinfo=timezone.utc)
    return db.scalar(select(func.coalesce(func.sum(XpEvent.amount), 0)).where(XpEvent.user_id == user.id, XpEvent.created_at >= start)) or 0
