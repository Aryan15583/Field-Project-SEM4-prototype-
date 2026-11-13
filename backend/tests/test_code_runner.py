"""The API's side of the code runner (Java / C / C++): the request it sends and how it reads the answer.
The runner service itself is tested in runner/tests."""
import pytest

from app.config import get_settings
from app.services import code_runner, grading


class _Resp:
    def __init__(self, body):
        self._body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self._body


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.setenv("CODE_RUNNER_URL", "http://runner.test/")
    monkeypatch.setenv("CODE_RUNNER_KEY", "shared-key")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_sends_key_and_all_inputs_in_one_request(runner, monkeypatch):
    seen = {}

    def fake_post(url, headers, json, timeout):
        seen.update(url=url, headers=headers, json=json)
        return _Resp({"compile": {"ok": True}, "runs": [{"stdout": "a\n", "stderr": "", "ok": True}, {"stdout": "b\n", "stderr": "", "ok": True}]})

    monkeypatch.setattr(code_runner.httpx, "post", fake_post)
    out = code_runner.run_tests("c", "int main(){}", [{"stdin": "1"}, {"stdin": "2"}])
    assert seen["url"] == "http://runner.test/api/v1/run" and seen["headers"] == {"X-Runner-Key": "shared-key"}
    assert seen["json"] == {"language": "c", "code": "int main(){}", "stdins": ["1", "2"]}  # compiled once, run twice
    assert [r["stdout"] for r in out] == ["a\n", "b\n"] and all(r["ok"] for r in out)


def test_compile_error_fails_every_test_with_the_message(runner, monkeypatch):
    monkeypatch.setattr(code_runner.httpx, "post", lambda *a, **k: _Resp({"compile": {"ok": False, "stderr": "main.c:1: error: nope"}, "runs": []}))
    out = code_runner.run_tests("c", "x", [{}, {}, {}])
    assert len(out) == 3 and all(not r["ok"] and "error: nope" in r["stderr"] for r in out)


def test_unreachable_runner_raises_so_grading_can_fall_back(runner, monkeypatch):
    def boom(*a, **k):
        raise code_runner.httpx.ConnectError("asleep")

    monkeypatch.setattr(code_runner.httpx, "post", boom)
    with pytest.raises(code_runner.RunnerUnavailable):
        code_runner.run_tests("java", "x", [{}])


def test_grading_uses_the_runner_and_falls_back_when_it_is_down(runner, monkeypatch):
    from types import SimpleNamespace

    ex = SimpleNamespace(kind="run", id=1, data={"language": "c", "tests": [{"stdin": ""}]},
                         solution={"expected": ["hi"], "require": [], "fallback": [r"printf"]})
    good = _Resp({"compile": {"ok": True}, "runs": [{"stdout": "hi\n", "stderr": "", "ok": True}]})
    monkeypatch.setattr(code_runner.httpx, "post", lambda *a, **k: good)
    assert grading.grade(ex, {"code": 'printf("hi");'})
    wrong = _Resp({"compile": {"ok": True}, "runs": [{"stdout": "bye\n", "stderr": "", "ok": True}]})
    monkeypatch.setattr(code_runner.httpx, "post", lambda *a, **k: wrong)
    assert not grading.grade(ex, {"code": 'printf("bye");'})  # real output decides, not the pattern

    def down(*a, **k):
        raise code_runner.httpx.ConnectError("asleep")

    monkeypatch.setattr(code_runner.httpx, "post", down)
    assert grading.grade(ex, {"code": 'printf("hi");'})  # runner asleep: the pattern check still lets the learner continue


def test_run_button_is_offered_only_when_a_runner_is_configured(monkeypatch):
    from app.schemas import public_exercise
    from types import SimpleNamespace

    ex = SimpleNamespace(kind="run", id=1, prompt="p", code=None, hint="", data={"language": "java", "tests": []})
    get_settings.cache_clear()
    monkeypatch.delenv("CODE_RUNNER_URL", raising=False)
    get_settings.cache_clear()
    assert public_exercise(ex)["data"]["server_runner"] is False
    monkeypatch.setenv("CODE_RUNNER_URL", "http://runner.test")
    get_settings.cache_clear()
    assert public_exercise(ex)["data"]["server_runner"] is True
    get_settings.cache_clear()


def test_warm_does_nothing_without_a_runner(monkeypatch):
    monkeypatch.delenv("CODE_RUNNER_URL", raising=False)
    get_settings.cache_clear()
    code_runner.warm()  # must not raise or start anything
