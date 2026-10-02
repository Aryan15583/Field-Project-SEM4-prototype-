"""Python projects - one at the end of each section (added to units 8, 12 and 16)."""
from .dsl import project, run, t

# ------------------------------------------------------------------ Beginner: grade book
GB1 = '''n = int(input())
scores = {}
for _ in range(n):
    name, score = input().split()
    scores[name] = int(score)
print(f"Loaded {len(scores)} students")'''

GB2 = GB1 + '''
average = sum(scores.values()) / len(scores)
print(f"Average: {average:.1f}")
top = max(scores, key=scores.get)
print(f"Top: {top} ({scores[top]})")'''

GB3 = '''def grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


''' + GB2 + '''
for name in sorted(scores):
    print(f"{name}: {grade(scores[name])}")'''

CLASS_IN = "3\nAda 95\nBo 72\nCy 80"
SMALL_IN = "2\nZed 59\nAmy 60"

BEGINNER = project(
    "Project: Grade book",
    "Time to build something real! Over three steps you'll write a grade book that reads a class's scores, works out "
    "statistics and assigns letter grades.\n\nEach step starts from YOUR code from the step before - you're growing one "
    "program, just like real developers do.\n\nInput looks like:\n3\nAda 95\nBo 72\nCy 80\n(the number of students, then "
    "one 'name score' per line).",
    run("Step 1 - Read the class: read the number of students, then each 'name score' line into a dictionary. Print "
        "'Loaded N students'.", "python",
        [t("class", stdin=CLASS_IN), t("small", stdin=SMALL_IN)], ["Loaded 3 students", "Loaded 2 students"],
        GB1, require=[r"\{|dict\("]),
    run("Step 2 - Statistics: after loading, also print the average (1 decimal) as 'Average: X' and the best student "
        "as 'Top: name (score)'.", "python",
        [t("class", stdin=CLASS_IN), t("small", stdin=SMALL_IN)],
        ["Loaded 3 students\nAverage: 82.3\nTop: Ada (95)", "Loaded 2 students\nAverage: 59.5\nTop: Amy (60)"],
        GB2, starter=GB1, carry=True, require=[r"max\(|sorted\(|for "]),
    run("Step 3 - Letter grades: write a function grade(score) (A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, else F). After the "
        "statistics, print every student alphabetically as 'name: grade'.", "python",
        [t("class", stdin=CLASS_IN), t("small", stdin=SMALL_IN)],
        ["Loaded 3 students\nAverage: 82.3\nTop: Ada (95)\nAda: A\nBo: C\nCy: B",
         "Loaded 2 students\nAverage: 59.5\nTop: Amy (60)\nAmy: D\nZed: F"],
        GB3, starter=GB2, carry=True, require=[r"def\s+grade\s*\("]),
)

# ------------------------------------------------------------------ Intermediate: library
LIB1 = '''class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def __str__(self):
        return f"{self.title} by {self.author} ({self.year})"'''

LIB2 = LIB1 + '''


class Library:
    def __init__(self):
        self.books = {}

    def add(self, book):
        self.books[book.title] = book

    def __len__(self):
        return len(self.books)

    def by_author(self, author):
        return sorted(b.title for b in self.books.values() if b.author == author)'''

LIB3 = LIB2 + '''

    def borrow(self, title):
        if title not in self.books:
            raise ValueError(f"no such book: {title}")
        if title in self.borrowed:
            return False
        self.borrowed.add(title)
        return True

    def give_back(self, title):
        self.borrowed.discard(title)

    def available(self):
        return sorted(t for t in self.books if t not in self.borrowed)'''
LIB3 = LIB3.replace("        self.books = {}\n", "        self.books = {}\n        self.borrowed = set()\n", 1)

LIB_SETUP = '''lib = Library()
for b in [Book("Dune", "Herbert", 1965), Book("Emma", "Austen", 1815), Book("Persuasion", "Austen", 1817)]:
    lib.add(b)
'''

