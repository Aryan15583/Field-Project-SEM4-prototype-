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
from .htmlcss import COURSE as HTMLCSS
from .java import COURSE as JAVA
from .javascript import COURSE as JAVASCRIPT
from .python import COURSE as PYTHON
from .sql import COURSE as SQL



def _with_projects(course: dict, module: str) -> dict:
    """Append each section's project as the last lesson of units 8, 12 and 16 (keeps existing keys stable)."""
    try:
        projects = importlib.import_module(f".{module}", __name__).PROJECTS
    except ModuleNotFoundError:
        return course
    for unit_number, lesson in projects.items():
        course["units"][unit_number - 1]["lessons"].append(lesson)
    return course


CURRICULUM = [
    _with_projects(PYTHON, "projects_python"),
    _with_projects(JAVASCRIPT, "projects_javascript"),
    _with_projects(JAVA, "projects_java"),
    _with_projects(CPP, "projects_cpp"),
    _with_projects(C, "projects_c"),
    _with_projects(SQL, "projects_sql"),
    _with_projects(HTMLCSS, "projects_htmlcss"),
]
