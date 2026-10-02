"""DSA projects - one at the end of each section (added to units 4, 6 and 8)."""
from .dsl import project, run, t

# ------------------------------------------------------------------ Beginner: undo/redo editor
EDIT_HEAD = """import sys

text = ''
"""
EDIT_1 = EDIT_HEAD + """for line in sys.stdin.read().splitlines():
    cmd, _, arg = line.partition(' ')
    if cmd == 'type':
        text += arg
    elif cmd == 'delete':
        text = text[:max(0, len(text) - int(arg))]
    elif cmd == 'print':
        print(text)
"""
EDIT_2 = EDIT_HEAD + """history = []  # a stack of earlier versions
for line in sys.stdin.read().splitlines():
    cmd, _, arg = line.partition(' ')
    if cmd == 'type':
        history.append(text)
        text += arg
    elif cmd == 'delete':
        history.append(text)
        text = text[:max(0, len(text) - int(arg))]
    elif cmd == 'undo':
        if history:
            text = history.pop()
    elif cmd == 'print':
        print(text)
"""
EDIT_3 = EDIT_HEAD + """history = []  # a stack of earlier versions
future = []   # a stack of undone versions
for line in sys.stdin.read().splitlines():
    cmd, _, arg = line.partition(' ')
    if cmd in ('type', 'delete'):
        history.append(text)
        future.clear()  # a new edit forgets the redo trail
        text = text + arg if cmd == 'type' else text[:max(0, len(text) - int(arg))]
    elif cmd == 'undo':
        if history:
            future.append(text)
            text = history.pop()
    elif cmd == 'redo':
        if future:
            history.append(text)
            text = future.pop()
    elif cmd == 'print':
        print(text)
"""
EDIT_STARTER = EDIT_HEAD + """for line in sys.stdin.read().splitlines():
    cmd, _, arg = line.partition(' ')
    # handle type, delete and print here
"""
TYPE_DELETE = "type Hello\ntype  world\nprint\ndelete 6\nprint\ndelete 99\ntype Hi\nprint"
UNDO = "type ab\ntype cd\nprint\nundo\nprint\nundo\nundo\ntype z\nprint\ndelete 1\nundo\nprint"
REDO = "type a\ntype b\ntype c\nundo\nundo\nprint\nredo\nprint\nredo\nredo\nprint\nundo\ntype X\nredo\nprint"

BEGINNER = project(
    "Project: Undo/redo text editor",
    "Every text editor has undo and redo - and both are just stacks. Build a tiny command-driven editor:\n\n"
    "1. type and delete.\n2. undo, with a stack of earlier versions.\n3. redo, with a second stack.\n\n"
    "Commands come one per line: 'type TEXT' adds TEXT (everything after the first space), 'delete N' removes the "
    "last N characters, 'print' prints the text.",
    run("Step 1 - Handle 'type TEXT', 'delete N' (never below empty) and 'print'.", "python",
        [t("edit", stdin=TYPE_DELETE)], ["Hello world\nHello\nHi"], EDIT_1, starter=EDIT_STARTER,
        hint="line.partition(' ') splits off the command; slicing removes the last N characters."),
    run("Step 2 - Add 'undo': before every type/delete, push the current text on a history stack; undo pops it back "
        "(and does nothing when there's no history).", "python",
        [t("edit", stdin=TYPE_DELETE), t("undo", stdin=UNDO)], ["Hello world\nHello\nHi", "abcd\nab\nz\nz"], EDIT_2,
        starter=EDIT_1, carry=True, require=[r"\.pop\(\)", r"append"]),
    run("Step 3 - Add 'redo' with a second stack: undo pushes the current text onto it, redo moves it back. Any new "
        "type/delete clears the redo stack.", "python",
        [t("undo", stdin=UNDO), t("redo", stdin=REDO)], ["abcd\nab\nz\nz", "a\nab\nabc\nabX"], EDIT_3,
        starter=EDIT_2, carry=True, require=[r"clear\(\)|=\s*\[\s*\]"]),
)

