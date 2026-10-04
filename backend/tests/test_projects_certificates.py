from datetime import datetime, timezone

from sqlalchemy import select

from app.curriculum import CURRICULUM
from app.db import SessionLocal
from app.models import Certificate, Course, Lesson, User, UserLesson, UserTest
from app.services import progress

from .conftest import enroll
from .test_checkpoints import _path, _take_test


def test_every_course_has_a_project_per_section(client):
    with SessionLocal() as db:
        projects = db.scalars(select(Lesson).where(Lesson.is_project.is_(True))).all()
        assert len(projects) == 3 * len(CURRICULUM)
        for p in projects:
            # the last unit of each section: 8/12/16 in the 16-unit courses, 4/6/8 in the 8-unit ones
            last = {u.section: u.position for u in sorted(p.unit.course.units, key=lambda u: u.position)}
            assert p.unit.position in last.values() and p.xp_reward == 30
            steps = sorted(p.exercises, key=lambda e: e.position)
            assert len(steps) == 3 and all(e.kind == "run" for e in steps)
            # later steps continue from the learner's own code (the SQL report queries are independent)
            if not (p.unit.course.slug == "sql" and p.unit.position in (7, 11)):
                assert all(e.data.get("carry") for e in steps[1:]), p.title


def test_project_flag_reaches_the_path(client):
    enroll(client)
    project = _path(client)["units"][7]["lessons"][3]
    assert project["project"] and project["title"].startswith("Project:") and project["xp"] == 30


def _complete_course_except_last_test(slug="python", email="learner@example.com") -> int:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        uid = db.scalar(select(User.id).where(User.email == email))
        course = db.scalar(select(Course).where(Course.slug == slug))
        for unit in course.units:
            for lesson in unit.lessons:
                db.add(UserLesson(user_id=uid, lesson_id=lesson.id, completed_count=1))
            if unit.id != course.units[-1].id:
                db.add(UserTest(user_id=uid, target=progress.unit_target(unit.id), best_score=8, attempts=1, passed_at=now))
        db.commit()
        return course.units[-1].id


def test_certificate_is_issued_when_the_course_is_complete(client):
    enroll(client)
    last_unit = _complete_course_except_last_test()
    assert client.get("/api/certificates").json() == []  # last chapter test still missing

    _, failed = _take_test(client, {"course": "python", "unit_id": last_unit}, correct=False)
    assert failed["certificate"] is None

    _, passed = _take_test(client, {"course": "python", "unit_id": last_unit})
    cert = passed["certificate"]
    assert cert and cert["course"] == "Python" and cert["name"] == "Learner" and cert["lessons"] == sum(
        len(u["lessons"]) for u in client.get("/api/courses/python").json()["units"]
    )
    assert len(cert["code"]) >= 16
    assert client.get("/api/certificates").json() == [cert]

    _, again = _take_test(client, {"course": "python", "unit_id": last_unit})
    assert again["certificate"] is None  # issued once
    with SessionLocal() as db:
        assert db.scalar(select(Certificate).where(Certificate.id == cert["code"])) is not None

    # anyone with the link can verify it - no sign-in needed
    client.post("/api/auth/logout")
    client.cookies.clear()
    assert client.get(f"/api/public/certificates/{cert['code']}").json() == cert
    assert client.get("/api/public/certificates/not-a-real-code-123").status_code == 404
    assert client.get("/api/certificates").status_code == 401


def test_no_certificate_while_lessons_are_missing(client):
    enroll(client)
    last_unit = _complete_course_except_last_test()
    with SessionLocal() as db:
        uid = db.scalar(select(User.id).where(User.email == "learner@example.com"))
        project = db.scalar(select(Lesson).where(Lesson.is_project.is_(True), Lesson.key.like("python/%")))
        db.delete(db.scalar(select(UserLesson).where(UserLesson.user_id == uid, UserLesson.lesson_id == project.id)))
        db.commit()
    _, res = _take_test(client, {"course": "python", "unit_id": last_unit})
    assert res["passed"] and res["certificate"] is None
