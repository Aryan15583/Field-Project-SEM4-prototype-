"""Server-side answer checking.

The API process never executes learner code:
- `code` exercises are matched against author-defined patterns;
- `run` exercises in browser languages (Python, JavaScript, SQL, HTML/CSS) are executed in the
  learner's browser, which reports what the program printed - the server compares that with
  expected outputs that never leave the server;
- `run` exercises in compiled languages (Java, C, C++) go to the isolated sandbox runner if one is
  configured, otherwise they fall back to pattern checks.
"""
import random

import regex

from ..models import Exercise
from . import code_runner

MAX_CODE_CHARS = 5000
MAX_TESTS = 8
REGEX_TIMEOUT = 0.2  # seconds - guards against catastrophic backtracking (ReDoS)


def _norm(text: str) -> str:
    return " ".join(text.strip().split())


def _norm_code(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))


def norm_output(text: str) -> str:
    """Ignore trailing spaces on each line and trailing blank lines (like most judges do)."""
    lines = [line.rstrip() for line in str(text).replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _patterns_ok(code: str, must: list[str], forbid: list[str] = ()) -> bool:
    code = _norm_code(code)
    flags = regex.MULTILINE
    return all(regex.search(p, code, flags, timeout=REGEX_TIMEOUT) for p in must) and not any(
        regex.search(p, code, flags, timeout=REGEX_TIMEOUT) for p in forbid
    )


def _grade_run(ex: Exercise, answer) -> bool:
    sol, data = ex.solution or {}, ex.data or {}
    if not isinstance(answer, dict):
        return False
    code = answer.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_CHARS:
        return False
    # structural requirements (e.g. "use a loop") so printing the expected text directly doesn't pass
    if not _patterns_ok(code, sol.get("require", []), sol.get("forbid", [])):
        return False
    expected = [norm_output(e) for e in sol.get("expected", [])]
    lang = data.get("language")
    if lang in code_runner.SERVER_LANGS:
        try:
            results = code_runner.run_tests(lang, code, data.get("tests", []))
            return len(results) == len(expected) and all(r["ok"] and norm_output(r["stdout"]) == e for r, e in zip(results, expected))
        except code_runner.RunnerUnavailable:
            return _patterns_ok(code, sol.get("fallback", []))
    outputs = answer.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != len(expected) or len(outputs) > MAX_TESTS:
        return False
    if not all(isinstance(o, str) and len(o) <= code_runner.MAX_OUTPUT for o in outputs):
        return False
    return all(norm_output(o) == e for o, e in zip(outputs, expected))


def grade(ex: Exercise, answer) -> bool:
    sol = ex.solution or {}
    try:
        if ex.kind == "mcq":
            return isinstance(answer, int) and not isinstance(answer, bool) and answer == sol.get("index")
        if ex.kind == "fill":
            return isinstance(answer, str) and len(answer) <= 200 and _norm(answer) in {_norm(a) for a in sol.get("accepted", [])}
        if ex.kind == "order":
            n = len(ex.data.get("lines", []))
            if not isinstance(answer, list) or len(answer) != n or not all(isinstance(i, int) for i in answer):
                return False
            return answer in sol.get("alternatives", [list(range(n))])
        if ex.kind == "code":
            if not isinstance(answer, str) or len(answer) > 2000:
                return False
            return _patterns_ok(answer, sol.get("patterns", []), sol.get("forbid", []))
        if ex.kind == "run":
            return _grade_run(ex, answer)
    except TimeoutError:
        return False
    return False


def reveal(ex: Exercise) -> str:
    """Human-readable correct answer, shown only AFTER the learner has answered."""
    sol = ex.solution or {}
    if ex.kind == "mcq":
        opts = ex.data.get("options", [])
        i = sol.get("index", 0)
        return opts[i] if 0 <= i < len(opts) else ""
    if ex.kind == "fill":
        return (sol.get("accepted") or [""])[0]
    if ex.kind == "order":
        return "\n".join(ex.data.get("lines", []))
    return sol.get("example", "")


def shuffled_lines(ex: Exercise) -> list[dict]:
    lines = [{"id": i, "text": t} for i, t in enumerate(ex.data.get("lines", []))]
    if len(lines) > 1:
        rng = random.SystemRandom()
        while [l["id"] for l in lines] == list(range(len(lines))):
            rng.shuffle(lines)
    return lines
