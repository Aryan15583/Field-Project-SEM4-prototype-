from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.curriculum import CURRICULUM
from app.db import SessionLocal
from app.models import Exercise, PracticeAttempt, ReviewItem, User

from .conftest import enroll
from .test_checkpoints import _path, _play_lesson, _wrong
from .test_learning import _answer_for


def _uid(email="learner@example.com"):
    with SessionLocal() as db:
        return db.scalar(select(User.id).where(User.email == email))


def _items(uid):
    with SessionLocal() as db:
        return {r.exercise_id: (r.box, r.lapses) for r in db.scalars(select(ReviewItem).where(ReviewItem.user_id == uid))}


def _first_lesson_with_mistake(client):
    """Play lesson 1, answering one quick question wrong once before getting it right."""
    lesson_id = _path(client)["units"][0]["lessons"][0]["id"]
    s = client.post(f"/api/lessons/{lesson_id}/start").json()
    with SessionLocal() as db:
        quick = [e for e in s["exercises"] if e["kind"] in ("mcq", "fill", "order", "code")]
        missed = quick[0]["id"]
        assert not client.post(f"/api/attempts/{s['attempt_id']}/answer", json={"exercise_id": missed, "answer": _wrong(db.get(Exercise, missed))}).json()["correct"]
        for e in s["exercises"]:
            client.post(f"/api/attempts/{s['attempt_id']}/answer", json={"exercise_id": e["id"], "answer": _answer_for(db.get(Exercise, e["id"]))})
        from app.models import LessonAttempt

        db.get(LessonAttempt, s["attempt_id"]).started_at -= timedelta(minutes=5)
        db.commit()
    assert client.post(f"/api/attempts/{s['attempt_id']}/complete").status_code == 200
    return missed, [e["id"] for e in quick]


def _practise(client, *, correct=True, course=None):
    t = client.post("/api/practice/start", json={"course": course} if course else {})
    assert t.status_code == 200, t.text
    t = t.json()
    with SessionLocal() as db:
        for q in t["questions"]:
            ex = db.get(Exercise, q["id"])
            r = client.post(f"/api/practice/{t['attempt_id']}/answer", json={"exercise_id": q["id"], "answer": _answer_for(ex) if correct else _wrong(ex)})
            assert r.status_code == 200 and r.json()["correct"] is correct
        db.get(PracticeAttempt, t["attempt_id"]).started_at -= timedelta(minutes=5)
        db.commit()
    return t, client.post(f"/api/practice/{t['attempt_id']}/complete").json()


def test_nothing_to_practise_before_any_lesson(client):
    enroll(client)
    assert client.get("/api/practice/summary").json()["total"] == 0
    assert client.post("/api/practice/start", json={}).status_code == 409


def test_lesson_answers_build_the_review_schedule(client):
    enroll(client)
    missed, quick = _first_lesson_with_mistake(client)
    items = _items(_uid())
    assert set(items) == set(quick)  # program-writing exercises aren't reviewed
    assert items[missed] == (0, 1)  # missed once -> box 0, due now
    assert all(items[i] == (1, 0) for i in quick if i != missed)  # right first time -> box 1, tomorrow
    s = client.get("/api/practice/summary").json()
    assert s["due"] == 1 and s["mistakes"] == 1 and s["total"] == len(quick)
    assert client.get("/api/practice/summary?course=python").json()["due"] == 1
    assert client.get("/api/practice/summary?course=sql").json()["total"] == 0


def test_practice_serves_mistakes_first_and_promotes_them(client):
    enroll(client)
    missed, quick = _first_lesson_with_mistake(client)
    t, res = _practise(client)
    ids = [q["id"] for q in t["questions"]]
    assert missed in ids and len(ids) == len(quick)  # only what this learner has met
    assert next(q for q in t["questions"] if q["id"] == missed)["review"] is True
    assert "solution" not in str(t)
    assert res["score"] == res["total"] and res["xp_awarded"] == 10
    assert {b["key"] for b in res["new_badges"]} >= {"practice"}
    items = _items(_uid())
    assert items[missed] == (1, 1)  # 0 -> 1, lapse remembered
    assert all(items[i][0] == 2 for i in quick if i != missed)  # 1 -> 2
    assert res["summary"]["due"] == 0


def test_wrong_in_practice_resets_the_box(client):
    enroll(client)
    _first_lesson_with_mistake(client)
    _practise(client, correct=False)
    items = _items(_uid())
    assert all(box == 0 for box, _ in items.values())
    assert client.get("/api/practice/summary").json()["due"] == len(items)


def test_practice_earns_a_heart_and_xp_is_capped_per_day(client):
    enroll(client)
    _first_lesson_with_mistake(client)  # the mistake cost one heart
    assert client.get("/api/auth/me").json()["hearts"] == 4
    _, res = _practise(client)
    assert res["heart_awarded"] and res["hearts"] == 5
    for _ in range(4):
        _, res = _practise(client)
        assert res["xp_awarded"] == 10 and not res["heart_awarded"]  # already full
    _, res = _practise(client)
    assert res["xp_awarded"] == 0 and res["xp_capped"]


def test_practice_answers_are_single_use_and_private(client):
    enroll(client)
    _first_lesson_with_mistake(client)
    t = client.post("/api/practice/start", json={}).json()
    q = t["questions"][0]
    with SessionLocal() as db:
        ans = _answer_for(db.get(Exercise, q["id"]))
    url = f"/api/practice/{t['attempt_id']}"
    assert client.post(f"{url}/complete").status_code == 400
    assert client.post(f"{url}/answer", json={"exercise_id": q["id"], "answer": ans}).status_code == 200
    assert client.post(f"{url}/answer", json={"exercise_id": q["id"], "answer": ans}).status_code == 409
    client.post("/api/auth/logout")
    enroll(client, "other@example.com", "Other")
    assert client.post(f"{url}/answer", json={"exercise_id": t["questions"][1]["id"], "answer": 0}).status_code == 404


def test_test_mistakes_also_come_back_in_practice(client):
    enroll(client)
    unit = _path(client)["units"][0]
    for lesson in unit["lessons"]:
        _play_lesson(client, lesson["id"])
    from .test_checkpoints import _take_test

    t, res = _take_test(client, {"course": "python", "unit_id": unit["id"]}, correct=False)
    items = _items(_uid())
    assert all(items[q["id"]][0] == 0 for q in t["questions"])
    assert client.get("/api/practice/summary").json()["due"] >= 8


def test_scheduling_intervals():
    from app.services import review

    assert review.INTERVAL_DAYS == [0, 1, 3, 7, 16, 35]
    assert review.MAX_BOX == 5


def test_overview_lists_every_course(client):
    enroll(client)
    _first_lesson_with_mistake(client)
    o = client.get("/api/practice/overview").json()
    assert o["all"]["due"] == 1 and len(o["courses"]) == len(CURRICULUM)
    py = next(c for c in o["courses"] if c["slug"] == "python")
    assert py["due"] == 1 and all(c["total"] == 0 for c in o["courses"] if c["slug"] != "python")
