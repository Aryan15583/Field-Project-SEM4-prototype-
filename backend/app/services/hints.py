"""Question-specific hints, built from each exercise's own content (no AI needed).

Three levels, each giving away a little more (a nudge, then narrowing it down, then nearly the answer):
- mcq   1: rules out two wrong options          2: the reasoning (author's explanation) or a third option ruled out
- fill  1: length and first letter              2: the reasoning, or more letters
- order 1: which line comes first               2: the first and last lines
- code  1: author hint / what to include        2: the reasoning
- run   1: the building blocks the solution uses (loop, condition, function, ...)   2: how the solution starts
An author-written hint (the `hint` column) is always used as level 1 when it exists.
"""
import random
import re
import zlib

from ..models import Exercise

MAX_LEVEL = 3

# building blocks a learner may need, found in the reference solution -> plain-language phrase
_CONSTRUCTS = [
    (r"\b(for|foreach)\b|\bfor\s*\(", "a loop that repeats steps (for)"),
    (r"\bwhile\b", "a loop that repeats while something is true (while)"),
    (r"\bif\b|\bswitch\b|\bcase\b|\bWHERE\b", "a decision (if / where)"),
    (r"\bdef\s|\bfunction\b|=>|\bstatic\s+\w+\s+\w+\s*\(|\bint\s+\w+\s*\(.*\)\s*\{", "a function you write yourself"),
    (r"\binput\s*\(|\bScanner\b|\bcin\b|\bscanf\b|\breadline\b|stdin", "reading the input the test gives you"),
    (r"\.split\(|\bsplit\(", "splitting text into pieces (split)"),
    (r"\bsorted\(|\.sort\(|\bORDER BY\b|\bsort\(", "sorting (sort / ORDER BY)"),
    (r"\bJOIN\b", "joining two tables (JOIN)"),
    (r"\bGROUP BY\b", "grouping rows (GROUP BY)"),
    (r"\bCOUNT\(|\bSUM\(|\bAVG\(|\bMAX\(|\bMIN\(", "a summary function (COUNT / SUM / AVG / MAX / MIN)"),
    (r"\{\s*[\w-]+\s*:", "a CSS rule: selector { property: value; }"),
    (r"<\w+[^>]*>", "HTML tags (opening and closing)"),
    (r"\bgit\s+(add|commit|branch|switch|merge|restore|revert)\b", "the right Git commands, in order"),
    (r"\bdict\b|\{\}|new Map|map\[|unordered_map|HashMap|\bMap<", "a dictionary / map to remember things"),
    (r"\[\]|\blist\b|\bvector\b|ArrayList|\bArray\b|new int\[", "a list / array to hold the values"),
    (r"\breturn\b", "a return value (return)"),
    (r"\bclass\b", "a class"),
    (r"\btry\b|\bcatch\b|\bexcept\b", "error handling (try / catch)"),
    (r"%|\bmod\b", "the remainder operator (%)"),
]


def _pick(ex: Exercise, items: list, n: int) -> list:
    """Deterministic 'random' choice per question, so a learner sees the same hint each time."""
    items = list(items)
    seed = zlib.crc32(f"{ex.id}".encode())
    out = []
    for i in range(min(n, len(items))):
        out.append(items.pop((seed >> (i * 3)) % len(items)))
    return out


_BOILERPLATE = re.compile(
    r"^\s*(#include|#define|import\b|from\b.*\bimport\b|using\b|package\b|public\s+class|class\s+Main|int\s+main|public\s+static\s+void\s+main|"
    r"<!DOCTYPE|<html|<head|<body|</|<title|[{}]\s*$|return\s+0;?\s*$)", re.IGNORECASE)


def _constructs(source: str, language: str) -> list[str]:
    html = language == "html"
    found = []
    for pattern, phrase in _CONSTRUCTS:
        if phrase.startswith("HTML tags") and not html:
            continue
        if phrase.startswith("a CSS rule") and language not in ("html", "css"):
            continue
        if phrase.startswith("the right Git") and language != "git":
            continue
        if phrase == "a class" and language in ("html", "css", "sql", "git"):
            continue
        if phrase.startswith("a function") and language in ("c", "cpp", "java"):
            # only a function OTHER than main counts
            defs = re.findall(r"^\s*(?:static\s+|public\s+)?[\w<>:*&]+\s+(\w+)\s*\([^;{]*\)\s*\{", source, re.MULTILINE)
            if not [d for d in defs if d != "main"]:
                continue
        elif not re.search(pattern, source, re.IGNORECASE):
            continue
        elif phrase.startswith("the remainder") and language in ("html", "git"):
            continue
        found.append(phrase)
    return found


def _first_sentence(text: str) -> str:
    text = " ".join((text or "").split())
    m = re.match(r"(.{20,}?[.!?])(\s|$)", text)
    return m.group(1) if m else text


