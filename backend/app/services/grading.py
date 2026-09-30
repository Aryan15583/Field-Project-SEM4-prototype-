"""Server-side answer checking. User code is never executed - it is matched against
author-defined patterns, so a malicious submission cannot run on the server."""
import random

import regex

from ..models import Exercise

MAX_CODE_CHARS = 2000
REGEX_TIMEOUT = 0.2  # seconds - guards against catastrophic backtracking (ReDoS)


def _norm(text: str) -> str:
    return " ".join(text.strip().split())


def _norm_code(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))


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
            if not isinstance(answer, str) or len(answer) > MAX_CODE_CHARS:
                return False
            code = _norm_code(answer)
            flags = regex.MULTILINE
            return all(regex.search(p, code, flags, timeout=REGEX_TIMEOUT) for p in sol.get("patterns", [])) and not any(
                regex.search(p, code, flags, timeout=REGEX_TIMEOUT) for p in sol.get("forbid", [])
            )
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
