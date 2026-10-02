from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Exercise, TestAttempt, User
from ..security.deps import get_current_user
from ..security.ratelimit import check
from ..services import ai_tutor

router = APIRouter(prefix="/api/ai", tags=["ai"])


class HintIn(BaseModel):
    exercise_id: int
    attempt: str | None = Field(None, max_length=2000)


@router.post("/hint")
async def get_hint(body: HintIn, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    # Per-user hourly budget: protects the paid AI API from abuse / cost-exhaustion attacks.
    allowed, retry = check(f"ai:u{user.id}", get_settings().rate_limit_ai_per_hour, 3600)
    if not allowed:
        raise HTTPException(429, "Hint limit reached for this hour. Try solving it on your own!", headers={"Retry-After": str(retry)})
    ex = db.get(Exercise, body.exercise_id)
    if ex is None:
        raise HTTPException(404, "Exercise not found")
    if _in_open_test(db, user, ex.id):
        raise HTTPException(403, "Hints aren't available during a test - you've got this!")
    text, source = await ai_tutor.hint(ex, body.attempt)
    return {"hint": text, "source": source}


@router.get("/status")
def status(user: Annotated[User, Depends(get_current_user)]):
    return {"ai_enabled": ai_tutor.configured()}


def _in_open_test(db: Session, user: User, exercise_id: int) -> bool:
    since = datetime.now(timezone.utc) - timedelta(hours=2)  # test attempts expire after 2 hours
    open_tests = db.scalars(
        select(TestAttempt.exercise_ids).where(
            TestAttempt.user_id == user.id, TestAttempt.completed_at.is_(None), TestAttempt.started_at >= since
        )
    )
    return any(exercise_id in ids for ids in open_tests)
