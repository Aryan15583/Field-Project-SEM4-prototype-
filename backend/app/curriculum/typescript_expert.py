"""TypeScript - Expert section, part 1 (units 9-15): advanced generics, conditional & template types, narrowing,
typed classes, overloads, modules and error handling. Programs are type-checked in strict mode and then run."""
from .dsl import fill, lesson, mcq, order, run, section, t, unit

REJECTS = "// @ts-expect-error\n"


def log(expr: str, name: str | None = None) -> dict:
    return t(name or expr, append=f"console.log({expr});")


EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 9
    unit(
        "Unit 9 · Advanced generics",
        lesson(
            "Multiple type parameters & defaults",
            """A generic can take several type parameters, and each can have a default:

function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b];
}
pair("x", 1);          // [string, number]

interface Box<T = string> { value: T; }
const b: Box = { value: "hi" };       // T defaults to string

Inference works per parameter: TypeScript works out A and B from the arguments, so you rarely write them by hand.""",
            mcq("What type does pair('x', 1) return?", ["[string, number]", "(string | number)[]", "[any, any]", "string"], 0),
            mcq("What does Box (without <...>) mean when T = string is the default?", ["Box<string>", "Box<any>", "An error", "Box<unknown>"], 0),
            mcq("Who usually supplies A and B?", ["Inference from the arguments", "The runtime", "You, always", "The linter"], 0),
            run("Write swap<A, B>(pair: [A, B]): [B, A] and a function zip<A, B>(as: A[], bs: B[]): [A, B][] that pairs items up to the shorter length.", "typescript",
                [log("swap([1, 'a'])"), log("JSON.stringify(zip([1, 2, 3], ['a', 'b']))", "zip"), t("types", append=REJECTS + "const s: [number, string] = swap([1, 'a']);\nconsole.log('checked');")],
                ["[ 'a', 1 ]", '[[1,"a"],[2,"b"]]', "checked"],
                "function swap<A, B>(pair: [A, B]): [B, A] {\n  return [pair[1], pair[0]];\n}\n\nfunction zip<A, B>(as: A[], bs: B[]): [A, B][] {\n  const n = Math.min(as.length, bs.length);\n  const out: [A, B][] = [];\n  for (let i = 0; i < n; i++) out.push([as[i], bs[i]]);\n  return out;\n}",
                forbid=[r"\bany\b"]),
        ),
        lesson(
            "Constraints with extends and keyof",
            """extends limits what a type parameter can be; keyof T is the union of T's property names:

function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((item) => item[key]);
}

const users = [{ name: "Ada", age: 36 }, { name: "Bo", age: 7 }];
pluck(users, "name");     // string[]
pluck(users, "age");      // number[]
pluck(users, "email");    // error: not a key of the user type

The return type T[K] looks up the property's type - it follows whatever key you pass.""",
            mcq("What does K extends keyof T require?", ["K must be a property name of T", "K must be a string", "K must equal T", "K must be a number"], 0),
            mcq("What is T[K] called?", ["An indexed access type", "A mapped type", "A tuple", "A literal"], 0),
            mcq("What does pluck(users, 'age') return?", ["number[]", "string[]", "any[]", "(string | number)[]"], 0),
            run("Write pluck<T, K extends keyof T>(items: T[], key: K): T[K][]. The test checks values and that a bad key is rejected.", "typescript",
                [t("values", append="const users = [{ name: 'Ada', age: 36 }, { name: 'Bo', age: 7 }];\nconsole.log(pluck(users, 'name').join(','), pluck(users, 'age').join(','));"),
                 t("rejects", append="const users = [{ name: 'Ada' }];\n" + REJECTS + "pluck(users, 'email');\nconsole.log('checked');")],
                ["Ada,Bo 36,7", "checked"], "function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {\n  return items.map((item) => item[key]);\n}",
                require=[r"keyof"], forbid=[r"\bany\b"]),
        ),
        lesson(
            "Generic factories & inference",
            """Generics shine in helpers that build or wrap values:

function createStore<S>(initial: S) {
  let state = initial;
  return {
    get: (): S => state,
    set: (next: S): void => { state = next; },
  };
}
const counter = createStore(0);     // S is inferred as number
counter.set(5);
counter.set("five");                // error

Return types are inferred too, so the object literal above gets a precise type without you writing it.""",
            mcq("How does S become number in createStore(0)?", ["Inferred from the argument", "You must write <number>", "It is any", "From the return"], 0),
            mcq("Why is counter.set('five') an error?", ["S is number", "set is private", "Strings aren't allowed anywhere", "set returns void"], 0),
            mcq("Do you need to annotate the return type of createStore?", ["No - it is inferred", "Yes, always", "Only for generics", "Only in classes"], 0),
            run("Write createStore<S>(initial: S) with get() and set(next: S), plus update(fn: (s: S) => S) that applies fn to the current state.", "typescript",
                [t("flow", append="const s = createStore(1);\ns.update((n) => n + 1);\ns.set(s.get() * 10);\nconsole.log(s.get());"),
                 t("objects", append="const s = createStore({ n: 1 });\ns.update((o) => ({ n: o.n + 5 }));\nconsole.log(s.get().n);"),
                 t("rejects", append="const s = createStore(1);\n" + REJECTS + "s.set('x');\nconsole.log('checked');")],
                ["20", "6", "checked"],
                "function createStore<S>(initial: S) {\n  let state = initial;\n  return {\n    get: (): S => state,\n    set: (next: S): void => {\n      state = next;\n    },\n    update: (fn: (s: S) => S): void => {\n      state = fn(state);\n    },\n  };\n}",
                forbid=[r"\bany\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 10
    unit(
        "Unit 10 · Conditional & template types",
        lesson(
            "Conditional types",
            """A conditional type chooses a type with a test, like a ternary for types:

type IsString<T> = T extends string ? "yes" : "no";
type A = IsString<"hi">;     // "yes"
type B = IsString<42>;       // "no"

It is DISTRIBUTIVE over unions: IsString<string | number> is "yes" | "no". A practical one:

type ElementOf<T> = T extends (infer E)[] ? E : T;
type X = ElementOf<number[]>;   // number""",
            mcq("What is IsString<42>?", ["'no'", "'yes'", "never", "string"], 0),
            mcq("What does 'infer E' do?", ["Captures a type found while matching", "Creates a variable", "Throws", "Loops"], 0),
            mcq("What is ElementOf<boolean[]>?", ["boolean", "boolean[]", "never", "unknown"], 0),
            run("Define type Unwrap<T> that gives U for Promise<U> and T otherwise, and a function id<T>(x: T): Unwrap<T> is NOT needed - just declare variables of those types: a: Unwrap<Promise<string>> = 'hi' and b: Unwrap<number> = 5. Print them.", "typescript",
                [t("run"), t("rejects", append=REJECTS + "const bad: Unwrap<Promise<string>> = 5;\nconsole.log('checked');")],
                ["hi 5", "hi 5\nchecked"],
                "type Unwrap<T> = T extends Promise<infer U> ? U : T;\nconst a: Unwrap<Promise<string>> = 'hi';\nconst b: Unwrap<number> = 5;\nconsole.log(a, b);",
                require=[r"Promise<infer"]),
        ),
        lesson(
            "Mapped types with key remapping",
            """Mapped types build a new object type by looping over keys, and 'as' can rename or filter them:

type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };

interface User { name: string; age: number }
type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number }

type Without<T, U> = { [K in keyof T as Exclude<K, U>]: T[K] };

Modifiers: add or remove readonly and ? with + and -: { -readonly [K in keyof T]-?: T[K] } makes everything writable and required.""",
            mcq("What does 'as' do inside a mapped type?", ["Renames or filters keys", "Casts values", "Adds readonly", "Imports"], 0),
            mcq("What does -readonly do?", ["Removes the readonly modifier", "Adds readonly", "Deletes the key", "Makes it optional"], 0),
            mcq("What does Capitalize<'name'> give?", ["'Name'", "'NAME'", "'name'", "string"], 0),
            run("Define type Mutable<T> = { -readonly [K in keyof T]: T[K] } and use it: a value of type Mutable<Readonly<{ n: number }>> can be reassigned. Print the result after n = 7.", "typescript",
                [t("run")], ["7"],
                "type Mutable<T> = { -readonly [K in keyof T]: T[K] };\nconst o: Mutable<Readonly<{ n: number }>> = { n: 1 };\no.n = 7;\nconsole.log(o.n);",
                require=[r"-readonly"]),
        ),
        lesson(
            "Template literal types",
            """Types can be built from string patterns:

type Event = "click" | "focus";
type Handler = `on${Capitalize<Event>}`;       // "onClick" | "onFocus"
type Px = `${number}px`;
const w: Px = "12px";                           // ok
const bad: Px = "12";                           // error

Combined with unions they generate whole families of valid strings - great for CSS values, event names and route paths.""",
            mcq("What is `on${Capitalize<'click'>}` as a type?", ["'onClick'", "'onclick'", "string", "'on'"], 0),
            mcq("Which value fits the type `${number}px`?", ["'12px'", "'12'", "'px12'", "12"], 0),
            mcq("Why use template literal types?", ["To describe exact string shapes", "To speed up code", "To format output", "To loop"], 0),
            run("Define type Direction = 'up' | 'down' and type Move = `move-${Direction}`. Write describe(m: Move): string returning the text after 'move-'. Calling describe('move-left') must be a type error.", "typescript",
                [log("describe('move-up')"), log("describe('move-down')"), t("rejects", append=REJECTS + "describe('move-left');\nconsole.log('checked');")],
                ["up", "down", "checked"],
                "type Direction = 'up' | 'down';\ntype Move = `move-${Direction}`;\n\nfunction describe(m: Move): string {\n  return m.slice('move-'.length);\n}",
                require=[r"`move-\$\{Direction\}`"]),
        ),
    ),
    # ------------------------------------------------------------------ 11
    unit(
        "Unit 11 · Narrowing in depth",
        lesson(
            "User-defined type guards",
            """A type guard is a function whose return type tells TypeScript what you proved:

function isString(x: unknown): x is string {
  return typeof x === "string";
}
function isUser(x: unknown): x is { name: string } {
  return typeof x === "object" && x !== null && "name" in x && typeof (x as { name: unknown }).name === "string";
}

if (isString(v)) v.toUpperCase();     // inside, v is string

The compiler trusts the guard - so write it carefully: a wrong guard hides real bugs.""",
            mcq("What does 'x is string' mean in a return type?", ["If true, x is a string", "x equals the text 'string'", "It returns a string", "It converts x"], 0),
            mcq("Inside if (isString(v)), what is the type of v?", ["string", "unknown", "any", "never"], 0),
            mcq("What is the danger of a wrong type guard?", ["TypeScript trusts it and hides bugs", "It crashes the compiler", "It is slower", "Nothing"], 0),
            run("Write isNumberArray(x: unknown): x is number[] (an array where every item is a number) and use it in sumAny(x: unknown): number returning the sum, or 0 when x isn't a number array.", "typescript",
                [log("sumAny([1, 2, 3])"), log("sumAny(['a', 1])"), log("sumAny('nope')"), log("sumAny([])")],
                ["6", "0", "0", "0"],
                "function isNumberArray(x: unknown): x is number[] {\n  return Array.isArray(x) && x.every((i) => typeof i === 'number');\n}\n\nfunction sumAny(x: unknown): number {\n  return isNumberArray(x) ? x.reduce((a, b) => a + b, 0) : 0;\n}",
                require=[r"x is number\[\]"], forbid=[r"\bany\b"]),
        ),
        lesson(
            "Exhaustive checks with never",
            """never is the type of values that can't exist. Use it to make the compiler prove you handled every case:

type Shape = { kind: "circle"; r: number } | { kind: "square"; s: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r ** 2;
    case "square": return s.s ** 2;
    default: {
      const _exhaustive: never = s;     // error if a new kind is added and not handled
      return _exhaustive;
    }
  }
}""",
            mcq("What is the type never?", ["A value that can't exist", "null", "undefined", "unknown"], 0),
            mcq("What happens when you add a new Shape kind but forget a case?", ["The 'never' assignment becomes a compile error", "Nothing", "A runtime crash only", "The kind is ignored"], 0),
            mcq("Why is this useful?", ["The compiler finds unhandled cases", "It speeds up switch", "It avoids breaks", "It removes types"], 0),
            run("Given type Light = 'red' | 'yellow' | 'green', write next(l: Light): Light (red->green, green->yellow, yellow->red) using a switch with an exhaustive never check.", "typescript",
                [log("next('red')"), log("next('green')"), log("next('yellow')")],
                ["green", "yellow", "red"],
                "type Light = 'red' | 'yellow' | 'green';\n\nfunction next(l: Light): Light {\n  switch (l) {\n    case 'red':\n      return 'green';\n    case 'green':\n      return 'yellow';\n    case 'yellow':\n      return 'red';\n    default: {\n      const _never: never = l;\n      return _never;\n    }\n  }\n}",
                require=[r"never"]),
        ),
        lesson(
            "The satisfies operator & const assertions",
            """satisfies checks that a value fits a type WITHOUT widening it:

const palette = { red: [255, 0, 0], green: "#0f0" } satisfies Record<string, string | number[]>;
palette.red.map((n) => n / 2);      // still known to be number[]
palette.green.toUpperCase();        // still known to be string

as const freezes literals deeply: const dirs = ["up", "down"] as const; has type readonly ["up", "down"].

typeof dirs[number] then gives "up" | "down".""",
            mcq("What does satisfies do?", ["Checks a value against a type but keeps its precise type", "Casts the value", "Widens the type", "Adds a property"], 0),
            mcq("What is the type of ['a', 'b'] as const?", ["readonly ['a', 'b']", "string[]", "any[]", "('a' | 'b')[]"], 0),
            mcq("How do you get 'up' | 'down' from const dirs = ['up', 'down'] as const?", ["(typeof dirs)[number]", "typeof dirs", "keyof dirs", "dirs[]"], 0),
            run("Create const modes = ['light', 'dark'] as const and type Mode = (typeof modes)[number]. Write isMode(x: string): x is Mode and print isMode('dark') and isMode('blue').", "typescript",
                [t("run")], ["true false"],
                "const modes = ['light', 'dark'] as const;\ntype Mode = (typeof modes)[number];\n\nfunction isMode(x: string): x is Mode {\n  return (modes as readonly string[]).includes(x);\n}\nconsole.log(isMode('dark'), isMode('blue'));",
                require=[r"as const"]),
        ),
    ),
    # ------------------------------------------------------------------ 12
    unit(
        "Unit 12 · Classes & access",
        lesson(
            "Parameter properties & access modifiers",
            """TypeScript can declare and assign fields right in the constructor:

class User {
  constructor(public name: string, private age: number, readonly id: number) {}
  describe() { return `${this.name} (${this.age})`; }
}

public (default) is visible everywhere; private only inside the class; protected inside the class and subclasses; readonly can be set once. These are compile-time checks - for runtime privacy use #field.""",
            mcq("What does 'private age: number' in a constructor do?", ["Declares a private field and assigns it", "Only declares a parameter", "Makes it public", "Makes it static"], 0),
            mcq("Who can access a protected member?", ["The class and its subclasses", "Everyone", "Only the class", "Only instances"], 0),
            mcq("Does TypeScript's 'private' exist at runtime?", ["No, it is a compile-time check", "Yes", "Only in strict mode", "Only for readonly"], 0),
            run("Write class Account(readonly id: number, private balance: number) with deposit(n), withdraw(n) (return false if not enough) and a method getBalance(). Reading acc.balance directly must be a type error.", "typescript",
                [t("flow", append="const a = new Account(1, 100);\na.deposit(50);\nconsole.log(a.withdraw(30), a.withdraw(500), a.getBalance());"), t("rejects", append="const a = new Account(2, 5);\n" + REJECTS + "console.log(a.balance);\nconsole.log('checked');")],
                ["true false 120", "5\nchecked"],
                "class Account {\n  constructor(readonly id: number, private balance: number) {}\n  deposit(n: number): void {\n    this.balance += n;\n  }\n  withdraw(n: number): boolean {\n    if (n > this.balance) return false;\n    this.balance -= n;\n    return true;\n  }\n  getBalance(): number {\n    return this.balance;\n  }\n}",
                require=[r"private\s+balance"]),
        ),
        lesson(
            "Abstract classes & polymorphism",
            """An abstract class can't be instantiated; it defines a contract and shared code for subclasses.

abstract class Shape {
  abstract area(): number;
  describe(): string { return `${this.constructor.name} with area ${this.area().toFixed(1)}`; }
}
class Rect extends Shape {
  constructor(private w: number, private h: number) { super(); }
  area() { return this.w * this.h; }
}

new Shape();   // error: cannot create an instance of an abstract class""",
            mcq("What must a subclass of an abstract class do?", ["Implement its abstract members", "Nothing", "Copy it", "Make them private"], 0),
            mcq("Can you write new Shape() for an abstract class Shape?", ["No", "Yes", "Only inside a method", "Only with as"], 0),
            mcq("Why use abstract classes?", ["Shared behaviour plus a required contract", "Faster code", "Hiding types", "Avoiding interfaces"], 0),
            run("Make abstract class Animal(name) with abstract sound(): string and speak() returning `${name} says ${sound}`. Add Dog (Woof) and Cat (Meow). Creating new Animal('x') must be a type error.", "typescript",
                [log("new Dog('Rex').speak()"), log("new Cat('Tom').speak()"), t("rejects", append=REJECTS + "new Animal('x');\nconsole.log('checked');")],
                ["Rex says Woof", "Tom says Meow", "checked"],
                "abstract class Animal {\n  constructor(protected name: string) {}\n  abstract sound(): string;\n  speak(): string {\n    return `${this.name} says ${this.sound()}`;\n  }\n}\nclass Dog extends Animal {\n  sound(): string {\n    return 'Woof';\n  }\n}\nclass Cat extends Animal {\n  sound(): string {\n    return 'Meow';\n  }\n}",
                require=[r"abstract\s+class"]),
        ),
        lesson(
            "this types & fluent builders",
            """Returning this lets methods chain, and the 'this' return type keeps subclass types:

class QueryBuilder {
  private parts: string[] = [];
  where(c: string): this { this.parts.push(`WHERE ${c}`); return this; }
  limit(n: number): this { this.parts.push(`LIMIT ${n}`); return this; }
  build(): string { return this.parts.join(" "); }
}

new QueryBuilder().where("a = 1").limit(5).build();

A fluent API reads like a sentence and is easy to extend.""",
            mcq("What does a method returning 'this' allow?", ["Chaining calls", "Recursion only", "Static access", "Private access"], 0),
            mcq("Why is the return type 'this' better than the class name?", ["Subclasses keep their own type when chaining", "It is shorter", "It is required", "It is faster"], 0),
            mcq("Which reads like a sentence?", ["builder.where(...).limit(5).build()", "build(where, limit)", "new B(a, b, c)", "B.run"], 0),
            run("Write class Html with tag(name): this, text(s): this and build(): string producing '<name>text</name>' elements one after another.", "typescript",
                [log("new Html().tag('b').text('hi').build()"), log("new Html().tag('p').text('a').tag('i').text('b').build()"), log("new Html().build()")],
                ["<b>hi</b>", "<p>a</p><i>b</i>", ""],
                "class Html {\n  private out: string[] = [];\n  private current = '';\n  tag(name: string): this {\n    this.current = name;\n    return this;\n  }\n  text(s: string): this {\n    this.out.push(`<${this.current}>${s}</${this.current}>`);\n    return this;\n  }\n  build(): string {\n    return this.out.join('');\n  }\n}",
                require=[r":\s*this"]),
        ),
    ),
    # ------------------------------------------------------------------ 13
    unit(
        "Unit 13 · Functions at the type level",
        lesson(
            "Overloads",
            """Overloads give one function several call signatures, with one implementation underneath:

function parse(x: string): number;
function parse(x: number): string;
function parse(x: string | number): string | number {
  return typeof x === "string" ? Number(x) : String(x);
}

parse("5");   // number
parse(5);     // string

Callers only see the overload lines, not the implementation signature.""",
            mcq("Who sees the implementation signature of an overloaded function?", ["Nobody outside - callers see only the overloads", "Everyone", "Only subclasses", "Only tests"], 0),
            mcq("What does parse('5') return in the example?", ["number", "string", "any", "unknown"], 0),
            mcq("Overloads are best when…", ["The return type depends on the argument types", "You want shorter code", "You use classes", "You avoid generics"], 0),
            run("Write overloads for double: double(x: number): number and double(x: string): string (repeat the text twice).", "typescript",
                [log("double(21)"), log("double('ab')"), t("rejects", append=REJECTS + "double(true);\nconsole.log('checked');")],
                ["42", "abab", "checked"],
                "function double(x: number): number;\nfunction double(x: string): string;\nfunction double(x: number | string): number | string {\n  return typeof x === 'number' ? x * 2 : x + x;\n}",
                require=[r"function double\(x: number\): number;"]),
        ),
        lesson(
            "ReturnType, Parameters & friends",
            """Utility types read the shape of existing functions:

function connect(host: string, port: number) { return { host, port, ok: true }; }

type Conn = ReturnType<typeof connect>;      // { host: string; port: number; ok: boolean }
type Args = Parameters<typeof connect>;      // [host: string, port: number]

Awaited<Promise<string>> unwraps a promise. Derive types from code instead of copying them - when the function changes, the derived types follow.""",
            mcq("What does ReturnType<typeof f> give?", ["The type f returns", "The parameter types", "f itself", "void"], 0),
            mcq("What does Parameters<typeof f> give?", ["A tuple of f's parameter types", "The return type", "A union", "never"], 0),
            mcq("Why derive types instead of copying them?", ["They update automatically when the source changes", "It is faster", "It avoids imports", "Copying is invalid"], 0),
            run("Given function makeUser(name: string, age: number) returning { name, age, tags: string[] }, define type User = ReturnType<typeof makeUser> and write printUser(u: User): string returning 'name:age:tags-count'.", "typescript",
                [log("printUser(makeUser('Ada', 36))"), t("rejects", append=REJECTS + "const u: User = { name: 'x' };\nconsole.log('checked');")],
                ["Ada:36:0", "checked"],
                "function makeUser(name: string, age: number) {\n  return { name, age, tags: [] as string[] };\n}\ntype User = ReturnType<typeof makeUser>;\n\nfunction printUser(u: User): string {\n  return `${u.name}:${u.age}:${u.tags.length}`;\n}",
                require=[r"ReturnType"]),
        ),
        lesson(
            "Higher-order generic functions",
            """Generics let helper functions keep full type information:

function compose<A, B, C>(f: (a: A) => B, g: (b: B) => C): (a: A) => C {
  return (a) => g(f(a));
}

const len = compose((s: string) => s.trim(), (s) => s.length);
len(" hi ");     // number

function groupBy<T, K extends string>(items: T[], key: (t: T) => K): Record<K, T[]> { ... }

Each type parameter links an input to an output, so mistakes show up at the call site.""",
            mcq("What does compose<A, B, C> link?", ["The output type of f to the input type of g", "Only the return", "Nothing", "The runtime values"], 0),
            mcq("What is the type of len(' hi ') above?", ["number", "string", "any", "unknown"], 0),
            mcq("Why type helper functions generically?", ["So callers keep precise types", "To speed them up", "To hide errors", "To avoid inference"], 0),
            run("Write groupBy<T, K extends string>(items: T[], key: (item: T) => K): Record<string, T[]> grouping items by the key result (keys in first-seen order).", "typescript",
                [log("JSON.stringify(groupBy(['apple', 'avocado', 'bean'], (s) => s[0]))"), log("JSON.stringify(groupBy([1, 2, 3, 4], (n) => (n % 2 ? 'odd' : 'even')))"), log("JSON.stringify(groupBy([], (x: string) => x))")],
                ['{"a":["apple","avocado"],"b":["bean"]}', '{"odd":[1,3],"even":[2,4]}', "{}"],
                "function groupBy<T, K extends string>(items: T[], key: (item: T) => K): Record<string, T[]> {\n  const out: Record<string, T[]> = {};\n  for (const item of items) {\n    const k = key(item);\n    (out[k] ??= []).push(item);\n  }\n  return out;\n}",
                forbid=[r"\bany\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 14
    unit(
        "Unit 14 · Safer data modelling",
        lesson(
            "Branded types",
            """Two different ids can both be numbers, yet mixing them is a bug. A 'brand' makes the types incompatible:

type UserId = number & { readonly __brand: "UserId" };
type OrderId = number & { readonly __brand: "OrderId" };

const asUserId = (n: number) => n as UserId;
function getUser(id: UserId) { ... }

getUser(asUserId(5));       // fine
getUser(7 as OrderId);      // error - an OrderId is not a UserId

The brand exists only in the type system; at runtime they're plain numbers.""",
            mcq("Why brand an id type?", ["To stop mixing up different kinds of numbers", "To make it faster", "To store more data", "To validate at runtime"], 0),
            mcq("Does the brand exist at runtime?", ["No - only in the type system", "Yes", "Only in classes", "Only for strings"], 0),
            mcq("How is a branded value created?", ["A cast (or a validating constructor)", "Automatically", "With new", "With enum"], 0),
            run("Create branded types Meters and Feet (numbers) with converters toMeters(f: Feet): Meters (feet * 0.3048, rounded to 2 decimals) and helper constructors. Passing Feet where Meters is expected must be a type error.", "typescript",
                [t("convert", append="const f = asFeet(100);\nconsole.log(toMeters(f));"), t("rejects", append="const f = asFeet(1);\nfunction show(m: Meters): number { return m; }\n" + REJECTS + "show(f);\nconsole.log('checked');")],
                ["30.48", "checked"],
                "type Meters = number & { readonly __unit: 'm' };\ntype Feet = number & { readonly __unit: 'ft' };\nconst asMeters = (n: number) => n as Meters;\nconst asFeet = (n: number) => n as Feet;\nfunction toMeters(f: Feet): Meters {\n  return asMeters(Math.round(f * 0.3048 * 100) / 100);\n}",
                require=[r"__unit|__brand"]),
        ),
        lesson(
            "Result types instead of exceptions",
            """A Result type makes success and failure part of the signature, so callers must handle both:

type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };

function parseAge(s: string): Result<number> {
  const n = Number(s);
  return Number.isInteger(n) && n >= 0 ? { ok: true, value: n } : { ok: false, error: "invalid age" };
}

const r = parseAge("12");
if (r.ok) r.value;      // number
else r.error;           // string

Discriminated unions narrow on ok, so you can't read value without checking.""",
            mcq("What does the Result type force callers to do?", ["Handle both success and failure", "Use try/catch", "Use async", "Ignore errors"], 0),
            mcq("Which property do we narrow on?", ["ok", "value", "error", "T"], 0),
            mcq("Why prefer this to throwing for expected failures?", ["Failures are visible in the type", "It is faster always", "Throw is deprecated", "It avoids types"], 0),
            run("Write type Result<T> = { ok: true; value: T } | { ok: false; error: string } and divide(a: number, b: number): Result<number> (error 'division by zero' when b is 0). Print value or error for several calls.", "typescript",
                [t("flow", append="for (const [a, b] of [[10, 4], [1, 0]] as [number, number][]) {\n  const r = divide(a, b);\n  console.log(r.ok ? r.value : r.error);\n}"), t("rejects", append="const r = divide(1, 2);\n" + REJECTS + "console.log(r.value);\nconsole.log('checked');")],
                ["2.5\ndivision by zero", "0.5\nchecked"],
                "type Result<T> = { ok: true; value: T } | { ok: false; error: string };\n\nfunction divide(a: number, b: number): Result<number> {\n  if (b === 0) return { ok: false, error: 'division by zero' };\n  return { ok: true, value: a / b };\n}",
                require=[r"ok:\s*true", r"ok:\s*false"]),
        ),
        lesson(
            "unknown, never & safe parsing",
            """unknown is the safe version of any: you can hold anything, but must narrow before using it.

function parseJson(text: string): unknown { return JSON.parse(text); }

const data = parseJson('{"a": 1}');
data.a;                         // error: data is unknown
if (typeof data === "object" && data !== null && "a" in data) { ... }

Rule of thumb: values from OUTSIDE your program (JSON, user input, network) are unknown until validated.""",
            mcq("What must you do before using an unknown value?", ["Narrow it", "Nothing", "Cast to never", "Call it"], 0),
            mcq("How does unknown differ from any?", ["unknown forces checks; any switches checking off", "No difference", "any is safer", "unknown is a number"], 0),
            mcq("Which values should start as unknown?", ["JSON from a network call", "Your own constants", "Loop counters", "Literals"], 0),
            run("Write readPort(text: string): number that parses JSON, expects an object with a numeric 'port' property, and returns it; return 80 for anything else (invalid JSON, missing or non-numeric port).", "typescript",
                [log("readPort('{\"port\": 8080}')"), log("readPort('{\"port\": \"x\"}')"), log("readPort('not json')"), log("readPort('[]')")],
                ["8080", "80", "80", "80"],
                "function readPort(text: string): number {\n  let data: unknown;\n  try {\n    data = JSON.parse(text);\n  } catch {\n    return 80;\n  }\n  if (typeof data === 'object' && data !== null && 'port' in data) {\n    const port = (data as { port: unknown }).port;\n    if (typeof port === 'number') return port;\n  }\n  return 80;\n}",
                require=[r"unknown"], forbid=[r":\s*any\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 15
    unit(
        "Unit 15 · Modules, declarations & tooling",
        lesson(
            "Type-only imports and exports",
            """import type brings in only a type - it is erased entirely from the compiled JavaScript:

import type { User } from "./models";
export type { User };

Why? It avoids runtime import cycles, makes bundles smaller, and states the intent: this file only needs the shape. With isolatedModules (used by most tools) you should mark type-only re-exports with export type.""",
            mcq("What happens to 'import type' at runtime?", ["It is erased", "It loads the module", "It throws", "It becomes a function"], 0),
            mcq("Why prefer import type for shapes?", ["No runtime import, smaller bundle, fewer cycles", "It is required", "It is faster to type", "It adds checks"], 0),
            mcq("Which is a type-only re-export?", ["export type { User }", "export { User }", "export default User", "import User"], 0),
            run("In one file you can still practise the idea: define interface Point and a function distance(a: Point, b: Point): number (Euclidean, rounded to 2 decimals). Print distance for (0,0)-(3,4).", "typescript",
                [log("distance({ x: 0, y: 0 }, { x: 3, y: 4 })"), log("distance({ x: 1, y: 1 }, { x: 2, y: 2 })")],
                ["5", "1.41"],
                "interface Point {\n  x: number;\n  y: number;\n}\n\nfunction distance(a: Point, b: Point): number {\n  return Math.round(Math.hypot(a.x - b.x, a.y - b.y) * 100) / 100;\n}",
                require=[r"interface\s+Point"]),
        ),
        lesson(
            "Declaration files & ambient types",
            """A .d.ts file contains only types - it describes JavaScript that has no types of its own:

declare function legacyAdd(a: number, b: number): number;
declare const VERSION: string;
declare module "left-pad" { export default function pad(s: string, n: number): string; }

The 'declare' keyword says 'this exists at runtime, trust me'. Packages usually ship their own .d.ts or get one from DefinitelyTyped (@types/...). Wrong declarations lie to the compiler, so keep them accurate.""",
            mcq("What does a .d.ts file contain?", ["Only type declarations", "Runtime code", "CSS", "Tests"], 0),
            mcq("What does 'declare' tell TypeScript?", ["This value exists at runtime already", "Create this variable", "Hide this variable", "Delete this"], 0),
            mcq("Where do types for old JS libraries often come from?", ["@types packages (DefinitelyTyped)", "The browser", "Node core", "npm audit"], 0),
            run("Use declare to describe a global that the host provides: declare const APP_NAME: string — and then write a function banner(): string returning APP_NAME uppercased. The test supplies APP_NAME with a plain var before calling.", "typescript",
                [t("run", append="// the host provides the global\n(globalThis as { APP_NAME?: string }).APP_NAME = 'codeingo';\nconsole.log(banner());")],
                ["CODEINGO"],
                "declare const APP_NAME: string;\n\nfunction banner(): string {\n  return APP_NAME.toUpperCase();\n}",
                require=[r"declare\s+const\s+APP_NAME"]),
        ),
        lesson(
            "tsconfig strictness & enums vs unions",
            """strict: true turns on a family of checks (strictNullChecks, noImplicitAny, ...). Turn it on from day one; it is far harder to add later.

Enums vs unions of literals:

enum Color { Red, Green }              // exists at runtime, numeric by default
type Color2 = "red" | "green";         // erased - just types

Most teams prefer string-literal unions (simpler, no runtime code, better narrowing); use const enums or enums only when you need runtime objects.""",
            mcq("Which option turns on the most important checks?", ["strict: true", "target", "outDir", "lib"], 0),
            mcq("Which exists at runtime?", ["An enum", "A union of literals", "An interface", "A type alias"], 0),
            mcq("Why do many teams prefer literal unions to enums?", ["No runtime code and simple narrowing", "They are faster to run", "Enums are invalid", "They allow any"], 0),
            run("Replace an enum with a union: define type Level = 'low' | 'mid' | 'high' and a function score(l: Level): number (1, 2, 3). Passing 'extreme' must be a type error.", "typescript",
                [log("score('low') + score('high')"), log("score('mid')"), t("rejects", append=REJECTS + "score('extreme');\nconsole.log('checked');")],
                ["4", "2", "checked"],
                "type Level = 'low' | 'mid' | 'high';\n\nfunction score(l: Level): number {\n  const table: Record<Level, number> = { low: 1, mid: 2, high: 3 };\n  return table[l];\n}",
                require=[r"type\s+Level"]),
        ),
    ),
)
