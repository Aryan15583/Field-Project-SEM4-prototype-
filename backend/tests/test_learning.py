from datetime import timedelta

from app.db import SessionLocal
from app.models import Exercise, LessonAttempt
from app.services import grading

from .conftest import enroll


def _first_lesson(client, slug="python"):
    path = client.get(f"/api/courses/{slug}").json()
    return path["units"][0]["lessons"]


def _answer_for(ex: Exercise):
    if ex.kind == "run":
        # browser languages report outputs; compiled ones fall back to patterns (no runner in tests)
        return {"code": ex.solution["example"], "outputs": ex.solution["expected"]}
    if ex.kind == "mcq":
        return ex.solution["index"]
    if ex.kind == "fill":
        return ex.solution["accepted"][0]
    if ex.kind == "order":
        return list(range(len(ex.data["lines"])))
    return ex.solution["example"]


def _backdate(attempt_id: str):
    with SessionLocal() as db:
        a = db.get(LessonAttempt, attempt_id)
        a.started_at = a.started_at - timedelta(minutes=5)
        db.commit()


def test_courses_and_locking(client):
    enroll(client)
    courses = client.get("/api/courses").json()
    assert {c["slug"] for c in courses} >= {"python", "javascript", "java", "cpp", "c", "sql", "html-css"}
    lessons = _first_lesson(client)
    assert lessons[0]["status"] == "unlocked" and lessons[1]["status"] == "locked"
    assert client.post(f"/api/lessons/{lessons[1]['id']}/start").status_code == 403


def test_solutions_never_sent_before_answering(client):
    enroll(client)
    lesson = _first_lesson(client)[0]
    body = client.post(f"/api/lessons/{lesson['id']}/start").json()
    text = str(body)
    assert "solution" not in text and "accepted" not in text and "patterns" not in text


def test_complete_lesson_awards_xp_streak_badges(client):
    enroll(client)
    lesson = _first_lesson(client)[0]
    start = client.post(f"/api/lessons/{lesson['id']}/start").json()
    aid = start["attempt_id"]
    # Can't finish without answering
    assert client.post(f"/api/attempts/{aid}/complete").status_code == 400
    with SessionLocal() as db:
        for e in start["exercises"]:
            ex = db.get(Exercise, e["id"])
            r = client.post(f"/api/attempts/{aid}/answer", json={"exercise_id": ex.id, "answer": _answer_for(ex)}).json()
            assert r["correct"], ex.prompt
    # Too fast -> rejected (anti-bot)
    assert client.post(f"/api/attempts/{aid}/complete").status_code == 400
    _backdate(aid)
    done = client.post(f"/api/attempts/{aid}/complete").json()
    assert done["xp_awarded"] == 15 and done["perfect"] and done["streak"] == 1
    assert {"first_lesson", "perfect"} <= {b["key"] for b in done["new_badges"]}
    # Replaying completion doesn't double-award
    assert client.post(f"/api/attempts/{aid}/complete").status_code == 409
    assert _first_lesson(client)[1]["status"] == "unlocked"
    me = client.get("/api/auth/me").json()
    assert me["xp_total"] == 15 and me["xp_today"] == 15
    lb = client.get("/api/leaderboard").json()["entries"]
    assert lb[0]["me"] and "email" not in lb[0]


def test_wrong_answer_costs_heart(client):
    enroll(client)
    lesson = _first_lesson(client)[0]
    start = client.post(f"/api/lessons/{lesson['id']}/start").json()
    ex = start["exercises"][0]
    r = client.post(f"/api/attempts/{start['attempt_id']}/answer", json={"exercise_id": ex["id"], "answer": 3}).json()
    assert r["correct"] is False and r["hearts"] == 4 and r["correct_answer"]


def test_cannot_use_other_users_attempt(client):
    enroll(client, "a@example.com", "A")
    lesson = _first_lesson(client)[0]
    start = client.post(f"/api/lessons/{lesson['id']}/start").json()
    client.post("/api/auth/logout")
    enroll(client, "b@example.com", "B")
    ex = start["exercises"][0]
    r = client.post(f"/api/attempts/{start['attempt_id']}/answer", json={"exercise_id": ex["id"], "answer": 0})
    assert r.status_code == 404


