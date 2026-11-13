"""Codeingo code runner: compiles and runs learner programs in C, C++ and Java.

A tiny service of its own, on purpose. It has no database, no user data and no secrets except RUNNER_KEY, so a
hostile program that escapes its limits finds nothing worth taking. The Codeingo API is the only caller: it checks
the learner is signed in and rate-limited, then posts the code here with the shared key.

What each run gets (see _run):
  - a fresh private temp directory, deleted afterwards
  - the unprivileged user "nobody" (when started as root - the Dockerfile does) so it cannot read this service's
    environment (RUNNER_KEY) or anything owned by root
  - no network, if the host lets us create a network namespace (reported by /api/health -> "network_isolated")
  - CPU, memory, process-count, open-file and output-size limits, a wall-clock timeout, and the whole process
    group is killed afterwards
  - an empty environment
"""
import asyncio
import hmac
import os
import resource
import shutil
import signal
import subprocess
import tempfile
import time

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

RUNNER_KEY = os.environ.get("RUNNER_KEY", "")
NOBODY = 65534
MAX_CODE = 20_000
MAX_STDIN = 10_000
MAX_RUNS = 8
MAX_OUTPUT = 4_000  # characters returned per stream
MAX_FILE_BYTES = 1_000_000  # a program (or compiler) can write at most this much, e.g. when it prints forever
CONCURRENCY = int(os.environ.get("RUNNER_CONCURRENCY", "2"))
MAX_WAITING = 6

# Same flags the curriculum validator (backend/scripts/validate_curriculum.py) uses, so what passes there passes here.
LANGS = {
    "c": {"file": "main.c", "compile": ["gcc", "-std=c11", "-O1", "-o", "prog", "main.c", "-lm"], "run": ["./prog"], "jvm": False},
    "cpp": {"file": "main.cpp", "compile": ["g++", "-std=c++17", "-O1", "-o", "prog", "main.cpp"], "run": ["./prog"], "jvm": False},
    "java": {
        "file": "Main.java",
        "compile": ["javac", "-J-Xmx256m", "-J-XX:+UseSerialGC", "Main.java"],
        "run": ["java", "-Xmx96m", "-Xss1m", "-XX:+UseSerialGC", "-XX:TieredStopAtLevel=1", "-cp", ".", "Main"],
        "jvm": True,
    },
}

app = FastAPI(title="Codeingo runner", docs_url=None, redoc_url=None, openapi_url=None)
_slots = asyncio.Semaphore(CONCURRENCY)
_waiting = 0


def _probe_network_isolation() -> bool:
    """True when `unshare --net` + `setpriv` work here (needs root and CAP_SYS_ADMIN)."""
    if os.geteuid() != 0 or not (shutil.which("unshare") and shutil.which("setpriv")):
        return False
    try:
        return subprocess.run(["unshare", "--net", "true"], capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


AS_ROOT = os.geteuid() == 0
NETWORK_ISOLATED = os.environ.get("RUNNER_ISOLATE_NETWORK", "1") != "0" and _probe_network_isolation()


class RunIn(BaseModel):
    language: str
    code: str = Field(max_length=MAX_CODE)
    stdins: list[str] = Field(default_factory=lambda: [""], min_length=1, max_length=MAX_RUNS)
    compile_timeout_ms: int = Field(20_000, ge=1_000, le=60_000)
    run_timeout_ms: int = Field(8_000, ge=500, le=20_000)


def _limits(jvm: bool, cpu_seconds: int):
    def apply():
        # setrlimit values are inherited across exec, so they bind the compiler / program, not this service
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE_BYTES, MAX_FILE_BYTES))
        resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
        resource.setrlimit(resource.RLIMIT_NPROC, (256 if jvm else 64, 256 if jvm else 64))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if not jvm:  # the JVM reserves a huge virtual range up front, so it is limited with -Xmx instead
            resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024, 768 * 1024 * 1024))

    return apply


def _wrap(cmd: list[str]) -> tuple[list[str], dict]:
    """Command + Popen kwargs that drop to `nobody` (and leave the network behind when possible)."""
    if NETWORK_ISOLATED:
        return ["unshare", "--net", "setpriv", "--reuid", str(NOBODY), "--regid", str(NOBODY), "--clear-groups", "--", *cmd], {}
    if AS_ROOT:
        return cmd, {"user": NOBODY, "group": NOBODY, "extra_groups": []}
    return cmd, {}  # started as a normal user (local development / tests): nothing to drop


