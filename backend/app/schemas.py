from pydantic import BaseModel
from sqlalchemy.orm import Session

from .models import Exercise, User
from .services import code_runner, gamification, grading


class MeOut(BaseModel):
    id: int
    email: str
    name: str
    avatar_url: str | None
    role: str
    xp_total: int
    xp_today: int
    daily_goal: int
    streak: int
    streak_best: int
    hearts: int
    max_hearts: int
    badges: list[str]
    mfa_method: str


def me_out(db: Session, user: User) -> dict:
    from .config import get_settings

    gamification.refill_hearts(user)
    db.commit()
    return MeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        role=user.role,
        xp_total=user.xp_total,
        xp_today=gamification.xp_today(db, user),
        daily_goal=user.daily_goal,
        streak=gamification.current_streak(user),
        streak_best=user.streak_best,
        hearts=user.hearts,
        max_hearts=get_settings().max_hearts,
        badges=[b.badge for b in user.badges],
        mfa_method=user.mfa_method,
    ).model_dump()


def public_exercise(ex: Exercise) -> dict:
    """Everything the learner needs to attempt an exercise - and nothing that reveals the answer."""
    data = dict(ex.data or {})
    if ex.kind == "order":
        # Stored in the correct order; only ever sent shuffled.
        data["lines"] = grading.shuffled_lines(ex)
    if ex.kind == "run" and data.get("language") in code_runner.SERVER_LANGS:
        data["server_runner"] = code_runner.configured()
    return {"id": ex.id, "kind": ex.kind, "prompt": ex.prompt, "code": ex.code, "data": data, "has_hint": bool(ex.hint)}
