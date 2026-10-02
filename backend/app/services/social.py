"""Friend codes, follows and the weekly XP leagues (everyone, or just you and the people you follow)."""
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Follow, User, XpEvent
from . import gamification

# no 0/O or 1/I/L, so a code read out loud or typed from a screenshot still works
_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LEN = 8
MAX_FOLLOWING = 100


def normalise_code(code: str) -> str:
    return "".join(ch for ch in code.upper() if ch.isalnum())


def ensure_code(db: Session, user: User) -> str:
    """Give the user a friend code the first time one is needed."""
    while not user.friend_code:
        candidate = "".join(secrets.choice(_ALPHABET) for _ in range(CODE_LEN))
        if db.scalar(select(User.id).where(User.friend_code == candidate)):
            continue
        user.friend_code = candidate
        try:
            db.commit()
        except IntegrityError:  # another request took it in the meantime
            db.rollback()
            user.friend_code = None
    return user.friend_code


def by_code(db: Session, code: str) -> User | None:
    code = normalise_code(code)
    if len(code) != CODE_LEN:
        return None
    return db.scalar(select(User).where(User.friend_code == code, User.is_active.is_(True)))


def following_ids(db: Session, user: User) -> set[int]:
    return set(db.scalars(select(Follow.followee_id).where(Follow.follower_id == user.id)))


def follower_ids(db: Session, user: User) -> set[int]:
    return set(db.scalars(select(Follow.follower_id).where(Follow.followee_id == user.id)))


def week_start() -> datetime:
    today = gamification.today()
    return datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time(), tzinfo=timezone.utc)


def weekly_xp(db: Session, user_ids: set[int]) -> dict[int, int]:
    if not user_ids:
        return {}
    rows = db.execute(
        select(XpEvent.user_id, func.sum(XpEvent.amount))
        .where(XpEvent.created_at >= week_start(), XpEvent.user_id.in_(user_ids))
        .group_by(XpEvent.user_id)
    ).all()
    return {uid: int(xp) for uid, xp in rows}


def league(db: Session, user: User, scope: str) -> list[dict]:
    """Weekly XP ranking. Only display names, avatars and friend codes are exposed - never emails."""
    following = following_ids(db, user)
    if scope == "friends":
        ids = following | {user.id}
        users = db.scalars(select(User).where(User.id.in_(ids), User.is_active.is_(True))).all()
        xp = weekly_xp(db, ids)
        # everyone you follow is listed, even with 0 XP this week
        rows = sorted(((u, xp.get(u.id, 0)) for u in users), key=lambda r: (-r[1], r[0].id))
    else:
        top = db.execute(
            select(User, func.sum(XpEvent.amount).label("xp"))
            .join(XpEvent, XpEvent.user_id == User.id)
            .where(XpEvent.created_at >= week_start(), User.is_active.is_(True))
            .group_by(User.id)
            .order_by(func.sum(XpEvent.amount).desc(), User.id)
            .limit(50)
        ).all()
        rows = [(u, int(x)) for u, x in top]
    for u, _ in rows:
        ensure_code(db, u)
    return [
        {
            "rank": i + 1,
            "name": u.name,
            "avatar_url": u.avatar_url,
            "code": u.friend_code,
            "xp": xp,
            "streak": gamification.current_streak(u),
            "me": u.id == user.id,
            "following": u.id in following,
        }
        for i, (u, xp) in enumerate(rows)
    ]


def friend_card(user: User, xp_week: int, follows_you: bool) -> dict:
    return {
        "code": user.friend_code,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "streak": gamification.current_streak(user),
        "xp_week": xp_week,
        "follows_you": follows_you,
    }