# ------------------------------------------------------------------ Intermediate: library catalogue
CAT_LOAD = """import sys

lines = sys.stdin.read().splitlines()
books = []
i = 0
while i < len(lines) and lines[i] != '---':
    title, year = lines[i].split('|')
    books.append((title, int(year)))
    i += 1
books.sort(key=lambda b: b[0].lower())
print(len(books), 'books')
for title, year in books:
    print(f'{title} ({year})')
"""
CAT_FIND = """
keys = [b[0].lower() for b in books]


def find(key):
    lo, hi = 0, len(keys) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if keys[mid] == key:
            return mid
        if keys[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
"""
CAT_PREFIX = """

def first_at_least(key):
    lo, hi = 0, len(keys)
    while lo < hi:
        mid = (lo + hi) // 2
        if keys[mid] < key:
            lo = mid + 1
        else:
            hi = mid
    return lo
"""
CAT_LOOP_FIND = """

for line in lines[i + 1:]:
    cmd, _, arg = line.partition(' ')
    if cmd == 'find':
        j = find(arg.lower())
        print(f'found: {books[j][0]} ({books[j][1]})' if j >= 0 else f'not found: {arg}')
"""
CAT_LOOP_PREFIX = CAT_LOOP_FIND + """    elif cmd == 'prefix':
        p = arg.lower()
        j = first_at_least(p)
        hits = []
        while j < len(keys) and keys[j].startswith(p):
            hits.append(books[j][0])
            j += 1
        print(', '.join(hits) if hits else 'none')
"""
CAT_1 = CAT_LOAD
CAT_2 = CAT_LOAD + CAT_FIND + CAT_LOOP_FIND
CAT_3 = CAT_LOAD + CAT_FIND + CAT_PREFIX + CAT_LOOP_PREFIX
SHELF = "Dune|1965\nemma|1815\nBeloved|1987\nDracula|1897\nAnimal Farm|1945\n---"
LISTING = "5 books\nAnimal Farm (1945)\nBeloved (1987)\nDracula (1897)\nDune (1965)\nemma (1815)"

INTERMEDIATE = project(
    "Project: Library catalogue",
    "Build the search behind a library catalogue - sort once, then answer lookups in O(log n):\n\n"
    "1. Load and sort the books.\n2. Find a title with binary search.\n3. Autocomplete: every title starting with a "
    "prefix.\n\nInput: lines 'Title|year' until a line '---', then commands. Titles are compared ignoring case.",
    run("Step 1 - Load the books, sort them by title ignoring case, and print 'N books' followed by each as 'Title (year)'.",
        "python", [t("shelf", stdin=SHELF)], [LISTING], CAT_1,
        starter="import sys\n\nlines = sys.stdin.read().splitlines()\nbooks = []\n", require=[r"key\s*="]),
    run("Step 2 - After '---', answer 'find TITLE' with your own binary search over the sorted (lower-case) titles: print "
        "'found: Title (year)' or 'not found: TITLE'.", "python",
        [t("find", stdin=SHELF + "\nfind dune\nfind Emma\nfind Ulysses")],
        [LISTING + "\nfound: Dune (1965)\nfound: emma (1815)\nnot found: Ulysses"], CAT_2, starter=CAT_1, carry=True,
        require=[r"//\s*2"], forbid=[r"\.index\(", r"\bbisect\b"]),
    run("Step 3 - Add 'prefix P': binary-search the first title >= P, then walk forward while titles start with P. "
        "Print them joined with ', ' (in sorted order), or 'none'.", "python",
        [t("autocomplete", stdin=SHELF + "\nfind dune\nprefix d\nprefix DU\nprefix z")],
        [LISTING + "\nfound: Dune (1965)\nDracula, Dune\nDune\nnone"], CAT_3, starter=CAT_2, carry=True,
        require=[r"startswith"], forbid=[r"\bbisect\b"]),
)