def test_daily_challenge_single_claim(client):
    enroll(client)
    d = client.get("/api/daily").json()
    ex_id = d["exercise"]["id"]
    with SessionLocal() as db:
        ans = _answer_for(db.get(Exercise, ex_id))
    r = client.post("/api/daily/answer", json={"exercise_id": ex_id, "answer": ans}).json()
    assert r["correct"] and r["xp_awarded"] == 20
    assert client.post("/api/daily/answer", json={"exercise_id": ex_id, "answer": ans}).status_code == 409


def test_every_seeded_exercise_accepts_its_own_answer(client):
    with SessionLocal() as db:
        exercises = db.query(Exercise).all()
        assert len(exercises) >= 800
        for ex in exercises:
            assert grading.grade(ex, _answer_for(ex)), f"{ex.id}: {ex.prompt}"
            assert not grading.grade(ex, "definitely wrong"), ex.prompt


def test_run_exercise_grading_uses_hidden_expected_output(client):
    enroll(client)
    with SessionLocal() as db:
        ex = next(e for e in db.query(Exercise).all() if e.kind == "run" and e.data["language"] == "python")
        good = {"code": ex.solution["example"], "outputs": ex.solution["expected"]}
        assert grading.grade(ex, good)
        # right code, wrong printed output -> rejected
        assert not grading.grade(ex, {**good, "outputs": ["nope"] * len(ex.solution["expected"])})
        # wrong number of outputs -> rejected
        assert not grading.grade(ex, {**good, "outputs": []})
        lesson_id = ex.lesson_id
    # the expected output is never sent to the browser
    start = client.post(f"/api/lessons/{lesson_id}/start")
    assert start.status_code in (200, 403)
    from app.schemas import public_exercise

    with SessionLocal() as db:
        pub = str(public_exercise(db.get(Exercise, ex.id)))
        assert "expected" not in pub and "example" not in pub and "require" not in pub


def test_require_patterns_block_print_the_answer(client):
    with SessionLocal() as db:
        ex = next(e for e in db.query(Exercise).all() if e.kind == "run" and e.solution.get("require") and e.data["language"] == "python")
        cheat = {"code": "print(" + repr(ex.solution["expected"][0]) + ")", "outputs": ex.solution["expected"]}
        assert not grading.grade(ex, cheat)


def test_compiled_language_without_runner_uses_fallback_patterns(client):
    with SessionLocal() as db:
        ex = next(e for e in db.query(Exercise).all() if e.kind == "run" and e.data["language"] == "java")
        assert grading.grade(ex, {"code": ex.solution["example"]})
        assert not grading.grade(ex, {"code": ex.data["starter"]})


def test_run_endpoint_reports_runner_unavailable(client):
    enroll(client)
    with SessionLocal() as db:
        ex = next(e for e in db.query(Exercise).all() if e.kind == "run" and e.data["language"] == "c")
    r = client.post("/api/run", json={"exercise_id": ex.id, "code": ex.solution["example"]})
    assert r.status_code == 503


def test_curriculum_sync_is_idempotent_and_respects_admin_edits(client):
    from app.models import Lesson
    from app.seed import sync_curriculum

    with SessionLocal() as db:
        before = db.query(Exercise).count()
        lesson = db.query(Lesson).filter(Lesson.key == "python/1/1").one()
        lesson.title = "Custom by admin"
        lesson.content_hash = None
        db.commit()
        sync_curriculum(db)
        assert db.query(Exercise).count() == before
        assert db.query(Lesson).filter(Lesson.key == "python/1/1").one().title == "Custom by admin"


def test_code_grading_is_whitespace_tolerant_and_bounded():
    ex = Exercise(kind="code", prompt="", data={}, solution={"patterns": [r"^\s*print\(\s*(['\"])hi\1\s*\)\s*$"]})
    assert grading.grade(ex, "  print( 'hi' )  \r\n")
    assert not grading.grade(ex, "print('hi')" + " " * 3000)  # over size cap


def test_ai_hint_falls_back_to_author_hint(client):
    enroll(client)
    lesson = _first_lesson(client)[0]
    ex = client.post(f"/api/lessons/{lesson['id']}/start").json()["exercises"][0]
    r = client.post("/api/ai/hint", json={"exercise_id": ex["id"]}).json()
    assert r["source"] == "author" and r["hint"]
