"""JavaScript projects - one at the end of each section (added to units 8, 12 and 16)."""
from .dsl import project, run, t

# ------------------------------------------------------------------ Beginner: to-do list
TODO1 = '''const todos = [];
let nextId = 1;

function addTodo(text) {
  const todo = { id: nextId++, text, done: false };
  todos.push(todo);
  return todo;
}'''

TODO2 = TODO1 + '''

function complete(id) {
  const todo = todos.find((t) => t.id === id);
  if (!todo) return false;
  todo.done = true;
  return true;
}

function remaining() {
  return todos.filter((t) => !t.done).length;
}'''

TODO3 = TODO2 + '''

function render() {
  return todos.map((t) => `[${t.done ? "x" : " "}] ${t.id}. ${t.text}`).join("\\n");
}'''

ADD3 = 'addTodo("Learn JS"); addTodo("Build app"); addTodo("Ship it");\n'

BEGINNER = project(
    "Project: To-do list",
    "Let's build the classic first app: a to-do list. Three steps, each continuing from your own code:\n\n1. Add "
    "to-dos with automatic ids.\n2. Complete them and count what's left.\n3. Render the list as text.",
    run("Step 1 - Keep an array todos and a counter. addTodo(text) adds {id, text, done: false} (ids start at 1) and "
        "returns it.", "javascript",
        [t("add", append='console.log(addTodo("Learn JS"));\nconsole.log(addTodo("Build app").id);'),
         t("stored", append=ADD3 + "console.log(todos.length);")],
        ["{ id: 1, text: 'Learn JS', done: false }\n2", "3"], TODO1, require=[r"function\s+addTodo|addTodo\s*="]),
    run("Step 2 - Add complete(id) (marks it done; returns true, or false if there's no such id) and remaining() "
        "(how many aren't done).", "javascript",
        [t("complete", append=ADD3 + "console.log(complete(2), complete(9));\nconsole.log(remaining());")],
        ["true false\n2"], TODO2, starter=TODO1, carry=True, require=[r"complete", r"remaining"]),
    run("Step 3 - Add render() returning one line per to-do: '[x] 2. Build app' when done, '[ ] 1. Learn JS' when not.",
        "javascript",
        [t("render", append=ADD3 + "complete(2);\nconsole.log(render());"),
         t("empty", append='console.log(JSON.stringify(render()));')],
        ["[ ] 1. Learn JS\n[x] 2. Build app\n[ ] 3. Ship it", '""'], TODO3, starter=TODO2, carry=True,
        require=[r"function\s+render|render\s*="]),
)

# ------------------------------------------------------------------ Intermediate: shopping cart
CART1 = '''class Cart {
  #items = [];

  add(name, price, qty = 1) {
    const found = this.#items.find((i) => i.name === name);
    if (found) found.qty += qty;
    else this.#items.push({ name, price, qty });
    return this;
  }

  get count() {
    return this.#items.reduce((n, i) => n + i.qty, 0);
  }

  get items() {
    return this.#items.map((i) => ({ ...i }));
  }
}'''

CART2 = CART1.replace('''  get items() {''', '''  subtotal() {
    return this.#items.reduce((sum, i) => sum + i.price * i.qty, 0);
  }

  remove(name) {
    this.#items = this.#items.filter((i) => i.name !== name);
    return this;
  }

  get items() {''')

CART3 = CART2.replace('''class Cart {
  #items = [];
''', '''const COUPONS = { SAVE10: 0.1, HALF: 0.5 };

class Cart {
  #items = [];
  #discount = 0;

  applyCoupon(code) {
    const rate = COUPONS[code.toUpperCase()];
    if (rate === undefined) throw new Error(`Unknown coupon: ${code}`);
    this.#discount = rate;
    return this;
  }

  total() {
    return Math.round(this.subtotal() * (1 - this.#discount) * 100) / 100;
  }
''')

FILL = 'const cart = new Cart().add("pen", 1.5, 2).add("book", 12).add("pen", 1.5);\n'

