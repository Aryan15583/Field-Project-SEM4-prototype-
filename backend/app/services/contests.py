"""Weekly contests: every course gets a new 10-question contest each ISO week (Monday 00:00 UTC).

Everyone gets the same questions; each learner has ONE timed run of 10 minutes. Ranking is by score, then
by time taken. Answers are graded on the server and only right/wrong is shown, so answers can't be shared
while the contest is live. Runs that run out of time are closed automatically.
"""
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Contest, ContestEntry, Course, User
from . import gamification
from .progress import QUIZ_KINDS

QUESTIONS = 10
DURATION = timedelta(minutes=10)
MIN_SECONDS_PER_ANSWER = 2  # anti-automation
XP_PER_CORRECT = 3
PERFECT_BONUS = 10


def week_bounds(now: datetime) -> tuple[str, datetime, datetime]:
    monday = (now - timedelta(days=now.weekday())).date()
    start = datetime.combine(monday, datetime.min.time(), tzinfo=timezone.utc)
    iso = monday.isocalendar()
    return f"{iso.year}-W{iso.week:02d}", start, start + timedelta(days=7)


def _pick(course: Course, week: str) -> list[int]:
    """Same questions for everyone this week: a seeded draw spread over the whole course."""
    rng = random.Random(f"{week}:{course.slug}")
    units = sorted(course.units, key=lambda u: u.position)
    pools = []
    for unit in units:
        pool = sorted((e.id for l in unit.lessons for e in l.exercises if e.kind in QUIZ_KINDS))
        if pool:
            rng.shuffle(pool)
            pools.append(pool)
    rng.shuffle(pools)
    picked: list[int] = []
    while len(picked) < QUESTIONS and any(pools):
        for pool in pools:
            if pool and len(picked) < QUESTIONS:
                picked.append(pool.pop())
    return picked


def current(db: Session, course: Course, now: datetime | None = None) -> Contest:
    week, start, end = week_bounds(now or datetime.now(timezone.utc))
    contest = db.scalar(select(Contest).where(Contest.course_id == course.id, Contest.week == week))
    if contest is None:
        contest = Contest(course_id=course.id, week=week, starts_at=start, ends_at=end, exercise_ids=_pick(course, week))
        db.add(contest)
        try:
            db.commit()
        except IntegrityError:  # created by a parallel request
            db.rollback()
            contest = db.scalar(select(Contest).where(Contest.course_id == course.id, Contest.week == week))
    return contest


def deadline(entry: ContestEntry, contest: Contest) -> datetime:
    return min(gamification.aware(entry.started_at) + DURATION, gamification.aware(contest.ends_at))


def finish(db: Session, entry: ContestEntry, contest: Contest, user: User, now: datetime | None = None) -> list[str]:
    """Close a run (on request or when its time is up) and award XP once. Returns new badges."""
    if entry.finished_at is not None:
        return []
    now = now or datetime.now(timezone.utc)
    end = min(now, deadline(entry, contest))
    entry.finished_at = end
    entry.time_ms = int((end - gamification.aware(entry.started_at)).total_seconds() * 1000)
    entry.score = sum(1 for v in entry.results.values() if v)
    entry.xp_awarded = entry.score * XP_PER_CORRECT + (PERFECT_BONUS if entry.score == len(contest.exercise_ids) else 0)
    gamification.award_xp(db, user, entry.xp_awarded, "contest")
    earned: list[str] = []
    gamification.grant_badge(db, user, "contender", earned)
    return earned


def close_expired(db: Session, contest: Contest, now: datetime | None = None) -> None:
    now = now or datetime.now(timezone.utc)
    open_entries = db.scalars(select(ContestEntry).where(ContestEntry.contest_id == contest.id, ContestEntry.finished_at.is_(None))).all()
    changed = False
    for e in open_entries:
        if deadline(e, contest) <= now:
            finish(db, e, contest, db.get(User, e.user_id), now)
            changed = True
    if changed:
        db.commit()


def ranking(db: Session, contest: Contest) -> list[tuple[ContestEntry, User]]:
    """Finished runs first (score desc, then time asc), then runs still in progress (live score)."""
    rows = db.execute(
        select(ContestEntry, User).join(User, User.id == ContestEntry.user_id).where(ContestEntry.contest_id == contest.id, User.is_active.is_(True))
    ).all()

    def key(row):
        e = row[0]
        live = sum(1 for v in e.results.values() if v)
        return (e.finished_at is None, -(e.score if e.finished_at else live), e.time_ms if e.finished_at else 0, e.id)

    return sorted(rows, key=key)


def rank_of(db: Session, contest: Contest, user_id: int) -> int | None:
    for i, (e, _) in enumerate(ranking(db, contest)):
        if e.user_id == user_id and e.finished_at is not None:
            return i + 1
    return None


def entrants(db: Session, contest: Contest) -> int:
    return db.scalar(select(func.count(ContestEntry.id)).where(ContestEntry.contest_id == contest.id)) or 0
