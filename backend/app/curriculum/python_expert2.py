"""Python Expert, part 2 (units 23-29): strings, regex, collections, data, functools, typing, algorithms, patterns."""
from .dsl import fill, lesson, mcq, order, run, section, t, unit

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Strings in depth",
        lesson(
            "Formatting with f-strings",
            """f-strings accept a format spec after a colon:

pi = 3.14159
f"{pi:.2f}"        # '3.14'   two decimals
f"{7:03d}"         # '007'    zero-padded width 3
f"{'hi':>6}"       # '    hi' right-aligned in 6
f"{'hi':<6}|"      # 'hi    |' left-aligned
f"{1234567:,}"     # '1,234,567'
f"{0.256:.1%}"     # '25.6%'

You can put any expression inside the braces: f"{a + b}" or f"{name.upper()}".""",
            mcq("What does f'{3.14159:.2f}' give?", ["3.14", "3.1", "3.142", "3.14159"], 0),
            mcq("What does f'{5:03d}' give?", ["005", "5", "500", "050"], 0),
            mcq("What does f'{1000000:,}' give?", ["1,000,000", "1000000", "1.000.000", "1,0"], 0),
            fill("Right-align in a field 8 wide.", "f\"{name:___8}\"", ">"),
            run("Read a name and a price (a decimal number). Print the name left-aligned in 10 characters, then the price with 2 decimals right-aligned in 8 characters, then a |.", "python",
                [t("pen", stdin="pen\n1.5"), t("notebook", stdin="notebook\n12.499"), t("long", stdin="highlighter\n3")],
                ["pen           1.50|", "notebook     12.50|", "highlighter    3.00|"],
                "name = input()\nprice = float(input())\nprint(f'{name:<10}{price:>8.2f}|')",
                require=[r"f['\"]"]),
        ),
        lesson(
            "Everyday string methods",
            """Strings have many handy methods (they never change the original - they return new strings):

"  hi  ".strip()              # 'hi'
"a,b,c".split(",")            # ['a', 'b', 'c']
"-".join(["a", "b"])          # 'a-b'
"hello".replace("l", "L")     # 'heLLo'
"Hello".startswith("He")      # True
"hello world".title()         # 'Hello World'
"abc".find("c")               # 2   (-1 if missing)
"a-b-c".count("-")            # 2""",
            mcq("What does 'a b c'.split() give?", ["['a', 'b', 'c']", "'abc'", "['a b c']", "('a', 'b', 'c')"], 0),
            mcq("What does ', '.join(['x', 'y']) give?", ["'x, y'", "['x, y']", "'xy'", "'x,y'"], 0),
            mcq("Does s.upper() change s itself?", ["No, it returns a new string", "Yes", "Only for ASCII", "Only in a loop"], 0),
            run("Read a sentence. Print the number of words, then the sentence with every word capitalised (title case), on two lines.", "python",
                [t("simple", stdin="hello big world"), t("spaces", stdin="  python   is fun  "), t("one", stdin="solo")],
                ["3\nHello Big World", "3\nPython Is Fun", "1\nSolo"],
                "words = input().split()\nprint(len(words))\nprint(' '.join(w.capitalize() for w in words))"),
        ),
        lesson(
            "Characters & Caesar cipher",
            """ord() gives a character's number and chr() turns a number back into a character:

ord("a")    # 97
chr(98)     # 'b'

To shift a lowercase letter by k places and wrap around the alphabet:

chr((ord(c) - ord("a") + k) % 26 + ord("a"))

str.isalpha(), isdigit(), islower() and isupper() test a character.""",
            mcq("What is ord('A')?", ["65", "97", "1", "64"], 0),
            mcq("What does chr(100) give?", ["'d'", "'c'", "'e'", "100"], 0),
            mcq("Why use % 26 in a Caesar shift?", ["To wrap past 'z' back to 'a'", "To make it faster", "To remove spaces", "To uppercase"], 0),
            run("Read a shift k, then a text. Print the text with every lowercase letter shifted forward by k (wrapping around z); leave everything else unchanged.", "python",
                [t("shift 3", stdin="3\nhello world"), t("wrap", stdin="2\nxyz"), t("keeps symbols", stdin="1\nabc, Z!")],
                ["khoor zruog", "zab", "bcd, Z!"],
                "k = int(input())\ntext = input()\nout = ''\nfor c in text:\n    if 'a' <= c <= 'z':\n        out += chr((ord(c) - ord('a') + k) % 26 + ord('a'))\n    else:\n        out += c\nprint(out)",
                require=[r"\bord\s*\(", r"\bchr\s*\("]),
        ),
    ),
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Regular expressions",
        lesson(
            "Matching with re",
            """Regular expressions describe text patterns. Use raw strings (r"...") so backslashes survive:

import re
re.search(r"\\d+", "order 66")      # finds the first run of digits -> match object
re.search(r"\\d+", "order 66").group()   # '66'
re.match(r"\\d+", "order 66")       # None - match only checks the START
re.fullmatch(r"[a-z]+", "abc")     # whole string must fit

Common pieces: \\d digit, \\w word character, \\s space, . any char, + one or more, * zero or more, ? optional, [abc] a set, ^ start, $ end.""",
            mcq("Which function checks only the START of a string?", ["re.match", "re.search", "re.findall", "re.sub"], 0),
            mcq("What does \\d+ match?", ["One or more digits", "A single letter", "Any text", "Spaces"], 0),
            mcq("What does re.search return when nothing matches?", ["None", "An empty string", "False", "An error"], 0),
            run("Read a line. Print VALID if it is a time in the form HH:MM (two digits, colon, two digits) and nothing else, otherwise INVALID. You may ignore ranges like hour 99.", "python",
                [t("ok", stdin="09:30"), t("short", stdin="9:30"), t("extra", stdin="09:30pm"), t("letters", stdin="ab:cd")],
                ["VALID", "INVALID", "INVALID", "INVALID"],
                "import re\ns = input()\nprint('VALID' if re.fullmatch(r'\\d\\d:\\d\\d', s) else 'INVALID')",
                require=[r"\bre\b"]),
        ),
        lesson(
            "Groups & findall",
            """Parentheses capture parts of a match:

m = re.search(r"(\\w+)@(\\w+)\\.com", "ada@mail.com")
m.group(1)      # 'ada'
m.group(2)      # 'mail'

findall returns every match (a list of strings, or of tuples when there are groups):

re.findall(r"\\d+", "a1 b22 c333")      # ['1', '22', '333']
re.findall(r"(\\w)=(\\d)", "a=1 b=2")    # [('a', '1'), ('b', '2')]

Named groups: (?P<year>\\d{4}) then m.group("year").""",
            mcq("What does re.findall(r'\\d+', 'x1y22') return?", ["['1', '22']", "[1, 22]", "'122'", "['x1', 'y22']"], 0),
            mcq("In re.search(r'(\\w+)@(\\w+)', 'a@b').group(2), what is returned?", ["'b'", "'a'", "'a@b'", "None"], 0),
            mcq("What does {4} mean in \\d{4}?", ["Exactly four times", "At most four", "The digit 4", "Four groups"], 0),
            run("Read a line of text. Print the sum of all whole numbers appearing in it (0 if none).", "python",
                [t("mixed", stdin="I have 3 cats and 12 fish"), t("none", stdin="no numbers here"), t("glued", stdin="a1b22c333")],
                ["15", "0", "356"], "import re\nprint(sum(int(n) for n in re.findall(r'\\d+', input())))",
                require=[r"findall"]),
        ),
        lesson(
            "sub & split",
            """re.sub replaces every match; re.split splits on a pattern:

re.sub(r"\\s+", " ", "a   b    c")           # 'a b c'
re.sub(r"\\d", "#", "a1b2")                   # 'a#b#'
re.split(r"[,;]\\s*", "a, b;c")              # ['a', 'b', 'c']

The replacement can use groups: re.sub(r"(\\w+) (\\w+)", r"\\2 \\1", "hello world") -> 'world hello'.""",
            mcq("What does re.sub(r'\\d', '#', 'a1b2') give?", ["'a#b#'", "'a1b2'", "'##'", "'#'"], 0),
            mcq("What does re.split(r'[,;]', 'a,b;c') give?", ["['a', 'b', 'c']", "['a,b;c']", "['a', 'b;c']", "'abc'"], 0),
            fill("Collapse runs of spaces into one.", "re.sub(r'___', ' ', text)", [" +", "\\s+", " {2,}"]),
            run("Read a line. Print it with every run of whitespace collapsed to a single space and no space at either end.", "python",
                [t("spaces", stdin="a   b    c"), t("edges", stdin="   hello   world  "), t("tabs", stdin="x\t\ty")],
                ["a b c", "hello world", "x y"], "import re\nprint(re.sub(r'\\s+', ' ', input()).strip())",
                require=[r"\bre\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · The collections module",
        lesson(
            "Counter",
            """Counter counts how many times each item appears:

from collections import Counter
c = Counter("banana")       # Counter({'a': 3, 'n': 2, 'b': 1})
c["a"]                      # 3
c["z"]                      # 0 - missing keys count as zero
c.most_common(2)            # [('a', 3), ('n', 2)]

Counters can be added and subtracted too, and update() adds more counts.""",
            mcq("What is Counter('aab')['a']?", ["2", "1", "'a'", "3"], 0),
            mcq("What does Counter('abc')['z'] give?", ["0", "KeyError", "None", "-1"], 0),
            mcq("What does most_common(1) return for Counter('aab')?", ["[('a', 2)]", "('a', 2)", "['a']", "2"], 0),
            run("Read words on one line. Print the most common word and its count as 'word count'. If tied, print the word that appears first in the input.", "python",
                [t("clear", stdin="a b a c a b"), t("tie", stdin="x y y x"), t("one", stdin="solo")],
                ["a 3", "x 2", "solo 1"],
                "from collections import Counter\nc = Counter(input().split())\nword, n = c.most_common(1)[0]\nprint(word, n)",
                require=[r"Counter"]),
        ),
        lesson(
            "defaultdict",
            """defaultdict creates a missing value for you the first time you touch a key, so no 'if key in d' checks:

from collections import defaultdict
groups = defaultdict(list)
for word in ["apple", "avocado", "banana"]:
    groups[word[0]].append(word)
# {'a': ['apple', 'avocado'], 'b': ['banana']}

defaultdict(int) is a counter; defaultdict(set) collects unique items.""",
            mcq("What does defaultdict(list)['x'] return for a new key?", ["[]", "None", "KeyError", "0"], 0),
            mcq("Which factory makes a counting dictionary?", ["int", "list", "set", "str"], 0),
            mcq("What's the main benefit?", ["No need to check or initialise missing keys", "It sorts keys", "It is immutable", "It stores order"], 0),
            run("Read words on one line. Group them by their first letter and print each group on its own line as 'letter: word1 word2', with letters in alphabetical order and words in input order.", "python",
                [t("groups", stdin="apple banana avocado blueberry cherry"), t("one", stdin="kiwi"), t("same", stdin="bb ba bc")],
                ["a: apple avocado\nb: banana blueberry\nc: cherry", "k: kiwi", "b: bb ba bc"],
                "from collections import defaultdict\ng = defaultdict(list)\nfor w in input().split():\n    g[w[0]].append(w)\nfor k in sorted(g):\n    print(k + ': ' + ' '.join(g[k]))",
                require=[r"defaultdict"]),
        ),
        lesson(
            "deque & namedtuple",
            """deque is a double-ended queue: fast appends and pops at BOTH ends.

from collections import deque
d = deque([1, 2, 3])
d.appendleft(0)      # deque([0, 1, 2, 3])
d.pop()              # 3
d.popleft()          # 0
d.rotate(1)          # moves items around the ring

A list's pop(0) is O(n); deque.popleft() is O(1) - use a deque for queues.

namedtuple makes a lightweight record: P = namedtuple("P", "x y"); p = P(1, 2); p.x.""",
            mcq("Which operation is O(1) on a deque but O(n) on a list?", ["popleft / pop(0)", "append", "len", "indexing"], 0),
            mcq("What does deque([1, 2, 3]).popleft() return?", ["1", "3", "2", "None"], 0),
            mcq("What does a namedtuple give you over a plain tuple?", ["Access fields by name", "Mutability", "Speed", "Sorting"], 0),
            run("Josephus game: read n and k. People 1..n stand in a circle; repeatedly count k people and remove the k-th, until one remains. Print the survivor's number. Use a deque.", "python",
                [t("7 3", stdin="7 3"), t("5 2", stdin="5 2"), t("single", stdin="1 4")],
                ["4", "3", "1"],
                "from collections import deque\nn, k = map(int, input().split())\nd = deque(range(1, n + 1))\nwhile len(d) > 1:\n    d.rotate(-(k - 1))\n    d.popleft()\nprint(d[0])",
                require=[r"deque"]),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · Working with data",
        lesson(
            "JSON",
            """JSON is the web's data format. The json module converts between text and Python objects:

import json
data = json.loads('{"name": "Ada", "langs": ["py", "js"]}')
data["langs"][0]            # 'py'
json.dumps({"a": 1, "b": [1, 2]})                 # '{"a": 1, "b": [1, 2]}'
json.dumps(data, indent=2, sort_keys=True)        # pretty-printed

JSON maps to Python like this: object -> dict, array -> list, string -> str, number -> int/float, true/false -> True/False, null -> None.""",
            mcq("What does json.loads turn JSON text into?", ["Python objects (dict, list, ...)", "A file", "A class", "Bytes"], 0),
            mcq("JSON null becomes which Python value?", ["None", "0", "''", "False"], 0),
            mcq("Which function converts a dict to JSON text?", ["json.dumps", "json.loads", "json.parse", "json.text"], 0),
            run("Read a JSON object with a 'items' list of objects that each have 'name' and 'price'. Print the total price, then the name of the most expensive item.", "python",
                [t("three", stdin='{"items": [{"name": "pen", "price": 2}, {"name": "book", "price": 10}, {"name": "bag", "price": 7}]}'),
                 t("one", stdin='{"items": [{"name": "gum", "price": 1}]}')],
                ["19\nbook", "1\ngum"],
                "import json\ndata = json.loads(input())\nitems = data['items']\nprint(sum(i['price'] for i in items))\nprint(max(items, key=lambda i: i['price'])['name'])",
                require=[r"json\.loads"]),
        ),
        lesson(
            "Parsing CSV-style text",
            """A lot of real data is lines of delimited text. Split each line, convert types, then work with the rows:

text = "ada,36\\nbo,41"
rows = [line.split(",") for line in text.splitlines()]
people = [(name, int(age)) for name, age in rows]

splitlines() splits on line breaks; strip() removes stray whitespace. Always convert numbers with int()/float() before comparing or adding - text '10' sorts before '9'.""",
            mcq("What is sorted(['10', '9']) ?", ["['10', '9']", "['9', '10']", "[9, 10]", "An error"], 0, "Strings compare character by character: '1' < '9'."),
            mcq("What does 'a\\nb'.splitlines() give?", ["['a', 'b']", "['a\\nb']", "'ab'", "['a', '\\n', 'b']"], 0),
            mcq("Why convert fields with int() before summing?", ["They arrive as text", "int is faster", "Strings can't be stored", "It's required by split"], 0),
            run("Read an integer n, then n lines of 'name,score'. Print the name with the highest score and the average score rounded to 1 decimal, on two lines.", "python",
                [t("three", stdin="3\nada,90\nbo,70\ncy,80"), t("two", stdin="2\nx,50\ny,51"), t("one", stdin="1\nsolo,100")],
                ["ada\n80.0", "y\n50.5", "solo\n100.0"],
                "n = int(input())\nrows = []\nfor _ in range(n):\n    name, score = input().split(',')\n    rows.append((name, int(score)))\nbest = max(rows, key=lambda r: r[1])\nprint(best[0])\nprint(round(sum(s for _, s in rows) / n, 1))"),
        ),
        lesson(
            "Dates with datetime",
            """The datetime module does calendar maths for you:

from datetime import date, timedelta
d = date(2024, 2, 28)
d + timedelta(days=2)                  # 2024-03-01 (2024 is a leap year)
(date(2024, 12, 25) - date(2024, 1, 1)).days    # 359
d.weekday()                            # 0 = Monday ... 6 = Sunday
d.strftime("%d/%m/%Y")                 # '28/02/2024'
date.fromisoformat("2025-03-09")

Subtracting two dates gives a timedelta; .days is how many days apart they are.""",
            mcq("What does date(2024, 12, 25) - date(2024, 12, 20) give?", ["A timedelta of 5 days", "5", "'5 days'", "A date"], 0),
            mcq("What does date.weekday() return for a Monday?", ["0", "1", "7", "'Mon'"], 0),
            mcq("What does timedelta(days=7) represent?", ["A duration of a week", "A date", "A time zone", "A year"], 0),
            run("Read two dates (YYYY-MM-DD) on separate lines. Print the number of days from the first to the second (may be negative).", "python",
                [t("month", stdin="2024-01-01\n2024-01-31"), t("leap", stdin="2024-02-28\n2024-03-01"), t("negative", stdin="2024-05-10\n2024-05-01")],
                ["30", "2", "-9"], "from datetime import date\na = date.fromisoformat(input())\nb = date.fromisoformat(input())\nprint((b - a).days)",
                require=[r"datetime"]),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · functools & recursion",
        lesson(
            "lru_cache (memoization)",
            """Memoization remembers results so repeated calls are instant. functools.lru_cache does it with one line:

from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(80)     # instant; without the cache it would take longer than your lifetime

It works for functions whose arguments are hashable (numbers, strings, tuples) and whose result depends only on the arguments.""",
            mcq("What does lru_cache store?", ["Results keyed by the arguments", "The function's code", "Error messages", "Only the last print"], 0),
            mcq("Why is un-cached recursive fib(n) so slow?", ["It recomputes the same values again and again", "Recursion is banned", "Ints are big", "It sorts"], 0),
            mcq("Which arguments can lru_cache handle?", ["Hashable ones like ints, strings, tuples", "Lists", "Dicts", "Any object"], 0),
            run("Read n. Print the number of ways to climb n stairs taking 1 or 2 steps at a time (n >= 1), using a recursive function with @lru_cache.", "python",
                [t("n=1", stdin="1"), t("n=5", stdin="5"), t("n=50", stdin="50")],
                ["1", "8", "20365011074"],
                "from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef ways(n):\n    if n <= 2:\n        return n\n    return ways(n - 1) + ways(n - 2)\n\nprint(ways(int(input())))",
                require=[r"lru_cache|cache"]),
        ),
        lesson(
            "reduce & partial",
            """functools.reduce folds a sequence into one value:

from functools import reduce
reduce(lambda a, b: a * b, [1, 2, 3, 4])        # 24
reduce(lambda a, b: a + b, [1, 2, 3], 10)       # 16 (10 is the starting value)

functools.partial pre-fills some arguments and gives you a new function:

from functools import partial
def power(base, exp): return base ** exp
square = partial(power, exp=2)
square(7)          # 49""",
            mcq("What does reduce(lambda a, b: a + b, [1, 2, 3]) return?", ["6", "[1, 2, 3]", "3", "0"], 0),
            mcq("What does partial do?", ["Creates a function with some arguments fixed", "Splits a list", "Delays a call", "Caches a result"], 0),
            fill("Fix the exponent to 3.", "cube = partial(power, exp=___)", "3"),
            run("Read numbers on one line. Print their product using functools.reduce.", "python",
                [t("four", stdin="1 2 3 4"), t("single", stdin="7"), t("negative", stdin="-2 5")],
                ["24", "7", "-10"], "from functools import reduce\nnums = [int(x) for x in input().split()]\nprint(reduce(lambda a, b: a * b, nums, 1))",
                require=[r"reduce"]),
        ),
        lesson(
            "Recursion patterns",
            """Recursion solves a problem by solving smaller copies of it. Every recursive function needs a BASE CASE that stops.

def flatten(x):
    if not isinstance(x, list):
        return [x]
    out = []
    for item in x:
        out += flatten(item)
    return out

flatten([1, [2, [3, 4]], 5])      # [1, 2, 3, 4, 5]

Typical shapes: sum of a list = first + sum(rest); a tree = this node + its children; permutations = pick one, permute the rest.""",
            mcq("What is a base case?", ["The simple case that stops the recursion", "The first call", "A loop", "An error"], 0),
            mcq("What happens if a recursive function has no base case?", ["RecursionError (stack overflow)", "It returns None", "It runs once", "It sorts"], 0),
            mcq("What does flatten([1, [2]]) return with the function above?", ["[1, 2]", "[1, [2]]", "[[1], [2]]", "[3]"], 0),
            run("Write depth(x) returning how deeply lists are nested: 0 for a non-list, 1 for a list with no lists inside, and so on. An empty list has depth 1.", "python",
                [t("flat", append="print(depth([1, 2, 3]))"), t("nested", append="print(depth([1, [2, [3]]]))"), t("plain", append="print(depth(5))"), t("empty", append="print(depth([]))")],
                ["1", "3", "0", "1"],
                "def depth(x):\n    if not isinstance(x, list):\n        return 0\n    return 1 + max((depth(i) for i in x), default=0)",
                starter="def depth(x):\n    pass\n"),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Types, errors & tests",
        lesson(
            "Type hints",
            """Type hints document what a function expects and returns. Python doesn't enforce them, but editors and tools like mypy use them:

def area(w: float, h: float) -> float:
    return w * h

names: list[str] = []
age: int | None = None          # an int or None

Use Optional/| None when a value may be missing. Hints make code self-documenting and catch bugs early.""",
            mcq("Does Python raise an error when you pass the wrong type to a hinted function?", ["No, hints aren't enforced at runtime", "Always", "Only for ints", "Only in classes"], 0),
            mcq("What does '-> int' after the parameters mean?", ["The function returns an int", "It takes an int", "It prints an int", "It loops"], 0),
            mcq("How do you hint 'an int or None'?", ["int | None", "int & None", "int or none", "[int, None]"], 0),
            run("Write a typed function average(nums: list[float]) -> float that returns the mean rounded to 2 decimals (0.0 for an empty list).", "python",
                [t("simple", append="print(average([1, 2, 4]))"), t("empty", append="print(average([]))"), t("single", append="print(average([5]))")],
                ["2.33", "0.0", "5.0"],
                "def average(nums: list[float]) -> float:\n    if not nums:\n        return 0.0\n    return round(sum(nums) / len(nums), 2)",
                starter="def average(nums: list[float]) -> float:\n    pass\n", require=[r"->\s*float"]),
        ),
        lesson(
            "Custom exceptions",
            """Define your own exception by subclassing Exception. Raise it with raise, catch it with except:

class InsufficientFunds(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFunds(f"need {amount - balance} more")
    return balance - amount

try:
    withdraw(10, 25)
except InsufficientFunds as e:
    print("Error:", e)

finally: always runs. else: runs only if no exception happened.""",
            mcq("Which keyword throws an exception?", ["raise", "throw", "error", "except"], 0),
            mcq("When does the finally block run?", ["Always", "Only on errors", "Only on success", "Never"], 0),
            mcq("How do you read the message of 'except MyError as e'?", ["print(e) / str(e)", "e.error", "e.text only", "You can't"], 0),
            run("Write class NegativeError(Exception) and a function safe_sqrt(x) that raises NegativeError for x < 0 and otherwise returns x ** 0.5. The program prints the result or 'negative' on error.", "python",
                [t("ok", append="try:\n    print(safe_sqrt(16))\nexcept NegativeError:\n    print('negative')"), t("bad", append="try:\n    print(safe_sqrt(-4))\nexcept NegativeError:\n    print('negative')")],
                ["4.0", "negative"],
                "class NegativeError(Exception):\n    pass\n\ndef safe_sqrt(x):\n    if x < 0:\n        raise NegativeError()\n    return x ** 0.5",
                starter="class NegativeError(Exception):\n    pass\n\ndef safe_sqrt(x):\n    pass\n", require=[r"\braise\b"]),
        ),
        lesson(
            "assert & testing mindset",
            """assert checks that something you believe is true - and raises AssertionError if not:

def is_prime(n):
    ...

assert is_prime(7)
assert not is_prime(8)

Good tests cover: a typical case, the edges (0, 1, empty), and a failure case. Small, pure functions (same input -> same output, no printing inside) are the easiest to test.

Write the tests first, watch them fail, then make them pass - that's test-driven development.""",
            mcq("What does assert x > 0 do when x is -1?", ["Raises AssertionError", "Prints False", "Returns None", "Nothing"], 0),
            mcq("Which functions are easiest to test?", ["Pure functions with no side effects", "Ones that read files", "Ones that print", "Ones using random"], 0),
            mcq("Which is an 'edge case' for a sum() function?", ["An empty list", "[1, 2, 3]", "[10, 20]", "[4, 5, 6]"], 0),
            run("Write is_palindrome(s) that ignores case and non-letters. The program prints the result for several inputs.", "python",
                [t("simple", append="print(is_palindrome('Racecar'))"), t("phrase", append="print(is_palindrome('A man, a plan, a canal: Panama'))"), t("no", append="print(is_palindrome('hello'))"), t("empty", append="print(is_palindrome(''))")],
                ["True", "True", "False", "True"],
                "def is_palindrome(s):\n    letters = [c.lower() for c in s if c.isalpha()]\n    return letters == letters[::-1]",
                starter="def is_palindrome(s):\n    pass\n"),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Algorithm toolkit & patterns",
        lesson(
            "heapq - priority queues",
            """A heap always gives you the smallest item fast. heapq works on a plain list:

import heapq
h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 3)
heapq.heappop(h)          # 1  (smallest first)
heapq.nsmallest(2, [5, 1, 3])   # [1, 3]
heapq.nlargest(2, [5, 1, 3])    # [5, 3]

Push/pop are O(log n). Push tuples like (priority, item) to order by priority.""",
            mcq("Which item does heappop return?", ["The smallest", "The largest", "The newest", "The oldest"], 0),
            mcq("What is the cost of heappush?", ["O(log n)", "O(1)", "O(n)", "O(n²)"], 0),
            mcq("How do you get the 3 largest items?", ["heapq.nlargest(3, data)", "heapq.top(3)", "heappop(3)", "sorted(data)[3]"], 0),
            run("Read numbers and a k on the last line. Print the k smallest numbers in ascending order, separated by spaces, using heapq.", "python",
                [t("three", stdin="9 4 7 1 8\n3"), t("all", stdin="5 2\n2"), t("one", stdin="3 3 1\n1")],
                ["1 4 7", "2 5", "1"],
                "import heapq\nnums = [int(x) for x in input().split()]\nk = int(input())\nprint(' '.join(map(str, heapq.nsmallest(k, nums))))",
                require=[r"heapq"]),
        ),
        lesson(
            "bisect & sorted data",
            """bisect finds where a value belongs in a SORTED list in O(log n):

import bisect
a = [10, 20, 30, 40]
bisect.bisect_left(a, 30)     # 2   (index of the first 30)
bisect.bisect_right(a, 30)    # 3   (just after the last 30)
bisect.insort(a, 25)          # inserts and keeps it sorted

bisect_right(a, x) tells you how many items are <= x.""",
            mcq("What does bisect_left([1, 3, 5], 4) return?", ["2", "1", "3", "4"], 0),
            mcq("The list must be…", ["sorted", "unique", "numbers only", "short"], 0),
            mcq("What does bisect_right(a, x) count?", ["Items <= x (in a sorted list)", "Items > x", "Items == x only", "Unique items"], 0),
            run("Read a sorted list of numbers, then a number x. Print how many items in the list are less than or equal to x, using bisect.", "python",
                [t("middle", stdin="1 3 3 5 9\n3"), t("none", stdin="4 5 6\n1"), t("all", stdin="1 2\n10")],
                ["3", "0", "2"], "import bisect\nnums = [int(v) for v in input().split()]\nx = int(input())\nprint(bisect.bisect_right(nums, x))",
                require=[r"bisect"]),
        ),
        lesson(
            "groupby & multi-key sorting",
            """sorted can sort by several keys at once with a tuple, and itertools.groupby groups neighbours with the same key (sort first!):

people = [("Bo", 30), ("Ada", 30), ("Cy", 25)]
sorted(people, key=lambda p: (-p[1], p[0]))
# oldest first, ties alphabetical: [('Ada', 30), ('Bo', 30), ('Cy', 25)]

from itertools import groupby
for key, items in groupby(sorted(words, key=len), key=len):
    print(key, list(items))

The negative sign flips a numeric key to descending.""",
            mcq("What does key=lambda p: (-p[1], p[0]) do?", ["Sort by p[1] descending, then p[0] ascending", "Sort by p[0] only", "Reverse the list", "Sort ascending by both"], 0),
            mcq("Why sort before groupby?", ["groupby only groups ADJACENT equal keys", "It is faster", "It is required by Python 3", "To remove duplicates"], 0),
            mcq("What does groupby return for each group?", ["(key, iterator of items)", "A list", "A dict", "A set"], 0),
            run("Read n then n lines of 'name score'. Print the names ordered by score descending, ties alphabetically, one per line.", "python",
                [t("ties", stdin="4\nbo 80\nada 90\ncy 80\ndee 70"), t("one", stdin="1\nsolo 5"), t("all tied", stdin="3\nc 1\na 1\nb 1")],
                ["ada\nbo\ncy\ndee", "solo", "a\nb\nc"],
                "n = int(input())\nrows = []\nfor _ in range(n):\n    name, score = input().split()\n    rows.append((name, int(score)))\nfor name, _ in sorted(rows, key=lambda r: (-r[1], r[0])):\n    print(name)",
                require=[r"sorted|sort\("]),
        ),
        lesson(
            "Design patterns: strategy & observer",
            """Strategy: pass in the behaviour as a function so you can swap it.

def total(prices, discount):
    return sum(discount(p) for p in prices)
total(prices, lambda p: p * 0.9)

Observer: an object keeps a list of callbacks and calls them when something happens.

class Button:
    def __init__(self):
        self.listeners = []
    def on_click(self, fn):
        self.listeners.append(fn)
    def click(self):
        for fn in self.listeners:
            fn()

Python's first-class functions make these patterns tiny.""",
            mcq("In the strategy pattern, behaviour is…", ["Passed in, often as a function", "Hard-coded with if/elif", "Stored in a file", "Inherited only"], 0),
            mcq("What does the observer pattern do?", ["Notifies registered listeners when something happens", "Sorts items", "Caches results", "Creates objects"], 0),
            mcq("Why are functions-as-values handy for patterns?", ["No extra classes needed for each behaviour", "They are faster", "They are required", "They avoid imports"], 0),
            run("Write class Emitter with on(fn) to register a callback and emit(value) to call every registered callback with the value, in registration order.", "python",
                [t("two listeners", append="e = Emitter()\ne.on(lambda v: print('A', v))\ne.on(lambda v: print('B', v * 2))\ne.emit(5)"), t("none", append="e = Emitter()\ne.emit(1)\nprint('done')"), t("twice", append="e = Emitter()\nlog = []\ne.on(log.append)\ne.emit(1)\ne.emit(2)\nprint(log)")],
                ["A 5\nB 10", "done", "[1, 2]"],
                "class Emitter:\n    def __init__(self):\n        self.listeners = []\n    def on(self, fn):\n        self.listeners.append(fn)\n    def emit(self, value):\n        for fn in self.listeners:\n            fn(value)",
                starter="class Emitter:\n    pass\n"),
        ),
    ),
)