# ------------------------------------------------------------------ Advanced: metro route planner
METRO_LOAD = """import sys
from collections import deque

lines = sys.stdin.read().splitlines()
graph = {}
i = 0
while i < len(lines) and lines[i] != '---':
    a, b = lines[i].split()
    graph.setdefault(a, set()).add(b)
    graph.setdefault(b, set()).add(a)
    i += 1
for station in sorted(graph):
    print(f"{station}: {', '.join(sorted(graph[station]))}")
"""
METRO_BFS_2 = """

def stops(start, goal):
    if start not in graph or goal not in graph:
        return None
    dist = {start: 0}
    q = deque([start])
    while q:
        node = q.popleft()
        if node == goal:
            return dist[node]
        for nb in sorted(graph[node]):
            if nb not in dist:
                dist[nb] = dist[node] + 1
                q.append(nb)
    return None


for line in lines[i + 1:]:
    _, a, b = line.split()
    n = stops(a, b)
    print(f'{a} -> {b}: no route' if n is None else f'{a} -> {b}: {n} stops')
"""
METRO_BFS_3 = """

def route(start, goal):
    if start not in graph or goal not in graph:
        return None
    parent = {start: None}
    q = deque([start])
    while q:
        node = q.popleft()
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1]
        for nb in sorted(graph[node]):
            if nb not in parent:
                parent[nb] = node
                q.append(nb)
    return None


for line in lines[i + 1:]:
    _, a, b = line.split()
    path = route(a, b)
    print(f'{a} -> {b}: no route' if path is None else f"{' -> '.join(path)} ({len(path) - 1} stops)")
"""
METRO = "A B\nB C\nC D\nA E\nE D\nD F\nG H\n---"
MAP = "A: B, E\nB: A, C\nC: B, D\nD: C, E, F\nE: A, D\nF: D\nG: H\nH: G"
QUERIES = "\nroute A F\nroute B E\nroute A A\nroute A G\nroute A Z"

ADVANCED = project(
    "Project: Metro route planner",
    "Journey planners are graph algorithms. Build one for a small metro map:\n\n1. Load the map as an adjacency "
    "list.\n2. Fewest stops between two stations with BFS.\n3. The actual route, rebuilt from BFS parents.\n\n"
    "Input: connections 'A B' (both directions) until '---', then queries 'route FROM TO'. Visit neighbours in "
    "alphabetical order so routes are predictable.",
    run("Step 1 - Build the adjacency list and print every station A-Z with its neighbours A-Z, as 'D: C, E, F'.", "python",
        [t("map", stdin=METRO)], [MAP], METRO_LOAD,
        starter="import sys\nfrom collections import deque\n\nlines = sys.stdin.read().splitlines()\ngraph = {}\n"),
    run("Step 2 - Answer each 'route A B' with BFS: print 'A -> B: N stops', or 'A -> B: no route' (also for unknown "
        "stations).", "python",
        [t("routes", stdin=METRO + QUERIES)],
        [MAP + "\nA -> F: 3 stops\nB -> E: 2 stops\nA -> A: 0 stops\nA -> G: no route\nA -> Z: no route"],
        METRO_LOAD + METRO_BFS_2, starter=METRO_LOAD, carry=True, require=[r"popleft"]),
    run("Step 3 - Print the route itself: record each station's parent during BFS, walk back from the goal, and print "
        "'A -> E -> D -> F (3 stops)' (or the same 'no route' line).", "python",
        [t("routes", stdin=METRO + QUERIES)],
        [MAP + "\nA -> E -> D -> F (3 stops)\nB -> A -> E (2 stops)\nA (0 stops)\nA -> G: no route\nA -> Z: no route"],
        METRO_LOAD + METRO_BFS_3, starter=METRO_LOAD + METRO_BFS_2, carry=True, require=[r"popleft", r"parent|prev|came_from"]),
)

PROJECTS = {4: BEGINNER, 6: INTERMEDIATE, 8: ADVANCED}
