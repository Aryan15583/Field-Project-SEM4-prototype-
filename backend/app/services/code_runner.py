"""Runs compiled-language exercises (Java, C, C++) in an isolated sandbox.

The API never executes learner code itself. When CODE_RUNNER_URL points at a self-hosted Piston
instance (https://github.com/engineer-man/piston - it isolates each run with cgroups/namespaces,
no network, CPU/memory/time limits), code is compiled and run there. Without it, the grader falls
back to pattern checks. Python, JavaScript, SQL and HTML run in the learner's own browser instead.
"""
import logging

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


def run_tests(language: str, code: str, tests: list[dict]) -> list[dict]:
    """Returns [{"stdout", "stderr", "ok"}] per test. Raises RunnerUnavailable on infra errors."""
    s = get_settings()
    if not configured() or language not in PISTON:
        raise RunnerUnavailable()
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
