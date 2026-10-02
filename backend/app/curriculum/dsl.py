"""Helpers for writing lessons compactly."""


def mcq(prompt, options, index, explanation="", hint="", code=None):
    return {"kind": "mcq", "prompt": prompt, "code": code, "data": {"options": options}, "solution": {"index": index},
            "explanation": explanation, "hint": hint}


def fill(prompt, code, accepted, explanation="", hint=""):
    """`code` contains exactly one ___ blank."""
    accepted = [accepted] if isinstance(accepted, str) else accepted
    return {"kind": "fill", "prompt": prompt, "code": code, "data": {}, "solution": {"accepted": accepted},
            "explanation": explanation, "hint": hint}


def order(prompt, lines, explanation="", hint="", alternatives=None):
    """`lines` in the correct order (they're shuffled when served)."""
    sol = {"alternatives": alternatives} if alternatives else {}
    return {"kind": "order", "prompt": prompt, "code": None, "data": {"lines": lines}, "solution": sol,
            "explanation": explanation, "hint": hint}


def code(prompt, patterns, example, starter="", explanation="", hint="", forbid=None):
    """Short snippet checked with regexes (no execution)."""
    return {"kind": "code", "prompt": prompt, "code": None, "data": {"starter": starter},
            "solution": {"patterns": patterns, "example": example, "forbid": forbid or []},
            "explanation": explanation, "hint": hint}


def t(name, **kw):
    """A test case. Keys by language:
    python/javascript: append (code run after the learner's), stdin (python input())
    java/c/cpp:        stdin
    sql:               append (a query run after the learner's statements)
    html:              selector + prop ("text", "count", "attr:<name>" or a CSS property)"""
    return {"name": name, **kw}


def run(prompt, language, tests, expected, example, starter="", require=None, forbid=None, fallback=None,
        setup=None, explanation="", hint="", carry=False):
    """`carry=True` (project steps): the editor starts from the learner's own code from the previous step;
    `starter` is only the fallback (use the previous step's reference solution)."""
    assert len(tests) == len(expected), prompt
    data = {"language": language, "starter": starter, "tests": tests}
    if carry:
        data["carry"] = True
    if setup:
        data["setup"] = setup
    sol = {"expected": expected, "example": example}
    if require:
        sol["require"] = require
    if forbid:
        sol["forbid"] = forbid
    if fallback:
        sol["fallback"] = fallback
    return {"kind": "run", "prompt": prompt, "code": None, "data": data, "solution": sol,
            "explanation": explanation, "hint": hint}


def lesson(title, intro, *exercises, xp=10, key=None):
    return {"title": title, "intro": intro, "exercises": list(exercises), "xp": xp, "key": key}


def project(title, intro, *steps, xp=30):
    """A multi-step build at the end of a section: each step is a `run` exercise that usually
    continues from the learner's code in the previous step (carry=True)."""
    return {"title": title, "intro": intro, "exercises": list(steps), "xp": xp, "key": None, "project": True}


def unit(title, *lessons):
    return {"title": title, "lessons": list(lessons)}


def section(name, *units):
    """Groups units into a path section (Beginner / Intermediate / Advanced), like Duolingo."""
    return [{**u, "section": name} for u in units]


def course(slug, title, icon, description, *units):
    flat = []
    for u in units:
        flat.extend(u if isinstance(u, list) else [u])
    return {"slug": slug, "title": title, "icon": icon, "description": description,
            "units": [{"section": "Beginner", **u} for u in flat]}
