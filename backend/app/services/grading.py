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


# ------------------------------------------------------------------ "almost right" detection
# A wrong answer that is CLOSE gets one free second chance with a plain-language note about what is off.
# The notes describe the kind of difference (capital letters, spaces, a missing line...) without giving the answer away.
def _edit_distance(a: str, b: str, cap: int = 4) -> int:
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _strip_punct(s: str) -> str:
    return regex.sub(r"[^\w]", "", s)


def _compare_text(got: str, want: str) -> str | None:
    """Why two texts differ, if they are close; None when they are not close at all."""
    if got == want:
        return None
    if got.lower() == want.lower():
        return "Capital letters matter here - check which letters should be upper or lower case."
    if "".join(got.split()) == "".join(want.split()):
        return "The words are right, but the spaces or line breaks are not - check the gaps between things."
    if _strip_punct(got).lower() == _strip_punct(want).lower():
        return "The letters are right, but check the punctuation - commas, full stops, brackets, quotes and symbols."
    try:
        g, w = float(got), float(want)
        if ("." in got or "." in want or abs(w) >= 10) and abs(g - w) <= max(1.0, abs(w) * 0.2):
            return "The number is close, but not exact - check your calculation, and rounding or decimals."
    except ValueError:
        pass
    if _edit_distance(got, want) <= max(1, min(3, len(want) // 5)):
        return "Very close - one or two characters are off. Check your spelling and symbols."
    return None


def _run_outputs(ex: Exercise, answer) -> list[str] | None:
    if not isinstance(answer, dict):
        return None
    data = ex.data or {}
    lang = data.get("language")
    if lang in code_runner.SERVER_LANGS:
        code = answer.get("code", "")
        try:
            return [norm_output(r["stdout"]) if r.get("ok") else "" for r in code_runner.run_tests(lang, code, data.get("tests", []))]
        except Exception:
            return None
    outs = answer.get("outputs")
    if isinstance(outs, list) and all(isinstance(o, str) for o in outs):
        return [norm_output(o) for o in outs]
    return None


def _near_run(ex: Exercise, answer) -> str | None:
    sol, data = ex.solution or {}, ex.data or {}
    expected = [norm_output(e) for e in sol.get("expected", [])]
    outs = _run_outputs(ex, answer)
    if not outs or len(outs) != len(expected) or len(expected) > MAX_TESTS:
        return None
    names = [(t.get("name") or f"test {i + 1}") for i, t in enumerate(data.get("tests", []))]
    names += [f"test {i + 1}" for i in range(len(names), len(expected))]
    if outs == expected:  # the output is right, so a required technique must be missing
        return "Your output is right, but this exercise asks you to solve it a particular way (for example with a loop, a function or a certain command). Re-read the task and use that approach."
    failing = [i for i, (o, e) in enumerate(zip(outs, expected)) if o != e]
    passed = len(expected) - len(failing)
    i = failing[0]
    got, want = outs[i], expected[i]
    gl, wl = got.split("\n"), want.split("\n")
    detail = None
    if len(gl) != len(wl):
        if gl and gl != [""]:
            detail = f"Your program printed {len(gl)} line{'s' if len(gl) != 1 else ''}, but the task needs {len(wl)}. Check how many times you print."
    else:
        for k, (a, b) in enumerate(zip(gl, wl)):
            if a != b:
                why = _compare_text(a, b)
                if why:
                    detail = f"Line {k + 1} of your output is {chr(34)}{a[:60]}{chr(34)}. {why}"
                break
    if passed >= 1 and len(expected) > 1:
        fails = ", ".join(f'"{names[i]}"' for i in failing[:3])
        head = f"Your program passed {passed} of {len(expected)} tests. It does not work for: {fails}."
        return head + (f" For {chr(34)}{names[i]}{chr(34)}: {detail}" if detail else " Think about what is different in those cases.")
    return detail


def near_miss(ex: Exercise, answer) -> str | None:
    """A short note about what is off when a WRONG answer is close, else None."""
    sol = ex.solution or {}
    try:
        if ex.kind == "fill" and isinstance(answer, str):
            got = _norm(answer)
            for acc in sol.get("accepted", []):
                why = _compare_text(got, _norm(acc))
                if why:
                    return why
            return None
        if ex.kind == "order":
            n = len(ex.data.get("lines", []))
            target = (sol.get("alternatives") or [list(range(n))])[0]
            if isinstance(answer, list) and len(answer) == n and n >= 3 and sorted(answer) == sorted(target):
                wrong = [i + 1 for i, (a, b) in enumerate(zip(answer, target)) if a != b]
                if 0 < len(wrong) <= 2:
                    where = " and ".join(str(i) for i in wrong)
                    return f"Almost! {n - len(wrong)} of {n} lines are in the right place. Look again at line{'s' if len(wrong) > 1 else ''} {where} (counting from the top) - {'they belong' if len(wrong) > 1 else 'it belongs'} somewhere else."
            return None
        if ex.kind == "run":
            return _near_run(ex, answer)
    except TimeoutError:
        return None
    return None


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
