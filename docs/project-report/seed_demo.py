"""Fills a throw-away demo database so the report's screenshots show a realistic account.
   python seed_demo.py base     -> other learners + the demo learner's progress
   python seed_demo.py contest  -> other learners' finished runs in this week's Python contest"""
import os, sys, random
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "/home/user/.vscode/backend")
from sqlalchemy import select
from app.db import SessionLocal
from app.models import *  # noqa
from app.services import social, progress, gamification

ME = "aryan.demo@example.com"
OTHERS = [("Diya Nair", 410, 9), ("Kabir Mehta", 360, 5), ("Meera Iyer", 295, 12), ("Zoya Khan", 240, 3), ("Vihaan Rao", 180, 2), ("Ishaan Gupta", 120, 1)]
now = datetime.now(timezone.utc)
rng = random.Random(7)

def course(db, slug): return db.scalar(select(Course).where(Course.slug == slug))

with SessionLocal() as db:
    if sys.argv[1] == "base":
        me = db.scalar(select(User).where(User.email == ME))
        py = course(db, "python")
        units = sorted(py.units, key=lambda u: u.position)
        for u in units[:2]:
            for l in u.lessons:
                db.add(UserLesson(user_id=me.id, lesson_id=l.id, completed_count=1, perfect=rng.random() > .4, first_completed_at=now - timedelta(days=3)))
            db.add(UserTest(user_id=me.id, target=progress.unit_target(u.id), best_score=7, attempts=1, passed_at=now - timedelta(days=2)))
        # a week and a half of activity
        total = 0
        for d in range(10, -1, -1):
            amt = rng.choice([20, 30, 40, 50, 60, 80]) if d not in (3, 7) else 0
            if amt:
                db.add(XpEvent(user_id=me.id, amount=amt, reason="lesson", created_at=now - timedelta(days=d, hours=2))); total += amt
        me.xp_total = total + 0; me.streak_current = 6; me.streak_best = 9; me.last_active_date = gamification.today(); me.hearts = 5
        for b in ("first_lesson", "perfect", "streak_3", "checkpoint", "practice", "xp_100"):
            db.add(UserBadge(user_id=me.id, badge=b))
        # review list: 14 python questions, a few missed (box 0) and due
        ex = [e for u in units[:2] for l in u.lessons for e in l.exercises if e.kind in ("mcq", "fill", "order", "code")][:14]
        for i, e in enumerate(ex):
            db.add(ReviewItem(user_id=me.id, exercise_id=e.id, box=0 if i < 6 else rng.choice([1, 2, 3]), due_at=now - timedelta(hours=1) if i < 8 else now + timedelta(days=2), lapses=1 if i < 6 else 0, reviews=rng.randint(1, 3), updated_at=now))
        # certificate for the Git course (shown on the profile + public certificate page)
        git = course(db, "git")
        db.add(Certificate(id="Qm7rT2xVbKp9Ld4Ws", user_id=me.id, course_id=git.id, holder_name="Aryan", course_title="Git", lessons=27, issued_at=now - timedelta(days=1)))
        db.commit()
        # other learners
        for name, xp, streak in OTHERS:
            u = User(email=name.split()[0].lower() + "@example.com", name=name, mfa_enabled=True, mfa_method="email", xp_total=xp, streak_current=streak, streak_best=streak, last_active_date=gamification.today(), hearts=5)
            db.add(u); db.flush(); social.ensure_code(db, u)
            left = xp
            for d in range(0, 5):
                part = min(left, max(10, xp // 5)) if left > 0 else 0
                if part: db.add(XpEvent(user_id=u.id, amount=part, reason="lesson", created_at=now - timedelta(hours=3 + d * 2))); left -= part
        db.commit()
        for u in db.scalars(select(User).where(User.name.in_(["Diya Nair", "Kabir Mehta", "Meera Iyer", "Zoya Khan"]))):
            db.add(Follow(follower_id=me.id, followee_id=u.id))
        db.add(Follow(follower_id=db.scalar(select(User.id).where(User.name == "Diya Nair")), followee_id=me.id))
        db.commit()
        print("seeded base")
    else:
        c = db.scalar(select(Contest).join(Course, Course.id == Contest.course_id).where(Course.slug == "python"))
        for name, score, ms in (("Diya Nair", 10, 212000), ("Meera Iyer", 9, 301000), ("Kabir Mehta", 9, 388000), ("Zoya Khan", 7, 455000)):
            uid = db.scalar(select(User.id).where(User.name == name))
            db.add(ContestEntry(contest_id=c.id, user_id=uid, started_at=now - timedelta(minutes=30), finished_at=now - timedelta(minutes=20), results={str(i): True for i in c.exercise_ids[:score]}, score=score, time_ms=ms, xp_awarded=score * 3))
        db.commit(); print("seeded contest", c.id)
