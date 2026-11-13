"""Runs compiled-language exercises (Java, C, C++) in an isolated sandbox.

The API never executes learner code itself. With CODE_RUNNER_URL + CODE_RUNNER_KEY the code goes to Codeingo's own
runner service (the runner/ folder: a separate container with no data or secrets, programs run as an unprivileged
user with CPU/memory/process/output limits). With only CODE_RUNNER_URL it speaks to a self-hosted Piston instance
(https://github.com/engineer-man/piston). Without a runner, the grader falls back to pattern checks.
Python, JavaScript, SQL and HTML run in the learner's own browser instead.
"""
import logging
import threading

import httpx

from ..config import get_settings

log = logging.getLogger("codeingo.runner")

SERVER_LANGS = {"java", "c", "cpp"}
PISTON = {"java": ("java", "Main.java"), "c": ("c", "main.c"), "cpp": ("c++", "main.cpp")}
MAX_OUTPUT = 4000


class RunnerUnavailable(Exception):
    pass


def configured() -> bool:
    return bool(get_settings().code_runner_url)


def warm() -> None:
    """Wakes a sleeping runner (free hosts stop idle services) without making the learner wait: fire and forget."""
    if not configured():
        return

    def ping() -> None:
        try:
            httpx.get(f"{get_settings().code_runner_url.rstrip('/')}/api/health", timeout=90)
        except httpx.HTTPError:
            pass

    threading.Thread(target=ping, daemon=True).start()


def _run_own_runner(language: str, code: str, tests: list[dict]) -> list[dict]:
    """Codeingo's runner: one request compiles once and runs every test input."""
    s = get_settings()
    try:
        resp = httpx.post(
            f"{s.code_runner_url.rstrip('/')}/api/v1/run",
            headers={"X-Runner-Key": s.code_runner_key},
            json={"language": language, "code": code, "stdins": [t.get("stdin", "") for t in tests] or [""]},
            timeout=60,
        )
        resp.raise_for_status()
        body = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("code runner error: %s", exc)
        raise RunnerUnavailable() from exc
    compiled = body.get("compile") or {}
    if not compiled.get("ok"):  # the program does not compile: same message for every test
        err = (compiled.get("stderr") or "Compilation failed")[:MAX_OUTPUT]
        return [{"stdout": "", "stderr": err, "ok": False} for _ in tests]
    return [{"stdout": (r.get("stdout") or "")[:MAX_OUTPUT], "stderr": (r.get("stderr") or "")[:MAX_OUTPUT], "ok": bool(r.get("ok"))}
            for r in (body.get("runs") or [])][: len(tests)]


def run_tests(language: str, code: str, tests: list[dict]) -> list[dict]:
    """Returns [{"stdout", "stderr", "ok"}] per test. Raises RunnerUnavailable on infra errors."""
    s = get_settings()
    if not configured() or language not in PISTON:
        raise RunnerUnavailable()
    if s.code_runner_key:
        return _run_own_runner(language, code, tests)
    lang, filename = PISTON[language]
    results = []
    try:
        with httpx.Client(timeout=30) as client:
            for t in tests:
                resp = client.post(
                    f"{s.code_runner_url.rstrip('/')}/api/v2/execute",
                    json={
                        "language": lang,
                        "version": "*",
                        "files": [{"name": filename, "content": code}],
                        "stdin": t.get("stdin", ""),
                        "compile_timeout": 10000,
                        "run_timeout": 3000,
                        "compile_memory_limit": 256_000_000,
                        "run_memory_limit": 128_000_000,
                    },
                )
                resp.raise_for_status()
                body = resp.json()
                compile_ = body.get("compile") or {}
                if compile_.get("code"):  # compilation failed - same error for every test
                    err = (compile_.get("stderr") or compile_.get("output") or "Compilation failed")[:MAX_OUTPUT]
                    return [{"stdout": "", "stderr": err, "ok": False} for _ in tests]
                run = body.get("run") or {}
                results.append(
                    {
                        "stdout": (run.get("stdout") or "")[:MAX_OUTPUT],
                        "stderr": (run.get("stderr") or "")[:MAX_OUTPUT],
                        "ok": run.get("code") == 0 and not run.get("signal"),
                    }
                )
    except httpx.HTTPError as exc:
        log.warning("code runner error: %s", exc)
        raise RunnerUnavailable() from exc
    return results