def local_hint(ex: Exercise, level: int = 1) -> tuple[str, bool]:
    """Returns (hint, more) - `more` says a stronger hint is available. Each level gives away a bit more:
    1 = a nudge, 2 = narrows it down, 3 = nearly the answer."""
    level = max(1, min(level, MAX_LEVEL))
    sol, data = ex.solution or {}, ex.data or {}
    author = (ex.hint or "").strip()
    expl = (ex.explanation or "").strip()
    more = level < MAX_LEVEL

    if ex.kind == "mcq":
        options = data.get("options", [])
        right = sol.get("index", 0)
        wrong = [o for i, o in enumerate(options) if i != right]
        q = lambda o: f"\u201c{o}\u201d"  # typographic quotes: options may themselves contain quote marks
        if len(options) <= 2:  # true/false style - nothing to rule out
            if level == 1:
                return author or "Work it out yourself first: go through the code or the statement one step at a time, then choose.", more
            if level == 2:
                return "Trace it again, slowly - write down what each part does, one line at a time, and see where it leads.", more
            return (f"Here is the reasoning: {expl}" if expl else f"The answer is {q(options[right])}."), False
        if level == 1:
            if author:
                return author, more
            gone = _pick(ex, wrong, 1)
            return f"One option you can cross out: {q(gone[0])} is not the answer. Read the rest again carefully and trace the code or idea step by step.", more
        if level == 2:
            keep = _pick(ex, wrong, 1)
            pair = [options[right], keep[0]]
            random.Random(zlib.crc32(f"p{ex.id}".encode())).shuffle(pair)
            return f"It is one of these two: {q(pair[0])} or {q(pair[1])}. Think about what separates them.", more
        return (f"Here is the reasoning: {expl}" if expl else f"The answer is {q(options[right])}."), False

    if ex.kind == "fill":
        answer = (sol.get("accepted") or [""])[0]
        short = len(answer) <= 2  # too short to show a letter without giving it away
        if level == 1:
            if author:
                return author, more
            if short:
                return f"The missing part is only {len(answer)} character{'s' if len(answer) != 1 else ''} long - look at the examples in the lesson text for the same kind of symbol or word.", more
            return f'The missing part is {len(answer)} characters long and starts with "{answer[:1]}".', more
        if level == 2:
            if short:
                return "It is the same symbol or word that the lesson example uses in this position - find that example and compare.", more
            return f"It looks like this: {answer[:2] + '_' * (len(answer) - 2)}", more
        if expl:
            return f"Here is the reasoning: {expl}", False
        return f"It is almost fully shown here: {answer[: max(1, len(answer) - 1)]}_", False

    if ex.kind == "order":
        lines = [l.strip() for l in data.get("lines", [])]
        if not lines:
            return author or "Work out what has to happen first, then what follows.", more
        if level == 1:
            return author or f'The first line is: "{lines[0]}". Now think about what has to come after it.', more
        if level == 2:
            return f'The first line is "{lines[0]}" and the last line is "{lines[-1]}". The others go in between - think about what each one needs from the one before it.', more
        if len(lines) <= 3:
            return "The order is: " + "  then  ".join(f'"{l}"' for l in lines[:-1]) + f"  and finally \"{lines[-1]}\".", False
        head = lines[:2]
        return f'It starts with "{head[0]}", then "{head[1]}", and it ends with "{lines[-1]}". Only the lines in the middle are left to place.', False

    if ex.kind == "code":
        example = (sol.get("example") or "").strip()
        if level == 1:
            return author or "Write it the way the example in the lesson does, then check brackets, quotes and spelling.", more
        if level == 2:
            return (f"Think about this: {expl}" if expl else "Compare each part of your code with the lesson example, character by character."), more
        return (f"One way to write it:\n{example}" if example else "Go back to the lesson example and copy its shape, changing only the parts the question asks about."), False

    # run
    example = (sol.get("example") or "").strip()
    language = data.get("language", "")
    lines = [l for l in example.splitlines() if l.strip() and not _BOILERPLATE.match(l)]
    tests = [t.get("name") for t in data.get("tests", []) if t.get("name")]
    if level == 1:
        if author:
            return author, bool(example)
        parts = _constructs(example, language)
        if parts:
            lead = "You will probably need: " + "; ".join(parts[:3]) + "."
        else:
            lead = "This one is short - read the task slowly and match it exactly."
        size = f" The finished program is about {len(lines)} line{'s' if len(lines) != 1 else ''} long." if len(lines) > 1 else " One line is enough."
        tested = f" It is tested with: {', '.join(tests[:4])}." if len(tests) > 1 else ""
        return lead + size + tested + " Use Run to check your output against the task.", bool(example)
    if not lines:
        return "Run your program and compare what it prints with what the task asks for, line by line.", False
    if level == 2:
        first = lines[0].strip()
        if len(lines) <= 2 and len(first) > 24:  # a short answer: show only its beginning, not all of it
            cut = first[: max(12, len(first) // 3)]
            first = cut.rsplit(" ", 1)[0] if " " in cut[8:] else cut
            first += " ..."
        return f"Here is how a solution can start: {first}   - now continue from there.", bool(example)
    # level 3: about half of the solution
    take = max(1, (len(lines) + 1) // 2)
    shown = lines[:take]
    if len(lines) <= 2:
        text = shown[0].strip()
        cut = text[: max(16, (len(text) * 2) // 3)]
        text = (cut.rsplit(" ", 1)[0] if " " in cut[10:] else cut) + " ..."
        shown = [text]
    return "Here is the first part of a solution:\n" + "\n".join(shown) + "\n...and the rest follows the same idea.", False
