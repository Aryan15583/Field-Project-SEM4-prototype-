"""Built-in curriculum: one module per language, written with the small helpers below.

Exercise kinds
- mcq / fill / order / code  - quick checks graded on the server
- run                        - the learner writes a real program that is executed:
    * python, javascript, sql, html  -> in the learner's browser (sandboxed worker / iframe)
    * java, c, cpp                   -> in the sandboxed server runner if configured,
                                        otherwise graded with `fallback` patterns
  The browser reports each test's output; the server compares it with `expected`, which is never
  sent to the browser. `require` patterns (optional) stop "just print the answer" shortcuts.

Every `run` exercise's reference solution is executed by `scripts/validate_curriculum.py`, which
checks that it really produces `expected`.
"""
import importlib

from .c import COURSE as C
from .cpp import COURSE as CPP
from .dsa import COURSE as DSA
from .git import COURSE as GIT
from .htmlcss import COURSE as HTMLCSS
from .java import COURSE as JAVA
from .javascript import COURSE as JAVASCRIPT
from .python import COURSE as PYTHON
from .sql import COURSE as SQL
from .typescript import COURSE as TYPESCRIPT



def _soften(course: dict, module: str) -> dict:
    """Replace Beginner lesson texts with plainer, more explained versions (questions untouched). Keys are
    "<unit>/<lesson>" counting only numbered units, so they ignore the Start-here units."""
    try:
        intros = importlib.import_module(f".{module}", __name__).INTROS
    except ModuleNotFoundError:
        return course
    n = 0
    for unit in course["units"]:
        if unit.get("key"):
            continue
        n += 1
        for li, lesson in enumerate(unit["lessons"]):
            text = intros.get(f"{n}/{li + 1}")
            if text and not lesson.get("project"):
                lesson["intro"] = text.strip()
    return course


def _with_projects(course: dict, module: str) -> dict:
    """Append each section's project as the last lesson of the section's final unit (units 8, 12 and 16 in the
    16-unit courses; 4, 6 and 8 in the 8-unit ones) - keeps existing lesson keys stable."""
    try:
        projects = importlib.import_module(f".{module}", __name__).PROJECTS
    except ModuleNotFoundError:
        return course
    offset = sum(1 for u in course["units"] if u.get("key"))  # leading Start-here units don't count as numbered units
    for unit_number, lesson in projects.items():
        course["units"][offset + unit_number - 1]["lessons"].append(lesson)
    return course


CURRICULUM = [
    _with_projects(PYTHON, "projects_python"),
    _with_projects(JAVASCRIPT, "projects_javascript"),
    _with_projects(TYPESCRIPT, "projects_typescript"),
    _with_projects(JAVA, "projects_java"),
    _with_projects(CPP, "projects_cpp"),
    _with_projects(C, "projects_c"),
    _with_projects(SQL, "projects_sql"),
    _with_projects(HTMLCSS, "projects_htmlcss"),
    _with_projects(GIT, "projects_git"),
    _with_projects(DSA, "projects_dsa"),
]

# plainer Beginner explanations (python_soft.py, dsa_soft.py, ...) - texts only, questions unchanged
CURRICULUM = [_soften(c, c["slug"].replace("-", "") + "_soft") for c in CURRICULUM]
