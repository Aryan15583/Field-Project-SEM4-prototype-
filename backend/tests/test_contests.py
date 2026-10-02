from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Contest, ContestEntry, Exercise, User
from app.curriculum import CURRICULUM
from app.services import contests

from .conftest import enroll
from .test_checkpoints import _wrong
from .test_learning import _answer_for


def _python(client):
    data = client.get("/api/contests").json()
    return next(c for c in data["current"] if c["course"] == "python")


def _rewind(contest_id, email="learner@example.com", seconds=60):
    """Pretend the run started earlier (answers need >= 2s each)."""
    with SessionLocal() as db:
        uid = db.scalar(select(User.id).where(User.email == email))
        e = db.scalar(select(ContestEntry).where(ContestEntry.contest_id == contest_id, ContestEntry.user_id == uid))
        e.started_at -= timedelta(seconds=seconds)
        db.commit()


def _play(client, contest_id, n_correct, email="learner@example.com"):
    run = client.post(f"/api/contests/{contest_id}/enter").json()
    _rewind(contest_id, email)
    with SessionLocal() as db:
        for i, q in enumerate(run["questions"]):
            ex = db.get(Exercise, q["id"])
            ans = _answer_for(ex) if i < n_correct else _wrong(ex)
            r = client.post(f"/api/contests/{contest_id}/answer", json={"exercise_id": q["id"], "answer": ans})
            assert r.status_code == 200, r.text
            assert "correct_answer" not in r.json()  # never revealed while the contest is live
    return client.post(f"/api/contests/{contest_id}/finish").json()


def test_every_course_has_a_weekly_contest_with_the_same_questions(client):
    enroll(client)
    data = client.get("/api/contests").json()
    assert data["questions"] == 10 and data["minutes"] == 10
    assert len(data["current"]) == len(CURRICULUM) and all(c["live"] and c["me"]["status"] == "open" for c in data["current"])
    c = _python(client)
    first = client.post(f"/api/contests/{c['id']}/enter").json()
    assert len(first["questions"]) == 10 and len({q["id"] for q in first["questions"]}) == 10
    assert all(q["kind"] in ("mcq", "fill", "order", "code") for q in first["questions"])
    assert all("solution" not in q for q in first["questions"])
    again = client.post(f"/api/contests/{c['id']}/enter").json()  # reload resumes the same run
    assert again["started_at"] == first["started_at"] and [q["id"] for q in again["questions"]] == [q["id"] for q in first["questions"]]

    client.post("/api/auth/logout")
    enroll(client, "rival@example.com", "Rival")
    theirs = client.post(f"/api/contests/{c['id']}/enter").json()
    assert [q["id"] for q in theirs["questions"]] == [q["id"] for q in first["questions"]]


def test_scoring_ranking_and_live_leaderboard(client):
    enroll(client, "ada@example.com", "Ada")
    cid = _python(client)["id"]
    res = _play(client, cid, 10, "ada@example.com")
    assert res["score"] == 10 and res["xp"] == 10 * contests.XP_PER_CORRECT + contests.PERFECT_BONUS
    assert res["rank"] == 1 and "contender" in res["new_badges"]
    assert client.post(f"/api/contests/{cid}/finish").json()["xp"] == 0  # XP only once
    assert client.post(f"/api/contests/{cid}/enter").status_code == 409  # one run per week

    client.post("/api/auth/logout")
    enroll(client, "bob@example.com", "Bob")
    run = client.post(f"/api/contests/{cid}/enter").json()
    _rewind(cid, "bob@example.com")
    with SessionLocal() as db:
        q = run["questions"][0]
        client.post(f"/api/contests/{cid}/answer", json={"exercise_id": q["id"], "answer": _answer_for(db.get(Exercise, q["id"]))})
    board = client.get(f"/api/contests/{cid}/leaderboard").json()
    assert board["live"] and [(e["name"], e["rank"], e["score"], e["finished"]) for e in board["entries"]] == [
        ("Ada", 1, 10, True),
        ("Bob", None, 1, False),  # in progress: live score, no rank yet
    ]
    assert all("email" not in e for e in board["entries"])
    assert client.post(f"/api/contests/{cid}/answer", json={"exercise_id": q["id"], "answer": 0}).status_code == 409
    res = client.post(f"/api/contests/{cid}/finish").json()
    assert res["score"] == 1 and res["rank"] == 2 and res["entrants"] == 2
    me = _python(client)["me"]
    assert me == {"status": "finished", "score": 1, "rank": 2}


def test_time_limit_and_anti_automation(client):
    enroll(client)
    cid = _python(client)["id"]
    run = client.post(f"/api/contests/{cid}/enter").json()
    q = run["questions"][0]
    assert client.post(f"/api/contests/{cid}/answer", json={"exercise_id": q["id"], "answer": 0}).status_code == 429  # instantly
    _rewind(cid, seconds=11 * 60)  # out of time
    assert client.post(f"/api/contests/{cid}/answer", json={"exercise_id": q["id"], "answer": 0}).status_code == 410
    with SessionLocal() as db:
        e = db.scalar(select(ContestEntry))
        assert e.finished_at is not None and e.time_ms == contests.DURATION.total_seconds() * 1000
    assert client.post(f"/api/contests/{cid}/answer", json={"exercise_id": 999999, "answer": 0}).status_code == 409


def test_expired_runs_are_closed_on_the_leaderboard(client):
    enroll(client)
    cid = _python(client)["id"]
    client.post(f"/api/contests/{cid}/enter")
    _rewind(cid, seconds=20 * 60)  # walked away mid-contest
    board = client.get(f"/api/contests/{cid}/leaderboard").json()
    assert board["entries"][0]["finished"] and board["entries"][0]["rank"] == 1


def test_hints_are_blocked_during_a_run(client):
    enroll(client)
    cid = _python(client)["id"]
    q = client.post(f"/api/contests/{cid}/enter").json()["questions"][0]
    assert client.post("/api/ai/hint", json={"exercise_id": q["id"], "attempt": "x"}).status_code == 403
    client.post(f"/api/contests/{cid}/finish")
    assert client.post("/api/ai/hint", json={"exercise_id": q["id"], "attempt": "x"}).status_code == 200


def test_ended_contest_and_new_week(client):
    enroll(client)
    cid = _python(client)["id"]
    with SessionLocal() as db:
        c = db.get(Contest, cid)
        c.ends_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    assert client.post(f"/api/contests/{cid}/enter").status_code == 410
    with SessionLocal() as db:
        week, start, end = contests.week_bounds(datetime(2030, 1, 9, 15, tzinfo=timezone.utc))
        assert week == "2030-W02" and start.weekday() == 0 and start.date().isoformat() == "2030-01-07" and (end - start).days == 7
