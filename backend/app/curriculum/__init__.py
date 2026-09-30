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
from .c import COURSE as C
from .cpp import COURSE as CPP
from .htmlcss import COURSE as HTMLCSS
from .java import COURSE as JAVA
from .javascript import COURSE as JAVASCRIPT
from .python import COURSE as PYTHON
from .sql import COURSE as SQL

CURRICULUM = [PYTHON, JAVASCRIPT, JAVA, CPP, C, SQL, HTMLCSS]
