"""Dashboard statistics, leaderboard and profile settings."""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Course, Lesson, Unit, User, UserLesson, XpEvent
from ..schemas import me_out
from ..security.deps import get_current_user
from ..services import gamification

router = APIRouter(prefix="/api", tags=["stats"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


@router.get("/stats")
def stats(user: CurrentUser, db: DB):
    today = gamification.today()
    start = today - timedelta(days=13)
    events = db.execute(
        select(XpEvent.amount, XpEvent.created_at).where(
            XpEvent.user_id == user.id,
            XpEvent.created_at >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc),
        )
    ).all()
    per_day = {start + timedelta(days=i): 0 for i in range(14)}
    for amount, created in events:
        d = gamification.aware(created).date()
        if d in per_day:
            per_day[d] += amount

    per_course = db.execute(
        select(Course.title, func.count(UserLesson.id))
        .select_from(UserLesson)
        .join(Lesson, Lesson.id == UserLesson.lesson_id)
        .join(Unit, Unit.id == Lesson.unit_id)
        .join(Course, Course.id == Unit.course_id)
        .where(UserLesson.user_id == user.id)
        .group_by(Course.title)
    ).all()
    earned = {b.badge: b.earned_at for b in user.badges}
    return {
        "xp_by_day": [{"day": d.strftime("%b %d"), "xp": xp} for d, xp in per_day.items()],
        "lessons_by_course": [{"course": title, "lessons": n} for title, n in per_course],
        "badges": [
            {"key": k, **meta, "earned": k in earned, "earned_at": earned[k].isoformat() if k in earned else None}
            for k, meta in gamification.BADGES.items()
        ],
        "lessons_completed": sum(n for _, n in per_course),
    }


@router.get("/leaderboard")
def leaderboard(user: CurrentUser, db: DB):
    """Weekly XP league. Only display names/avatars are exposed - never emails."""
    today = gamification.today()
    week_start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time(), tzinfo=timezone.utc)
    rows = db.execute(
        select(User.id, User.name, User.avatar_url, func.sum(XpEvent.amount).label("xp"))
        .join(XpEvent, XpEvent.user_id == User.id)
        .where(XpEvent.created_at >= week_start, User.is_active.is_(True))
        .group_by(User.id, User.name, User.avatar_url)
        .order_by(func.sum(XpEvent.amount).desc(), User.id)
        .limit(50)
    ).all()
    board = [
        {"rank": i + 1, "name": name, "avatar_url": avatar, "xp": int(xp), "me": uid == user.id}
        for i, (uid, name, avatar, xp) in enumerate(rows)
    ]
    return {"week_start": week_start.date().isoformat(), "entries": board}


class ProfileIn(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=60, pattern=r"^[^<>]*$")
    daily_goal: int | None = Field(None, ge=10, le=200)


@router.patch("/profile")
def update_profile(body: ProfileIn, user: CurrentUser, db: DB):
    if body.name is not None:
        user.name = body.name.strip()
    if body.daily_goal is not None:
        user.daily_goal = body.daily_goal
    db.commit()
    return me_out(db, user)
