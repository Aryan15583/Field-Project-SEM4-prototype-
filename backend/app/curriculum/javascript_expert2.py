"""JavaScript - Expert section, part 2 (units 23-29): async patterns, data structures, algorithms, graphs, numbers,
design patterns and mini-projects."""
from .dsl import fill, lesson, mcq, order, run, section, t, unit


def log(expr: str) -> dict:
    return t(expr, append=f"console.log({expr});")


def js(expr: str) -> dict:
    return t(expr, append=f"console.log(JSON.stringify({expr}));")


EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Async patterns",
        lesson(
            "Retry and timeout",
            """Real networks fail. Two everyday patterns:

Retry - try again a few times before giving up:

async function retry(fn, times) {
  for (let i = 1; ; i++) {
    try { return await fn(); }
    catch (err) { if (i >= times) throw err; }
  }
}

Timeout - race the work against a timer with Promise.race:

Promise.race([work(), new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 100))]);""",
            mcq("What does Promise.race resolve or reject with?", ["The first promise to settle", "The last promise", "All results", "The slowest"], 0),
            mcq("In retry(), when do we rethrow the error?", ["After the last attempt fails", "Immediately", "Never", "Before the first try"], 0),
            mcq("Why retry only a limited number of times?", ["To avoid looping forever on a permanent failure", "It's required by async", "To save memory", "To sort errors"], 0),
            run("Write async retry(fn, times) that calls fn until it succeeds, giving up (throwing the last error) after times attempts.", "javascript",
                [t("succeeds on 3rd", append="let n = 0;\nretry(async () => { if (++n < 3) throw new Error('fail' + n); return 'ok'; }, 5).then((v) => console.log(v, n));"),
                 t("gives up", append="let n = 0;\nretry(async () => { n++; throw new Error('boom' + n); }, 2).catch((e) => console.log(e.message, n));")],
                ["ok 3", "boom2 2"],
                "async function retry(fn, times) {\n  for (let i = 1; ; i++) {\n    try {\n      return await fn();\n    } catch (err) {\n      if (i >= times) throw err;\n    }\n  }\n}",
                require=[r"\basync\b", r"\bawait\b"]),
        ),
        lesson(
            "Sequential vs parallel",
            """await in a loop runs tasks ONE AFTER ANOTHER. Promise.all runs them AT THE SAME TIME:

// sequential - total time = sum of the delays
for (const id of ids) results.push(await load(id));

// parallel - total time = the longest delay
const results = await Promise.all(ids.map(load));

Use sequential when order or rate limits matter; use parallel for independent work. Promise.allSettled never rejects - it reports each outcome as { status, value | reason }.""",
            mcq("What is the total time of three awaited 100 ms tasks in a for loop?", ["About 300 ms", "About 100 ms", "About 0 ms", "About 600 ms"], 0),
            mcq("What is the total time with Promise.all of the same three?", ["About 100 ms", "About 300 ms", "About 33 ms", "About 1 s"], 0),
            mcq("Which never rejects?", ["Promise.allSettled", "Promise.all", "Promise.race", "Promise.any"], 0),
            run("Write async settleAll(tasks) where tasks is an array of functions returning promises. Run them in parallel and resolve to an array of 'ok:<value>' or 'fail:<message>' strings in the same order.", "javascript",
                [t("mixed", append="settleAll([async () => 1, async () => { throw new Error('x'); }, async () => 3]).then((r) => console.log(r.join(' ')));"),
                 t("empty", append="settleAll([]).then((r) => console.log(r.length));")],
                ["ok:1 fail:x ok:3", "0"],
                "async function settleAll(tasks) {\n  const results = await Promise.allSettled(tasks.map((fn) => fn()));\n  return results.map((r) => (r.status === 'fulfilled' ? 'ok:' + r.value : 'fail:' + r.reason.message));\n}",
                require=[r"allSettled|Promise\.all"]),
        ),
        lesson(
            "Concurrency limits & async iteration",
            """Starting 1000 requests at once can overload a server. A pool runs only N at a time:

async function pool(items, limit, worker) {
  const results = [];
  let next = 0;
  async function lane() {
    while (next < items.length) {
      const i = next++;
      results[i] = await worker(items[i]);
    }
  }
  await Promise.all(Array.from({ length: limit }, lane));
  return results;
}

for await (const x of asyncIterable) loops over values that arrive over time, such as pages of results or streams.""",
            mcq("Why limit concurrency?", ["To avoid overloading servers or memory", "To make code synchronous", "To sort results", "It's required by await"], 0),
            mcq("What does for await...of loop over?", ["Async iterables (values that arrive over time)", "Only arrays", "Only strings", "Only promises once"], 0),
            mcq("In pool(), what do the 'lanes' share?", ["The next index counter", "A copy of items each", "Nothing", "The results of other lanes"], 0),
            run("Write async pool(items, limit, worker) that runs worker(item) for every item with at most `limit` running at once and returns results in item order. The test records the maximum concurrency.", "javascript",
                [t("limit 2", append="let active = 0, max = 0;\nconst worker = async (x) => { active++; max = Math.max(max, active); await new Promise((r) => setTimeout(r, 10)); active--; return x * 2; };\npool([1, 2, 3, 4, 5], 2, worker).then((r) => console.log(r.join(','), max));"),
                 t("limit 1", append="let active = 0, max = 0;\nconst worker = async (x) => { active++; max = Math.max(max, active); await null; active--; return x; };\npool([7, 8, 9], 1, worker).then((r) => console.log(r.join(','), max));")],
                ["2,4,6,8,10 2", "7,8,9 1"],
                "async function pool(items, limit, worker) {\n  const results = [];\n  let next = 0;\n  async function lane() {\n    while (next < items.length) {\n      const i = next++;\n      results[i] = await worker(items[i]);\n    }\n  }\n  await Promise.all(Array.from({ length: limit }, lane));\n  return results;\n}",
                require=[r"\basync\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Data structures in JavaScript",
        lesson(
            "Stacks and queues",
            """A stack is last-in-first-out (LIFO); a queue is first-in-first-out (FIFO).

stack.push(x); stack.pop();        // arrays are great stacks - both O(1)
queue.push(x); queue.shift();      // shift() is O(n) on big arrays!

For a fast queue keep a head index instead of shifting:

class Queue {
  #items = []; #head = 0;
  enqueue(x) { this.#items.push(x); }
  dequeue() { return this.#items[this.#head++]; }
  get size() { return this.#items.length - this.#head; }
}

Stacks power undo, the call stack and bracket matching; queues power task lines and breadth-first search.""",
            mcq("Which order does a stack follow?", ["Last in, first out", "First in, first out", "Random", "Sorted"], 0),
            mcq("Which array method removes from the END (stack pop)?", ["pop()", "shift()", "splice(0, 1)", "slice()"], 0),
            mcq("Why can shift() be slow on a huge array?", ["It moves every remaining item", "It sorts", "It copies twice", "It is async"], 0),
            run("Write isBalanced(text) returning true if every (, [ and { is closed in the right order (ignore other characters). Use a stack.", "javascript",
                [log('isBalanced("([]{})")'), log('isBalanced("(]")'), log('isBalanced("((")'), log('isBalanced("a(b)c")')],
                ["true", "false", "false", "true"],
                "function isBalanced(text) {\n  const pairs = { ')': '(', ']': '[', '}': '{' };\n  const stack = [];\n  for (const ch of text) {\n    if ('([{'.includes(ch)) stack.push(ch);\n    else if (ch in pairs) {\n      if (stack.pop() !== pairs[ch]) return false;\n    }\n  }\n  return stack.length === 0;\n}",
                require=[r"\.push\(", r"\.pop\("]),
        ),
        lesson(
            "Linked lists",
            """A linked list is a chain of nodes, each pointing to the next. Inserting at the front is O(1); reaching the nth item is O(n).

class Node { constructor(value, next = null) { this.value = value; this.next = next; } }

class LinkedList {
  head = null;
  prepend(v) { this.head = new Node(v, this.head); }
  *[Symbol.iterator]() { for (let n = this.head; n; n = n.next) yield n.value; }
}

Reversing: walk the list, pointing each node back at the previous one.""",
            mcq("How fast is inserting at the head of a linked list?", ["O(1)", "O(n)", "O(log n)", "O(n²)"], 0),
            mcq("How do you reach the 5th node?", ["Walk from the head", "Index directly", "Binary search", "Hash it"], 0),
            mcq("What does a node contain?", ["A value and a pointer to the next node", "Only a value", "An index", "A key"], 0),
            run("Write class LinkedList with append(value), toArray(), and reverse() (reverses in place by re-pointing nodes).", "javascript",
                [t("append", append="const l = new LinkedList();\nl.append(1); l.append(2); l.append(3);\nconsole.log(l.toArray().join(','));"),
                 t("reverse", append="const l = new LinkedList();\n[1, 2, 3, 4].forEach((v) => l.append(v));\nl.reverse();\nconsole.log(l.toArray().join(','));"),
                 t("empty", append="const l = new LinkedList();\nl.reverse();\nconsole.log(l.toArray().length);")],
                ["1,2,3", "4,3,2,1", "0"],
                "class LinkedList {\n  constructor() {\n    this.head = null;\n  }\n  append(value) {\n    const node = { value, next: null };\n    if (!this.head) { this.head = node; return; }\n    let cur = this.head;\n    while (cur.next) cur = cur.next;\n    cur.next = node;\n  }\n  toArray() {\n    const out = [];\n    for (let n = this.head; n; n = n.next) out.push(n.value);\n    return out;\n  }\n  reverse() {\n    let prev = null;\n    let cur = this.head;\n    while (cur) {\n      const next = cur.next;\n      cur.next = prev;\n      prev = cur;\n      cur = next;\n    }\n    this.head = prev;\n  }\n}",
                require=[r"\.next"]),
        ),
        lesson(
            "LRU cache with Map",
            """A Map remembers insertion order, so it can build a Least-Recently-Used cache: when full, evict the OLDEST entry; every read moves an entry to the 'newest' end.

class LRU {
  constructor(max) { this.max = max; this.map = new Map(); }
  get(key) {
    if (!this.map.has(key)) return undefined;
    const v = this.map.get(key);
    this.map.delete(key);
    this.map.set(key, v);      // re-insert = newest
    return v;
  }
  set(key, v) {
    this.map.delete(key);
    this.map.set(key, v);
    if (this.map.size > this.max) this.map.delete(this.map.keys().next().value);
  }
}""",
            mcq("What does map.keys().next().value give?", ["The oldest inserted key", "The newest key", "A random key", "The size"], 0),
            mcq("Why delete then set on a read?", ["To move the key to the newest position", "To free memory", "To copy the value", "To sort"], 0),
            mcq("What does an LRU cache evict when full?", ["The least recently used entry", "The largest value", "The newest entry", "A random one"], 0),
            run("Write class LRU(max) with get(key) (undefined if missing) and set(key, value), evicting the least recently used when the size exceeds max.", "javascript",
                [t("evicts", append="const c = new LRU(2);\nc.set('a', 1); c.set('b', 2); c.get('a'); c.set('c', 3);\nconsole.log(c.get('a'), c.get('b'), c.get('c'));"),
                 t("overwrite", append="const c = new LRU(1);\nc.set('x', 1); c.set('x', 2);\nconsole.log(c.get('x'));")],
                ["1 undefined 3", "2"],
                "class LRU {\n  constructor(max) {\n    this.max = max;\n    this.map = new Map();\n  }\n  get(key) {\n    if (!this.map.has(key)) return undefined;\n    const v = this.map.get(key);\n    this.map.delete(key);\n    this.map.set(key, v);\n    return v;\n  }\n  set(key, v) {\n    this.map.delete(key);\n    this.map.set(key, v);\n    if (this.map.size > this.max) this.map.delete(this.map.keys().next().value);\n  }\n}",
                require=[r"new\s+Map"]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · Algorithms",
        lesson(
            "Sorting by hand: merge sort",
            """Merge sort splits the list in half, sorts each half recursively, then merges two sorted halves. It is O(n log n) and stable.

function mergeSort(a) {
  if (a.length <= 1) return a;
  const mid = a.length >> 1;
  return merge(mergeSort(a.slice(0, mid)), mergeSort(a.slice(mid)));
}

merge walks both halves with two pointers, always taking the smaller front item. Note: Array.prototype.sort sorts numbers as TEXT by default - always pass a comparator: arr.sort((a, b) => a - b).""",
            mcq("What does [10, 9, 1].sort() give?", ["[1, 10, 9]", "[1, 9, 10]", "[10, 9, 1]", "An error"], 0, "Without a comparator items are compared as strings."),
            mcq("What is merge sort's time complexity?", ["O(n log n)", "O(n)", "O(n²)", "O(log n)"], 0),
            mcq("What comparator sorts numbers ascending?", ["(a, b) => a - b", "(a, b) => a > b", "a - b", "(a, b) => b"], 0),
            run("Write mergeSort(arr) returning a new sorted array of numbers (do NOT use .sort()).", "javascript",
                [js("mergeSort([5, 2, 9, 1, 5, 6])"), js("mergeSort([])"), js("mergeSort([3, -1, 2, -5])")],
                ["[1,2,5,5,6,9]", "[]", "[-5,-1,2,3]"],
                "function mergeSort(a) {\n  if (a.length <= 1) return a;\n  const mid = a.length >> 1;\n  const l = mergeSort(a.slice(0, mid));\n  const r = mergeSort(a.slice(mid));\n  const out = [];\n  let i = 0, j = 0;\n  while (i < l.length && j < r.length) out.push(l[i] <= r[j] ? l[i++] : r[j++]);\n  return out.concat(l.slice(i), r.slice(j));\n}",
                forbid=[r"\.sort\("]),
        ),
        lesson(
            "Sliding window",
            """Instead of recomputing every window from scratch, slide it: add the new item entering, subtract the one leaving. O(n) instead of O(n·k).

function maxWindowSum(nums, k) {
  let sum = 0;
  for (let i = 0; i < k; i++) sum += nums[i];
  let best = sum;
  for (let i = k; i < nums.length; i++) {
    sum += nums[i] - nums[i - k];
    best = Math.max(best, sum);
  }
  return best;
}""",
            mcq("What does the sliding window avoid?", ["Re-summing every window from scratch", "Using arrays", "Using loops", "Recursion"], 0),
            mcq("What is the complexity of maxWindowSum above?", ["O(n)", "O(n·k)", "O(n²)", "O(log n)"], 0),
            mcq("When the window moves one step, what changes?", ["One item enters and one leaves", "Everything", "Nothing", "The array is sorted"], 0),
            run("Write longestUnique(text) returning the length of the longest substring with no repeated characters, using a sliding window and a Set or Map.", "javascript",
                [log('longestUnique("abcabcbb")'), log('longestUnique("bbbbb")'), log('longestUnique("pwwkew")'), log('longestUnique("")')],
                ["3", "1", "3", "0"],
                "function longestUnique(text) {\n  const seen = new Set();\n  let left = 0, best = 0;\n  for (let right = 0; right < text.length; right++) {\n    while (seen.has(text[right])) seen.delete(text[left++]);\n    seen.add(text[right]);\n    best = Math.max(best, right - left + 1);\n  }\n  return best;\n}",
                require=[r"Set|Map"]),
        ),
        lesson(
            "Dynamic programming",
            """Dynamic programming solves a big problem by combining answers to overlapping smaller ones, remembering each answer once.

Coin change (fewest coins for an amount): best[a] = 1 + min(best[a - coin]) over the coins.

function minCoins(coins, amount) {
  const best = Array(amount + 1).fill(Infinity);
  best[0] = 0;
  for (let a = 1; a <= amount; a++)
    for (const c of coins) if (c <= a) best[a] = Math.min(best[a], best[a - c] + 1);
  return best[amount] === Infinity ? -1 : best[amount];
}""",
            mcq("What does dynamic programming reuse?", ["Answers to overlapping subproblems", "Random numbers", "Global state", "Sorting"], 0),
            mcq("What is best[0] in coin change?", ["0 coins", "1 coin", "Infinity", "-1"], 0),
            mcq("Which problem has overlapping subproblems?", ["Fibonacci", "Printing a list", "Reversing a string", "Sum of two numbers"], 0),
            run("Write minCoins(coins, amount) returning the fewest coins that make the amount, or -1 if impossible.", "javascript",
                [log("minCoins([1, 5, 10, 25], 63)"), log("minCoins([2], 3)"), log("minCoins([1, 3, 4], 6)"), log("minCoins([5], 0)")],
                ["6", "-1", "2", "0"],
                "function minCoins(coins, amount) {\n  const best = Array(amount + 1).fill(Infinity);\n  best[0] = 0;\n  for (let a = 1; a <= amount; a++) {\n    for (const c of coins) {\n      if (c <= a) best[a] = Math.min(best[a], best[a - c] + 1);\n    }\n  }\n  return best[amount] === Infinity ? -1 : best[amount];\n}"),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · Graphs, trees & recursion",
        lesson(
            "Trees and recursion",
            """A tree node has a value and children. Most tree problems are recursive: handle this node, then ask each child.

const tree = { value: 1, children: [{ value: 2, children: [] }, { value: 3, children: [{ value: 4, children: [] }] }] };

function sum(node) {
  return node.value + node.children.reduce((s, c) => s + sum(c), 0);
}
function height(node) {
  return 1 + Math.max(0, ...node.children.map(height));
}

The base case is a node with no children.""",
            mcq("What is the base case for sum(node) above?", ["A node with no children", "The root", "An empty array of trees", "A number"], 0),
            mcq("What does height of a single leaf node return?", ["1", "0", "-1", "Infinity"], 0),
            mcq("Which problems fit recursion naturally?", ["Trees and nested data", "Simple counters", "String length", "Printing"], 0),
            run("Write countNodes(node) and maxDepth(node) for nodes shaped { value, children: [] } (a leaf has depth 1). The test prints both.", "javascript",
                [t("tree", append="const t = { value: 1, children: [{ value: 2, children: [] }, { value: 3, children: [{ value: 4, children: [] }] }] };\nconsole.log(countNodes(t), maxDepth(t));"),
                 t("leaf", append="const t = { value: 9, children: [] };\nconsole.log(countNodes(t), maxDepth(t));")],
                ["4 3", "1 1"],
                "function countNodes(node) {\n  return 1 + node.children.reduce((s, c) => s + countNodes(c), 0);\n}\nfunction maxDepth(node) {\n  return 1 + Math.max(0, ...node.children.map(maxDepth));\n}",
                require=[r"countNodes\s*\(\s*c|countNodes\([^)]*children"]),
        ),
        lesson(
            "Breadth-first search",
            """BFS explores a graph level by level using a queue - it finds the SHORTEST path in an unweighted graph.

function bfs(graph, start, goal) {
  const dist = new Map([[start, 0]]);
  const queue = [start];
  for (let i = 0; i < queue.length; i++) {
    const node = queue[i];
    if (node === goal) return dist.get(node);
    for (const next of graph[node] ?? []) {
      if (!dist.has(next)) { dist.set(next, dist.get(node) + 1); queue.push(next); }
    }
  }
  return -1;
}""",
            mcq("What data structure drives BFS?", ["A queue", "A stack", "A heap", "A set only"], 0),
            mcq("What does BFS find in an unweighted graph?", ["The shortest path (fewest edges)", "The longest path", "A random path", "The cheapest weighted path"], 0),
            mcq("Why keep a visited/dist Map?", ["To avoid revisiting nodes forever", "To sort", "To copy the graph", "To count edges"], 0),
            run("Write shortestPath(graph, start, goal) returning the fewest edges between two nodes (graph is an object of arrays), or -1 if unreachable.", "javascript",
                [t("path", append="const g = { a: ['b', 'c'], b: ['d'], c: ['d'], d: ['e'], e: [] };\nconsole.log(shortestPath(g, 'a', 'e'));"),
                 t("same", append="console.log(shortestPath({ a: [] }, 'a', 'a'));"),
                 t("unreachable", append="console.log(shortestPath({ a: [], b: [] }, 'a', 'b'));")],
                ["3", "0", "-1"],
                "function shortestPath(graph, start, goal) {\n  const dist = new Map([[start, 0]]);\n  const queue = [start];\n  for (let i = 0; i < queue.length; i++) {\n    const node = queue[i];\n    if (node === goal) return dist.get(node);\n    for (const next of graph[node] ?? []) {\n      if (!dist.has(next)) {\n        dist.set(next, dist.get(node) + 1);\n        queue.push(next);\n      }\n    }\n  }\n  return -1;\n}",
                require=[r"queue|\.shift\("]),
        ),
        lesson(
            "Backtracking: permutations",
            """Backtracking builds an answer one choice at a time, and undoes (backs out of) a choice to try the next one.

function permutations(items) {
  const out = [];
  function build(current, rest) {
    if (rest.length === 0) { out.push(current); return; }
    rest.forEach((x, i) => build([...current, x], [...rest.slice(0, i), ...rest.slice(i + 1)]));
  }
  build([], items);
  return out;
}

There are n! permutations - this explodes quickly, so it only suits small inputs.""",
            mcq("How many permutations does a 4-item list have?", ["24", "16", "12", "4"], 0),
            mcq("What is 'backtracking'?", ["Trying a choice, then undoing it to try another", "Reading backwards", "Sorting", "Caching"], 0),
            mcq("Why only use it on small inputs?", ["The number of results grows factorially", "It is async", "It uses globals", "It cannot return"], 0),
            run("Write subsets(items) returning every subset of the array (including the empty one), as arrays, ordered so that the result for [1,2] is [[],[1],[2],[1,2]].", "javascript",
                [js("subsets([1, 2])"), js("subsets([])"), js("subsets([1, 2, 3]).length")],
                ["[[],[1],[2],[1,2]]", "[[]]", "8"],
                "function subsets(items) {\n  let out = [[]];\n  for (const x of items) out = out.concat(out.map((s) => [...s, x]));\n  return out;\n}"),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · Numbers, bits & precision",
        lesson(
            "Floating point surprises",
            """JavaScript numbers are 64-bit floats, so some decimals can't be stored exactly:

0.1 + 0.2             // 0.30000000000000004
0.1 + 0.2 === 0.3     // false

Compare with a tolerance (Math.abs(a - b) < Number.EPSILON * 10) or work in whole units like cents:

const cents = Math.round(19.99 * 100);   // 1999

Number.MAX_SAFE_INTEGER is 2^53 - 1; beyond it integers lose precision (use BigInt).""",
            mcq("What is 0.1 + 0.2 === 0.3?", ["false", "true", "NaN", "An error"], 0),
            mcq("Why store money as cents?", ["Whole numbers avoid float rounding errors", "It's faster", "JS requires it", "It saves memory"], 0),
            mcq("What is Number.MAX_SAFE_INTEGER?", ["9007199254740991", "2147483647", "Infinity", "1e100"], 0),
            run("Write sumPrices(strings) taking prices like '19.99' and returning the exact total as a string with 2 decimals, by converting each price to whole cents first.", "javascript",
                [log('sumPrices(["0.10", "0.20"])'), log('sumPrices(["19.99", "5.01"])'), log("sumPrices([])")],
                ["0.30", "25.00", "0.00"],
                "function sumPrices(strings) {\n  const cents = strings.reduce((s, p) => s + Math.round(parseFloat(p) * 100), 0);\n  return (cents / 100).toFixed(2);\n}",
                require=[r"Math\.round"]),
        ),
        lesson(
            "BigInt",
            """BigInt holds integers of any size. Write them with an n suffix and don't mix with normal numbers:

2n ** 100n                 // 1267650600228229401496703205376n
BigInt(10) + 5n            // 15n
5n / 2n                    // 2n (integer division)
typeof 5n                  // 'bigint'

Great for factorials, huge ids and exact arithmetic. Convert back with Number(x) or String(x) (careful: Number() loses precision above 2^53).""",
            mcq("How do you write a BigInt literal?", ["42n", "BigInt42", "42.0", "big(42)"], 0),
            mcq("What is 7n / 2n?", ["3n", "3.5n", "3.5", "4n"], 0),
            mcq("Can you do 5n + 1?", ["No - TypeError, mix only with BigInt", "Yes, gives 6n", "Yes, gives 6", "Gives NaN"], 0),
            run("Write factorial(n) returning n! as a STRING using BigInt, so large values stay exact.", "javascript",
                [log("factorial(5)"), log("factorial(20)"), log("factorial(25)"), log("factorial(0)")],
                ["120", "2432902008176640000", "15511210043330985984000000", "1"],
                "function factorial(n) {\n  let result = 1n;\n  for (let i = 2n; i <= BigInt(n); i++) result *= i;\n  return result.toString();\n}",
                require=[r"BigInt|\d+n\b"]),
        ),
        lesson(
            "Bitwise operators",
            """Numbers are bits underneath. Bitwise operators work on their 32-bit form:

5 & 3     // 1   AND   (101 & 011 = 001)
5 | 3     // 7   OR
5 ^ 3     // 6   XOR
~5        // -6  NOT
1 << 4    // 16  shift left (multiply by 2^4)
16 >> 2   // 4   shift right (divide by 2^2)

Uses: flags (permissions packed in one number), fast powers of two, and checking oddness: n & 1. A power of two has exactly one 1-bit: n > 0 && (n & (n - 1)) === 0.""",
            mcq("What is 6 & 3?", ["2", "7", "3", "1"], 0, "110 & 011 = 010."),
            mcq("What does 1 << 3 give?", ["8", "3", "4", "16"], 0),
            mcq("What does n & 1 tell you?", ["Whether n is odd", "Whether n is prime", "Whether n is negative", "n squared"], 0),
            run("Write isPowerOfTwo(n) using a bitwise check, and countBits(n) returning how many 1 bits n has (n >= 0).", "javascript",
                [t("power", append="console.log(isPowerOfTwo(16), isPowerOfTwo(18), isPowerOfTwo(1), isPowerOfTwo(0));"), t("bits", append="console.log(countBits(0), countBits(7), countBits(1024), countBits(255));")],
                ["true false true false", "0 3 1 8"],
                "function isPowerOfTwo(n) {\n  return n > 0 && (n & (n - 1)) === 0;\n}\nfunction countBits(n) {\n  let count = 0;\n  while (n > 0) {\n    count += n & 1;\n    n >>= 1;\n  }\n  return count;\n}",
                require=[r"&"]),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Patterns in JavaScript",
        lesson(
            "Event emitter (pub/sub)",
            """The publish-subscribe pattern decouples code: publishers announce events, subscribers listen, and neither knows about the other.

class Emitter {
  #handlers = new Map();
  on(event, fn) { (this.#handlers.get(event) ?? this.#handlers.set(event, []).get(event)).push(fn); return this; }
  emit(event, ...args) { (this.#handlers.get(event) ?? []).forEach((fn) => fn(...args)); }
}

Browsers (addEventListener), Node and most frameworks use this idea.""",
            mcq("What does the pub/sub pattern decouple?", ["Publishers from subscribers", "Code from data", "Classes from files", "Async from sync"], 0),
            mcq("What does emit('click', 1) do?", ["Calls every handler registered for 'click' with 1", "Registers a handler", "Removes handlers", "Returns the handlers"], 0),
            mcq("Which browser API uses this pattern?", ["addEventListener", "parseInt", "JSON.parse", "Math.max"], 0),
            run("Write class Emitter with on(event, fn), off(event, fn) and emit(event, ...args). Handlers run in the order they were added; emitting an event with no handlers does nothing.", "javascript",
                [t("order", append="const e = new Emitter();\ne.on('x', (v) => console.log('A' + v));\ne.on('x', (v) => console.log('B' + v));\ne.emit('x', 1);\ne.emit('none');"),
                 t("off", append="const e = new Emitter();\nconst f = () => console.log('hit');\ne.on('y', f);\ne.emit('y');\ne.off('y', f);\ne.emit('y');\nconsole.log('end');")],
                ["A1\nB1", "hit\nend"],
                "class Emitter {\n  constructor() {\n    this.handlers = new Map();\n  }\n  on(event, fn) {\n    if (!this.handlers.has(event)) this.handlers.set(event, []);\n    this.handlers.get(event).push(fn);\n  }\n  off(event, fn) {\n    this.handlers.set(event, (this.handlers.get(event) ?? []).filter((h) => h !== fn));\n  }\n  emit(event, ...args) {\n    for (const fn of this.handlers.get(event) ?? []) fn(...args);\n  }\n}",
                require=[r"emit"]),
        ),
        lesson(
            "State machines",
            """A state machine is a table of 'in state S, event E leads to state T'. It replaces tangled if/else with data:

const transitions = {
  idle:    { start: "running" },
  running: { pause: "paused", stop: "idle" },
  paused:  { resume: "running", stop: "idle" },
};

const next = (state, event) => transitions[state]?.[event] ?? state;

Invalid events simply leave the state unchanged. UI flows, game logic, parsers and traffic lights fit this model.""",
            mcq("What does a transitions table map?", ["(state, event) to the next state", "Strings to numbers", "Classes to files", "Errors to messages"], 0),
            mcq("What should happen on an event that isn't valid in a state?", ["State stays the same (or an explicit error)", "The program crashes silently", "It picks a random state", "The table changes"], 0),
            mcq("Which is a good fit for a state machine?", ["A traffic light", "Adding two numbers", "Reversing a string", "Sorting"], 0),
            run("Write run(events) for a door with states closed, open, locked: open (closed->open), close (open->closed), lock (closed->locked), unlock (locked->closed). Start closed, ignore invalid events, return the final state.", "javascript",
                [log('run(["open", "close", "lock"])'), log('run(["lock", "open", "unlock", "open"])'), log("run([])")],
                ["locked", "open", "closed"],
                "function run(events) {\n  const table = {\n    closed: { open: 'open', lock: 'locked' },\n    open: { close: 'closed' },\n    locked: { unlock: 'closed' },\n  };\n  let state = 'closed';\n  for (const e of events) state = table[state][e] ?? state;\n  return state;\n}"),
        ),
        lesson(
            "Middleware pipelines",
            """A middleware pipeline passes a request through a chain of functions; each can act, then call next() to continue. Express, Redux and Koa work like this.

function compose(middlewares) {
  return (ctx) => {
    let i = -1;
    const dispatch = (n) => {
      if (n <= i) throw new Error("next() called twice");
      i = n;
      const fn = middlewares[n];
      if (!fn) return;
      return fn(ctx, () => dispatch(n + 1));
    };
    return dispatch(0);
  };
}""",
            mcq("What does calling next() do in middleware?", ["Runs the following middleware", "Ends the program", "Restarts", "Returns the context"], 0),
            mcq("Which libraries use this pattern?", ["Express and Koa", "Math and JSON", "Array and Map", "Date and Intl"], 0),
            mcq("A middleware that never calls next()…", ["Stops the chain", "Repeats", "Skips itself", "Throws"], 0),
            run("Write compose(middlewares) returning a function run(ctx). Each middleware is (ctx, next) => ...; calling next() runs the next one. The test logs the order.", "javascript",
                [t("order", append="const log = [];\nconst run = compose([\n  (ctx, next) => { log.push('a-in'); next(); log.push('a-out'); },\n  (ctx, next) => { log.push('b-in'); next(); log.push('b-out'); },\n  (ctx) => { log.push('end'); },\n]);\nrun({});\nconsole.log(log.join(' '));"),
                 t("stops early", append="const log = [];\nconst run = compose([\n  () => { log.push('only'); },\n  () => { log.push('never'); },\n]);\nrun({});\nconsole.log(log.join(' '));")],
                ["a-in b-in end b-out a-out", "only"],
                "function compose(middlewares) {\n  return (ctx) => {\n    const dispatch = (n) => {\n      const fn = middlewares[n];\n      if (!fn) return;\n      return fn(ctx, () => dispatch(n + 1));\n    };\n    return dispatch(0);\n  };\n}",
                require=[r"next|dispatch"]),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Mini projects & quality",
        lesson(
            "Writing your own assertions",
            """A tiny test helper catches mistakes early:

function assertEqual(actual, expected, label) {
  const a = JSON.stringify(actual), e = JSON.stringify(expected);
  console.log(a === e ? `PASS ${label}` : `FAIL ${label}: expected ${e}, got ${a}`);
}

Good tests check the normal case, the edge cases (empty, one item, negative), and a failure case. Name each test after the behaviour it checks.""",
            mcq("Why compare with JSON.stringify?", ["It lets you compare arrays and objects by content", "It is faster", "It sorts", "It avoids errors"], 0),
            mcq("Which is an edge case for sum(array)?", ["An empty array", "[1, 2, 3]", "[5, 6]", "[4]"], 0),
            mcq("Why name tests after behaviour?", ["Failures then explain what broke", "It is required", "It runs faster", "It avoids imports"], 0),
            run("Write assertEqual(actual, expected, label) printing 'PASS label' when the JSON forms match, otherwise 'FAIL label'.", "javascript",
                [t("pass", append="assertEqual([1, 2], [1, 2], 'arrays');"), t("fail", append="assertEqual({ a: 1 }, { a: 2 }, 'objects');"), t("primitives", append="assertEqual(3, 3, 'num');\nassertEqual('a', 'b', 'str');")],
                ["PASS arrays", "FAIL objects", "PASS num\nFAIL str"],
                "function assertEqual(actual, expected, label) {\n  console.log(JSON.stringify(actual) === JSON.stringify(expected) ? 'PASS ' + label : 'FAIL ' + label);\n}",
                require=[r"JSON\.stringify"]),
        ),
        lesson(
            "Mini project: a tokenizer",
            """A tokenizer turns text into a list of tokens - the first step of every calculator, compiler or template engine.

"12 + 3*4"  ->  [{type:"num", value:12}, {type:"op", value:"+"}, {type:"num", value:3}, ...]

Loop over the characters; collect digits into numbers, push operators, skip spaces, and throw on anything unexpected. A regex with the g flag and matchAll can do it in one pass: /\\s*(\\d+|[-+*/()])/g.""",
            mcq("What is a token?", ["A meaningful chunk of text such as a number or operator", "A password", "A variable", "A loop"], 0),
            mcq("What should a tokenizer do with an unexpected character?", ["Report an error", "Ignore it silently", "Convert it to 0", "Crash the browser"], 0),
            mcq("Which regex flag finds every match?", ["g", "i", "m", "s"], 0),
            run("Write tokenize(text) returning an array of strings: numbers (digits) and the operators + - * / ( ). Ignore spaces; throw an Error('bad character') for anything else.", "javascript",
                [js('tokenize("12 + 3*4")'), js('tokenize("(1+2)")'), t("bad", append="try { tokenize('1 $ 2'); } catch (e) { console.log(e.message); }")],
                ['["12","+","3","*","4"]', '["(","1","+","2",")"]', "bad character"],
                "function tokenize(text) {\n  const tokens = [];\n  let i = 0;\n  while (i < text.length) {\n    const ch = text[i];\n    if (ch === ' ') { i++; continue; }\n    if (/\\d/.test(ch)) {\n      let num = '';\n      while (i < text.length && /\\d/.test(text[i])) num += text[i++];\n      tokens.push(num);\n    } else if ('+-*/()'.includes(ch)) {\n      tokens.push(ch);\n      i++;\n    } else {\n      throw new Error('bad character');\n    }\n  }\n  return tokens;\n}"),
        ),
        lesson(
            "Mini project: an expression evaluator",
            """Evaluate arithmetic with correct precedence (* and / before + and -) and brackets using recursive descent: one function per precedence level.

expression := term (("+" | "-") term)*
term       := factor (("*" | "/") factor)*
factor     := number | "(" expression ")"

Each function consumes tokens from a shared position and returns a number. This is the same idea real programming-language parsers use.""",
            mcq("Why do we have separate expression and term functions?", ["To give * and / higher precedence than + and -", "For speed", "To avoid recursion", "To store numbers"], 0),
            mcq("What does factor handle?", ["A number or a bracketed expression", "Only +", "Only strings", "Nothing"], 0),
            mcq("What is 2 + 3 * 4?", ["14", "20", "24", "9"], 0),
            run("Write evaluate(text) for expressions with whole numbers, + - * /, spaces and parentheses, respecting precedence. Division may give decimals.", "javascript",
                [log('evaluate("2 + 3 * 4")'), log('evaluate("(2 + 3) * 4")'), log('evaluate("10 / 4 - 1")'), log('evaluate("7")')],
                ["14", "20", "1.5", "7"],
                "function evaluate(text) {\n  const tokens = text.match(/\\d+|[-+*/()]/g);\n  let pos = 0;\n  const peek = () => tokens[pos];\n  function factor() {\n    const tok = tokens[pos++];\n    if (tok === '(') {\n      const v = expression();\n      pos++;\n      return v;\n    }\n    return Number(tok);\n  }\n  function term() {\n    let v = factor();\n    while (peek() === '*' || peek() === '/') {\n      const op = tokens[pos++];\n      const r = factor();\n      v = op === '*' ? v * r : v / r;\n    }\n    return v;\n  }\n  function expression() {\n    let v = term();\n    while (peek() === '+' || peek() === '-') {\n      const op = tokens[pos++];\n      const r = term();\n      v = op === '+' ? v + r : v - r;\n    }\n    return v;\n  }\n  return expression();\n}",
                forbid=[r"\beval\s*\(", r"new\s+Function"]),
        ),
        lesson(
            "Mini project: a todo reducer",
            """State management in a nutshell: a reducer takes (state, action) and returns the NEW state. It never mutates the old one.

function reducer(state, action) {
  switch (action.type) {
    case "add": return [...state, { id: action.id, text: action.text, done: false }];
    case "toggle": return state.map((t) => (t.id === action.id ? { ...t, done: !t.done } : t));
    case "remove": return state.filter((t) => t.id !== action.id);
    default: return state;
  }
}

Pure reducers are trivially testable and make state changes easy to log, replay and undo - the idea behind Redux.""",
            mcq("What does a reducer return?", ["The new state", "Nothing", "A promise", "The action"], 0),
            mcq("Why must a reducer be pure?", ["Same input must give same output so changes are predictable", "It runs faster", "JS requires it", "To avoid arrays"], 0),
            mcq("Which array method toggles one item without mutating?", ["map with a spread copy", "push", "splice", "sort"], 0),
            run("Write reducer(state, action) for a todo list with actions add {id, text}, toggle {id}, remove {id}. Return a new array each time and leave unknown actions unchanged.", "javascript",
                [t("flow", append="let s = [];\ns = reducer(s, { type: 'add', id: 1, text: 'milk' });\ns = reducer(s, { type: 'add', id: 2, text: 'eggs' });\ns = reducer(s, { type: 'toggle', id: 1 });\ns = reducer(s, { type: 'remove', id: 2 });\nconsole.log(JSON.stringify(s));"),
                 t("immutable", append="const s0 = [{ id: 1, text: 'a', done: false }];\nconst s1 = reducer(s0, { type: 'toggle', id: 1 });\nconsole.log(s0[0].done, s1[0].done, s0 === s1);"),
                 t("unknown", append="const s = [{ id: 1, text: 'a', done: false }];\nconsole.log(reducer(s, { type: 'zzz' }) === s);")],
                ['[{"id":1,"text":"milk","done":true}]', "false true false", "true"],
                "function reducer(state, action) {\n  switch (action.type) {\n    case 'add':\n      return [...state, { id: action.id, text: action.text, done: false }];\n    case 'toggle':\n      return state.map((t) => (t.id === action.id ? { ...t, done: !t.done } : t));\n    case 'remove':\n      return state.filter((t) => t.id !== action.id);\n    default:\n      return state;\n  }\n}",
                forbid=[r"\.push\(|\.splice\("]),
        ),
    ),
)
