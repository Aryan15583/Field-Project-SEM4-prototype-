from datetime import timedelta

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Exercise, LessonAttempt, TestAttempt, User, UserLesson

from .conftest import enroll
from .test_learning import _answer_for


def _path(client, slug="python"):
    return client.get(f"/api/courses/{slug}").json()


def _play_lesson(client, lesson_id):
    s = client.post(f"/api/lessons/{lesson_id}/start")
    assert s.status_code == 200, s.text
    s = s.json()
    with SessionLocal() as db:
        for e in s["exercises"]:
            ans = _answer_for(db.get(Exercise, e["id"]))
            assert client.post(f"/api/attempts/{s['attempt_id']}/answer", json={"exercise_id": e["id"], "answer": ans}).json()["correct"]
        a = db.get(LessonAttempt, s["attempt_id"])
        a.started_at -= timedelta(minutes=5)
        db.commit()
    assert client.post(f"/api/attempts/{s['attempt_id']}/complete").status_code == 200


def _wrong(ex: Exercise):
    if ex.kind == "mcq":
        return (ex.solution["index"] + 1) % len(ex.data["options"])
    if ex.kind == "order":
        return list(range(len(ex.data["lines"])))[::-1]
    return "definitely wrong ¯\\_(ツ)_/¯"


def _take_test(client, body, *, correct=True, finish=True):
    r = client.post("/api/tests/start", json=body)
    assert r.status_code == 200, r.text
    t = r.json()
    with SessionLocal() as db:
        for q in t["questions"]:
            ex = db.get(Exercise, q["id"])
            res = client.post(f"/api/tests/{t['attempt_id']}/answer", json={"exercise_id": q["id"], "answer": _answer_for(ex) if correct else _wrong(ex)})
            assert res.status_code == 200 and res.json()["correct"] is correct
        a = db.get(TestAttempt, t["attempt_id"])
        a.started_at -= timedelta(minutes=5)
        db.commit()
    if not finish:
        return t, None
    return t, client.post(f"/api/tests/{t['attempt_id']}/complete").json()


def test_unit_test_gates_the_next_unit(client):
    enroll(client)
    path = _path(client)
    u1, u2 = path["units"][0], path["units"][1]
    assert u1["test"]["status"] == "locked" and u1["test"]["questions"] == 8 and u1["test"]["pass_mark"] == 6
    assert client.post("/api/tests/start", json={"course": "python", "unit_id": u1["id"]}).status_code == 403
    for lesson in u1["lessons"]:
        _play_lesson(client, lesson["id"])

    path = _path(client)
    assert path["units"][0]["test"]["status"] == "unlocked"
    assert path["units"][1]["lessons"][0]["status"] == "locked"  # chapter test not passed yet
    assert client.post(f"/api/lessons/{u2['lessons'][0]['id']}/start").status_code == 403

    _, failed = _take_test(client, {"course": "python", "unit_id": u1["id"]}, correct=False)
    assert failed["passed"] is False and failed["score"] == 0 and failed["xp_awarded"] == 0
    assert _path(client)["units"][1]["lessons"][0]["status"] == "locked"

    xp_before = client.get("/api/auth/me").json()["xp_total"]
    t, passed = _take_test(client, {"course": "python", "unit_id": u1["id"]})
    assert passed["passed"] and passed["score"] == passed["total"] == 8 and passed["xp_awarded"] == 20
    assert "checkpoint" in {b["key"] for b in passed["new_badges"]}
    assert client.get("/api/auth/me").json()["xp_total"] == xp_before + 20
    path = _path(client)
    assert path["units"][0]["test"]["status"] == "passed"
    assert path["units"][1]["lessons"][0]["status"] == "unlocked"

    _, again = _take_test(client, {"course": "python", "unit_id": u1["id"]})
    assert again["passed"] and again["xp_awarded"] == 0  # retakes are practice


def test_test_questions_reveal_nothing_and_are_answered_once(client):
    enroll(client)
    unit = _path(client)["units"][0]
    for lesson in unit["lessons"]:
        _play_lesson(client, lesson["id"])
    t = client.post("/api/tests/start", json={"course": "python", "unit_id": unit["id"]}).json()
    assert len(t["questions"]) == 8 and len({q["id"] for q in t["questions"]}) == 8
    assert all(q["kind"] in ("mcq", "fill", "order", "code") for q in t["questions"])
    blob = str(t)
    assert "solution" not in blob and "accepted" not in blob and "'index'" not in blob
    q = t["questions"][0]
    with SessionLocal() as db:
        ans = _answer_for(db.get(Exercise, q["id"]))
    url = f"/api/tests/{t['attempt_id']}"
    assert client.post(f"{url}/complete").status_code == 400  # not finished
    assert client.post(f"{url}/answer", json={"exercise_id": q["id"], "answer": ans}).status_code == 200
    assert client.post(f"{url}/answer", json={"exercise_id": q["id"], "answer": ans}).status_code == 409
    other = next(i for i in range(1, 10_000) if i not in {x["id"] for x in t["questions"]})
    assert client.post(f"{url}/answer", json={"exercise_id": other, "answer": 0}).status_code == 404
    # no AI hints for a question in an unfinished test
    assert client.post("/api/ai/hint", json={"exercise_id": t["questions"][1]["id"]}).status_code == 403


