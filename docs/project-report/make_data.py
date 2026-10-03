"""Collects accurate facts for the report from the code itself: code excerpts, REST routes, table columns, statistics."""
import os, sys, json, ast, re, pathlib
ROOT = pathlib.Path("/home/user/.vscode")
sys.path.insert(0, str(ROOT / "backend")); os.environ.setdefault("ENV", "test")

def py_func(path, name):
    src = (ROOT / path).read_text(); tree = ast.parse(src); lines = src.splitlines()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return "\n".join(lines[n.lineno - 1 : n.end_lineno])
    raise KeyError(name)
def span(path, a, b): return "\n".join((ROOT / path).read_text().splitlines()[a - 1 : b])
def js_block(path, start_pat, max_lines=45):
    lines = (ROOT / path).read_text().splitlines()
    i = next(k for k, l in enumerate(lines) if re.search(start_pat, l)); depth = 0; out = []
    for l in lines[i:]:
        out.append(l); depth += l.count("{") - l.count("}")
        if depth <= 0 and len(out) > 1: break
        if len(out) >= max_lines: out.append("  // ..."); break
    return "\n".join(out)

snips = [
  ("5.1.1", "Application factory - backend/app/main.py", "py", span("backend/app/main.py", 36, 78)),
  ("5.1.2", "E-mail 2-step code: issue and verify - backend/app/security/mfa.py", "py", py_func("backend/app/security/mfa.py", "issue_email_code") + "\n\n" + py_func("backend/app/security/mfa.py", "verify_email_code")),
  ("5.1.3", "Server-side grading - backend/app/services/grading.py", "py", py_func("backend/app/services/grading.py", "grade")),
  ("5.1.4", "Spaced repetition (Leitner boxes) - backend/app/services/review.py", "py", py_func("backend/app/services/review.py", "record")),
  ("5.1.5", "Passkey sign-in verification - backend/app/security/passkeys.py", "py", py_func("backend/app/security/passkeys.py", "authenticate")),
  ("5.1.6", "Contest scoring and ranking - backend/app/services/contests.py", "py", py_func("backend/app/services/contests.py", "finish") + "\n\n" + py_func("backend/app/services/contests.py", "ranking")),
  ("5.1.7", "TypeScript type-checking in the browser - frontend/public/runners/ts-shared.mjs", "js", js_block("frontend/public/runners/ts-shared.mjs", r"export function compileTs", 55)),
  ("5.1.8", "Per-request Content-Security-Policy - frontend/proxy.js", "js", span("frontend/proxy.js", 8, 40)),
]
json.dump([{"id": a, "title": b, "lang": c, "code": d} for a, b, c, d in snips], open("data_snippets.json", "w"), indent=1)

from app.main import app
routes = []
for path, ops in app.openapi()["paths"].items():
    for m, op in ops.items():
        routes.append({"m": m.upper(), "p": path, "tag": (op.get("tags") or ["misc"])[0]})
routes.sort(key=lambda x: (x["tag"], x["p"], x["m"]))
json.dump(routes, open("data_routes.json", "w"), indent=1)

from app.curriculum import CURRICULUM
stats = {"courses": len(CURRICULUM), "lessons": sum(len(u["lessons"]) for c in CURRICULUM for u in c["units"]),
         "exercises": sum(len(l["exercises"]) for c in CURRICULUM for u in c["units"] for l in u["lessons"]),
         "projects": sum(1 for c in CURRICULUM for u in c["units"] for l in u["lessons"] if l.get("project")),
         "runnable": sum(1 for c in CURRICULUM for u in c["units"] for l in u["lessons"] for e in l["exercises"] if e["kind"] == "run"),
         "by_course": [{"slug": c["slug"], "title": c["title"], "units": len(c["units"]), "lessons": sum(len(u["lessons"]) for u in c["units"])} for c in CURRICULUM]}
code_lines = {}
for label, pat in (("backend_py", "backend/app/**/*.py"), ("tests_py", "backend/tests/*.py"), ("frontend_js", "frontend/{app,components,views,lib}/**/*.js*"), ("runners_js", "frontend/public/runners/*.mjs")):
    files = [p for p in ROOT.glob(pat.replace("{app,components,views,lib}", "*")) ] if "{" not in pat else [p for d in ("app", "components", "views", "lib") for p in (ROOT / "frontend" / d).rglob("*.js*")]
    if label == "backend_py": files = [p for p in files if "curriculum" not in str(p)]
    code_lines[label] = sum(len(p.read_text(errors="ignore").splitlines()) for p in files if p.is_file())
code_lines["curriculum_py"] = sum(len(p.read_text().splitlines()) for p in (ROOT / "backend/app/curriculum").glob("*.py"))
stats["code_lines"] = code_lines
json.dump(stats, open("data_stats.json", "w"), indent=1)
print(json.dumps(stats, indent=1)); print(len(routes), "routes")
