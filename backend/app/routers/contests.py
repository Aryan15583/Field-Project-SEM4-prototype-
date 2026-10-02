"""Weekly contests with a live leaderboard (see services/contests.py)."""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Contest, ContestEntry, Course, Exercise, Lesson, Unit, User
from ..schemas import public_exercise
from ..security.deps import get_current_user
from ..security.ratelimit import limit
from ..services import contests, gamification, grading, review
from .learn import AnswerIn

router = APIRouter(prefix="/api/contests", tags=["contests"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


def _courses(db: Session) -> list[Course]:
    return list(
        db.scalars(
            select(Course).order_by(Course.position).options(selectinload(Course.units).selectinload(Unit.lessons).selectinload(Lesson.exercises))
        )
    )


def _summary(db: Session, contest: Contest, course: Course, user: User) -> dict:
    now = datetime.now(timezone.utc)
    contests.close_expired(db, contest, now)
    mine = db.scalar(select(ContestEntry).where(ContestEntry.contest_id == contest.id, ContestEntry.user_id == user.id))
    status = "open" if mine is None else ("finished" if mine.finished_at else "running")
    top = contests.ranking(db, contest)
    leader = next(((u.name, e.score) for e, u in top if e.finished_at), None)
    return {
        "id": contest.id,
        "week": contest.week,
        "course": course.slug,
        "course_title": course.title,
        "icon": course.icon,
        "questions": len(contest.exercise_ids),
        "minutes": int(contests.DURATION.total_seconds() // 60),
        "starts_at": gamification.aware(contest.starts_at).isoformat(),
        "ends_at": gamification.aware(contest.ends_at).isoformat(),
        "live": gamification.aware(contest.ends_at) > now,
        "entrants": len(top),
        "leader": {"name": leader[0], "score": leader[1]} if leader else None,
        "me": {
            "status": status,
            "score": mine.score if mine and mine.finished_at else None,
            "rank": contests.rank_of(db, contest, user.id) if mine and mine.finished_at else None,
        },
    }


@router.get("")
def list_contests(user: CurrentUser, db: DB):
    """This week's contest for every course, plus last week's results."""
    now = datetime.now(timezone.utc)
    current, previous = [], []
    for course in _courses(db):
        current.append(_summary(db, contests.current(db, course, now), course, user))
        week, _, _ = contests.week_bounds(now - timedelta(days=7))
        last = db.scalar(select(Contest).where(Contest.course_id == course.id, Contest.week == week))
        if last is not None and contests.entrants(db, last):
            s = _summary(db, last, course, user)
            if s["me"]["rank"] and s["me"]["rank"] <= 3 and s["entrants"] >= 3:
                gamification.grant_badge(db, user, "podium", [])
                db.commit()
            previous.append(s)
    return {"current": current, "previous": previous, "minutes": int(contests.DURATION.total_seconds() // 60), "questions": contests.QUESTIONS}


def _contest(db: Session, contest_id: int) -> tuple[Contest, Course]:
    contest = db.get(Contest, contest_id)
    if contest is None:
        raise HTTPException(404, "Contest not found")
    return contest, db.get(Course, contest.course_id)


def _entry(db: Session, contest: Contest, user: User, *, lock=False) -> ContestEntry:
    q = select(ContestEntry).where(ContestEntry.contest_id == contest.id, ContestEntry.user_id == user.id)
    entry = db.scalar(q.with_for_update() if lock else q)
    if entry is None:
        raise HTTPException(404, "You haven't entered this contest")
    return entry


@router.post("/{contest_id}/enter", dependencies=[Depends(limit("contest_enter", 20))])
def enter(contest_id: int, user: CurrentUser, db: DB):
    """Start (or resume, after a reload) your one timed run."""
    contest, course = _contest(db, contest_id)
    now = datetime.now(timezone.utc)
    if gamification.aware(contest.ends_at) <= now:
        raise HTTPException(410, "This contest has ended")
    entry = db.scalar(select(ContestEntry).where(ContestEntry.contest_id == contest.id, ContestEntry.user_id == user.id))
    if entry is None:
        entry = ContestEntry(contest_id=contest.id, user_id=user.id, results={})
        db.add(entry)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            entry = _entry(db, contest, user)
    contests.close_expired(db, contest, now)
    if entry.finished_at is not None:
        raise HTTPException(409, "You've already taken this week's contest - see the leaderboard")
    by_id = {e.id: e for e in db.scalars(select(Exercise).where(Exercise.id.in_(contest.exercise_ids)))}
    return {
        "contest_id": contest.id,
        "title": f"{course.title} · Weekly contest",
        "course": course.slug,
        "started_at": gamification.aware(entry.started_at).isoformat(),
        "deadline": contests.deadline(entry, contest).isoformat(),
        "answered": entry.results,  # resume: what's already answered
        "questions": [public_exercise(by_id[i]) for i in contest.exercise_ids if i in by_id],
    }


@router.post("/{contest_id}/answer", dependencies=[Depends(limit("contest_answer", 60))])
def answer(contest_id: int, body: AnswerIn, user: CurrentUser, db: DB):
    contest, _ = _contest(db, contest_id)
    entry = _entry(db, contest, user, lock=True)  # serialises parallel answers
    now = datetime.now(timezone.utc)
    if entry.finished_at is not None:
        raise HTTPException(409, "Your run is finished")
    if contests.deadline(entry, contest) <= now:
        contests.finish(db, entry, contest, user, now)
        db.commit()
        raise HTTPException(410, "Time's up!")
    if body.exercise_id not in contest.exercise_ids:
        raise HTTPException(404, "Question not found")
    key = str(body.exercise_id)
    if key in entry.results:
        raise HTTPException(409, "You've already answered this question")
    elapsed = (now - gamification.aware(entry.started_at)).total_seconds()
    if elapsed < contests.MIN_SECONDS_PER_ANSWER * (len(entry.results) + 1):
        raise HTTPException(429, "Slow down a little!")
    ex = db.get(Exercise, body.exercise_id)
    correct = grading.grade(ex, body.value())
    review.record(db, user, ex, correct)
    entry.results = {**entry.results, key: correct}
    db.commit()
    # only right/wrong while the contest is live - answers aren't revealed, so they can't be passed around
    return {"correct": correct, "answered": len(entry.results), "score": sum(entry.results.values())}


@router.post("/{contest_id}/finish")
def finish(contest_id: int, user: CurrentUser, db: DB):
    contest, _ = _contest(db, contest_id)
    entry = _entry(db, contest, user, lock=True)
    already = entry.finished_at is not None
    badges = contests.finish(db, entry, contest, user)
    db.commit()
    return {
        "score": entry.score,
        "total": len(contest.exercise_ids),
        "time_ms": entry.time_ms,
        "xp": 0 if already else entry.xp_awarded,
        "rank": contests.rank_of(db, contest, user.id),
        "entrants": contests.entrants(db, contest),
        "new_badges": badges,
    }


@router.get("/{contest_id}/leaderboard", dependencies=[Depends(limit("contest_board", 60))])
def leaderboard(contest_id: int, user: CurrentUser, db: DB):
    """Polled every few seconds by the contest page while the contest is live."""
    contest, course = _contest(db, contest_id)
    now = datetime.now(timezone.utc)
    contests.close_expired(db, contest, now)
    rows = contests.ranking(db, contest)
    entries, rank = [], 0
    for e, u in rows:
        done = e.finished_at is not None
        if done:
            rank += 1
        if len(entries) < 100 or u.id == user.id:
            entries.append({
                "rank": rank if done else None,
                "name": u.name,
                "avatar_url": u.avatar_url,
                "score": e.score if done else sum(1 for v in e.results.values() if v),
                "answered": len(e.results),
                "time_ms": e.time_ms if done else None,
                "finished": done,
                "me": u.id == user.id,
            })
    return {
        "contest_id": contest.id,
        "title": f"{course.title} · Weekly contest",
        "course": course.slug,
        "week": contest.week,
        "questions": len(contest.exercise_ids),
        "ends_at": gamification.aware(contest.ends_at).isoformat(),
        "live": gamification.aware(contest.ends_at) > now,
        "entries": entries,
    }