INTERMEDIATE = project(
    "Project: Shopping cart",
    "Build the shopping cart every online shop needs, using a class with private fields:\n\n1. Add items (merging "
    "duplicates) and count them.\n2. Subtotal and removing items.\n3. Coupons and the final total.",
    run("Step 1 - class Cart with a private #items array. add(name, price, qty = 1) merges an existing item's qty and "
        "returns this (so calls chain). A count getter sums the quantities; an items getter returns copies.",
        "javascript",
        [t("add & count", append=FILL + "console.log(cart.count);\nconsole.log(cart.items);"),
         t("private", append=FILL + "console.log(Object.keys(cart).length);")],
        ["4\n[ { name: 'pen', price: 1.5, qty: 3 }, { name: 'book', price: 12, qty: 1 } ]", "0"],
        CART1, require=[r"class\s+Cart", r"#items"]),
    run("Step 2 - Add subtotal() (price × qty summed) and remove(name).", "javascript",
        [t("subtotal", append=FILL + "console.log(cart.subtotal());\nconsole.log(cart.remove(\"pen\").subtotal());")],
        ["16.5\n12"], CART2, starter=CART1, carry=True, require=[r"subtotal\s*\(", r"remove\s*\("]),
    run("Step 3 - Add applyCoupon(code) (SAVE10 = 10% off, HALF = 50% off, case-insensitive; unknown codes throw "
        "Error('Unknown coupon: CODE')) and total() (discounted subtotal rounded to cents).", "javascript",
        [t("coupon", append=FILL + "console.log(cart.total());\nconsole.log(cart.applyCoupon(\"save10\").total());"),
         t("unknown", append=FILL + 'try {\n  cart.applyCoupon("FREE");\n} catch (e) {\n  console.log(e.message);\n}')],
        ["16.5\n14.85", "Unknown coupon: FREE"], CART3, starter=CART2, carry=True,
        require=[r"applyCoupon", r"throw\s+new\s+Error"]),
)

# ------------------------------------------------------------------ Advanced: task runner
TASK1 = '''const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function runSequential(tasks) {
  const results = [];
  for (const task of tasks) {
    results.push(await task());
  }
  return results;
}'''

TASK2 = TASK1 + '''

async function runLimited(tasks, limit) {
  const results = new Array(tasks.length);
  let next = 0;
  async function worker() {
    while (next < tasks.length) {
      const i = next++;
      results[i] = await tasks[i]();
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, tasks.length) }, worker));
  return results;
}'''

TASK3 = TASK2 + '''

async function retry(fn, attempts) {
  let lastError;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}'''

MAKE = '''const log = [];
let running = 0, peak = 0;
const job = (name, ms) => async () => {
  running++; peak = Math.max(peak, running); log.push("start " + name);
  await sleep(ms);
  running--; log.push("end " + name);
  return name.toUpperCase();
};
'''

ADVANCED = project(
    "Project: Async task runner",
    "Servers and build tools run lots of async jobs. You'll write a tiny task runner:\n\n1. Run tasks one after "
    "another.\n2. Run them in parallel - but never more than N at once - keeping results in order.\n3. Retry flaky "
    "tasks.\n\nA task is a function that returns a promise.",
    run("Step 1 - Write sleep(ms) and async runSequential(tasks): await each task in turn and return the results "
        "array.", "javascript",
        [t("sequential", append=MAKE + 'runSequential([job("a", 30), job("b", 10)]).then((r) => console.log(r, log.join(", "), peak));')],
        ["[ 'A', 'B' ] start a, end a, start b, end b 1"], TASK1, require=[r"async\s+function\s+runSequential", r"await"]),
    run("Step 2 - Add runLimited(tasks, limit): run up to `limit` tasks at the same time, start the next as soon as one "
        "finishes, and return results in the original order.", "javascript",
        [t("limit 2", append=MAKE + 'runLimited([job("a", 40), job("b", 10), job("c", 10), job("d", 10)], 2)'
                                   '.then((r) => console.log(r, peak));'),
         t("limit bigger than tasks", append=MAKE + 'runLimited([job("x", 5)], 4).then((r) => console.log(r, peak));')],
        ["[ 'A', 'B', 'C', 'D' ] 2", "[ 'X' ] 1"], TASK2, starter=TASK1, carry=True, require=[r"runLimited"]),
    run("Step 3 - Add retry(fn, attempts): call fn until it resolves; if every attempt fails, throw the last error.",
        "javascript",
        [t("flaky", append='let calls = 0;\nconst flaky = async () => { calls++; if (calls < 3) throw new Error("fail " + calls); return "ok"; };\n'
                           'retry(flaky, 5).then((r) => console.log(r, calls));'),
         t("gives up", append='const broken = async () => { throw new Error("down"); };\n'
                              'retry(broken, 2).catch((e) => console.log("gave up:", e.message));')],
        ["ok 3", "gave up: down"], TASK3, starter=TASK2, carry=True, require=[r"retry"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
