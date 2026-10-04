"""Data Structures & Algorithms - Expert section, part 2 (units 16-21): graphs, union-find, dynamic programming,
greedy & backtracking, strings/math/bits, and capstone problem solving. Python (Pyodide)."""
from .dsl import lesson, mcq, order, run, section, t, unit


def pr(expr: str) -> dict:
    return t(expr, append=f"print({expr})")


EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 16
    unit(
        "Unit 16 · Graph algorithms",
        lesson(
            "Grids as graphs: counting islands",
            """A grid is a graph: each cell connects to its 4 neighbours. To count ISLANDS of land cells ('1'), scan every cell; when you find unvisited land, flood-fill the whole island with DFS/BFS and count one.

def dfs(r, c):
    if not (0 <= r < R and 0 <= c < C) or grid[r][c] != "1": return
    grid[r][c] = "0"                  # mark visited
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)): dfs(r + dr, c + dc)

Each cell is visited once: O(R × C).""",
            mcq("How many neighbours does a cell have in a 4-direction grid?", ["Up to 4", "Up to 8", "Exactly 2", "Exactly 1"], 0),
            mcq("Why mark cells visited?", ["To avoid counting or visiting them again", "To sort them", "To save memory", "To change colour"], 0),
            mcq("What is the complexity of flood fill over a whole grid?", ["O(R × C)", "O((R × C)²)", "O(R + C)", "O(log n)"], 0),
            run("Read R then R rows of '0'/'1' characters. Print the number of islands (groups of connected '1' cells, up/down/left/right).", "python",
                [t("three", stdin="4\n11000\n11000\n00100\n00011"), t("none", stdin="2\n00\n00"), t("one", stdin="3\n111\n010\n111")],
                ["3", "0", "1"],
                "import sys\nsys.setrecursionlimit(10000)\nR = int(input())\ngrid = [list(input()) for _ in range(R)]\nC = len(grid[0])\ndef dfs(r, c):\n    if not (0 <= r < R and 0 <= c < C) or grid[r][c] != '1':\n        return\n    grid[r][c] = '0'\n    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n        dfs(r + dr, c + dc)\ncount = 0\nfor r in range(R):\n    for c in range(C):\n        if grid[r][c] == '1':\n            count += 1\n            dfs(r, c)\nprint(count)"),
        ),
        lesson(
            "Topological sort",
            """A topological order lists tasks so every task comes AFTER the tasks it depends on (only possible in a directed graph with no cycles). Kahn's algorithm: repeatedly take a node with in-degree 0, output it, and reduce its neighbours' in-degrees.

if the output has fewer nodes than the graph, there was a CYCLE - the tasks depend on each other and can't be ordered.

Uses: build systems, course prerequisites, spreadsheet formulas.""",
            mcq("What does a topological order guarantee?", ["Each task comes after its dependencies", "Shortest paths", "Sorted values", "No edges"], 0),
            mcq("When is no topological order possible?", ["When the graph has a cycle", "When it has many nodes", "When it is a tree", "Never"], 0),
            mcq("Which nodes does Kahn's algorithm take first?", ["In-degree 0 (no dependencies)", "The largest", "Random ones", "Leaves"], 0),
            run("Read n and m, then m lines 'a b' meaning a must come before b (nodes 0..n-1). Print one valid order using Kahn's algorithm, taking the smallest available node each time; print IMPOSSIBLE if there is a cycle.", "python",
                [t("order", stdin="4 3\n0 1\n1 2\n0 3"), t("cycle", stdin="3 3\n0 1\n1 2\n2 0"), t("no edges", stdin="3 0")],
                ["0 1 2 3", "IMPOSSIBLE", "0 1 2"],
                "import heapq\nn, m = map(int, input().split())\nadj = [[] for _ in range(n)]\nindeg = [0] * n\nfor _ in range(m):\n    a, b = map(int, input().split())\n    adj[a].append(b)\n    indeg[b] += 1\nready = [i for i in range(n) if indeg[i] == 0]\nheapq.heapify(ready)\norder = []\nwhile ready:\n    x = heapq.heappop(ready)\n    order.append(x)\n    for y in adj[x]:\n        indeg[y] -= 1\n        if indeg[y] == 0:\n            heapq.heappush(ready, y)\nprint(' '.join(map(str, order)) if len(order) == n else 'IMPOSSIBLE')"),
        ),
        lesson(
            "Dijkstra's shortest path",
            """For graphs with non-negative edge WEIGHTS, Dijkstra finds the cheapest path from a start node. Keep a min-heap of (distance, node); pop the closest unfinished node, and relax its neighbours (try a shorter route through it).

dist = {start: 0}; heap = [(0, start)]
while heap:
    d, u = heappop(heap)
    if d > dist.get(u, inf): continue
    for v, w in adj[u]:
        if d + w < dist.get(v, inf): dist[v] = d + w; heappush(heap, (d + w, v))

O((V + E) log V). It fails with negative weights.""",
            mcq("What does Dijkstra require of edge weights?", ["Non-negative", "Integers only", "All equal", "Sorted"], 0),
            mcq("What does 'relaxing' an edge mean?", ["Trying a shorter route through a node", "Deleting the edge", "Sorting edges", "Ignoring weights"], 0),
            mcq("What data structure picks the closest node?", ["A min-heap", "A stack", "A queue", "A set"], 0),
            run("Read n m, then m lines 'a b w' (undirected edge, weight w), nodes 0..n-1. Print the shortest distance from 0 to n-1, or -1 if unreachable.", "python",
                [t("path", stdin="5 6\n0 1 4\n0 2 1\n2 1 2\n1 3 1\n2 3 5\n3 4 3"), t("unreachable", stdin="3 1\n0 1 5"), t("same", stdin="1 0")],
                ["7", "-1", "0"],
                "import heapq\nn, m = map(int, input().split())\nadj = [[] for _ in range(n)]\nfor _ in range(m):\n    a, b, w = map(int, input().split())\n    adj[a].append((b, w))\n    adj[b].append((a, w))\ndist = {0: 0}\nheap = [(0, 0)]\nwhile heap:\n    d, u = heapq.heappop(heap)\n    if d > dist.get(u, float('inf')):\n        continue\n    for v, w in adj[u]:\n        if d + w < dist.get(v, float('inf')):\n            dist[v] = d + w\n            heapq.heappush(heap, (d + w, v))\nprint(dist.get(n - 1, -1))",
                require=[r"heapq"]),
        ),
    ),
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Connectivity & spanning trees",
        lesson(
            "Union-find (disjoint sets)",
            """Union-find keeps track of groups: find(x) returns the group's representative; union(a, b) merges two groups. With path compression it's nearly O(1):

parent = list(range(n))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]      # path halving
        x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)

Perfect for 'are these two connected?' as edges arrive one by one.""",
            mcq("What does find(x) return?", ["The representative of x's group", "The size of the group", "A neighbour of x", "x's index"], 0),
            mcq("What does path compression do?", ["Makes future finds faster", "Sorts groups", "Deletes nodes", "Counts edges"], 0),
            mcq("Union-find answers which question quickly?", ["Are a and b in the same group?", "What is the shortest path?", "What is the maximum?", "How deep is the tree?"], 0),
            run("Read n and m, then m lines 'a b' (edges, nodes 0..n-1). Print the number of connected components, using union-find.", "python",
                [t("two", stdin="5 3\n0 1\n1 2\n3 4"), t("none", stdin="4 0"), t("one", stdin="3 3\n0 1\n1 2\n2 0")],
                ["2", "4", "1"],
                "n, m = map(int, input().split())\nparent = list(range(n))\ndef find(x):\n    while parent[x] != x:\n        parent[x] = parent[parent[x]]\n        x = parent[x]\n    return x\ncomponents = n\nfor _ in range(m):\n    a, b = map(int, input().split())\n    ra, rb = find(a), find(b)\n    if ra != rb:\n        parent[ra] = rb\n        components -= 1\nprint(components)"),
        ),
        lesson(
            "Minimum spanning tree (Kruskal)",
            """A spanning tree connects all nodes using the fewest edges (n - 1) with no cycles; the MINIMUM one has the smallest total weight (cheapest network cabling, for example).

Kruskal: sort edges by weight; take each edge if it joins two DIFFERENT groups (union-find says they aren't connected yet).

O(E log E), dominated by the sort.""",
            mcq("How many edges does a spanning tree of n nodes have?", ["n - 1", "n", "n + 1", "2n"], 0),
            mcq("When does Kruskal skip an edge?", ["Its ends are already connected", "It's the heaviest", "It's the first", "It's negative"], 0),
            mcq("What does Kruskal sort first?", ["The edges by weight", "The nodes", "The groups", "Nothing"], 0),
            run("Read n m, then m lines 'a b w'. Print the total weight of a minimum spanning tree, or -1 if the graph isn't connected.", "python",
                [t("classic", stdin="4 5\n0 1 10\n0 2 6\n0 3 5\n1 3 15\n2 3 4"), t("disconnected", stdin="3 1\n0 1 2"), t("single", stdin="1 0")],
                ["19", "-1", "0"],
                "n, m = map(int, input().split())\nedges = sorted((w, a, b) for a, b, w in (map(int, input().split()) for _ in range(m)))\nparent = list(range(n))\ndef find(x):\n    while parent[x] != x:\n        parent[x] = parent[parent[x]]\n        x = parent[x]\n    return x\ntotal = used = 0\nfor w, a, b in edges:\n    ra, rb = find(a), find(b)\n    if ra != rb:\n        parent[ra] = rb\n        total += w\n        used += 1\nprint(total if used == n - 1 else -1)"),
        ),
        lesson(
            "Cycle detection & bipartite graphs",
            """In an UNDIRECTED graph a cycle exists if a DFS meets an already-visited node that is not its parent. A graph is BIPARTITE if its nodes can be coloured with two colours so every edge joins different colours - equivalent to having no odd-length cycle.

BFS colouring: colour the start 0, give every neighbour the opposite colour, and fail if an edge joins two same-coloured nodes.

Bipartite graphs model two-sided problems: students and courses, jobs and workers.""",
            mcq("What makes a graph bipartite?", ["Two colours separate every edge's ends", "It has two nodes", "It has no edges", "It is a tree only"], 0),
            mcq("A bipartite graph can't contain…", ["An odd-length cycle", "An even cycle", "A path", "Isolated nodes"], 0),
            mcq("What does BFS colouring do for each neighbour?", ["Gives it the opposite colour", "Gives it the same colour", "Skips it", "Deletes it"], 0),
            run("Read n m, then m undirected edges 'a b'. Print YES if the graph can be 2-coloured (bipartite), otherwise NO.", "python",
                [t("even cycle", stdin="4 4\n0 1\n1 2\n2 3\n3 0"), t("triangle", stdin="3 3\n0 1\n1 2\n2 0"), t("two parts", stdin="5 3\n0 1\n2 3\n3 4")],
                ["YES", "NO", "YES"],
                "from collections import deque\nn, m = map(int, input().split())\nadj = [[] for _ in range(n)]\nfor _ in range(m):\n    a, b = map(int, input().split())\n    adj[a].append(b)\n    adj[b].append(a)\ncolor = [-1] * n\nok = True\nfor s in range(n):\n    if color[s] != -1:\n        continue\n    color[s] = 0\n    q = deque([s])\n    while q and ok:\n        u = q.popleft()\n        for v in adj[u]:\n            if color[v] == -1:\n                color[v] = 1 - color[u]\n                q.append(v)\n            elif color[v] == color[u]:\n                ok = False\nprint('YES' if ok else 'NO')"),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Dynamic programming",
        lesson(
            "0/1 knapsack",
            """Choose items, each at most once, to maximise value without exceeding a weight capacity. DP over capacity: best[w] = the best value achievable with weight limit w. Process items one at a time and update capacities from HIGH to LOW so each item is used once.

for weight, value in items:
    for cap in range(W, weight - 1, -1):
        best[cap] = max(best[cap], best[cap - weight] + value)

O(n × W). Iterating low to high would let an item be used many times (the unbounded knapsack).""",
            mcq("Why iterate capacities from high to low?", ["So each item is used at most once", "To go faster", "To avoid zeros", "To sort"], 0),
            mcq("What is best[w]?", ["Best value with weight limit w", "Number of items", "Weight of the best item", "Total value"], 0),
            mcq("What is the complexity?", ["O(n × W)", "O(n²)", "O(2^n)", "O(W)"], 0),
            run("Read W (capacity) on line 1, then n, then n lines 'weight value'. Print the maximum total value (each item at most once).", "python",
                [t("classic", stdin="50\n3\n10 60\n20 100\n30 120"), t("tiny", stdin="5\n2\n6 10\n7 20"), t("all fit", stdin="10\n2\n3 4\n4 5")],
                ["220", "0", "9"],
                "W = int(input())\nn = int(input())\nbest = [0] * (W + 1)\nfor _ in range(n):\n    weight, value = map(int, input().split())\n    for cap in range(W, weight - 1, -1):\n        best[cap] = max(best[cap], best[cap - weight] + value)\nprint(best[W])"),
        ),
        lesson(
            "Longest common subsequence",
            """The longest common subsequence (LCS) of two strings keeps characters in order but not necessarily adjacent. Table dp[i][j] = LCS length of the first i characters of a and the first j of b:

if a[i-1] == b[j-1]: dp[i][j] = dp[i-1][j-1] + 1
else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])

O(len(a) × len(b)). It powers diff tools, DNA comparison and version control.""",
            mcq("What does a subsequence keep?", ["Order, not adjacency", "Adjacency only", "Nothing", "Sorted order"], 0),
            mcq("When a[i-1] == b[j-1], what happens?", ["Extend the diagonal by 1", "Take the max of neighbours", "Reset to 0", "Skip"], 0),
            mcq("What is the complexity?", ["O(len(a) × len(b))", "O(n)", "O(2^n)", "O(log n)"], 0),
            run("Read two strings on separate lines. Print the length of their longest common subsequence.", "python",
                [t("classic", stdin="abcde\nace"), t("none", stdin="abc\ndef"), t("same", stdin="python\npython")],
                ["3", "0", "6"],
                "a = input()\nb = input()\ndp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]\nfor i in range(1, len(a) + 1):\n    for j in range(1, len(b) + 1):\n        if a[i - 1] == b[j - 1]:\n            dp[i][j] = dp[i - 1][j - 1] + 1\n        else:\n            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])\nprint(dp[len(a)][len(b)])"),
        ),
        lesson(
            "Edit distance",
            """Edit distance (Levenshtein) is the fewest single-character insertions, deletions and substitutions that turn one word into another. dp[i][j] = cost for the first i characters of a and the first j of b:

if same character: dp[i][j] = dp[i-1][j-1]
else: 1 + min(dp[i-1][j] (delete), dp[i][j-1] (insert), dp[i-1][j-1] (replace))

Base cases: turning a prefix into the empty string costs its length. Used by spell checkers and search suggestions.""",
            mcq("Which three edits count?", ["Insert, delete, substitute", "Sort, swap, reverse", "Copy, move, paste", "Add, merge, split"], 0),
            mcq("What is the edit distance between 'cat' and 'cat'?", ["0", "1", "3", "6"], 0),
            mcq("What are the base cases?", ["Prefix to empty string costs its length", "All zeros", "All ones", "Infinity"], 0),
            run("Read two words on separate lines. Print their edit distance (insert, delete or replace one character per step).", "python",
                [t("kitten", stdin="kitten\nsitting"), t("same", stdin="abc\nabc"), t("empty", stdin="\nabc")],
                ["3", "0", "3"],
                "a = input()\nb = input()\ndp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]\nfor i in range(len(a) + 1):\n    dp[i][0] = i\nfor j in range(len(b) + 1):\n    dp[0][j] = j\nfor i in range(1, len(a) + 1):\n    for j in range(1, len(b) + 1):\n        if a[i - 1] == b[j - 1]:\n            dp[i][j] = dp[i - 1][j - 1]\n        else:\n            dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])\nprint(dp[len(a)][len(b)])"),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Greedy & backtracking",
        lesson(
            "Greedy: interval scheduling",
            """A greedy algorithm makes the best-looking choice at each step and never looks back. It only works when that local choice is provably safe.

Maximum number of non-overlapping meetings: sort by END time, then take each meeting that starts at or after the last chosen end. Finishing early leaves the most room for the rest.

def schedule(meetings):
    last_end, count = -inf, 0
    for s, e in sorted(meetings, key=lambda m: m[1]):
        if s >= last_end: count += 1; last_end = e""",
            mcq("What do you sort by for maximum non-overlapping meetings?", ["End time", "Start time", "Length", "Name"], 0),
            mcq("When does greedy work?", ["When the local choice is provably safe", "Always", "Never", "On sorted data only"], 0),
            mcq("Why pick the earliest-finishing meeting?", ["It leaves the most room for others", "It is shortest", "It is first", "It has a better name"], 0),
            run("Read n then n lines 'start end'. Print the maximum number of non-overlapping meetings (a meeting may start exactly when another ends).", "python",
                [t("classic", stdin="6\n1 4\n3 5\n0 6\n5 7\n3 9\n5 9"), t("all overlap", stdin="3\n1 10\n2 9\n3 8"), t("touching", stdin="3\n1 2\n2 3\n3 4")],
                ["2", "1", "3"],
                "n = int(input())\nmeetings = [tuple(map(int, input().split())) for _ in range(n)]\nlast_end, count = float('-inf'), 0\nfor s, e in sorted(meetings, key=lambda m: m[1]):\n    if s >= last_end:\n        count += 1\n        last_end = e\nprint(count)"),
        ),
        lesson(
            "Backtracking: combinations",
            """Backtracking explores choices recursively and undoes (backtracks) a choice to try the next. Combination sum: find all ways to pick numbers (reuse allowed) that sum to a target.

def solve(start, remaining, path):
    if remaining == 0: results.append(path[:]); return
    for i in range(start, len(nums)):
        if nums[i] > remaining: break          # sorted, so later numbers are too big
        path.append(nums[i]); solve(i, remaining - nums[i], path); path.pop()

path.pop() is the 'undo'. Sorting enables the early break (pruning).""",
            mcq("What does path.pop() do in backtracking?", ["Undoes the last choice", "Finishes the search", "Sorts", "Adds a result"], 0),
            mcq("What is pruning?", ["Stopping branches that can't succeed", "Sorting results", "Deleting numbers", "Adding branches"], 0),
            mcq("Why pass i (not i + 1) in the recursive call?", ["Numbers may be reused", "To skip numbers", "To count steps", "To sort"], 0),
            run("Read numbers (distinct positive) on line 1 and a target on line 2. Print how many combinations (order doesn't matter, numbers may be reused) add up to the target.", "python",
                [t("classic", stdin="2 3 6 7\n7"), t("coins", stdin="1 2 5\n5"), t("none", stdin="4 6\n3")],
                ["2", "4", "0"],
                "nums = sorted(int(x) for x in input().split())\ntarget = int(input())\ncount = 0\ndef solve(start, remaining):\n    global count\n    if remaining == 0:\n        count += 1\n        return\n    for i in range(start, len(nums)):\n        if nums[i] > remaining:\n            break\n        solve(i, remaining - nums[i])\nsolve(0, target)\nprint(count)"),
        ),
        lesson(
            "N-Queens (counting solutions)",
            """Place n queens on an n × n board so none attack each other (no shared row, column or diagonal). Backtrack row by row, trying each column and keeping sets of used columns and diagonals.

cols, diag1, diag2 = set(), set(), set()
def place(r):
    if r == n: return 1
    total = 0
    for c in range(n):
        if c in cols or r - c in diag1 or r + c in diag2: continue
        cols.add(c); diag1.add(r - c); diag2.add(r + c)
        total += place(r + 1)
        cols.remove(c); diag1.remove(r - c); diag2.remove(r + c)
    return total""",
            mcq("What uniquely identifies a '\\' diagonal?", ["r - c", "r + c", "c", "r"], 0),
            mcq("What uniquely identifies a '/' diagonal?", ["r + c", "r - c", "c", "r"], 0),
            mcq("Why place one queen per row?", ["Two queens in a row would attack", "It is faster to type", "Python requires it", "Boards have n rows"], 0),
            run("Read n. Print the number of ways to place n queens on an n × n board so that none attack each other.", "python",
                [t("n=4", stdin="4"), t("n=6", stdin="6"), t("n=1", stdin="1")],
                ["2", "4", "1"],
                "n = int(input())\ncols, d1, d2 = set(), set(), set()\ndef place(r):\n    if r == n:\n        return 1\n    total = 0\n    for c in range(n):\n        if c in cols or r - c in d1 or r + c in d2:\n            continue\n        cols.add(c)\n        d1.add(r - c)\n        d2.add(r + c)\n        total += place(r + 1)\n        cols.remove(c)\n        d1.remove(r - c)\n        d2.remove(r + c)\n    return total\nprint(place(0))"),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Strings, math & bits",
        lesson(
            "Palindromes: expand around the centre",
            """To find the longest palindromic substring, treat every position (and every gap between characters) as a possible CENTRE and expand outward while both ends match.

def expand(s, l, r):
    while l >= 0 and r < len(s) and s[l] == s[r]:
        l -= 1; r += 1
    return r - l - 1          # length of the palindrome found

Try odd centres expand(s, i, i) and even centres expand(s, i, i + 1). O(n²) time, O(1) space - simple and fast for ordinary strings.""",
            mcq("How many centres does a string of length n have?", ["2n - 1", "n", "n / 2", "n²"], 0),
            mcq("What does expand return when s[l] != s[r] immediately?", ["The length found so far (0 or 1)", "-1", "n", "An error"], 0),
            mcq("What is the complexity?", ["O(n²)", "O(n)", "O(n log n)", "O(2^n)"], 0),
            run("Read a string. Print the length of its longest palindromic substring.", "python",
                [t("babad", stdin="babad"), t("even", stdin="cbbd"), t("single", stdin="a")],
                ["3", "2", "1"],
                "s = input()\ndef expand(l, r):\n    while l >= 0 and r < len(s) and s[l] == s[r]:\n        l -= 1\n        r += 1\n    return r - l - 1\nbest = 0\nfor i in range(len(s)):\n    best = max(best, expand(i, i), expand(i, i + 1))\nprint(best)"),
        ),
        lesson(
            "gcd, primes and the sieve",
            """Euclid's algorithm computes the greatest common divisor fast: gcd(a, b) = gcd(b, a % b) until b is 0. And lcm(a, b) = a * b // gcd(a, b).

The Sieve of Eratosthenes finds all primes up to n: start with all numbers marked prime, then for each prime p cross out p*p, p*p + p, ... O(n log log n).

is_prime = [True] * (n + 1); is_prime[0:2] = [False, False]
for p in range(2, int(n ** 0.5) + 1):
    if is_prime[p]:
        for m in range(p * p, n + 1, p): is_prime[m] = False""",
            mcq("What is gcd(12, 18)?", ["6", "3", "12", "36"], 0),
            mcq("Why start crossing out at p * p?", ["Smaller multiples were already crossed out", "It is faster to type", "p * p is prime", "To skip 2"], 0),
            mcq("What is lcm(4, 6)?", ["12", "24", "2", "10"], 0),
            run("Read n. Print the number of primes up to and including n, then the gcd of the first and last of them (use a sieve). If n < 2 print 0 and 0.", "python",
                [t("n=30", stdin="30"), t("n=2", stdin="2"), t("n=1", stdin="1")],
                ["10\n1", "1\n2", "0\n0"],
                "from math import gcd\nn = int(input())\nif n < 2:\n    print(0)\n    print(0)\nelse:\n    is_prime = [True] * (n + 1)\n    is_prime[0] = is_prime[1] = False\n    for p in range(2, int(n ** 0.5) + 1):\n        if is_prime[p]:\n            for m in range(p * p, n + 1, p):\n                is_prime[m] = False\n    primes = [i for i in range(n + 1) if is_prime[i]]\n    print(len(primes))\n    print(gcd(primes[0], primes[-1]))"),
        ),
        lesson(
            "Bit tricks",
            """Bit operations solve some puzzles in O(1) space:

x ^ x == 0 and x ^ 0 == x, so XOR-ing all numbers cancels the pairs: the number that appears ONCE is left.
n & (n - 1) clears the lowest set bit - a power of two has exactly one set bit.
(n >> i) & 1 reads bit i. n & 1 tests odd.
Python ints have unlimited size, so shifting never overflows.""",
            mcq("What is 6 ^ 6?", ["0", "6", "12", "1"], 0),
            mcq("What does n & (n - 1) do?", ["Clears the lowest set bit", "Doubles n", "Negates n", "Reads bit 0"], 0),
            mcq("How do you find the single non-repeated number in a list of pairs?", ["XOR everything together", "Sort it", "Sum it", "Count it"], 0),
            run("Read numbers on line 1 (every number appears twice except one). Print the one that appears once, using XOR. Then print how many 1 bits it has.", "python",
                [t("classic", stdin="4 1 2 1 2"), t("single", stdin="7"), t("big", stdin="10 20 10 5 5")],
                ["4\n1", "7\n3", "20\n2"],
                "from functools import reduce\nnums = [int(x) for x in input().split()]\nx = reduce(lambda a, b: a ^ b, nums)\nprint(x)\nprint(bin(x).count('1'))"),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Problem-solving capstone",
        lesson(
            "A problem-solving routine",
            """When a problem looks hard, follow a routine:

1. UNDERSTAND - restate it, work an example by hand, note the input sizes and edge cases (empty, one item, duplicates, negatives).
2. BRUTE FORCE - say the obvious slow solution and its Big-O.
3. FIND THE BOTTLENECK - what repeated work can a hash map, sorting, a heap, two pointers or DP remove?
4. CODE the improved idea cleanly.
5. TEST with the examples and the edge cases; trace a small input by hand.

Input size hints the complexity you need: n up to 10^5 needs about O(n log n); n up to 20 allows O(2^n); n up to 500 allows O(n³).""",
            order("Order the routine.", ["Understand the problem and edge cases", "Write the brute-force idea and its Big-O", "Find the bottleneck and a better structure", "Code the improved idea", "Test with examples and edge cases"]),
            mcq("n is up to 100,000. Which complexity is realistic?", ["O(n log n)", "O(n²)", "O(2^n)", "O(n!)"], 0),
            mcq("n is up to 20. Which can work?", ["O(2^n)", "O(n!) is always fine", "Nothing", "Only O(1)"], 0),
            run("Practise step 1: read numbers and print the three edge-case checks as 'empty single duplicates' flags: whether the list is empty (False here, input is never empty), has exactly one number, and has any duplicate. Print the last two as True/False separated by a space.", "python",
                [t("single", stdin="5"), t("dups", stdin="1 2 2"), t("plain", stdin="3 4 5")],
                ["True False", "False True", "False False"],
                "nums = input().split()\nprint(len(nums) == 1, len(set(nums)) != len(nums))"),
        ),
        lesson(
            "Choosing the right structure",
            """Match the need to the structure:

- Fast lookup / membership / counting -> dict or set (O(1))
- Process in arrival order -> queue (deque); undo/nesting -> stack
- Always need the smallest or largest -> heap
- Sorted data, ranges, 'first >= x' -> sorted list + bisect (or a balanced tree)
- Many 'are they connected?' queries -> union-find
- Prefix lookups on words -> trie
- Hierarchies -> tree; networks -> graph

Naming the operation you repeat most is usually enough to pick the structure.""",
            mcq("You repeatedly need the smallest of a changing set. What do you use?", ["A heap", "A list sorted each time", "A dict", "A stack"], 0),
            mcq("You need O(1) 'have I seen this?' checks. What do you use?", ["A set", "A list", "A heap", "A queue"], 0),
            mcq("Process tasks in the order they arrive:", ["A queue", "A stack", "A heap", "A set"], 0),
            run("Read words on one line. Print the first word that appears twice (or NONE), using a set.", "python",
                [t("repeat", stdin="a b c b a"), t("none", stdin="x y z"), t("immediate", stdin="q q")],
                ["b", "NONE", "q"],
                "seen = set()\nanswer = 'NONE'\nfor w in input().split():\n    if w in seen:\n        answer = w\n        break\n    seen.add(w)\nprint(answer)"),
        ),
        lesson(
            "Design: a time-based key-value store",
            """Design questions combine structures. Store (timestamp, value) per key and answer 'the value at or before time t':

set(key, value, ts):   append (ts, value) to the key's list - timestamps arrive increasing, so the list stays SORTED
get(key, ts):          binary search for the last timestamp <= ts

Dict gives O(1) key lookup; bisect gives O(log n) time lookup. Always say the cost of each operation out loud.""",
            mcq("Why is each key's list sorted by time?", ["Timestamps arrive in increasing order", "Python sorts it", "Dicts sort values", "It isn't"], 0),
            mcq("How do you find the latest value at or before ts?", ["Binary search", "Scan from the start always", "Sort every time", "Hash the ts"], 0),
            mcq("What is get's complexity?", ["O(log n)", "O(1)", "O(n)", "O(n²)"], 0),
            run("Write class TimeMap with set(key, value, ts) and get(key, ts) returning the value with the largest timestamp <= ts, or '' if none. Use a dict of lists and bisect.", "python",
                [t("flow", append="m = TimeMap()\nm.set('a', 'v1', 1)\nm.set('a', 'v2', 4)\nprint(m.get('a', 1), m.get('a', 3), m.get('a', 4), repr(m.get('a', 0)), repr(m.get('b', 5)))"), t("many keys", append="m = TimeMap()\nm.set('x', 1, 10)\nm.set('y', 2, 10)\nprint(m.get('x', 99), m.get('y', 99))")],
                ["v1 v1 v2 '' ''", "1 2"],
                "import bisect\n\nclass TimeMap:\n    def __init__(self):\n        self.times = {}\n        self.values = {}\n    def set(self, key, value, ts):\n        self.times.setdefault(key, []).append(ts)\n        self.values.setdefault(key, []).append(value)\n    def get(self, key, ts):\n        i = bisect.bisect_right(self.times.get(key, []), ts)\n        return self.values[key][i - 1] if i else ''",
                starter="class TimeMap:\n    def __init__(self):\n        self.data = {}\n"),
        ),
        lesson(
            "Capstone: a task scheduler",
            """A last challenge that uses several ideas: tasks have a priority and a name; always run the HIGHEST priority task next, breaking ties by the name alphabetically. A heap of (-priority, name) does it in O(log n) per operation.

Use cases: operating system schedulers, job queues, game AI. The same pattern - 'always give me the best item next' - is a priority queue.""",
            mcq("Why store -priority in a min-heap?", ["To make the highest priority pop first", "To save memory", "To sort names", "Python requires it"], 0),
            mcq("What breaks ties between equal priorities in (-p, name)?", ["The name, alphabetically", "Random choice", "The order added always", "Nothing"], 0),
            mcq("What structure is a scheduler?", ["A priority queue", "A stack", "A set", "A linked list"], 0),
            run("Read n, then n lines 'priority name'. Print the names in the order a scheduler would run them: highest priority first, ties alphabetically.", "python",
                [t("ties", stdin="4\n2 write\n5 deploy\n2 test\n5 build"), t("one", stdin="1\n1 solo"), t("same", stdin="3\n1 c\n1 a\n1 b")],
                ["build deploy test write", "solo", "a b c"],
                "import heapq\nn = int(input())\nh = []\nfor _ in range(n):\n    p, name = input().split()\n    heapq.heappush(h, (-int(p), name))\nout = []\nwhile h:\n    out.append(heapq.heappop(h)[1])\nprint(' '.join(out))",
                require=[r"heapq"]),
        ),
    ),
)
