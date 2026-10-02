"""TypeScript projects - one at the end of each section (added to units 4, 6 and 8)."""
from .dsl import project, run, t
from .typescript import REJECTS

# ------------------------------------------------------------------ Beginner: typed shopping cart
CART_1 = """interface Item {
  name: string;
  price: number;
  qty: number;
}

function addItem(cart: Item[], item: Item): Item[] {
  if (cart.some((i) => i.name === item.name)) {
    return cart.map((i) => (i.name === item.name ? { ...i, qty: i.qty + item.qty } : i));
  }
  return [...cart, item];
}

function subtotal(cart: Item[]): number {
  return cart.reduce((sum, i) => sum + i.price * i.qty, 0);
}
"""
CART_2 = CART_1 + """
type Discount = { kind: "percent"; amount: number } | { kind: "fixed"; amount: number };

function total(cart: Item[], discount?: Discount): number {
  const sub = subtotal(cart);
  if (!discount) return sub;
  const off = discount.kind === "percent" ? (sub * discount.amount) / 100 : discount.amount;
  return Math.max(0, Math.round((sub - off) * 100) / 100);
}
"""
CART_3 = CART_2 + """
function receipt(cart: Item[], discount?: Discount): string[] {
  const lines = cart.map((i) => `${i.name} x${i.qty} ${(i.price * i.qty).toFixed(2)}`);
  const sum = total(cart, discount);
  if (discount) lines.push(`discount -${(subtotal(cart) - sum).toFixed(2)}`);
  lines.push(`total ${sum.toFixed(2)}`);
  return lines;
}
"""
FILL_CART = """let cart: Item[] = [];
cart = addItem(cart, { name: "pen", price: 1.5, qty: 2 });
cart = addItem(cart, { name: "book", price: 12, qty: 1 });
cart = addItem(cart, { name: "pen", price: 1.5, qty: 1 });
"""

BEGINNER = project(
    "Project: Typed shopping cart",
    "Build the logic behind an online shop's cart - and let the types catch mistakes:\n\n1. An Item interface, "
    "adding items (same name = more quantity) and a subtotal.\n2. Discount codes as a discriminated union.\n3. A "
    "printable receipt.\n\nThe tests also try some WRONG calls marked // @ts-expect-error - they only pass when your types "
    "reject them.",
    run("Step 1 - Declare interface Item { name; price; qty }, addItem(cart, item) that returns a NEW cart (adding the "
        "quantity if the name is already there), and subtotal(cart).", "typescript",
        [t("cart", append=FILL_CART + "console.log(cart.length, cart[0].qty, subtotal(cart));"),
         t("types", append="const c: Item[] = [];\n" + REJECTS + 'addItem(c, { name: "x", price: 1 });\nconsole.log(subtotal(c));')],
        ["2 3 16.5", "0"], CART_1, starter="interface Item {\n  // name, price and qty\n}\n",
        require=[r"interface\s+Item"], forbid=[r"\bany\b"]),
    run("Step 2 - Add type Discount = { kind: \"percent\"; amount } | { kind: \"fixed\"; amount } and total(cart, "
        "discount?) - never below 0, rounded to cents.", "typescript",
        [t("discounts", append=FILL_CART + 'console.log(total(cart));\nconsole.log(total(cart, { kind: "percent", amount: 10 }));\n'
                                           'console.log(total(cart, { kind: "fixed", amount: 20 }));'),
         t("types", append="const c: Item[] = [];\n" + REJECTS + 'total(c, { kind: "bogo", amount: 1 });\nconsole.log(total(c));')],
        ["16.5\n14.85\n0", "0"], CART_2, starter=CART_1, carry=True, require=[r"kind\s*:\s*\"percent\""], forbid=[r"\bany\b"]),
    run("Step 3 - Write receipt(cart, discount?): string[] - one line per item ('pen x3 4.50'), then 'discount -1.65' if "
        "a discount was given, then 'total 14.85'. Money always has 2 decimals.", "typescript",
        [t("receipt", append=FILL_CART + 'console.log(receipt(cart, { kind: "percent", amount: 10 }).join("\\n"));'),
         t("no discount", append=FILL_CART + 'console.log(receipt(cart).join("\\n"));')],
        ["pen x3 4.50\nbook x1 12.00\ndiscount -1.65\ntotal 14.85", "pen x3 4.50\nbook x1 12.00\ntotal 16.50"],
        CART_3, starter=CART_2, carry=True, require=[r"toFixed\(\s*2\s*\)"], forbid=[r"\bany\b"]),
)

