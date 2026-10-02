"""Dashboard statistics, leaderboard and profile settings."""
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Course, Lesson, Unit, User, UserLesson, XpEvent
from ..schemas import me_out
from ..security.deps import get_current_user
from ..services import gamification, social

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
        .where(UserLesson.user_id == user.id, UserLesson.completed_count > 0)
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
def leaderboard(user: CurrentUser, db: DB, scope: Literal["global", "friends"] = "global"):
    """Weekly XP league - everyone, or just you and the people you follow."""
    return {"week_start": social.week_start().date().isoformat(), "scope": scope, "entries": social.league(db, user, scope)}


class ProfileIn(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=60, pattern=r"^[^<>]*$")
    daily_goal: int | None = Field(None, ge=10, le=200)
    reminder_emails: bool | None = None


@router.patch("/profile")
def update_profile(body: ProfileIn, user: CurrentUser, db: DB):
    if body.name is not None:
        user.name = body.name.strip()
    if body.daily_goal is not None:
        user.daily_goal = body.daily_goal
    if body.reminder_emails is not None:
        user.reminder_emails = body.reminder_emails
    db.commit()
    return me_out(db, user)