def _execute(cmd: list[str], cwd: str, iodir: str, stdin: str, timeout_s: float, jvm: bool, name: str) -> dict:
    """Runs one command; returns {stdout, stderr, code, signal, timed_out}. Output goes to files, never to memory.
    The files live in `iodir` (owned by us, unreachable for the program): were they in the program's own directory it
    could swap one for a symlink to a root-only file and we would read that back as "its output"."""
    out_path, err_path = os.path.join(iodir, f"{name}.out"), os.path.join(iodir, f"{name}.err")
    argv, extra = _wrap(cmd)
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": cwd, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
    timed_out = False
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        proc = subprocess.Popen(
            argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True,
            preexec_fn=_limits(jvm, max(2, int(timeout_s) + 2)), **extra,
        )
        try:
            proc.communicate(stdin.encode("utf-8", "replace")[:MAX_STDIN], timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)  # the program and anything it started
            except (ProcessLookupError, PermissionError):
                pass
            proc.wait()
            if proc.stdin:
                proc.stdin.close()

    def read(path: str) -> str:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as f:
            return f.read(MAX_OUTPUT * 4).decode("utf-8", "replace")[:MAX_OUTPUT]

    code = proc.returncode
    sig = signal.Signals(-code).name if code is not None and code < 0 else None
    stderr = read(err_path)
    if timed_out:
        sig, stderr = "SIGKILL", (stderr + "\nTime limit exceeded").strip()
    elif sig == "SIGXCPU":
        stderr = (stderr + "\nTime limit exceeded").strip()
    elif sig == "SIGXFSZ":
        stderr = (stderr + "\nToo much output").strip()
    return {"stdout": read(out_path), "stderr": stderr, "code": code, "signal": sig, "timed_out": timed_out}


def _run(req: RunIn) -> dict:
    spec = LANGS[req.language]
    started = time.monotonic()
    work = tempfile.mkdtemp(prefix="run-")  # the program's directory
    iodir = tempfile.mkdtemp(prefix="io-")  # ours: output files; mkdtemp makes it 0700 and owned by us
    try:
        if AS_ROOT:
            os.chown(work, NOBODY, NOBODY)
        os.chmod(work, 0o700)
        path = os.path.join(work, spec["file"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(req.code)
        if AS_ROOT:
            os.chown(path, NOBODY, NOBODY)
        built = _execute(spec["compile"], work, iodir, "", req.compile_timeout_ms / 1000, spec["jvm"], "compile")
        if built["code"] != 0:
            msg = built["stderr"] or built["stdout"] or "Compilation failed"
            return {"compile": {"ok": False, "stderr": msg[:MAX_OUTPUT]}, "runs": [], "ms": int((time.monotonic() - started) * 1000)}
        runs = []
        for stdin in req.stdins:
            r = _execute(spec["run"], work, iodir, stdin, req.run_timeout_ms / 1000, spec["jvm"], "run")
            runs.append({"stdout": r["stdout"], "stderr": r["stderr"], "ok": r["code"] == 0 and not r["signal"], "signal": r["signal"]})
        return {"compile": {"ok": True, "stderr": ""}, "runs": runs, "ms": int((time.monotonic() - started) * 1000)}
    finally:
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(iodir, ignore_errors=True)


def _check_key(key: str) -> None:
    if not RUNNER_KEY:
        raise HTTPException(503, "RUNNER_KEY is not configured on the runner")
    if not hmac.compare_digest(key.encode(), RUNNER_KEY.encode()):
        raise HTTPException(401, "Bad runner key")


@app.get("/api/health")
def health():
    return {"status": "ok", "languages": sorted(LANGS), "network_isolated": NETWORK_ISOLATED, "unprivileged_user": AS_ROOT,
            "configured": bool(RUNNER_KEY)}


@app.post("/api/v1/run")
async def run(body: RunIn, x_runner_key: str = Header("")):
    global _waiting
    _check_key(x_runner_key)
    if body.language not in LANGS:
        raise HTTPException(400, "Unsupported language")
    if any(len(s) > MAX_STDIN for s in body.stdins):
        raise HTTPException(413, "stdin too large")
    if _waiting >= MAX_WAITING:
        raise HTTPException(429, "The runner is busy, try again in a moment")
    _waiting += 1
    try:
        async with _slots:
            return await asyncio.to_thread(_run, body)
    finally:
        _waiting -= 1