# ------------------------------------------------------------------ Intermediate: generic data store
STORE_HEAD = """class Store<T extends { id: number }> {
  private items = new Map<number, T>();
"""
STORE_GET = """
  get(id: number): T | undefined {
    return this.items.get(id);
  }

  all(): T[] {
    return [...this.items.values()];
  }
"""
STORE_QUERY = """
  where<K extends keyof T>(key: K, value: T[K]): T[] {
    return this.all().filter((item) => item[key] === value);
  }
"""
STORE_1 = STORE_HEAD + """
  add(item: T): void {
    this.items.set(item.id, item);
  }
""" + STORE_GET + "}\n"
STORE_2 = STORE_HEAD + """
  add(item: T): void {
    this.items.set(item.id, item);
  }

  remove(id: number): boolean {
    return this.items.delete(id);
  }
""" + STORE_GET + STORE_QUERY + "}\n"
STORE_3 = """type StoreEvent<T> = { type: "added"; item: T } | { type: "removed"; id: number };

""" + STORE_HEAD + """  private listeners: ((event: StoreEvent<T>) => void)[] = [];

  subscribe(listener: (event: StoreEvent<T>) => void): void {
    this.listeners.push(listener);
  }

  private emit(event: StoreEvent<T>): void {
    for (const listener of this.listeners) listener(event);
  }

  add(item: T): void {
    this.items.set(item.id, item);
    this.emit({ type: "added", item });
  }

  remove(id: number): boolean {
    const removed = this.items.delete(id);
    if (removed) this.emit({ type: "removed", id });
    return removed;
  }
""" + STORE_GET + STORE_QUERY + "}\n"
BOOKS = """interface Book {
  id: number;
  title: string;
  author: string;
}
const s = new Store<Book>();
s.add({ id: 1, title: "Dune", author: "Herbert" });
s.add({ id: 2, title: "Emma", author: "Austen" });
s.add({ id: 3, title: "Persuasion", author: "Austen" });
"""

INTERMEDIATE = project(
    "Project: Generic data store",
    "Build a tiny in-memory database that works for ANY record type - the kind of class real apps use for "
    "caches and state:\n\n1. A generic Store<T> keyed by id.\n2. Type-safe queries and removal.\n3. Change events "
    "listeners can subscribe to.",
    run("Step 1 - Write class Store<T extends { id: number }> with add(item), get(id): T | undefined and all(): T[], "
        "keeping items in a private Map.", "typescript",
        [t("books", append=BOOKS + "console.log(s.get(2)?.title, s.all().length, s.get(9));"),
         t("types", append=BOOKS + REJECTS + 's.add({ id: 4, title: "No author" });\n' + REJECTS + "const bad = new Store<string>();\nconsole.log(s.all().length);")],
        ["Emma 3 undefined", "4"], STORE_1, starter="class Store<T extends { id: number }> {\n}\n",
        require=[r"class\s+Store\s*<\s*T\s+extends", r"private"], forbid=[r"\bany\b"]),
    run("Step 2 - Add remove(id): boolean and where<K extends keyof T>(key: K, value: T[K]): T[] - so only real property "
        "names and matching value types are accepted.", "typescript",
        [t("query", append=BOOKS + 'console.log(s.where("author", "Austen").map((b) => b.title));\nconsole.log(s.remove(1), s.remove(1), s.all().length);'),
         t("types", append=BOOKS + REJECTS + 's.where("author", 42);\n' + REJECTS + 's.where("year", 1999);\nconsole.log("checked");')],
        ["[ 'Emma', 'Persuasion' ]\ntrue false 2", "checked"], STORE_2, starter=STORE_1, carry=True,
        require=[r"K\s+extends\s+keyof\s+T"], forbid=[r"\bany\b"]),
    run("Step 3 - Add change events: type StoreEvent<T> = { type: \"added\"; item: T } | { type: \"removed\"; id: number }, "
        "subscribe(listener), and emit an event from add and (successful) remove.", "typescript",
        [t("events", append="interface Book {\n  id: number;\n  title: string;\n  author: string;\n}\nconst s = new Store<Book>();\n"
                             "s.subscribe((e) => console.log(e.type === \"added\" ? `+ ${e.item.title}` : `- #${e.id}`));\n"
                             's.add({ id: 1, title: "Dune", author: "Herbert" });\ns.add({ id: 2, title: "Emma", author: "Austen" });\n'
                             "s.remove(1);\ns.remove(1);\nconsole.log(s.all().length);")],
        ["+ Dune\n+ Emma\n- #1\n1"], STORE_3, starter=STORE_2, carry=True, require=[r"StoreEvent", r"subscribe"], forbid=[r"\bany\b"]),
)

