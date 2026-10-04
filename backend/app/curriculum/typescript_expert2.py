"""TypeScript - Expert section, part 2 (units 16-21): typed async, data structures, algorithms, patterns, validation
and capstone projects. Programs are type-checked in strict mode and then run."""
from .dsl import lesson, mcq, run, section, t, unit

REJECTS = "// @ts-expect-error\n"


def log(expr: str, name: str | None = None) -> dict:
    return t(name or expr, append=f"console.log({expr});")


EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 16
    unit(
        "Unit 16 · Typed async code",
        lesson(
            "Promise<T> and Promise.all with tuples",
            """An async function always returns Promise<T> where T is what you return. Promise.all keeps the type of EACH slot when you pass a tuple:

async function load(): Promise<[string, number]> {
  const [name, age] = await Promise.all([getName(), getAge()]);   // [string, number]
  return [name, age];
}

await unwraps one level: await Promise<number> is number. A function returning Promise<void> signals 'done, no value'.""",
            mcq("What type does an async function returning 5 have?", ["Promise<number>", "number", "void", "Promise<void>"], 0),
            mcq("What does await Promise<string> produce?", ["string", "Promise<string>", "unknown", "void"], 0),
            mcq("What does Promise.all([a(), b()]) give for a(): Promise<string>, b(): Promise<number>?", ["Promise<[string, number]>", "Promise<(string | number)[]>", "Promise<any>", "[string, number]"], 0),
            run("Write async function both<A, B>(a: Promise<A>, b: Promise<B>): Promise<[A, B]> using Promise.all. The test prints the tuple types' values.", "typescript",
                [t("run", append="both(Promise.resolve('x'), Promise.resolve(2)).then(([s, n]) => console.log(s.toUpperCase(), n + 1));"),
                 t("rejects", append="both(Promise.resolve('x'), Promise.resolve(2)).then(([s, n]) => {\n  " + REJECTS + "const bad: string = n;\n  console.log('checked', s);\n});")],
                ["X 3", "checked x"],
                "async function both<A, B>(a: Promise<A>, b: Promise<B>): Promise<[A, B]> {\n  const [x, y] = await Promise.all([a, b]);\n  return [x, y];\n}",
                require=[r"Promise\.all"], forbid=[r"\bany\b"]),
        ),
        lesson(
            "Typed async results",
            """Combine async with a Result type so failures are part of the signature instead of surprise rejections:

type Result<T> = { ok: true; value: T } | { ok: false; error: string };

async function safe<T>(work: () => Promise<T>): Promise<Result<T>> {
  try { return { ok: true, value: await work() }; }
  catch (e) { return { ok: false, error: e instanceof Error ? e.message : String(e) }; }
}

Callers get a value they can narrow instead of needing try/catch everywhere.""",
            mcq("What does safe() turn a rejection into?", ["A { ok: false, error } result", "A crash", "undefined", "A retry"], 0),
            mcq("Why check e instanceof Error?", ["catch variables are unknown", "Errors are numbers", "It is faster", "To log"], 0),
            mcq("What is the benefit for callers?", ["Failures show up in the type", "Shorter stack traces", "Faster promises", "No awaits"], 0),
            run("Write the Result type and async safe<T>(work: () => Promise<T>): Promise<Result<T>>. The test prints successes and failures.", "typescript",
                [t("flow", append="safe(async () => 42).then((r) => console.log(r.ok ? r.value : r.error));\nsafe(async () => { throw new Error('boom'); }).then((r) => console.log(r.ok ? r.value : r.error));"),
                 t("string throw", append="safe(async () => { throw 'plain'; }).then((r) => console.log(r.ok ? r.value : r.error));")],
                ["42\nboom", "plain"],
                "type Result<T> = { ok: true; value: T } | { ok: false; error: string };\n\nasync function safe<T>(work: () => Promise<T>): Promise<Result<T>> {\n  try {\n    return { ok: true, value: await work() };\n  } catch (e) {\n    return { ok: false, error: e instanceof Error ? e.message : String(e) };\n  }\n}",
                forbid=[r":\s*any\b"]),
        ),
        lesson(
            "Async generators",
            """An async generator yields values over time, typed as AsyncGenerator<Yield, Return, Next>. Consume it with for await:

async function* pages(n: number): AsyncGenerator<number[]> {
  for (let p = 1; p <= n; p++) yield [p * 10, p * 10 + 1];
}

for await (const page of pages(2)) console.log(page);

Perfect for paginated APIs and streams: you handle one chunk at a time without loading everything.""",
            mcq("What does for await...of consume?", ["An async iterable", "Only arrays", "Only promises once", "A string"], 0),
            mcq("What does the type AsyncGenerator<number[]> yield?", ["Arrays of numbers", "Numbers", "Promises", "Strings"], 0),
            mcq("When is an async generator useful?", ["Paginated or streaming data", "Constants", "Pure maths", "Type guards"], 0),
            run("Write async function* countdown(n: number): AsyncGenerator<number> yielding n, n-1, ... 1 (with an await between values), and an async function collect<T>(source: AsyncIterable<T>): Promise<T[]>.", "typescript",
                [t("collect", append="collect(countdown(3)).then((a) => console.log(a.join(',')));"), t("empty", append="collect(countdown(0)).then((a) => console.log(a.length));")],
                ["3,2,1", "0"],
                "async function* countdown(n: number): AsyncGenerator<number> {\n  for (let i = n; i >= 1; i--) {\n    await Promise.resolve();\n    yield i;\n  }\n}\n\nasync function collect<T>(source: AsyncIterable<T>): Promise<T[]> {\n  const out: T[] = [];\n  for await (const x of source) out.push(x);\n  return out;\n}",
                require=[r"async function\*", r"for await"]),
        ),
    ),
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Typed data structures",
        lesson(
            "A generic Stack and Queue",
            """Classes with a type parameter hold one kind of value safely:

class Stack<T> {
  private items: T[] = [];
  push(x: T): void { this.items.push(x); }
  pop(): T | undefined { return this.items.pop(); }
  get size(): number { return this.items.length; }
}

const s = new Stack<number>();
s.push("x");        // error

pop() returns T | undefined - the empty case is in the type, so callers must handle it.""",
            mcq("Why does pop() return T | undefined?", ["The stack might be empty", "It is async", "T may be a string", "undefined is faster"], 0),
            mcq("What does new Stack<number>() prevent?", ["Pushing non-numbers", "Popping", "Empty stacks", "Reading size"], 0),
            mcq("What is the order of a stack?", ["Last in, first out", "First in, first out", "Sorted", "Random"], 0),
            run("Write generic classes Stack<T> (push, pop, peek, size) and Queue<T> (enqueue, dequeue, size). pop/peek/dequeue return T | undefined.", "typescript",
                [t("stack", append="const s = new Stack<number>();\ns.push(1); s.push(2);\nconsole.log(s.peek(), s.pop(), s.pop(), s.pop(), s.size);"), t("queue", append="const q = new Queue<string>();\nq.enqueue('a'); q.enqueue('b');\nconsole.log(q.dequeue(), q.size, q.dequeue(), q.dequeue());"),
                 t("rejects", append="const s = new Stack<number>();\n" + REJECTS + "s.push('x');\nconsole.log('checked');")],
                ["2 2 1 undefined 0", "a 1 b undefined", "checked"],
                "class Stack<T> {\n  private items: T[] = [];\n  push(x: T): void {\n    this.items.push(x);\n  }\n  pop(): T | undefined {\n    return this.items.pop();\n  }\n  peek(): T | undefined {\n    return this.items[this.items.length - 1];\n  }\n  get size(): number {\n    return this.items.length;\n  }\n}\n\nclass Queue<T> {\n  private items: T[] = [];\n  enqueue(x: T): void {\n    this.items.push(x);\n  }\n  dequeue(): T | undefined {\n    return this.items.shift();\n  }\n  get size(): number {\n    return this.items.length;\n  }\n}",
                forbid=[r"\bany\b"]),
        ),
        lesson(
            "Typed event emitter",
            """Use a map of event names to payload types so emit and on are checked:

type Events = { login: { user: string }; logout: undefined };

class Emitter<E extends Record<string, unknown>> {
  private handlers: { [K in keyof E]?: ((p: E[K]) => void)[] } = {};
  on<K extends keyof E>(event: K, fn: (p: E[K]) => void): void { (this.handlers[event] ??= []).push(fn); }
  emit<K extends keyof E>(event: K, payload: E[K]): void { this.handlers[event]?.forEach((fn) => fn(payload)); }
}

emitter.emit("login", { user: 1 });   // error: wrong payload""",
            mcq("What does K extends keyof E guarantee?", ["The event name exists", "The payload is a string", "Handlers exist", "E is empty"], 0),
            mcq("What happens if you emit('login', 5) with login: { user: string }?", ["Compile error", "Works", "Runtime error", "Ignored"], 0),
            mcq("What does E[K] mean?", ["The payload type of event K", "The key", "A function", "An array"], 0),
            run("Write class Emitter<E extends Record<string, unknown>> with on(event, fn) and emit(event, payload). Use it with type Events = { add: number; name: string }.", "typescript",
                [t("flow", append="const e = new Emitter<{ add: number; name: string }>();\ne.on('add', (n) => console.log(n + 1));\ne.on('name', (s) => console.log(s.toUpperCase()));\ne.emit('add', 4);\ne.emit('name', 'ada');"),
                 t("rejects", append="const e = new Emitter<{ add: number }>();\n" + REJECTS + "e.emit('add', 'x');\nconsole.log('checked');")],
                ["5\nADA", "checked"],
                "class Emitter<E extends Record<string, unknown>> {\n  private handlers: { [K in keyof E]?: ((p: E[K]) => void)[] } = {};\n  on<K extends keyof E>(event: K, fn: (p: E[K]) => void): void {\n    (this.handlers[event] ??= []).push(fn);\n  }\n  emit<K extends keyof E>(event: K, payload: E[K]): void {\n    this.handlers[event]?.forEach((fn) => fn(payload));\n  }\n}",
                forbid=[r":\s*any\b"]),
        ),
        lesson(
            "Readonly collections & tuples",
            """readonly stops mutation at the type level - great for function inputs you promise not to change:

function total(nums: readonly number[]): number { ... }
nums.push(1);              // error on a readonly number[]

ReadonlyArray<T>, Readonly<T>, ReadonlyMap and ReadonlySet exist too. Tuples can be readonly or labelled: type Range = readonly [start: number, end: number].

Returning a readonly view stops callers from corrupting your internal state.""",
            mcq("What does a readonly number[] parameter promise?", ["The function won't mutate the array", "The array is empty", "The array is sorted", "It is a tuple"], 0),
            mcq("Is readonly checked at runtime?", ["No, only by the compiler", "Yes", "Only in classes", "Only for arrays"], 0),
            mcq("Why return a readonly view of internal data?", ["Callers can't corrupt it", "It is faster", "It is shorter", "It sorts"], 0),
            run("Write class Playlist with private songs: string[], add(title), and a getter list(): readonly string[]. Modifying the returned list (list.push) must be a type error.", "typescript",
                [t("flow", append="const p = new Playlist();\np.add('a'); p.add('b');\nconsole.log(p.list.join(','), p.list.length);"), t("rejects", append="const p = new Playlist();\n" + REJECTS + "p.list.push('x');\nconsole.log('checked');")],
                ["a,b 2", "checked"],
                "class Playlist {\n  private songs: string[] = [];\n  add(title: string): void {\n    this.songs.push(title);\n  }\n  get list(): readonly string[] {\n    return this.songs;\n  }\n}",
                require=[r"readonly string\[\]"]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Typed algorithms",
        lesson(
            "Generic binary search",
            """A generic binary search works on any sorted array and any ordering, with a comparator:

function binarySearch<T>(items: readonly T[], target: T, cmp: (a: T, b: T) => number): number {
  let lo = 0, hi = items.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const c = cmp(items[mid], target);
    if (c === 0) return mid;
    if (c < 0) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}

The comparator returns negative, zero or positive - the same convention as Array.sort.""",
            mcq("What does the comparator return for a < b?", ["A negative number", "A positive number", "true", "0"], 0),
            mcq("What is the complexity?", ["O(log n)", "O(n)", "O(n²)", "O(1)"], 0),
            mcq("What must be true of the array?", ["It is sorted by the same ordering", "It has unique items", "It holds numbers", "It is short"], 0),
            run("Write generic binarySearch<T>(items: readonly T[], target: T, cmp: (a: T, b: T) => number): number returning the index or -1.", "typescript",
                [log("binarySearch([1, 3, 5, 7, 9], 7, (a, b) => a - b)"), log("binarySearch(['ant', 'bee', 'cat'], 'bee', (a, b) => a.localeCompare(b))"), log("binarySearch([2, 4], 3, (a, b) => a - b)")],
                ["3", "1", "-1"],
                "function binarySearch<T>(items: readonly T[], target: T, cmp: (a: T, b: T) => number): number {\n  let lo = 0;\n  let hi = items.length - 1;\n  while (lo <= hi) {\n    const mid = (lo + hi) >> 1;\n    const c = cmp(items[mid], target);\n    if (c === 0) return mid;\n    if (c < 0) lo = mid + 1;\n    else hi = mid - 1;\n  }\n  return -1;\n}",
                forbid=[r"indexOf|findIndex"]),
        ),
        lesson(
            "Sorting objects by a key",
            """Write a reusable sorter that takes a key function and never mutates the input:

function sortBy<T, K extends string | number>(items: readonly T[], key: (t: T) => K): T[] {
  return [...items].sort((a, b) => (key(a) < key(b) ? -1 : key(a) > key(b) ? 1 : 0));
}

The type parameter K is limited to things that can be compared with < and >. Copying first with [...items] keeps the original order intact.""",
            mcq("Why copy with [...items] before sort?", ["sort mutates the array in place", "To save memory", "To make it async", "sort needs a copy to run"], 0),
            mcq("Why constrain K to string | number?", ["So < and > make sense", "To speed up", "To use generics", "To avoid arrays"], 0),
            mcq("What does key: (t: T) => K let callers do?", ["Choose what to sort by", "Skip sorting", "Reverse order", "Filter"], 0),
            run("Write sortBy<T, K extends string | number>(items: readonly T[], key: (item: T) => K): T[] returning a new array sorted ascending by key (stable), leaving the input unchanged.", "typescript",
                [t("by age", append="const people = [{ n: 'Bo', a: 30 }, { n: 'Ada', a: 25 }, { n: 'Cy', a: 30 }];\nconsole.log(sortBy(people, (p) => p.a).map((p) => p.n).join(','));\nconsole.log(people.map((p) => p.n).join(','));"),
                 t("by name", append="console.log(sortBy(['pear', 'fig', 'apple'], (s) => s).join(','));"),
                 t("rejects", append=REJECTS + "sortBy([1, 2], () => ({}));\nconsole.log('checked');")],
                ["Ada,Bo,Cy\nBo,Ada,Cy", "apple,fig,pear", "checked"],
                "function sortBy<T, K extends string | number>(items: readonly T[], key: (item: T) => K): T[] {\n  return [...items].sort((a, b) => {\n    const ka = key(a);\n    const kb = key(b);\n    return ka < kb ? -1 : ka > kb ? 1 : 0;\n  });\n}",
                forbid=[r"\bany\b"]),
        ),
        lesson(
            "A typed graph with BFS",
            """A graph can be generic over its node type, stored as a Map of adjacency lists:

class Graph<N> {
  private edges = new Map<N, N[]>();
  addEdge(a: N, b: N): void {
    (this.edges.get(a) ?? this.edges.set(a, []).get(a)!).push(b);
  }
  neighbours(n: N): readonly N[] { return this.edges.get(n) ?? []; }
}

BFS uses a queue and a visited set, and returns the nodes in the order reached. Typing the node as N means a graph of strings or of numbers both work.""",
            mcq("What does a BFS use to explore level by level?", ["A queue", "A stack", "A heap", "A tree"], 0),
            mcq("Why a visited Set<N>?", ["To avoid visiting a node twice", "To sort nodes", "To count edges", "To remove cycles from the data"], 0),
            mcq("What does Graph<N> let you do?", ["Use any node type", "Only numbers", "Only strings", "Only objects"], 0),
            run("Write class Graph<N> with addEdge(a, b) (directed) and bfs(start: N): N[] returning the nodes in breadth-first order (each once).", "typescript",
                [t("strings", append="const g = new Graph<string>();\ng.addEdge('a', 'b'); g.addEdge('a', 'c'); g.addEdge('b', 'd'); g.addEdge('c', 'd');\nconsole.log(g.bfs('a').join(''));"),
                 t("numbers", append="const g = new Graph<number>();\ng.addEdge(1, 2); g.addEdge(2, 3); g.addEdge(3, 1);\nconsole.log(g.bfs(1).join(','));"),
                 t("rejects", append="const g = new Graph<number>();\n" + REJECTS + "g.addEdge(1, 'x');\nconsole.log('checked');")],
                ["abcd", "1,2,3", "checked"],
                "class Graph<N> {\n  private edges = new Map<N, N[]>();\n  addEdge(a: N, b: N): void {\n    const list = this.edges.get(a) ?? [];\n    list.push(b);\n    this.edges.set(a, list);\n  }\n  bfs(start: N): N[] {\n    const seen = new Set<N>([start]);\n    const queue: N[] = [start];\n    for (let i = 0; i < queue.length; i++) {\n      for (const next of this.edges.get(queue[i]) ?? []) {\n        if (!seen.has(next)) {\n          seen.add(next);\n          queue.push(next);\n        }\n      }\n    }\n    return queue;\n  }\n}",
                forbid=[r"\bany\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Patterns with types",
        lesson(
            "State machines with discriminated unions",
            """Model each state as a variant, and write transitions as a function from (state, event) to the next state. The compiler checks you didn't forget a combination.

type State = { tag: "idle" } | { tag: "loading"; since: number } | { tag: "done"; data: string } | { tag: "failed"; reason: string };
type Event = { type: "fetch"; at: number } | { type: "ok"; data: string } | { type: "fail"; reason: string };

Each state carries only the data that makes sense for it - no 'data' on a loading state, no 'reason' on a done one. Impossible states become unrepresentable.""",
            mcq("What does 'impossible states unrepresentable' mean?", ["Types can't describe invalid combinations", "States are private", "No errors ever", "States are numbers"], 0),
            mcq("Which field tells variants apart?", ["The tag/kind literal", "The first key", "The length", "Any string"], 0),
            mcq("Why carry data only in the right state?", ["You can't read data before it exists", "Memory", "Speed", "Style"], 0),
            run("Implement type State = { tag: 'idle' } | { tag: 'loading' } | { tag: 'done'; data: string } and function next(s: State, ev: 'fetch' | 'ok:<text>'): State where 'fetch' moves idle -> loading, and 'ok:text' moves loading -> done with that data; anything else leaves the state unchanged. Print the tag/data.", "typescript",
                [t("flow", append="let s: State = { tag: 'idle' };\ns = next(s, 'ok:early');\nconsole.log(s.tag);\ns = next(s, 'fetch');\nconsole.log(s.tag);\ns = next(s, 'ok:hello');\nconsole.log(s.tag === 'done' ? s.data : '?');"),
                 t("rejects", append="const s: State = { tag: 'idle' };\n" + REJECTS + "console.log(s.data);\nconsole.log('checked');")],
                ["idle\nloading\nhello", "undefined\nchecked"],
                "type State = { tag: 'idle' } | { tag: 'loading' } | { tag: 'done'; data: string };\n\nfunction next(s: State, ev: string): State {\n  if (s.tag === 'idle' && ev === 'fetch') return { tag: 'loading' };\n  if (s.tag === 'loading' && ev.startsWith('ok:')) return { tag: 'done', data: ev.slice(3) };\n  return s;\n}",
                require=[r"tag:\s*'done'"]),
        ),
        lesson(
            "Builder pattern with growing types",
            """A typed builder can track which fields have been set, so build() is only allowed when required fields exist:

class RequestBuilder<Has extends { url?: true } = {}> {
  private cfg: { url?: string; method: string } = { method: "GET" };
  url(u: string): RequestBuilder<Has & { url: true }> { this.cfg.url = u; return this as never; }
  method(m: string): this { this.cfg.method = m; return this; }
  build(this: RequestBuilder<{ url: true }>): string { return `${this.cfg.method} ${this.cfg.url}`; }
}

Calling build() before url() is a compile error. It is advanced, but shows how types can enforce an order of steps.""",
            mcq("What does the Has type parameter track?", ["Which required fields were already set", "The return value", "Runtime state", "The class name"], 0),
            mcq("What happens if you call build() before url()?", ["A compile error", "A runtime error", "Nothing", "An empty string"], 0),
            mcq("Why is this pattern useful?", ["Misuse is caught before the program runs", "It is faster", "It uses fewer classes", "It avoids generics"], 0),
            run("Write a simpler typed builder: class Pizza with size(s: 'small' | 'large'): this, topping(t: string): this, and build(): string returning e.g. 'large: ham, olives'. Calling size('huge') must be a type error.", "typescript",
                [log("new Pizza().size('large').topping('ham').topping('olives').build()"), log("new Pizza().size('small').build()"), t("rejects", append=REJECTS + "new Pizza().size('huge');\nconsole.log('checked');")],
                ["large: ham, olives", "small: ", "checked"],
                "class Pizza {\n  private s: 'small' | 'large' = 'small';\n  private toppings: string[] = [];\n  size(s: 'small' | 'large'): this {\n    this.s = s;\n    return this;\n  }\n  topping(t: string): this {\n    this.toppings.push(t);\n    return this;\n  }\n  build(): string {\n    return `${this.s}: ${this.toppings.join(', ')}`;\n  }\n}",
                require=[r"\):\s*this"]),
        ),
        lesson(
            "Dependency injection with interfaces",
            """Depend on an interface, not a concrete class, and pass the dependency in. Tests can then supply a fake:

interface Clock { now(): number }
class Greeter {
  constructor(private clock: Clock) {}
  greet(name: string): string { return this.clock.now() < 12 ? `Good morning, ${name}` : `Hello, ${name}`; }
}

new Greeter({ now: () => 9 }).greet("Ada");

Any object with a now() method fits - a real clock, a fixed fake or a mock.""",
            mcq("What does 'depend on an interface' give you?", ["Swappable implementations", "Faster code", "Fewer files", "Global state"], 0),
            mcq("Why does injection help tests?", ["You can pass a fake dependency", "Tests run faster", "Tests need no code", "It removes classes"], 0),
            mcq("Which object satisfies Clock?", ["{ now: () => 5 }", "{ time: 5 }", "5", "() => 5"], 0),
            run("Write interface Logger { log(msg: string): void }, and class Service(private logger: Logger) with run(n: number) that logs 'start', then each number 1..n as a string, then 'done'. The test passes a Logger that collects messages.", "typescript",
                [t("flow", append="const lines: string[] = [];\nnew Service({ log: (m) => lines.push(m) }).run(2);\nconsole.log(lines.join(','));"), t("none", append="const lines: string[] = [];\nnew Service({ log: (m) => lines.push(m) }).run(0);\nconsole.log(lines.join(','));"),
                 t("rejects", append=REJECTS + "new Service({ write: () => {} });\nconsole.log('checked');")],
                ["start,1,2,done", "start,done", "checked"],
                "interface Logger {\n  log(msg: string): void;\n}\n\nclass Service {\n  constructor(private logger: Logger) {}\n  run(n: number): void {\n    this.logger.log('start');\n    for (let i = 1; i <= n; i++) this.logger.log(String(i));\n    this.logger.log('done');\n  }\n}",
                require=[r"interface\s+Logger"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Validation & parsing",
        lesson(
            "Runtime validators with type predicates",
            """Types vanish at runtime, so data from outside needs real checks. Write small validators that double as type guards:

type Validator<T> = (x: unknown) => x is T;
const isString: Validator<string> = (x): x is string => typeof x === "string";
const isNumber: Validator<number> = (x): x is number => typeof x === "number";

function arrayOf<T>(item: Validator<T>): Validator<T[]> {
  return (x): x is T[] => Array.isArray(x) && x.every(item);
}

Validators compose: arrayOf(isNumber) checks an array of numbers AND tells TypeScript the type.""",
            mcq("Why do we need runtime validators?", ["Types are erased at runtime", "Types are slow", "TypeScript can't check", "JSON is typed"], 0),
            mcq("What does arrayOf(isNumber) return?", ["A validator for number[]", "A number", "An array", "A boolean"], 0),
            mcq("What do validators that return 'x is T' give the compiler?", ["Narrowing information", "Speed", "Comments", "Nothing"], 0),
            run("Write type Validator<T> = (x: unknown) => x is T, isString, isNumber, arrayOf(item) and optional(item) (accepts undefined or a valid item).", "typescript",
                [t("flow", append="console.log(arrayOf(isNumber)([1, 2]), arrayOf(isNumber)([1, 'x']), optional(isString)(undefined), optional(isString)(5));"),
                 t("narrow", append="const v: unknown = ['a', 'b'];\nif (arrayOf(isString)(v)) console.log(v.map((s) => s.toUpperCase()).join(''));")],
                ["true false true false", "AB"],
                "type Validator<T> = (x: unknown) => x is T;\nconst isString: Validator<string> = (x): x is string => typeof x === 'string';\nconst isNumber: Validator<number> = (x): x is number => typeof x === 'number';\nfunction arrayOf<T>(item: Validator<T>): Validator<T[]> {\n  return (x): x is T[] => Array.isArray(x) && x.every((i) => item(i));\n}\nfunction optional<T>(item: Validator<T>): Validator<T | undefined> {\n  return (x): x is T | undefined => x === undefined || item(x);\n}",
                forbid=[r":\s*any\b"]),
        ),
        lesson(
            "Schemas that infer types",
            """A tiny schema can describe an object once and give you BOTH a validator and the TypeScript type:

const schema = { name: "string", age: "number" } as const;
type Infer<S extends Record<string, "string" | "number">> = {
  [K in keyof S]: S[K] extends "string" ? string : number;
};
type User = Infer<typeof schema>;      // { name: string; age: number }

This is how libraries like Zod work: one source of truth for runtime checks and static types.""",
            mcq("What is the benefit of one schema for both checks and types?", ["They can't drift apart", "It is shorter always", "It avoids classes", "It speeds up runtime"], 0),
            mcq("What does Infer<typeof schema> compute?", ["The object type the schema describes", "The runtime value", "A function", "A string"], 0),
            mcq("Why use 'as const' on the schema?", ["To keep literal types like 'string'", "To freeze it at runtime only", "To compile faster", "To add methods"], 0),
            run("Write a mini schema: type Kind = 'string' | 'number', type Infer<S>, and parse<S extends Record<string, Kind>>(schema: S, data: unknown): Infer<S> | null that returns the data when every field matches its kind, otherwise null.", "typescript",
                [t("ok", append="const s = { name: 'string', age: 'number' } as const;\nconst r = parse(s, { name: 'Ada', age: 36 });\nconsole.log(r ? r.name.toUpperCase() + r.age : 'bad');"),
                 t("bad", append="const s = { name: 'string' } as const;\nconsole.log(parse(s, { name: 5 }), parse(s, null));"),
                 t("rejects", append="const s = { n: 'number' } as const;\nconst r = parse(s, { n: 1 });\n" + REJECTS + "const x: string = r!.n;\nconsole.log('checked');")],
                ["ADA36", "null null", "checked"],
                "type Kind = 'string' | 'number';\ntype Infer<S extends Record<string, Kind>> = {\n  [K in keyof S]: S[K] extends 'string' ? string : number;\n};\n\nfunction parse<S extends Record<string, Kind>>(schema: S, data: unknown): Infer<S> | null {\n  if (typeof data !== 'object' || data === null) return null;\n  for (const key of Object.keys(schema)) {\n    if (typeof (data as Record<string, unknown>)[key] !== schema[key]) return null;\n  }\n  return data as Infer<S>;\n}",
                require=[r"Infer"]),
        ),
        lesson(
            "Parsing strings into typed values",
            """Parsing turns loosely-typed text into precise types, and returns a clear failure when it can't:

function parsePoint(s: string): { x: number; y: number } | null {
  const m = /^\\((-?\\d+),\\s*(-?\\d+)\\)$/.exec(s);
  return m ? { x: Number(m[1]), y: Number(m[2]) } : null;
}

'Parse, don't validate': produce a typed value once at the edge, then the rest of the program can trust it and never re-check.""",
            mcq("What does 'parse, don't validate' recommend?", ["Turn input into a precise type once, at the edge", "Validate everywhere", "Avoid types", "Use any"], 0),
            mcq("What does parsePoint return for bad text?", ["null", "An error", "0", "undefined"], 0),
            mcq("Why is the result type 'T | null'?", ["Callers must handle failure", "null is faster", "It is optional", "JSON needs it"], 0),
            run("Write parseDuration(s: string): number | null turning strings like '2h30m', '45m' or '90s' into total seconds (h, m and s parts optional but at least one present, in that order); null if it doesn't match.", "typescript",
                [log("parseDuration('2h30m')"), log("parseDuration('45m')"), log("parseDuration('90s')"), log("parseDuration('abc')"), log("parseDuration('')")],
                ["9000", "2700", "90", "null", "null"],
                "function parseDuration(s: string): number | null {\n  const m = /^(?:(\\d+)h)?(?:(\\d+)m)?(?:(\\d+)s)?$/.exec(s);\n  if (!m || s === '') return null;\n  return Number(m[1] ?? 0) * 3600 + Number(m[2] ?? 0) * 60 + Number(m[3] ?? 0);\n}",
                forbid=[r":\s*any\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Capstone projects",
        lesson(
            "A typed reducer store",
            """Combine unions, generics and closures into a small Redux-style store:

function createStore<S, A>(reducer: (state: S, action: A) => S, initial: S) {
  let state = initial;
  const listeners: (() => void)[] = [];
  return {
    getState: (): S => state,
    dispatch(action: A): void { state = reducer(state, action); listeners.forEach((l) => l()); },
    subscribe(l: () => void): void { listeners.push(l); },
  };
}

Because A is a discriminated union of actions, dispatching a wrong action is a compile error.""",
            mcq("What does dispatch(action) do?", ["Computes the next state via the reducer and notifies listeners", "Mutates state in place", "Reads state", "Creates actions"], 0),
            mcq("Why is the action type a union?", ["So only valid actions can be dispatched", "To save memory", "To use classes", "To avoid generics"], 0),
            mcq("What must a reducer never do?", ["Mutate the old state", "Return a new object", "Use switch", "Take two arguments"], 0),
            run("Write createStore<S, A>(reducer, initial) with getState, dispatch and subscribe. The test uses a counter reducer with actions 'inc' | 'dec' | { type: 'add'; n: number }.", "typescript",
                [t("flow", append="type Action = { type: 'inc' } | { type: 'dec' } | { type: 'add'; n: number };\nconst store = createStore((s: number, a: Action) => (a.type === 'inc' ? s + 1 : a.type === 'dec' ? s - 1 : s + a.n), 0);\nlet calls = 0;\nstore.subscribe(() => calls++);\nstore.dispatch({ type: 'inc' });\nstore.dispatch({ type: 'add', n: 10 });\nstore.dispatch({ type: 'dec' });\nconsole.log(store.getState(), calls);"),
                 t("rejects", append="type Action = { type: 'inc' };\nconst store = createStore((s: number, a: Action) => s + 1, 0);\n" + REJECTS + "store.dispatch({ type: 'boom' });\nconsole.log('checked');")],
                ["10 3", "checked"],
                "function createStore<S, A>(reducer: (state: S, action: A) => S, initial: S) {\n  let state = initial;\n  const listeners: (() => void)[] = [];\n  return {\n    getState: (): S => state,\n    dispatch(action: A): void {\n      state = reducer(state, action);\n      listeners.forEach((l) => l());\n    },\n    subscribe(l: () => void): void {\n      listeners.push(l);\n    },\n  };\n}",
                forbid=[r":\s*any\b"]),
        ),
        lesson(
            "Typed route params",
            """Template literal types can read a route pattern and produce the parameter names:

type Params<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` ? Name | Params<`/${Rest}`> :
  P extends `${string}:${infer Name}` ? Name : never;

type P = Params<"/users/:id/posts/:postId">;     // "id" | "postId"

function path<P extends string>(pattern: P, params: Record<Params<P>, string>): string { ... }

Forgetting a parameter, or adding a wrong one, becomes a compile error.""",
            mcq("What does Params<'/users/:id'> evaluate to?", ["'id'", "'users'", "string", "never"], 0),
            mcq("What happens if you forget a route parameter?", ["Compile error", "Runtime crash only", "Nothing", "An empty URL"], 0),
            mcq("Which features make this possible?", ["Template literal and conditional types", "Classes", "Enums", "Decorators"], 0),
            run("Write a type Params<P extends string> that extracts the :names from a path like '/users/:id/posts/:postId', and a function url<P extends string>(pattern: P, params: Record<Params<P>, string>): string replacing each :name with its value.", "typescript",
                [log("url('/users/:id/posts/:postId', { id: '7', postId: '42' })"), log("url('/home', {})"), t("rejects", append=REJECTS + "url('/users/:id', {});\nconsole.log('checked');")],
                ["/users/7/posts/42", "/home", "checked"],
                "type Params<P extends string> = P extends `${string}:${infer Name}/${infer Rest}` ? Name | Params<`/${Rest}`> : P extends `${string}:${infer Name}` ? Name : never;\n\nfunction url<P extends string>(pattern: P, params: Record<Params<P>, string>): string {\n  return pattern.replace(/:(\\w+)/g, (_, name: string) => (params as Record<string, string>)[name]);\n}",
                require=[r"infer"]),
        ),
        lesson(
            "Typed config with defaults",
            """Merge user options with defaults and keep precise types using Partial and Required:

interface Options { host: string; port: number; secure: boolean }
const defaults: Options = { host: "localhost", port: 80, secure: false };

function configure(opts: Partial<Options> = {}): Options {
  return { ...defaults, ...opts };
}

Partial<T> makes every field optional for the caller; the function still RETURNS the full Options. Spread order matters: later keys win.""",
            mcq("What does Partial<Options> mean?", ["Every field is optional", "Fields are removed", "Fields are readonly", "Fields are strings"], 0),
            mcq("In { ...defaults, ...opts }, which wins on a clash?", ["opts", "defaults", "The first", "Neither"], 0),
            mcq("What does the function return?", ["The full Options", "Partial<Options>", "void", "unknown"], 0),
            run("Write interface Options { host: string; port: number; secure: boolean }, defaults, and configure(opts: Partial<Options> = {}): Options. Add describe(o: Options): string returning 'http(s)://host:port'.", "typescript",
                [log("describe(configure())"), log("describe(configure({ port: 8080, secure: true }))"), t("rejects", append=REJECTS + "configure({ port: '80' });\nconsole.log('checked');")],
                ["http://localhost:80", "https://localhost:8080", "checked"],
                "interface Options {\n  host: string;\n  port: number;\n  secure: boolean;\n}\nconst defaults: Options = { host: 'localhost', port: 80, secure: false };\n\nfunction configure(opts: Partial<Options> = {}): Options {\n  return { ...defaults, ...opts };\n}\nfunction describe(o: Options): string {\n  return `${o.secure ? 'https' : 'http'}://${o.host}:${o.port}`;\n}",
                require=[r"Partial<Options>"]),
        ),
        lesson(
            "Mini project: a typed command parser",
            """Put it together: parse text commands into a discriminated union, then run them exhaustively.

type Command = { kind: "add"; n: number } | { kind: "reset" } | { kind: "unknown"; text: string };

function parse(line: string): Command { ... }
function run(total: number, c: Command): number {
  switch (c.kind) { case "add": return total + c.n; case "reset": return 0; case "unknown": return total; }
}

Parsing at the edge into a precise union means the rest of the program only deals with valid, typed data.""",
            mcq("Why parse into a union first?", ["The rest of the code deals only with valid typed data", "It is shorter", "It avoids switch", "It is faster"], 0),
            mcq("What does a switch over c.kind give you?", ["Narrowed variants and exhaustiveness checks", "Nothing", "Runtime types", "Speed"], 0),
            mcq("What does the 'unknown' variant keep?", ["The original text for error messages", "A number", "Nothing", "A function"], 0),
            run("Write type Command = {kind:'add'; n:number} | {kind:'sub'; n:number} | {kind:'reset'} | {kind:'unknown'; text:string}, parse(line: string): Command ('add 5', 'sub 2', 'reset'; anything else, including a missing or non-numeric number, is unknown) and run(commands: string[]): number applying them from 0 (unknown commands are ignored).", "typescript",
                [log("run(['add 5', 'add 10', 'sub 3'])"), log("run(['add 4', 'reset', 'add 2', 'jump'])"), log("run(['add x', 'sub'])"), log("parse('sub 2').kind")],
                ["12", "2", "0", "sub"],
                "type Command =\n  | { kind: 'add'; n: number }\n  | { kind: 'sub'; n: number }\n  | { kind: 'reset' }\n  | { kind: 'unknown'; text: string };\n\nfunction parse(line: string): Command {\n  const [word, arg] = line.split(' ');\n  const n = Number(arg);\n  if (word === 'reset') return { kind: 'reset' };\n  if ((word === 'add' || word === 'sub') && arg !== undefined && Number.isFinite(n)) return { kind: word, n };\n  return { kind: 'unknown', text: line };\n}\n\nfunction run(commands: string[]): number {\n  let total = 0;\n  for (const c of commands.map(parse)) {\n    switch (c.kind) {\n      case 'add':\n        total += c.n;\n        break;\n      case 'sub':\n        total -= c.n;\n        break;\n      case 'reset':\n        total = 0;\n        break;\n      case 'unknown':\n        break;\n    }\n  }\n  return total;\n}",
                require=[r"kind:\s*'unknown'"]),
        ),
    ),
)
