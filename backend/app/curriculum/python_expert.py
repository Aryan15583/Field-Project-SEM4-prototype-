"""Python - Expert section (units 17-29): functions in depth, generators, decorators, OOP, regex, collections,
functools, typing, algorithms and patterns. Every program here runs in the browser (Pyodide)."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Functions in depth",
        lesson(
            "Default & keyword arguments",
            """Parameters can have defaults, and callers can name arguments:

def greet(name, greeting="Hello", punct="!"):
    return f"{greeting}, {name}{punct}"

greet("Ada")                      # Hello, Ada!
greet("Ada", punct="?")           # Hello, Ada?
greet(greeting="Hi", name="Bo")   # keyword arguments can come in any order

Never use a mutable default like def f(items=[]) - the same list is shared by every call. Use None and create the list inside.""",
            mcq("What does greet('Ada', punct='?') return with the function above?", ["Hello, Ada?", "Hello, Ada!", "Ada?", "An error"], 0),
            mcq("Why is def add(x, items=[]) a bug-prone default?", ["The list is created once and shared between calls", "Lists can't be defaults", "It's slower", "It always raises"], 0),
            fill("Give the parameter a default of 10.", "def scale(value, factor___10):", "="),
            order("Order the safe pattern for a list default.", ["def add(x, items=None):", "    if items is None:", "        items = []", "    items.append(x)", "    return items"]),
            run("Write power(base, exp=2) that returns base ** exp. Then the program calls it.", "python",
                [t("default", append="print(power(5))"), t("explicit", append="print(power(2, 10))"), t("keyword", append="print(power(exp=3, base=4))")],
                ["25", "1024", "64"], "def power(base, exp=2):\n    return base ** exp",
                starter="def power(base, exp=2):\n    pass\n", require=[r"exp\s*=\s*2"]),
        ),
        lesson(
            "*args and **kwargs",
            """*args collects extra positional arguments into a tuple; **kwargs collects extra keyword arguments into a dict:

def show(*args, **kwargs):
    print(args, kwargs)

show(1, 2, x=3)      # (1, 2) {'x': 3}

The same stars UNPACK when calling:

nums = [1, 2, 3]
print(*nums)            # 1 2 3
opts = {"sep": "-"}
print(1, 2, **opts)     # 1-2""",
            mcq("What type is args inside def f(*args)?", ["tuple", "list", "dict", "set"], 0),
            mcq("What does f(1, 2, a=3) put in kwargs for def f(*args, **kwargs)?", ["{'a': 3}", "(3,)", "[3]", "{3: 'a'}"], 0),
            mcq("What does print(*[1, 2, 3]) print?", ["1 2 3", "[1, 2, 3]", "(1, 2, 3)", "An error"], 0),
            fill("Collect any number of positional arguments.", "def total(___nums):", "*"),
            run("Write total(*nums) that returns the sum of all its arguments (0 if none).", "python",
                [t("three", append="print(total(1, 2, 3))"), t("none", append="print(total())"), t("unpack", append="print(total(*[10, 20]))")],
                ["6", "0", "30"], "def total(*nums):\n    return sum(nums)", starter="def total(*nums):\n    pass\n", require=[r"\*nums"]),
        ),
        lesson(
            "Closures",
            """A function defined inside another function remembers the variables around it - even after the outer function has returned. That's a closure.

def make_counter():
    count = 0
    def step():
        nonlocal count
        count += 1
        return count
    return step

c = make_counter()
c(); c()        # 1, then 2

nonlocal lets the inner function REASSIGN the outer variable. Each call to make_counter() creates a fresh, independent counter.""",
            mcq("What does c() return the third time?", ["3", "1", "0", "An error"], 0, code="c = make_counter()\nc(); c(); print(c())"),
            mcq("What does the nonlocal keyword allow?", ["Reassigning a variable of the enclosing function", "Creating a global", "Making a constant", "Importing a module"], 0),
            mcq("Two counters made by make_counter() share their count.", ["False - each has its own", "True", "Only in loops", "Only with nonlocal"], 0),
            fill("Let the inner function change total.", "___ total", "nonlocal"),
            run("Write make_multiplier(n) that returns a function multiplying its argument by n.", "python",
                [t("double", append="d = make_multiplier(2)\nprint(d(21))"), t("triple", append="print(make_multiplier(3)(5))"),
                 t("independent", append="a = make_multiplier(2)\nb = make_multiplier(10)\nprint(a(1), b(1))")],
                ["42", "15", "2 10"], "def make_multiplier(n):\n    def times(x):\n        return x * n\n    return times",
                starter="def make_multiplier(n):\n    pass\n"),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Higher-order functions",
        lesson(
            "lambda, map & filter",
            """Functions are values: you can pass them around.

lambda x: x * 2        # an anonymous one-line function

list(map(lambda x: x * 2, [1, 2, 3]))        # [2, 4, 6]
list(filter(lambda x: x > 1, [1, 2, 3]))     # [2, 3]

map and filter return lazy iterators, so wrap them in list() to see the result. Comprehensions often read better, but map/filter shine when you already have a named function: list(map(str, [1, 2])) -> ['1', '2'].""",
            mcq("What does list(map(len, ['a', 'bb', 'ccc'])) give?", ["[1, 2, 3]", "6", "['a', 'bb']", "[3]"], 0),
            mcq("What does list(filter(lambda n: n % 2, [1, 2, 3, 4])) give?", ["[1, 3]", "[2, 4]", "[True, False, True, False]", "[1, 2, 3, 4]"], 0, "n % 2 is truthy (1) for odd numbers."),
            fill("Complete the lambda that adds one.", "inc = lambda x: x ___ 1", "+"),
            run("Read numbers on one line. Print the squares of the even ones as a list, using filter and map with lambdas.", "python",
                [t("mixed", stdin="1 2 3 4"), t("no evens", stdin="1 3 5"), t("all evens", stdin="2 6")],
                ["[4, 16]", "[]", "[4, 36]"],
                "nums = [int(x) for x in input().split()]\nprint(list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))))",
                require=[r"\bmap\b", r"\bfilter\b", r"lambda"]),
        ),
        lesson(
            "Sorting with key",
            """sorted() and list.sort() take a key function that says WHAT to sort by:

words = ["pear", "fig", "banana"]
sorted(words)                    # alphabetical
sorted(words, key=len)           # by length: ['fig', 'pear', 'banana']
sorted(words, key=len, reverse=True)

Sort pairs by their second item: sorted(pairs, key=lambda p: p[1]). Python's sort is stable: items that compare equal keep their original order.""",
            mcq("What does sorted(['bb', 'a', 'ccc'], key=len) return?", ["['a', 'bb', 'ccc']", "['a', 'bb', 'ccc'] sorted alphabetically only", "['ccc', 'bb', 'a']", "['bb', 'a', 'ccc']"], 0),
            mcq("What does 'stable sort' mean?", ["Equal items keep their original order", "It never raises", "It sorts in place", "It sorts numbers only"], 0),
            fill("Sort largest first.", "sorted(nums, ___=True)", "reverse"),
            run("Read words on one line. Print them sorted by length (shortest first); words of equal length keep their input order.", "python",
                [t("mixed", stdin="pear fig banana kiwi"), t("same length", stdin="bb aa cc"), t("one", stdin="solo")],
                ["fig pear kiwi banana", "bb aa cc", "solo"], "words = input().split()\nprint(' '.join(sorted(words, key=len)))",
                require=[r"key\s*="]),
        ),
        lesson(
            "Passing functions as arguments",
            """A function that takes or returns another function is a higher-order function.

def apply_twice(f, x):
    return f(f(x))

apply_twice(lambda n: n + 3, 10)     # 16

Callbacks, sort keys, decorators and event handlers all use this idea. A function's name without parentheses is the function itself; with parentheses it is CALLED.""",
            mcq("What does apply_twice(lambda n: n * 2, 5) return?", ["20", "10", "7", "25"], 0),
            mcq("What is the difference between f and f()?", ["f is the function; f() calls it", "No difference", "f() is faster", "f is a string"], 0),
            fill("Pass the function itself (don't call it).", "result = apply(___, 3)  # square is a function", "square"),
            run("Write apply_n(f, x, n) that applies f to x, n times, and returns the result.", "python",
                [t("add three times", append="print(apply_n(lambda v: v + 3, 0, 3))"), t("double 4 times", append="print(apply_n(lambda v: v * 2, 1, 4))"), t("zero times", append="print(apply_n(lambda v: v + 1, 7, 0))")],
                ["9", "16", "7"], "def apply_n(f, x, n):\n    for _ in range(n):\n        x = f(x)\n    return x",
                starter="def apply_n(f, x, n):\n    pass\n"),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Iterators & generators",
        lesson(
            "How for loops really work",
            """A for loop asks an iterable for an iterator and keeps calling next() until StopIteration:

it = iter([10, 20])
next(it)    # 10
next(it)    # 20
next(it)    # raises StopIteration

Lists, strings, dicts, files and range() are all iterable. An iterator remembers where it is, and it can only be used once.""",
            mcq("What does next(it) raise when the iterator is exhausted?", ["StopIteration", "IndexError", "KeyError", "ValueError"], 0),
            mcq("Which is an iterator, not just an iterable?", ["iter([1, 2])", "[1, 2]", "'abc'", "range(3)"], 0, "iter() returns an iterator; lists, strings and ranges are iterables."),
            mcq("What does this print?", ["1 2", "1 1", "2 3", "An error"], 0, code="it = iter([1, 2, 3])\nprint(next(it), next(it))"),
            run("Read numbers on one line. Using iter() and next() only (no for loop, no indexing), print the first and the second number separated by a space.", "python",
                [t("four", stdin="7 8 9 10"), t("two", stdin="1 2")],
                ["7 8", "1 2"], "it = iter(input().split())\nprint(next(it), next(it))",
                require=[r"\biter\s*\(", r"\bnext\s*\("], forbid=[r"\bfor\b", r"\[\s*\d"]),
        ),
        lesson(
            "Generators with yield",
            """A function with yield becomes a generator: it produces values one at a time and pauses between them.

def countdown(n):
    while n > 0:
        yield n
        n -= 1

list(countdown(3))      # [3, 2, 1]

Generators are lazy - they compute the next value only when asked, so they can even be infinite and use almost no memory.""",
            mcq("What does list(countdown(3)) give?", ["[3, 2, 1]", "[1, 2, 3]", "3", "[]"], 0),
            mcq("What is the main benefit of a generator?", ["Values are made one at a time, saving memory", "It runs on the GPU", "It is always faster", "It can't raise errors"], 0),
            fill("Turn this into a generator by producing each value.", "for n in nums:\n    ___ n * 2", "yield"),
            run("Write evens(limit) as a generator that yields the even numbers from 0 up to but not including limit.", "python",
                [t("ten", append="print(list(evens(10)))"), t("zero", append="print(list(evens(0)))"), t("lazy", append="g = evens(100)\nprint(next(g), next(g), next(g))")],
                ["[0, 2, 4, 6, 8]", "[]", "0 2 4"], "def evens(limit):\n    for n in range(0, limit, 2):\n        yield n",
                starter="def evens(limit):\n    pass\n", require=[r"\byield\b"]),
        ),
        lesson(
            "Generator expressions & itertools",
            """A generator expression is a comprehension with round brackets - lazy and memory-friendly:

total = sum(n * n for n in range(1000000))

The itertools module has more building blocks:

from itertools import islice, count, chain, product
list(islice(count(1), 3))          # [1, 2, 3]  (count is infinite)
list(chain([1, 2], [3]))           # [1, 2, 3]
list(product("ab", [0, 1]))        # [('a', 0), ('a', 1), ('b', 0), ('b', 1)]""",
            mcq("What does sum(n for n in range(4)) give?", ["6", "10", "4", "3"], 0),
            mcq("What does list(islice(count(5), 3)) give?", ["[5, 6, 7]", "[0, 1, 2]", "[5, 5, 5]", "[6, 7, 8]"], 0),
            mcq("Which is lazy?", ["(x for x in data)", "[x for x in data]", "{x for x in data}", "list(data)"], 0),
            run("Read an integer n. Print the sum of the squares of 1..n using a generator expression inside sum().", "python",
                [t("n=3", stdin="3"), t("n=10", stdin="10"), t("n=0", stdin="0")],
                ["14", "385", "0"], "n = int(input())\nprint(sum(i * i for i in range(1, n + 1)))",
                require=[r"sum\s*\(\s*[^\[\]]*\bfor\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Decorators & context managers",
        lesson(
            "Writing a decorator",
            """A decorator wraps a function to add behaviour without changing its code.

def shout(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@shout
def hello(name):
    return "hello " + name

hello("ada")      # 'HELLO ADA'

@shout above hello is exactly hello = shout(hello). Use *args/**kwargs so the wrapper accepts anything.""",
            mcq("What is @shout written above def hello()... equivalent to?", ["hello = shout(hello)", "shout = hello(shout)", "hello = shout()", "shout(hello())"], 0),
            mcq("Why does the wrapper take *args, **kwargs?", ["So it works for functions with any parameters", "To make it faster", "Decorators require it", "To avoid closures"], 0),
            mcq("A decorator is a function that…", ["takes a function and returns a function", "returns a number", "takes a class only", "prints text"], 0),
            run("Write a decorator double that doubles the number returned by the function it wraps.", "python",
                [t("add", append="@double\ndef add(a, b):\n    return a + b\nprint(add(2, 3))"), t("seven", append="@double\ndef seven():\n    return 7\nprint(seven())")],
                ["10", "14"], "def double(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs) * 2\n    return wrapper",
                starter="def double(func):\n    pass\n"),
        ),
        lesson(
            "functools.wraps & decorators with arguments",
            """A wrapper hides the original function's name. functools.wraps copies it back:

from functools import wraps

def repeat(times):                 # decorator with an argument = a function that returns a decorator
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def ping():
    print("ping")

Three layers: repeat(3) returns decorator, which returns wrapper.""",
            mcq("What does functools.wraps(func) preserve?", ["The name and docstring of func", "The speed of func", "The arguments of func", "Nothing"], 0),
            mcq("How many nested functions does @repeat(3) need?", ["Three: repeat, decorator, wrapper", "One", "Two", "Four"], 0),
            fill("Apply the decorator with an argument.", "___repeat(2)\ndef hi(): ...", "@"),
            run("Write a decorator factory repeat(times) so a decorated function runs times times. The program decorates a function that prints 'hey'.", "python",
                [t("three", append="@repeat(3)\ndef hey():\n    print('hey')\nhey()"), t("once", append="@repeat(1)\ndef hey():\n    print('hey')\nhey()"), t("name kept", append="@repeat(2)\ndef greet():\n    pass\nprint(greet.__name__)")],
                ["hey\nhey\nhey", "hey", "greet"],
                "from functools import wraps\n\ndef repeat(times):\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            result = None\n            for _ in range(times):\n                result = func(*args, **kwargs)\n            return result\n        return wrapper\n    return decorator",
                starter="from functools import wraps\n\ndef repeat(times):\n    pass\n", require=[r"wraps"]),
        ),
        lesson(
            "Context managers",
            """with guarantees cleanup, even if an error happens inside. Anything with __enter__ and __exit__ works:

class Tag:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print("<" + self.name + ">")
        return self
    def __exit__(self, exc_type, exc, tb):
        print("</" + self.name + ">")

with Tag("p"):
    print("text")        # <p> / text / </p>

contextlib.contextmanager builds one from a generator with a single yield.""",
            mcq("When does __exit__ run?", ["When the with block ends, even after an error", "Only after an error", "Before __enter__", "Never"], 0),
            mcq("Which statement is the safe way to open a file?", ["with open(path) as f:", "f = open(path)", "open(path).close", "import open"], 0),
            fill("Use the context manager.", "___ Tag('b'):", "with"),
            run("Write a context manager class Box with __enter__ printing 'open' and __exit__ printing 'close'. The program uses it around a print.", "python",
                [t("normal", append="with Box():\n    print('inside')"), t("with error", append="try:\n    with Box():\n        raise ValueError\nexcept ValueError:\n    print('caught')")],
                ["open\ninside\nclose", "open\nclose\ncaught"],
                "class Box:\n    def __enter__(self):\n        print('open')\n        return self\n    def __exit__(self, exc_type, exc, tb):\n        print('close')\n        return False",
                starter="class Box:\n    pass\n", require=[r"__enter__", r"__exit__"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Classes in depth",
        lesson(
            "Dunder methods",
            """Special methods with double underscores let your objects work with Python's syntax:

class Vec:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)
    def __repr__(self):
        return f"Vec({self.x}, {self.y})"
    def __len__(self):
        return 2

print(Vec(1, 2) + Vec(3, 4))      # Vec(4, 6)

__repr__ is what print/REPL show; __eq__, __lt__, __getitem__, __iter__, __contains__ work the same way.""",
            mcq("Which method runs for a + b?", ["__add__", "__plus__", "__sum__", "__concat__"], 0),
            mcq("What does print(obj) use when __str__ is missing?", ["__repr__", "__init__", "__name__", "Nothing"], 0),
            mcq("Which method makes len(obj) work?", ["__len__", "__size__", "__count__", "__length__"], 0),
            run("Write a class Money(cents) where Money(150) + Money(275) is Money(425) and printing a Money shows $4.25 (use __add__ and __str__).", "python",
                [t("add", append="print(Money(150) + Money(275))"), t("zero cents", append="print(Money(500))"), t("pad", append="print(Money(5))")],
                ["$4.25", "$5.00", "$0.05"],
                "class Money:\n    def __init__(self, cents):\n        self.cents = cents\n    def __add__(self, other):\n        return Money(self.cents + other.cents)\n    def __str__(self):\n        return f'${self.cents // 100}.{self.cents % 100:02d}'",
                starter="class Money:\n    def __init__(self, cents):\n        self.cents = cents\n", require=[r"__add__", r"__str__"]),
        ),
        lesson(
            "Properties",
            """@property turns a method into an attribute you can read like data - perfect for computed values and validation:

class Circle:
    def __init__(self, r):
        self._r = r
    @property
    def area(self):
        return 3.14 * self._r ** 2
    @property
    def r(self):
        return self._r
    @r.setter
    def r(self, value):
        if value < 0:
            raise ValueError("negative")
        self._r = value

c = Circle(2)
c.area        # no parentheses""",
            mcq("How do you read a property?", ["obj.area (no parentheses)", "obj.area()", "obj.get_area", "obj['area']"], 0),
            mcq("What does a @x.setter allow?", ["Validating assignments like obj.x = 5", "Making x private", "Deleting x", "Calling x"], 0),
            mcq("Why use a leading underscore like self._r?", ["It signals 'internal, don't touch'", "Python hides it", "It makes it faster", "It is required"], 0),
            run("Write a class Temp(celsius) with a property fahrenheit returning celsius * 9 / 5 + 32.", "python",
                [t("boiling", append="print(Temp(100).fahrenheit)"), t("freezing", append="print(Temp(0).fahrenheit)"), t("negative", append="print(Temp(-40).fahrenheit)")],
                ["212.0", "32.0", "-40.0"], "class Temp:\n    def __init__(self, celsius):\n        self.celsius = celsius\n    @property\n    def fahrenheit(self):\n        return self.celsius * 9 / 5 + 32",
                starter="class Temp:\n    def __init__(self, celsius):\n        self.celsius = celsius\n", require=[r"@property"]),
        ),
        lesson(
            "Dataclasses",
            """@dataclass writes __init__, __repr__ and __eq__ for you:

from dataclasses import dataclass, field

@dataclass
class Item:
    name: str
    price: float = 0.0
    tags: list = field(default_factory=list)

Item("pen", 1.5)
# Item(name='pen', price=1.5, tags=[])

Use field(default_factory=list) for mutable defaults. frozen=True makes instances immutable, and order=True adds comparisons.""",
            mcq("Which methods does @dataclass generate automatically?", ["__init__, __repr__, __eq__", "__add__ only", "__len__", "None"], 0),
            mcq("How do you give a dataclass field an empty list default?", ["field(default_factory=list)", "= []", "= list", "= None only"], 0),
            mcq("What does frozen=True do?", ["Makes instances immutable", "Makes them faster", "Hides fields", "Adds sorting"], 0),
            run("Make a dataclass Point with int fields x and y (y defaults to 0). Print two Points and compare them.", "python",
                [t("repr", append="print(Point(1, 2))"), t("default", append="print(Point(5))"), t("equal", append="print(Point(1, 2) == Point(1, 2), Point(1, 2) == Point(2, 1))")],
                ["Point(x=1, y=2)", "Point(x=5, y=0)", "True False"],
                "from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: int\n    y: int = 0",
                starter="from dataclasses import dataclass\n\n", require=[r"@dataclass"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Inheritance & design",
        lesson(
            "Inheritance & super()",
            """A subclass reuses and extends a parent class. super() calls the parent's version:

class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."

class Dog(Animal):
    def __init__(self, name, tricks):
        super().__init__(name)
        self.tricks = tricks
    def speak(self):
        return "Woof"

Dog overrides speak(); isinstance(d, Animal) is True because a Dog IS an Animal.""",
            mcq("What does super().__init__(name) do?", ["Runs the parent's __init__", "Creates a new class", "Deletes the parent", "Imports Animal"], 0),
            mcq("What does isinstance(Dog('Rex', []), Animal) return?", ["True", "False", "None", "An error"], 0),
            mcq("What is overriding?", ["A subclass redefining a parent's method", "Calling two methods", "Deleting a method", "Copying a class"], 0),
            run("Write Shape with area() returning 0, and Square(side) that inherits from it and overrides area(). Call both.", "python",
                [t("square", append="print(Square(4).area())"), t("shape", append="print(Shape().area())"), t("isinstance", append="print(isinstance(Square(1), Shape))")],
                ["16", "0", "True"], "class Shape:\n    def area(self):\n        return 0\n\nclass Square(Shape):\n    def __init__(self, side):\n        self.side = side\n    def area(self):\n        return self.side ** 2",
                starter="class Shape:\n    pass\n\nclass Square(Shape):\n    pass\n", require=[r"class\s+Square\s*\(\s*Shape\s*\)"]),
        ),
        lesson(
            "Polymorphism & duck typing",
            """'If it walks like a duck…' - Python cares about what an object CAN DO, not its class. Any object with the right method works:

class Cat:
    def speak(self): return "Meow"
class Robot:
    def speak(self): return "Beep"

for thing in [Cat(), Robot()]:
    print(thing.speak())

No shared parent is needed. This keeps code flexible: write functions that call methods, not functions that check types.""",
            mcq("What is duck typing?", ["Using an object if it has the needed methods", "A kind of loop", "A way to import", "Checking types strictly"], 0),
            mcq("Which is the more 'Pythonic' habit?", ["Call the method and let it work", "Check the class with a long if/elif first", "Convert everything to str", "Avoid methods"], 0),
            mcq("Two unrelated classes both define area(). Can one function call .area() on either?", ["Yes", "No", "Only with a shared parent", "Only for numbers"], 0),
            run("Write a function describe(items) that prints speak() of every item. The program defines Cat (Meow) and Dog (Woof) with no shared parent.", "python",
                [t("both", append="class Cat:\n    def speak(self):\n        return 'Meow'\nclass Dog:\n    def speak(self):\n        return 'Woof'\ndescribe([Cat(), Dog(), Cat()])")],
                ["Meow\nWoof\nMeow"], "def describe(items):\n    for item in items:\n        print(item.speak())",
                starter="def describe(items):\n    pass\n"),
        ),
        lesson(
            "Class & static methods, composition",
            """@classmethod receives the class (cls) - handy for alternative constructors. @staticmethod receives nothing special; it's just a function grouped with the class.

class User:
    count = 0
    def __init__(self, name):
        self.name = name
        User.count += 1
    @classmethod
    def from_email(cls, email):
        return cls(email.split("@")[0])
    @staticmethod
    def valid(name):
        return len(name) > 1

Prefer composition ('has a') over inheritance ('is a') when objects merely USE each other: a Car has an Engine.""",
            mcq("What does a classmethod receive as its first argument?", ["cls (the class)", "self", "Nothing", "The module"], 0),
            mcq("When is composition better than inheritance?", ["When one object merely uses another ('has a')", "Never", "When classes are identical", "When using dataclasses"], 0),
            fill("Mark an alternative constructor.", "___\ndef from_text(cls, text):", "@classmethod"),
            run("Write a class Person(name) with a classmethod from_full(text) that takes 'First Last' and creates Person(First).", "python",
                [t("first", append="print(Person.from_full('Ada Lovelace').name)"), t("another", append="print(Person.from_full('Bo Peep').name)")],
                ["Ada", "Bo"], "class Person:\n    def __init__(self, name):\n        self.name = name\n    @classmethod\n    def from_full(cls, text):\n        return cls(text.split()[0])",
                starter="class Person:\n    def __init__(self, name):\n        self.name = name\n", require=[r"@classmethod"]),
        ),
    ),
)