# ------------------------------------------------------------------ Advanced: type-safe API client
API_1 = """type Status = "todo" | "doing" | "done";

interface Task {
  id: number;
  title: string;
  status: Status;
}

const STATUSES: readonly string[] = ["todo", "doing", "done"];

function isTask(v: unknown): v is Task {
  if (typeof v !== "object" || v === null) return false;
  const t = v as Record<string, unknown>;
  return typeof t.id === "number" && typeof t.title === "string" && typeof t.status === "string" && STATUSES.includes(t.status);
}

function parseTasks(json: string): Task[] {
  const data: unknown = JSON.parse(json);
  return Array.isArray(data) ? data.filter(isTask) : [];
}
"""
API_2 = API_1 + """
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

async function loadTasks(path: string): Promise<Result<Task[]>> {
  try {
    const text = await fakeFetch(path);
    return { ok: true, value: parseTasks(text) };
  } catch (e) {
    if (e instanceof SyntaxError) return { ok: false, error: "bad JSON" };
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}
"""
API_3 = API_2 + """
function label(status: Status): string {
  switch (status) {
    case "todo":
      return "To do";
    case "doing":
      return "In progress";
    case "done":
      return "Done";
    default: {
      const unreachable: never = status;
      return unreachable;
    }
  }
}

function report(tasks: Task[]): string[] {
  const counts: Record<Status, number> = { todo: 0, doing: 0, done: 0 };
  for (const task of tasks) counts[task.status]++;
  return (Object.keys(counts) as Status[]).map((s) => `${label(s)}: ${counts[s]}`);
}
"""
TASKS_JSON = ('[{"id":1,"title":"Plan","status":"done"},{"id":2,"title":"Build","status":"doing"},'
              '{"id":3,"title":"Test","status":"todo"},{"id":4,"title":"Ship","status":"todo"},'
              '{"id":"5","title":"Bad id","status":"todo"},{"id":6,"title":"Bad status","status":"later"}]')
# the "server" the tests provide (fakeFetch is declared after your code - function declarations are hoisted)
FAKE_SERVER = ("const SERVER: Record<string, string> = {\n  \"/tasks\": " + repr(TASKS_JSON) + ",\n  \"/broken\": \"{not json\",\n};\n"
               "function fakeFetch(path: string): Promise<string> {\n  return new Promise((resolve, reject) =>\n"
               "    setTimeout(() => (path in SERVER ? resolve(SERVER[path]) : reject(new Error(`404 ${path}`))), 20),\n  );\n}\n")

ADVANCED = project(
    "Project: Type-safe API client",
    "Real apps talk to servers, and server data can be anything. Build a client that never trusts it:\n\n1. Validate "
    "raw JSON into Task objects with a type guard.\n2. Load tasks asynchronously and return a Result instead of "
    "throwing.\n3. A status report with an exhaustive switch.\n\nFrom step 2 the tests provide "
    "fakeFetch(path: string): Promise<string> - a pretend server with /tasks and a /broken endpoint.",
    run("Step 1 - Define type Status = \"todo\" | \"doing\" | \"done\", interface Task { id; title; status }, a type guard "
        "isTask(v: unknown): v is Task, and parseTasks(json: string): Task[] that keeps only valid tasks.", "typescript",
        [t("parse", append=f"console.log(parseTasks({TASKS_JSON!r}).map((t) => t.title));\nconsole.log(parseTasks('{{\"id\":1}}'));")],
        ["[ 'Plan', 'Build', 'Test', 'Ship' ]\n[]"], API_1, starter="type Status = \"todo\" | \"doing\" | \"done\";\n",
        require=[r"v\s+is\s+Task", r"unknown"], forbid=[r"\bany\b"]),
    run("Step 2 - Add type Result<T> = { ok: true; value: T } | { ok: false; error: string } and async "
        "loadTasks(path): Promise<Result<Task[]>> using fakeFetch. Never throw: a failed request gives its error "
        "message, invalid JSON gives 'bad JSON'.", "typescript",
        [t("load", append=FAKE_SERVER + "async function main() {\n  for (const path of [\"/tasks\", \"/missing\", \"/broken\"]) {\n"
                                         "    const r = await loadTasks(path);\n    console.log(r.ok ? `${r.value.length} tasks` : `error: ${r.error}`);\n  }\n"
                                         "  const r = await loadTasks(\"/tasks\");\n  " + REJECTS + "  r.value;\n}\nmain();")],
        ["4 tasks\nerror: 404 /missing\nerror: bad JSON"], API_2, starter=API_1, carry=True,
        require=[r"Promise\s*<\s*Result\s*<\s*Task\[\]\s*>\s*>", r"catch"], forbid=[r"\bany\b"]),
    run("Step 3 - Write label(status: Status) with an exhaustive switch (a never check in default) and report(tasks): "
        "string[] - one 'Label: count' line per status, in the order todo, doing, done.", "typescript",
        [t("report", append=FAKE_SERVER + "async function main() {\n  const r = await loadTasks(\"/tasks\");\n"
                                           "  if (r.ok) console.log(report(r.value).join(\"\\n\"));\n}\nmain();")],
        ["To do: 2\nIn progress: 1\nDone: 1"], API_3, starter=API_2, carry=True, require=[r":\s*never\s*=", r"Record\s*<\s*Status"],
        forbid=[r"\bany\b"]),
)

PROJECTS = {4: BEGINNER, 6: INTERMEDIATE, 8: ADVANCED}