def test_tests_must_not_be_rushed_and_belong_to_their_user(client):
    enroll(client)
    unit = _path(client)["units"][0]
    for lesson in unit["lessons"]:
        _play_lesson(client, lesson["id"])
    t = client.post("/api/tests/start", json={"course": "python", "unit_id": unit["id"]}).json()
    with SessionLocal() as db:
        for q in t["questions"]:
            client.post(f"/api/tests/{t['attempt_id']}/answer", json={"exercise_id": q["id"], "answer": _answer_for(db.get(Exercise, q["id"]))})
    assert client.post(f"/api/tests/{t['attempt_id']}/complete").status_code == 400  # too fast
    client.post("/api/auth/logout")
    enroll(client, "intruder@example.com", "Intruder")
    assert client.post(f"/api/tests/{t['attempt_id']}/complete").status_code == 404


def test_readiness_test_jumps_to_the_next_section(client):
    enroll(client)
    path = _path(client)
    start = sum(1 for u in path["units"] if u["title"].startswith("Start here"))  # gentle intro units in front
    beginner_lessons = sum(len(u["lessons"]) for u in path["units"] if u["section"] == "Beginner")
    assert path["section_tests"] == {
        "Intermediate": {"status": "available", "questions": 15, "pass_mark": 12, "xp": 50},
        "Advanced": {"status": "available", "questions": 15, "pass_mark": 12, "xp": 50},
        "Expert": {"status": "available", "questions": 15, "pass_mark": 12, "xp": 50},
    }
    first_intermediate = next(u for u in path["units"] if u["section"] == "Intermediate")

    _, failed = _take_test(client, {"course": "python", "section": "Intermediate"}, correct=False)
    assert failed["passed"] is False and failed["lessons_skipped"] == 0
    assert _path(client)["units"][start + 8]["lessons"][0]["status"] == "locked"

    t, res = _take_test(client, {"course": "python", "section": "Intermediate"})
    assert len(t["questions"]) == 15 and res["passed"] and res["xp_awarded"] == 50 and res["lessons_skipped"] == beginner_lessons
    assert {b["key"] for b in res["new_badges"]} >= {"jumper"}
    assert "first_lesson" not in {b["key"] for b in res["new_badges"]}  # testing out isn't "playing" a lesson

    path = _path(client)
    beginner = [l for u in path["units"] if u["section"] == "Beginner" for l in u["lessons"]]
    assert all(l["status"] == "completed" for l in beginner)
    assert all(u["test"]["status"] == "passed" for u in path["units"] if u["section"] == "Beginner")
    assert next(u for u in path["units"] if u["id"] == first_intermediate["id"])["lessons"][0]["status"] == "unlocked"
    assert path["section_tests"]["Intermediate"]["status"] == "passed"
    assert path["section_tests"]["Advanced"]["status"] == "available"
    with SessionLocal() as db:
        uid = db.scalar(select(User.id).where(User.email == "learner@example.com"))
        rows = db.scalars(select(UserLesson).where(UserLesson.user_id == uid)).all()
        assert len(rows) == beginner_lessons and all(r.tested_out and r.completed_count == 0 for r in rows)
    stats = client.get("/api/stats").json()
    assert stats["lessons_completed"] == 0  # stats count lessons actually played


def test_existing_progress_stays_unlocked_without_chapter_tests(client):
    enroll(client)
    path = _path(client)
    u1, u2 = path["units"][0], path["units"][1]
    with SessionLocal() as db:
        uid = db.scalar(select(User.id).where(User.email == "learner@example.com"))
        for lesson in u1["lessons"] + u2["lessons"][:1]:  # progress made before chapter tests existed
            db.add(UserLesson(user_id=uid, lesson_id=lesson["id"], completed_count=1))
        db.commit()
    path = _path(client)
    assert path["units"][1]["lessons"][1]["status"] == "unlocked"
    assert path["units"][0]["test"]["status"] == "unlocked"  # can still take it for practice


def test_unknown_targets(client):
    enroll(client)
    assert client.post("/api/tests/start", json={"course": "python", "section": "Beginner"}).status_code == 404
    assert client.post("/api/tests/start", json={"course": "python", "section": "Wizard"}).status_code == 404
    assert client.post("/api/tests/start", json={"course": "nope", "unit_id": 1}).status_code == 404
    assert client.post("/api/tests/start", json={"course": "python", "unit_id": 999999}).status_code == 404
    assert client.post("/api/tests/start", json={"course": "python"}).status_code == 400
