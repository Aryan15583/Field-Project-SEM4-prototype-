"""Friends (follow by friend code) and one-click unsubscribe from streak reminder emails."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Follow, User
from ..security.deps import get_current_user
from ..security.ratelimit import limit
from ..services import gamification, reminders, social

router = APIRouter(prefix="/api", tags=["social"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]
Code = Annotated[str, Field(min_length=4, max_length=20, pattern=r"^[A-Za-z0-9 -]+$")]


class FollowIn(BaseModel):
    code: Code


def _target(db: Session, user: User, code: str) -> User:
    other = social.by_code(db, code)
    if other is None:
        raise HTTPException(404, "No learner has that friend code.")
    if other.id == user.id:
        raise HTTPException(400, "That's your own friend code.")
    return other


@router.get("/friends")
def friends(user: CurrentUser, db: DB):
    following = db.scalars(
        select(User).join(Follow, Follow.followee_id == User.id).where(Follow.follower_id == user.id, User.is_active.is_(True))
    ).all()
    followers = social.follower_ids(db, user)
    xp = social.weekly_xp(db, {u.id for u in following})
    cards = [social.friend_card(u, xp.get(u.id, 0), u.id in followers) for u in following]
    cards.sort(key=lambda c: (-c["xp_week"], c["name"].lower()))
    return {"code": social.ensure_code(db, user), "following": cards, "followers": len(followers)}


@router.get("/friends/lookup", dependencies=[Depends(limit("friend_lookup", 30))])
def lookup(user: CurrentUser, db: DB, code: Annotated[str, Query(min_length=4, max_length=20)]):
    """Preview who a code (e.g. from an invite link) belongs to before following them."""
    other = _target(db, user, code)
    following = db.scalar(select(Follow.id).where(Follow.follower_id == user.id, Follow.followee_id == other.id)) is not None
    return {"code": other.friend_code, "name": other.name, "avatar_url": other.avatar_url, "following": following}


@router.post("/friends", dependencies=[Depends(limit("follow", 20))])
def follow(body: FollowIn, user: CurrentUser, db: DB):
    other = _target(db, user, body.code)
    following = social.following_ids(db, user)
    new_badges: list[str] = []
    if other.id not in following:
        if len(following) >= social.MAX_FOLLOWING:
            raise HTTPException(400, f"You can follow up to {social.MAX_FOLLOWING} people.")
        db.add(Follow(follower_id=user.id, followee_id=other.id))
        gamification.grant_badge(db, user, "friend", new_badges)
        db.commit()
    xp = social.weekly_xp(db, {other.id}).get(other.id, 0)
    follows_you = user.id in social.following_ids(db, other)
    return {"friend": social.friend_card(other, xp, follows_you), "new_badges": new_badges}


@router.delete("/friends/{code}")
def unfollow(code: str, user: CurrentUser, db: DB):
    other = social.by_code(db, code)
    if other is not None:
        db.execute(delete(Follow).where(Follow.follower_id == user.id, Follow.followee_id == other.id))
        db.commit()
    return {"ok": True}


@router.post("/public/unsubscribe", dependencies=[Depends(limit("unsubscribe", 20))])
def unsubscribe(db: DB, u: int = Query(..., ge=1), t: str = Query(..., max_length=64)):
    """Turn streak reminders off. Authorised by the signed link in the email - no sign-in needed."""
    if not reminders.valid_token(u, t):
        raise HTTPException(400, "This unsubscribe link is invalid.")
    user = db.get(User, u)
    if user is not None:
        user.reminder_emails = False
        db.commit()
    return {"ok": True}
