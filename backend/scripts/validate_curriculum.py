"""Validates the built-in curriculum by actually running it.

For every exercise:
  * structural checks (options/indices, one ___ blank, regexes compile, tests == expected, ...)
  * the exercise's own reference answer is accepted by the real grader
  * `run` exercises: the reference solution is EXECUTED with the real toolchain and must print
    exactly `expected` for every test -
        python -> python3          javascript / sql / html -> Node + the browser runners' own code
        java   -> javac + java     c -> gcc                cpp -> g++
    and the empty/starter program must NOT pass (so the tests actually test something).

Usage:  python scripts/validate_curriculum.py [language ...]
Needs python3, node (+ frontend deps installed), and optionally javac/gcc/g++ for those courses.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ENV", "test")

from app.curriculum import CURRICULUM  # noqa: E402
from app.models import Exercise  # noqa: E402
from app.services import grading  # noqa: E402

FRONTEND = ROOT.parent / "frontend"
norm = grading.norm_output
errors: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


# ------------------------------------------------------------------ executors
def run_python(code: str, tests: list[dict]) -> list[str]:
    outs = []
    for t in tests:
        p = subprocess.run([sys.executable, "-c", f"{code}\n{t.get('append', '')}"], input=t.get("stdin", ""),
                           capture_output=True, text=True, timeout=15)
        outs.append(p.stdout if p.returncode == 0 else p.stdout + "\n[stderr] " + p.stderr[-300:])
    return outs


COMPILE = {
    "c": ("main.c", ["gcc", "-std=c11", "-O0", "-o", "prog", "main.c", "-lm"], ["./prog"]),
    "cpp": ("main.cpp", ["g++", "-std=c++17", "-O0", "-o", "prog", "main.cpp"], ["./prog"]),
    "java": ("Main.java", ["javac", "Main.java"], ["java", "-cp", ".", "Main"]),
}


def run_compiled(lang: str, code: str, tests: list[dict]) -> list[str] | None:
    fname, build, exe = COMPILE[lang]
    if not shutil.which(build[0]):
        return None
    with tempfile.TemporaryDirectory() as d:
        Path(d, fname).write_text(code)
        b = subprocess.run(build, cwd=d, capture_output=True, text=True, timeout=60)
        if b.returncode:
            return [f"[compile error] {b.stderr[-500:]}"] * len(tests)
        outs = []
        for t in tests:
            p = subprocess.run(exe, cwd=d, input=t.get("stdin", ""), capture_output=True, text=True, timeout=15,
                               env={**os.environ, "JAVA_TOOL_OPTIONS": ""})
            outs.append(p.stdout if p.returncode == 0 else p.stdout + "\n[stderr] " + p.stderr[-300:])
        return outs


def run_node_batch(jobs: list[dict]) -> list:
    if not jobs:
        return []
    p = subprocess.run(["node", str(FRONTEND / "scripts/run-examples.mjs")], input=json.dumps(jobs),
                       capture_output=True, text=True, timeout=600, cwd=FRONTEND)
    if p.returncode:
        raise SystemExit(f"node runner failed:\n{p.stderr}")
    return json.loads(p.stdout)


# ------------------------------------------------------------------ checks
def as_model(e: dict) -> Exercise:
    return Exercise(kind=e["kind"], prompt=e["prompt"], code=e.get("code"), data=e["data"], solution=e["solution"])


def check_static(where: str, e: dict) -> None:
    k, d, s = e["kind"], e["data"], e["solution"]
    if len(e["prompt"]) > 1000:
        err(where, "prompt too long")
    if k == "mcq":
        opts = d["options"]
        if not (2 <= len(opts) <= 6) or not (0 <= s["index"] < len(opts)) or len(set(opts)) != len(opts):
            err(where, "bad mcq options/index")
        answer = s["index"]
    elif k == "fill":
        if (e.get("code") or "").count("___") != 1:
            err(where, "fill code must contain exactly one ___")
        answer = s["accepted"][0]
    elif k == "order":
        if len(d["lines"]) < 2 or len(set(d["lines"])) != len(d["lines"]):
            err(where, "order lines must be >=2 and unique")
        answer = list(range(len(d["lines"])))
    elif k == "code":
        answer = s["example"]
    elif k == "run":
        return  # graded by execution below
    else:
        err(where, f"unknown kind {k}")
        return
    if not grading.grade(as_model(e), answer):
        err(where, "reference answer is rejected by the grader")


def check_run_patterns(where: str, e: dict) -> None:
    s, lang = e["solution"], e["data"]["language"]
    ex = s["example"]
    for key in ("require", "fallback"):
        for p in s.get(key, []):
            if not grading._patterns_ok(ex, [p]):
                err(where, f"{key} pattern {p!r} doesn't match the reference solution")
    for p in s.get("forbid", []):
        if not grading._patterns_ok(ex, [], [p]):
            err(where, f"forbid pattern {p!r} matches the reference solution")
    if lang in ("java", "c", "cpp") and not s.get("fallback"):
        err(where, "compiled-language run exercise needs fallback patterns")
    if lang in ("java", "c", "cpp") and grading._patterns_ok(e["data"].get("starter", ""), s.get("fallback", [])):
        err(where, "starter code already satisfies the fallback patterns")


def compare(where: str, e: dict, outs, what: str) -> None:
    exp = e["solution"]["expected"]
    if outs is None:
        return
    if isinstance(outs, dict):
        err(where, f"{what} failed: {outs.get('error')}")
        return
    for i, (o, x) in enumerate(zip(outs, exp)):
        o = o["stdout"] if isinstance(o, dict) else o
        if what == "reference" and norm(o) != norm(x):
            err(where, f"test {i + 1} ({e['data']['tests'][i].get('name')}): expected {x!r} but the reference printed {o!r}")
    if what == "starter":
        got = [norm(o["stdout"] if isinstance(o, dict) else o) for o in outs]
        if got == [norm(x) for x in exp]:
            err(where, "the starter code already passes every test")


def main(only: set[str]) -> None:
    node_jobs, node_meta = [], []
    counts = {}
    for c in CURRICULUM:
        if only and c["slug"] not in only:
            continue
        n_ex = n_run = 0
        for ui, u in enumerate(c["units"]):
            for li, l in enumerate(u["lessons"]):
                if not l["exercises"]:
                    err(f"{c['slug']}/{ui + 1}/{li + 1}", "lesson has no exercises")
                for ei, e in enumerate(l["exercises"]):
                    where = f"{c['slug']} u{ui + 1} l{li + 1} ({l['title']}) ex{ei + 1}"
                    n_ex += 1
                    check_static(where, e)
                    if e["kind"] != "run":
                        continue
                    n_run += 1
                    check_run_patterns(where, e)
                    d, s = e["data"], e["solution"]
                    lang, tests = d["language"], d["tests"]
                    for label, src in (("reference", s["example"]), ("starter", d.get("starter", ""))):
                        if lang == "python":
                            compare(where, e, run_python(src, tests), label)
                        elif lang in COMPILE:
                            compare(where, e, run_compiled(lang, src, tests), label)
                        else:
                            node_jobs.append({"lang": lang, "code": src, "tests": tests, "setup": d.get("setup")})
                            node_meta.append((where, e, label))
        counts[c["slug"]] = (sum(len(u["lessons"]) for u in c["units"]), n_ex, n_run)
    for (where, e, label), outs in zip(node_meta, run_node_batch(node_jobs)):
        compare(where, e, outs, label)

    for slug, (lessons, ex, runs) in counts.items():
        print(f"{slug:12} lessons={lessons:3}  exercises={ex:4}  runnable={runs:3}")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)
    print("\nOK - every reference answer is accepted and every program prints its expected output.")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
