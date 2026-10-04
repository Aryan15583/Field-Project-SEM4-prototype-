"""JavaScript - Expert section, part 1 (units 17-22): functional patterns, iterators, objects, classes, text, errors."""
from .dsl import fill, lesson, mcq, order, run, section, t, unit


def log(expr: str) -> dict:
    return t(expr, append=f"console.log({expr});")


def js(expr: str) -> dict:
    """A test that prints the JSON form of an expression (stable for arrays and objects)."""
    return t(expr, append=f"console.log(JSON.stringify({expr}));")


EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Functional patterns",
        lesson(
            "Currying & composition",
            """Currying turns f(a, b) into f(a)(b). Composition chains small functions into one:

const add = (a) => (b) => a + b;
add(2)(3);                         // 5
const add10 = add(10);             // a reusable function

const compose = (...fns) => (x) => fns.reduceRight((acc, fn) => fn(acc), x);
const pipe    = (...fns) => (x) => fns.reduce((acc, fn) => fn(acc), x);

pipe(trim, upper, exclaim)(" hi ")     // reads left to right

Small single-purpose functions are easy to test and reuse.""",
            mcq("What does add(2)(3) return for const add = (a) => (b) => a + b?", ["5", "a function", "23", "undefined"], 0),
            mcq("In pipe(f, g)(x), which runs first?", ["f", "g", "Both at once", "Neither"], 0),
            mcq("What is the main benefit of currying?", ["Pre-filling arguments to make new functions", "Faster loops", "Avoiding variables", "Async code"], 0),
            fill("Pass the accumulated value through each function in turn.", "const pipe = (...fns) => (x) => fns.___((acc, fn) => fn(acc), x);", "reduce"),
            run("Write pipe(...fns) that returns a function applying fns to its argument left to right.", "javascript",
                [log("pipe((x) => x + 1, (x) => x * 2)(5)"), log("pipe((s) => s.trim(), (s) => s.toUpperCase())('  hi ')"), log("pipe()(7)")],
                ["12", "HI", "7"], "const pipe = (...fns) => (x) => fns.reduce((acc, fn) => fn(acc), x);",
                require=[r"reduce"]),
        ),
        lesson(
            "Memoization",
            """Cache the result of a pure function so the same input is never computed twice:

function memoize(fn) {
  const cache = new Map();
  return (arg) => {
    if (!cache.has(arg)) cache.set(arg, fn(arg));
    return cache.get(arg);
  };
}

Use cache.has(), not a truthiness check - a cached result might legitimately be 0 or "". Only memoize PURE functions (same input -> same output, no side effects).""",
            mcq("Why use cache.has(arg) instead of if (cache.get(arg))?", ["A cached result may be falsy, like 0", "has is faster", "get is deprecated", "Maps can't be falsy"], 0),
            mcq("Which functions are safe to memoize?", ["Pure functions", "Ones reading the clock", "Ones using random", "Ones sending requests"], 0),
            mcq("What data structure is a good cache here?", ["Map", "Array", "Set of strings", "String"], 0),
            run("Write memoize(fn) for single-argument functions. The test counts how many times the wrapped function really runs.", "javascript",
                [t("counts", append="let calls = 0;\nconst slow = memoize((n) => { calls++; return n * n; });\nconsole.log(slow(4), slow(4), slow(5), calls);"),
                 t("falsy result", append="let c = 0;\nconst z = memoize(() => { c++; return 0; });\nz(1); z(1); z(1);\nconsole.log(c);")],
                ["16 16 25 2", "1"],
                "function memoize(fn) {\n  const cache = new Map();\n  return (arg) => {\n    if (!cache.has(arg)) cache.set(arg, fn(arg));\n    return cache.get(arg);\n  };\n}",
                require=[r"\.has\("]),
        ),
        lesson(
            "Immutable updates",
            """Instead of changing data in place, build a new copy. This avoids surprising bugs and is how React and Redux work.

const user = { name: "Ada", tags: ["a"] };
const renamed = { ...user, name: "Bo" };            // new object
const moreTags = { ...user, tags: [...user.tags, "b"] };   // copy the array too
const without = user.tags.filter((t) => t !== "a");

Spread is a SHALLOW copy: nested objects are still shared. structuredClone(obj) makes a deep copy. Object.freeze stops changes (shallowly).""",
            mcq("What does { ...user, name: 'Bo' } do?", ["Makes a new object with name replaced", "Changes user", "Deletes user", "Makes user frozen"], 0),
            mcq("Is a spread copy deep or shallow?", ["Shallow", "Deep", "Both", "Neither"], 0),
            mcq("Which makes a DEEP copy?", ["structuredClone(obj)", "{ ...obj }", "Object.assign({}, obj)", "obj.slice()"], 0),
            run("Write addTag(user, tag) that returns a NEW user with the tag appended to tags, leaving the original unchanged.", "javascript",
                [t("new copy", append='const u = { name: "Ada", tags: ["a"] };\nconst v = addTag(u, "b");\nconsole.log(JSON.stringify(v), JSON.stringify(u), u === v);'),
                 t("no tags yet", append='console.log(JSON.stringify(addTag({ name: "Bo", tags: [] }, "x")));')],
                ['{"name":"Ada","tags":["a","b"]} {"name":"Ada","tags":["a"]} false', '{"name":"Bo","tags":["x"]}'],
                "function addTag(user, tag) {\n  return { ...user, tags: [...user.tags, tag] };\n}", require=[r"\.\.\."], forbid=[r"\.push\("]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Iterators & generators",
        lesson(
            "Iterables and for...of",
            """for...of works on anything iterable: arrays, strings, Maps, Sets. Under the hood the object has a [Symbol.iterator]() method returning an object with next():

const it = [10, 20][Symbol.iterator]();
it.next();   // { value: 10, done: false }
it.next();   // { value: 20, done: false }
it.next();   // { value: undefined, done: true }

You can make your own objects iterable by giving them a [Symbol.iterator] method. Spread (...), destructuring and Array.from all use it.""",
            mcq("What does it.next() return when finished?", ["{ value: undefined, done: true }", "null", "undefined", "An error"], 0),
            mcq("Which can for...of loop over?", ["Arrays, strings, Maps and Sets", "Only arrays", "Only objects", "Only numbers"], 0),
            mcq("What does an object need to be iterable?", ["A [Symbol.iterator]() method", "A length", "To be an array", "A next property only"], 0),
            run("Create an object range(start, end) that is iterable (a [Symbol.iterator] method) yielding start, start+1, ... end-1. The test spreads it into an array.", "javascript",
                [js("[...range(1, 5)]"), js("[...range(3, 3)]"), t("for of", append="let s = 0;\nfor (const n of range(0, 4)) s += n;\nconsole.log(s);")],
                ["[1,2,3,4]", "[]", "6"],
                "function range(start, end) {\n  return {\n    [Symbol.iterator]() {\n      let n = start;\n      return { next: () => (n < end ? { value: n++, done: false } : { value: undefined, done: true }) };\n    },\n  };\n}",
                require=[r"Symbol\.iterator"]),
        ),
        lesson(
            "Generator functions",
            """function* creates a generator: yield produces a value and pauses.

function* count(from) {
  let n = from;
  while (true) yield n++;      // infinite, but lazy
}

const g = count(5);
g.next().value;   // 5
g.next().value;   // 6

yield* delegates to another iterable. Generators are iterable, so [...gen] and for...of work on them. Combine with a take() helper to use infinite sequences safely.""",
            mcq("What does function* create?", ["A generator function", "A pointer", "A class", "An async function"], 0),
            mcq("Why can count() above be infinite safely?", ["Values are produced lazily, one per next()", "JS stops at 1000", "It isn't really infinite", "Memory is unlimited"], 0),
            fill("Produce a value and pause.", "function* f() { ___ 1; }", "yield"),
            run("Write a generator fibonacci() that yields 0, 1, 1, 2, 3, 5, ... forever, and a function take(n, iterable) returning the first n values as an array.", "javascript",
                [js("take(8, fibonacci())"), js("take(0, fibonacci())"), js("take(3, [9, 8, 7, 6])")],
                ["[0,1,1,2,3,5,8,13]", "[]", "[9,8,7]"],
                "function* fibonacci() {\n  let [a, b] = [0, 1];\n  while (true) {\n    yield a;\n    [a, b] = [b, a + b];\n  }\n}\nfunction take(n, iterable) {\n  const out = [];\n  if (n <= 0) return out;\n  for (const x of iterable) {\n    out.push(x);\n    if (out.length === n) break;\n  }\n  return out;\n}",
                require=[r"function\s*\*", r"\byield\b"]),
        ),
        lesson(
            "Lazy pipelines",
            """Chaining generators builds a lazy pipeline: no step creates a full array, and work stops as soon as the consumer stops asking.

function* map(it, fn)    { for (const x of it) yield fn(x); }
function* filter(it, fn) { for (const x of it) if (fn(x)) yield x; }

const firstSquares = take(3, filter(map(naturals(), (n) => n * n), (n) => n % 2 === 1));

Compare with arrays: [...bigRange].map().filter() builds two huge arrays first. Lazy pipelines handle huge or infinite data.""",
            mcq("What is the advantage of a lazy pipeline?", ["Little memory, stops early", "It is shorter", "It sorts", "It is async"], 0),
            mcq("When does a generator run its body?", ["When the consumer asks for the next value", "At creation", "Never", "When imported"], 0),
            mcq("Which can process an infinite sequence?", ["Generators with take()", "Array.map", "Array.filter", "forEach"], 0),
            run("Write lazy helpers map(iterable, fn) and filter(iterable, fn) as generators, and use them: print the first 3 even squares of the natural numbers 1, 2, 3, ... (finish with a loop that breaks).", "javascript",
                [t("pipeline", append="function* naturals() { let n = 1; while (true) yield n++; }\nconst out = [];\nfor (const v of filter(map(naturals(), (n) => n * n), (n) => n % 2 === 0)) {\n  out.push(v);\n  if (out.length === 3) break;\n}\nconsole.log(out.join(' '));"),
                 t("only some", append="console.log([...map(filter([1, 2, 3, 4], (n) => n > 2), (n) => n * 10)].join(' '));")],
                ["4 16 36", "30 40"],
                "function* map(iterable, fn) {\n  for (const x of iterable) yield fn(x);\n}\nfunction* filter(iterable, fn) {\n  for (const x of iterable) if (fn(x)) yield x;\n}",
                require=[r"function\s*\*"]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Objects in depth",
        lesson(
            "Object utilities",
            """Turn objects into arrays and back:

const o = { a: 1, b: 2 };
Object.keys(o);        // ['a', 'b']
Object.values(o);      // [1, 2]
Object.entries(o);     // [['a', 1], ['b', 2]]
Object.fromEntries([["x", 1], ["y", 2]]);   // { x: 1, y: 2 }

Round-tripping through entries lets you use array methods on objects:

Object.fromEntries(Object.entries(prices).map(([k, v]) => [k, v * 2]));

Object.groupBy(items, fn) groups items by a key.""",
            mcq("What does Object.entries({ a: 1 }) return?", ["[['a', 1]]", "['a']", "[1]", "{ a: 1 }"], 0),
            mcq("Which turns [['x', 1]] back into an object?", ["Object.fromEntries", "Object.assign", "Object.keys", "Object.create"], 0),
            fill("Get just the values.", "Object.___(prices)", "values"),
            run("Write mapValues(obj, fn) returning a new object with the same keys and each value passed through fn.", "javascript",
                [js("mapValues({ a: 1, b: 2 }, (v) => v * 10)"), js("mapValues({}, (v) => v)"), js('mapValues({ x: "hi" }, (v) => v.toUpperCase())')],
                ['{"a":10,"b":20}', "{}", '{"x":"HI"}'],
                "function mapValues(obj, fn) {\n  return Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, fn(v)]));\n}",
                require=[r"Object\.entries|Object\.keys"]),
        ),
        lesson(
            "Grouping and counting",
            """A common job: group items or count them by a key.

const counts = {};
for (const w of words) counts[w] = (counts[w] ?? 0) + 1;

const groups = {};
for (const w of words) (groups[w.length] ??= []).push(w);

??= assigns only if the left side is null or undefined. Object.groupBy(words, w => w.length) does grouping in one call (Node 21+). Maps handle non-string keys.""",
            mcq("What does a ??= b do?", ["Assigns b only if a is null/undefined", "Always assigns", "Compares", "Throws"], 0),
            mcq("Which makes a counter from words?", ["counts[w] = (counts[w] ?? 0) + 1", "counts[w]++ always", "counts.push(w)", "counts = w"], 0),
            mcq("(groups[k] ??= []).push(x) does what?", ["Creates the array if missing, then pushes", "Always replaces the array", "Fails if missing", "Sorts"], 0),
            run("Write groupByLength(words) returning an object whose keys are word lengths and values are arrays of the words (in input order).", "javascript",
                [js('groupByLength(["a", "bb", "cc", "d"])'), js("groupByLength([])"), js('groupByLength(["xyz"])')],
                ['{"1":["a","d"],"2":["bb","cc"]}', "{}", '{"3":["xyz"]}'],
                "function groupByLength(words) {\n  const groups = {};\n  for (const w of words) (groups[w.length] ??= []).push(w);\n  return groups;\n}"),
        ),
        lesson(
            "Property descriptors, getters & Symbols",
            """Every property has settings. Object.defineProperty controls them:

const o = {};
Object.defineProperty(o, "id", { value: 7, writable: false, enumerable: false });
o.id = 9;        // silently ignored (throws in strict mode)

Getters compute a value when read; Symbols make unique keys that never clash:

const total = { items: [1, 2], get sum() { return this.items.reduce((a, b) => a + b, 0); } };
const secret = Symbol("secret");
const obj = { [secret]: 1, visible: 2 };
Object.keys(obj);     // ['visible'] - symbol keys are hidden from keys()""",
            mcq("What does writable: false do?", ["Prevents assigning a new value", "Hides the property", "Deletes it", "Makes it a getter"], 0),
            mcq("Does Object.keys() list Symbol keys?", ["No", "Yes", "Only for arrays", "Only in strict mode"], 0),
            mcq("When does a getter run?", ["Each time the property is read", "Once at creation", "Never", "When written"], 0),
            run("Create an object makeRect(w, h) with a getter area (w * h) and a getter perimeter (2 * (w + h)) that update when w or h change.", "javascript",
                [t("initial", append="const r = makeRect(3, 4);\nconsole.log(r.area, r.perimeter);"), t("updates", append="const r = makeRect(2, 2);\nr.w = 10;\nconsole.log(r.area, r.perimeter);")],
                ["12 14", "20 24"],
                "function makeRect(w, h) {\n  return {\n    w,\n    h,\n    get area() { return this.w * this.h; },\n    get perimeter() { return 2 * (this.w + this.h); },\n  };\n}",
                require=[r"\bget\s+area"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Classes in depth",
        lesson(
            "Private fields & static members",
            """Fields starting with # are truly private - only code inside the class can touch them:

class Counter {
  #count = 0;
  static created = 0;
  constructor() { Counter.created++; }
  increment() { return ++this.#count; }
  get value() { return this.#count; }
}

new Counter().#count      // SyntaxError

static members belong to the class itself, not instances (Counter.created). This keeps internal state safe from accidental outside changes.""",
            mcq("Who can read a #private field?", ["Only code inside the class", "Anyone", "Subclasses only", "The module"], 0),
            mcq("What is a static member?", ["Belongs to the class, not instances", "A constant", "A private field", "An async method"], 0),
            fill("Declare a private field.", "class A { ___secret = 1; }", "#"),
            run("Write class BankAccount with a private #balance, deposit(n), withdraw(n) (ignore a withdrawal larger than the balance by returning false, otherwise true) and a getter balance.", "javascript",
                [t("flow", append="const a = new BankAccount();\na.deposit(100);\nconsole.log(a.withdraw(30), a.withdraw(100), a.balance);"), t("private", append="const b = new BankAccount();\nconsole.log(b.balance, b['#balance']);")],
                ["true false 70", "0 undefined"],
                "class BankAccount {\n  #balance = 0;\n  deposit(n) {\n    this.#balance += n;\n  }\n  withdraw(n) {\n    if (n > this.#balance) return false;\n    this.#balance -= n;\n    return true;\n  }\n  get balance() {\n    return this.#balance;\n  }\n}",
                require=[r"#balance"]),
        ),
        lesson(
            "Inheritance & super",
            """extends builds a subclass; super() calls the parent constructor (required before using this) and super.method() calls the parent's version:

class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound`; }
}
class Dog extends Animal {
  speak() { return super.speak() + " - Woof"; }
}

new Dog("Rex").speak();   // 'Rex makes a sound - Woof'""",
            mcq("What must a subclass constructor call before using this?", ["super()", "this()", "parent()", "new Parent()"], 0),
            mcq("What does super.speak() call?", ["The parent's speak", "A static method", "The child's speak", "A global"], 0),
            mcq("What does instanceof check?", ["The prototype chain", "The name", "The type string", "The constructor args"], 0),
            run("Write class Shape with area() returning 0 and describe() returning `${this.constructor.name}: ${this.area()}`; then class Circle (r) and Rect (w, h) extending it.", "javascript",
                [log("new Circle(1).describe().slice(0, 10)"), log("new Rect(2, 5).describe()"), log("new Shape().describe()")],
                ["Circle: 3.", "Rect: 10", "Shape: 0"],
                "class Shape {\n  area() { return 0; }\n  describe() { return `${this.constructor.name}: ${this.area()}`; }\n}\nclass Circle extends Shape {\n  constructor(r) { super(); this.r = r; }\n  area() { return Math.PI * this.r ** 2; }\n}\nclass Rect extends Shape {\n  constructor(w, h) { super(); this.w = w; this.h = h; }\n  area() { return this.w * this.h; }\n}",
                require=[r"extends\s+Shape"]),
        ),
        lesson(
            "Mixins & composition",
            """JavaScript has single inheritance. To share behaviour across unrelated classes, use a mixin - a function that takes a class and returns an extended one:

const Serializable = (Base) => class extends Base {
  toJSON() { return { type: this.constructor.name, ...this }; }
};

class User extends Serializable(Object) {}

Often plain composition is simpler: give an object the pieces it needs (a logger, a store) instead of making it inherit them.""",
            mcq("What is a mixin?", ["A function that adds behaviour to a class", "A kind of loop", "A module", "A promise"], 0),
            mcq("Can a JS class extend two parents?", ["No - single inheritance only", "Yes", "Only with mixins as parents", "Only in strict mode"], 0),
            mcq("Prefer composition when…", ["One object merely uses another", "Classes are identical", "You need static fields", "You write async code"], 0),
            run("Write a mixin Walker(Base) that adds a walk() method returning `${this.name} walks`. Apply it to class Person (constructor(name)).", "javascript",
                [t("works", append="class Person { constructor(name) { this.name = name; } }\nclass Walking extends Walker(Person) {}\nconsole.log(new Walking('Ada').walk());"),
                 t("other base", append="class Robot { constructor() { this.name = 'R2'; } }\nconsole.log(new (Walker(Robot))().walk());")],
                ["Ada walks", "R2 walks"],
                "const Walker = (Base) => class extends Base {\n  walk() {\n    return `${this.name} walks`;\n  }\n};",
                require=[r"class\s+extends\s+Base|extends\s+Base"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Text, regex & formatting",
        lesson(
            "Regex in JavaScript",
            """Regex literals sit between slashes; flags follow: g (all matches), i (ignore case), m (multiline).

/\\d+/.test("a12")                    // true
"a1b22".match(/\\d+/g)                 // ['1', '22']
"2024-05-09".match(/(?<y>\\d{4})-(?<m>\\d\\d)/).groups.y   // '2024'
[..."a1b22".matchAll(/\\d+/g)].map((m) => m[0])        // ['1', '22']

replace with a function lets you compute each replacement:

"a1 b2".replace(/\\d/g, (d) => d * 2)   // 'a2 b4'""",
            mcq("What does the g flag do?", ["Finds all matches, not just the first", "Ignores case", "Makes it greedy", "Groups"], 0),
            mcq("What does 'a1b22'.match(/\\d+/g) return?", ["['1', '22']", "'1'", "[1, 22]", "['a', 'b']"], 0),
            fill("Test whether the string contains a digit.", "/\\d/.___(text)", "test"),
            run("Write extractNumbers(text) returning an array of all whole numbers in the text as numbers (negative sign included).", "javascript",
                [js('extractNumbers("a 12, b -5 and 300")'), js('extractNumbers("none here")'), js('extractNumbers("x7y8")')],
                ["[12,-5,300]", "[]", "[7,8]"],
                "function extractNumbers(text) {\n  return (text.match(/-?\\d+/g) ?? []).map(Number);\n}", require=[r"match|matchAll|exec"]),
        ),
        lesson(
            "replace with callbacks & templates",
            """String.replace with a function gets the match and groups, so you can build a tiny template engine:

const render = (tpl, data) =>
  tpl.replace(/\\{\\{(\\w+)\\}\\}/g, (_, key) => data[key] ?? "");

render("Hi {{name}}!", { name: "Ada" });    // 'Hi Ada!'

replaceAll(str, replacement) replaces every literal occurrence. Case conversion helpers: toUpperCase, toLowerCase, and padStart/padEnd for alignment.""",
            mcq("What does the callback of replace receive?", ["The match, then captured groups", "Only the index", "Nothing", "The whole string"], 0),
            mcq("What does 'x'.padStart(3, '0') give?", ["'00x'", "'x00'", "'x'", "'000'"], 0),
            mcq("Which replaces every literal occurrence?", ["replaceAll", "replaceOne", "swap", "split"], 0),
            run("Write render(template, data) replacing every {{key}} with data[key] (empty string if missing).", "javascript",
                [log('render("Hi {{name}}, you are {{age}}!", { name: "Ada", age: 36 })'), log('render("{{a}}-{{b}}", { a: 1 })'), log('render("no tags", {})')],
                ["Hi Ada, you are 36!", "1-", "no tags"],
                "function render(template, data) {\n  return template.replace(/\\{\\{(\\w+)\\}\\}/g, (_, key) => data[key] ?? \"\");\n}",
                require=[r"replace"]),
        ),
        lesson(
            "Intl, dates & number formatting",
            """The Intl API formats numbers and dates for any locale. Always pass an explicit locale so results are predictable:

new Intl.NumberFormat("en-US").format(1234567.891)     // '1,234,567.891'
new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(5)   // '$5.00'
(0.256).toFixed(1)                                     // '0.3'

Dates: use UTC methods to avoid time-zone surprises.

const d = new Date(Date.UTC(2024, 0, 31));    // months start at 0!
d.toISOString().slice(0, 10)                   // '2024-01-31'""",
            mcq("What is the month number for January in new Date(y, m, d)?", ["0", "1", "12", "-1"], 0),
            mcq("What does (3.14159).toFixed(2) return?", ["'3.14'", "3.14", "3", "'3.1'"], 0),
            mcq("Why pass 'en-US' to Intl.NumberFormat explicitly?", ["So the result doesn't depend on the user's settings", "It's required", "It's faster", "It adds symbols"], 0),
            run("Write addDays(isoDate, n) taking 'YYYY-MM-DD' and returning the date n days later in the same format (use UTC).", "javascript",
                [log('addDays("2024-02-28", 2)'), log('addDays("2024-12-31", 1)'), log('addDays("2024-03-01", -1)')],
                ["2024-03-01", "2025-01-01", "2024-02-29"],
                "function addDays(isoDate, n) {\n  const d = new Date(isoDate + 'T00:00:00Z');\n  d.setUTCDate(d.getUTCDate() + n);\n  return d.toISOString().slice(0, 10);\n}",
                require=[r"Date"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Errors & defensive code",
        lesson(
            "Custom errors",
            """Subclass Error to make errors you can tell apart:

class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

try {
  throw new ValidationError("too short", "password");
} catch (e) {
  if (e instanceof ValidationError) console.log(e.field);
  else throw e;           // not ours - rethrow
}""",
            mcq("What does 'throw e' in the else branch do?", ["Passes an unknown error up", "Ignores it", "Logs it", "Ends the program silently"], 0),
            mcq("How do you check which error type was caught?", ["e instanceof MyError", "typeof e", "e == MyError", "e.type"], 0),
            mcq("Which line must a custom Error constructor call first?", ["super(message)", "this.name", "throw", "return"], 0),
            run("Write class ValidationError extends Error and validateAge(n) that throws it (message 'invalid age') unless n is an integer from 0 to 150. The test prints OK or the message.", "javascript",
                [t("ok", append="try { validateAge(30); console.log('OK'); } catch (e) { console.log(e.message); }"), t("negative", append="try { validateAge(-1); console.log('OK'); } catch (e) { console.log(e.name + ': ' + e.message); }"), t("float", append="try { validateAge(2.5); console.log('OK'); } catch (e) { console.log(e instanceof ValidationError); }")],
                ["OK", "ValidationError: invalid age", "true"],
                "class ValidationError extends Error {\n  constructor(message) {\n    super(message);\n    this.name = 'ValidationError';\n  }\n}\nfunction validateAge(n) {\n  if (!Number.isInteger(n) || n < 0 || n > 150) throw new ValidationError('invalid age');\n}",
                require=[r"extends\s+Error"]),
        ),
        lesson(
            "Safe JSON & parsing input",
            """Data from outside (users, networks) can be anything. JSON.parse throws on bad text, so wrap it:

function safeParse(text, fallback = null) {
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

Number("12px") is NaN, parseInt("12px") is 12, Number("") is 0 - know which one you need. Check with Number.isNaN, and validate shapes before using fields.""",
            mcq("What does JSON.parse('{bad') do?", ["Throws SyntaxError", "Returns null", "Returns {}", "Returns undefined"], 0),
            mcq("What is Number('12px')?", ["NaN", "12", "0", "undefined"], 0),
            mcq("What does parseInt('12px') return?", ["12", "NaN", "0", "'12'"], 0),
            run("Write safeParse(text, fallback) returning the parsed value or fallback when the text is not valid JSON.", "javascript",
                [js('safeParse(\'{"a":1}\', null)'), js('safeParse("not json", "oops")'), js('safeParse("[1,2]", [])')],
                ['{"a":1}', '"oops"', "[1,2]"], "function safeParse(text, fallback = null) {\n  try {\n    return JSON.parse(text);\n  } catch {\n    return fallback;\n  }\n}",
                require=[r"\btry\b", r"\bcatch\b"]),
        ),
        lesson(
            "Error causes & finally",
            """Wrap low-level errors in a meaningful one and keep the original as the cause:

try {
  JSON.parse(text);
} catch (err) {
  throw new Error("Config is invalid", { cause: err });
}

finally runs whether or not an error happened - ideal for cleanup:

function work() {
  console.log("start");
  try { return "result"; }
  finally { console.log("cleanup"); }   // runs BEFORE the return completes
}""",
            mcq("What is printed by calling work() above?", ["start, cleanup (then returns 'result')", "start only", "cleanup, start", "result"], 0),
            mcq("What is the { cause } option for?", ["Linking the original error", "Hiding errors", "Retrying", "Logging"], 0),
            mcq("When does finally run?", ["Always", "Only on error", "Only on success", "Never"], 0),
            run("Write loadConfig(text) that parses JSON; on failure throws new Error('bad config') with the original error as cause. The test prints the message and whether the cause is a SyntaxError.", "javascript",
                [t("good", append="console.log(JSON.stringify(loadConfig('{\"a\":1}')));"), t("bad", append="try { loadConfig('{oops'); } catch (e) { console.log(e.message, e.cause instanceof SyntaxError); }")],
                ['{"a":1}', "bad config true"],
                "function loadConfig(text) {\n  try {\n    return JSON.parse(text);\n  } catch (err) {\n    throw new Error('bad config', { cause: err });\n  }\n}",
                require=[r"cause"]),
        ),
    ),
)