INTERMEDIATE = project(
    "Project: Library system",
    "Build a small library system with classes, step by step:\n\n1. A Book class with a friendly __str__.\n2. A Library "
    "that stores books, knows its size (len) and finds books by author.\n3. Borrowing and returning books, with an "
    "error for books that don't exist.\n\nEach step continues from your previous code.",
    run("Step 1 - Write class Book(title, author, year) whose str() is 'Title by Author (year)'.", "python",
        [t("one book", append='print(Book("Dune", "Herbert", 1965))'),
         t("attributes", append='b = Book("Emma", "Austen", 1815)\nprint(b.title, b.year)')],
        ["Dune by Herbert (1965)", "Emma 1815"], LIB1, require=[r"class\s+Book", r"def\s+__str__"]),
    run("Step 2 - Add class Library with add(book), len(library) and by_author(author) returning that author's "
        "titles sorted alphabetically.", "python",
        [t("size", append=LIB_SETUP + "print(len(lib))"),
         t("by author", append=LIB_SETUP + 'print(lib.by_author("Austen"))\nprint(lib.by_author("Nobody"))')],
        ["3", "['Emma', 'Persuasion']\n[]"], LIB2, starter=LIB1, carry=True,
        require=[r"class\s+Library", r"def\s+__len__"]),
    run("Step 3 - Add borrow(title) (True if borrowed, False if already out; raise ValueError for unknown titles), "
        "give_back(title) and available() (sorted titles not borrowed).", "python",
        [t("borrowing", append=LIB_SETUP + 'print(lib.borrow("Dune"), lib.borrow("Dune"))\nprint(lib.available())\n'
                                             'lib.give_back("Dune")\nprint(lib.available())'),
         t("unknown title", append=LIB_SETUP + 'try:\n    lib.borrow("Ulysses")\nexcept ValueError as e:\n    print("error:", e)')],
        ["True False\n['Emma', 'Persuasion']\n['Dune', 'Emma', 'Persuasion']", "error: no such book: Ulysses"],
        LIB3, starter=LIB2, carry=True, require=[r"raise\s+ValueError", r"def\s+available"]),
)

# ------------------------------------------------------------------ Advanced: log analyzer
LOG1 = '''def parse(lines):
    """Yield one dict per valid 'HH:MM LEVEL message' line."""
    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) < 3 or ":" not in parts[0]:
            continue
        hh, _, mm = parts[0].partition(":")
        if not (hh.isdigit() and mm.isdigit()):
            continue
        yield {"hour": int(hh), "level": parts[1], "message": parts[2]}'''

LOG2 = '''from collections import Counter


''' + LOG1 + '''


def summary(lines):
    return dict(sorted(Counter(entry["level"] for entry in parse(lines)).items()))'''

LOG3 = LOG2 + '''


def busiest_error_hour(lines):
    hours = Counter(e["hour"] for e in parse(lines) if e["level"] == "ERROR")
    if not hours:
        return None
    return min(hours.items(), key=lambda item: (-item[1], item[0]))'''

LOGS = '''LOGS = [
    "09:15 INFO server started",
    "09:20 ERROR disk full",
    "not a log line",
    "10:01 WARN slow response",
    "10:05 ERROR timeout",
    "10:30 ERROR timeout",
    "",
    "xx:yy INFO broken time",
    "11:00 INFO backup done",
]
'''

ADVANCED = project(
    "Project: Log analyzer",
    "Real programs produce logs - lots of them. You'll build an analyzer the professional way:\n\n1. A generator that "
    "parses lines lazily and skips junk.\n2. A summary built with collections.Counter.\n3. A query that finds the "
    "busiest hour for errors.\n\nLines look like '10:05 ERROR timeout' (time, level, message).",
    run("Step 1 - Write a generator parse(lines) yielding {'hour': int, 'level': str, 'message': str} for each valid "
        "'HH:MM LEVEL message' line. Skip lines with fewer than 3 parts or a bad time.", "python",
        [t("parse", append=LOGS + "for e in parse(LOGS):\n    print(e['hour'], e['level'], e['message'])"),
         t("is a generator", append="import types\nprint(isinstance(parse([]), types.GeneratorType))")],
        ["9 INFO server started\n9 ERROR disk full\n10 WARN slow response\n10 ERROR timeout\n10 ERROR timeout\n11 INFO backup done",
         "True"], LOG1, require=[r"\byield\b"]),
    run("Step 2 - Add summary(lines) returning a dict of level -> count, with keys in alphabetical order (use "
        "collections.Counter and your parse generator).", "python",
        [t("summary", append=LOGS + "print(summary(LOGS))"), t("empty", append="print(summary([]))")],
        ["{'ERROR': 3, 'INFO': 2, 'WARN': 1}", "{}"], LOG2, starter=LOG1, carry=True, require=[r"Counter"]),
    run("Step 3 - Add busiest_error_hour(lines) returning (hour, count) for the hour with the most ERROR entries "
        "(earliest hour wins a tie), or None if there are no errors.", "python",
        [t("busiest", append=LOGS + "print(busiest_error_hour(LOGS))"),
         t("tie and none", append='print(busiest_error_hour(["08:00 ERROR a", "07:00 ERROR b"]))\nprint(busiest_error_hour(["08:00 INFO ok"]))')],
        ["(10, 2)", "(7, 1)\nNone"], LOG3, starter=LOG2, carry=True, require=[r"def\s+busiest_error_hour"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
