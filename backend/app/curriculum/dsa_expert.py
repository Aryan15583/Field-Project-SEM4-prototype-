"""Data Structures & Algorithms - Expert section, part 1 (units 9-15): sorting, searching, hashing, stacks & queues,
linked lists, trees, heaps & intervals. Taught in Python (runs in the browser with Pyodide)."""
from .dsl import fill, lesson, mcq, order, run, section, t, unit


def pr(expr: str) -> dict:
    return t(expr, append=f"print({expr})")


EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 9
    unit(
        "Unit 9 · Sorting in depth",
        lesson(
            "Merge sort",
            """Merge sort splits the list in half, sorts each half recursively, then MERGES the two sorted halves. It is O(n log n) in every case and stable.

def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: out.append(left[i]); i += 1
        else: out.append(right[j]); j += 1
    return out + left[i:] + right[j:]

It needs O(n) extra memory for the merges.""",
            mcq("What is merge sort's time complexity?", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 0),
            mcq("Why does merge sort use extra memory?", ["The merge builds a new list", "It uses recursion only", "It copies strings", "It does not"], 0),
            mcq("What does 'stable' mean for a sort?", ["Equal items keep their original order", "It never fails", "It uses no memory", "It is in place"], 0),
            run("Write merge_sort(a) returning a new sorted list (do NOT use sorted() or .sort()).", "python",
                [pr("merge_sort([5, 2, 9, 1, 5, 6])"), pr("merge_sort([])"), pr("merge_sort([3, -1, 2, -5, 0])")],
                ["[1, 2, 5, 5, 6, 9]", "[]", "[-5, -1, 0, 2, 3]"],
                "def merge_sort(a):\n    if len(a) <= 1:\n        return a\n    mid = len(a) // 2\n    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])\n    out, i, j = [], 0, 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            out.append(left[i])\n            i += 1\n        else:\n            out.append(right[j])\n            j += 1\n    return out + left[i:] + right[j:]",
                starter="def merge_sort(a):\n    pass\n", forbid=[r"\bsorted\s*\(", r"\.sort\s*\("]),
        ),
        lesson(
            "Quicksort and partitioning",
            """Quicksort picks a PIVOT, partitions the others into 'smaller' and 'larger', and sorts each part:

def quicksort(a):
    if len(a) <= 1:
        return a
    pivot = a[len(a) // 2]
    return quicksort([x for x in a if x < pivot]) + [x for x in a if x == pivot] + quicksort([x for x in a if x > pivot])

Average O(n log n); worst case O(n²) with bad pivots (for example always picking the smallest). Real implementations pick pivots carefully and partition in place.""",
            mcq("What is quicksort's average time?", ["O(n log n)", "O(n²)", "O(n)", "O(1)"], 0),
            mcq("When does quicksort hit O(n²)?", ["With consistently bad pivots", "On random data", "On empty lists", "Never"], 0),
            mcq("What does partitioning do?", ["Splits items around the pivot", "Merges lists", "Reverses", "Counts"], 0),
            run("Write quicksort(a) using the pivot-and-partition idea (three list comprehensions). Return a new sorted list.", "python",
                [pr("quicksort([3, 6, 1, 8, 2, 9, 2])"), pr("quicksort([])"), pr("quicksort([1, 1, 1])")],
                ["[1, 2, 2, 3, 6, 8, 9]", "[]", "[1, 1, 1]"],
                "def quicksort(a):\n    if len(a) <= 1:\n        return a\n    pivot = a[len(a) // 2]\n    return quicksort([x for x in a if x < pivot]) + [x for x in a if x == pivot] + quicksort([x for x in a if x > pivot])",
                starter="def quicksort(a):\n    pass\n", forbid=[r"\bsorted\s*\(", r"\.sort\s*\("]),
        ),
        lesson(
            "Counting sort & the n log n limit",
            """Comparison sorts (merge, quick, heap...) can't beat O(n log n) in general. But when the values are SMALL integers you can skip comparing: counting sort tallies how many of each value there are, then writes them out - O(n + k) for values 0..k.

def counting_sort(a, k):
    counts = [0] * (k + 1)
    for x in a: counts[x] += 1
    return [v for v, c in enumerate(counts) for _ in range(c)]

Radix sort applies the same idea digit by digit.""",
            mcq("What is the best any comparison sort can do in general?", ["O(n log n)", "O(n)", "O(log n)", "O(1)"], 0),
            mcq("When is counting sort a good choice?", ["Small integer values", "Long strings", "Floats", "Objects"], 0),
            mcq("What is counting sort's time for n items with values 0..k?", ["O(n + k)", "O(n²)", "O(k²)", "O(log n)"], 0),
            run("Write counting_sort(a, k) for integers in 0..k returning a new sorted list, without sorted() or sort().", "python",
                [pr("counting_sort([4, 1, 3, 1, 0, 4], 4)"), pr("counting_sort([], 5)"), pr("counting_sort([2, 2, 2], 2)")],
                ["[0, 1, 1, 3, 4, 4]", "[]", "[2, 2, 2]"],
                "def counting_sort(a, k):\n    counts = [0] * (k + 1)\n    for x in a:\n        counts[x] += 1\n    out = []\n    for v, c in enumerate(counts):\n        out.extend([v] * c)\n    return out",
                starter="def counting_sort(a, k):\n    pass\n", forbid=[r"\bsorted\s*\(", r"\.sort\s*\("]),
        ),
    ),
    # ------------------------------------------------------------------ 10
    unit(
        "Unit 10 · Searching variants",
        lesson(
            "Lower and upper bound",
            """Binary search can find the FIRST position where a value could go (lower bound) or the position AFTER the last equal value (upper bound). The difference counts duplicates.

def lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x: lo = mid + 1
        else: hi = mid
    return lo

For upper bound use a[mid] <= x. Python's bisect_left / bisect_right do exactly this.""",
            mcq("What does lower_bound return for [1, 2, 2, 3] and 2?", ["1", "2", "3", "0"], 0),
            mcq("What does upper_bound return for [1, 2, 2, 3] and 2?", ["3", "1", "2", "4"], 0),
            mcq("How do you count the copies of x in a sorted list?", ["upper_bound - lower_bound", "lower_bound only", "len(a)", "upper_bound + 1"], 0),
            run("Write lower_bound(a, x) and upper_bound(a, x) by hand (no bisect), then count_of(a, x) = upper - lower.", "python",
                [pr("count_of([1, 2, 2, 2, 3], 2)"), pr("count_of([1, 3], 2)"), pr("(lower_bound([1, 2, 2, 3], 2), upper_bound([1, 2, 2, 3], 2))")],
                ["3", "0", "(1, 3)"],
                "def lower_bound(a, x):\n    lo, hi = 0, len(a)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if a[mid] < x:\n            lo = mid + 1\n        else:\n            hi = mid\n    return lo\n\ndef upper_bound(a, x):\n    lo, hi = 0, len(a)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if a[mid] <= x:\n            lo = mid + 1\n        else:\n            hi = mid\n    return lo\n\ndef count_of(a, x):\n    return upper_bound(a, x) - lower_bound(a, x)",
                starter="def lower_bound(a, x):\n    pass\n\ndef upper_bound(a, x):\n    pass\n\ndef count_of(a, x):\n    pass\n", forbid=[r"bisect", r"\.count\("]),
        ),
        lesson(
            "Binary search on the answer",
            """Binary search isn't only for lists. If you can ask 'is X big enough?' and the answer flips from no to yes at some point, binary search the ANSWER.

Example - the smallest eating speed k so that you finish all piles in h hours:

def can_finish(piles, h, k):
    return sum(-(-p // k) for p in piles) <= h      # -(-p // k) is ceiling division

lo, hi = 1, max(piles); search for the smallest k where can_finish is True.""",
            mcq("When can you binary search on the answer?", ["When feasibility flips once from false to true", "Always", "Only on lists", "Only for primes"], 0),
            mcq("What does -(-p // k) compute?", ["Ceiling of p / k", "Floor of p / k", "p % k", "Negative k"], 0),
            mcq("What is the typical cost?", ["O(n log(range))", "O(n²)", "O(n)", "O(1)"], 0),
            run("Read piles on line 1 (space-separated) and hours h on line 2. Print the smallest integer eating speed k that finishes all piles within h hours (each hour you eat from one pile, at most k bananas).", "python",
                [t("classic", stdin="3 6 7 11\n8"), t("tight", stdin="30 11 23 4 20\n5"), t("loose", stdin="30 11 23 4 20\n6")],
                ["4", "30", "23"],
                "piles = [int(x) for x in input().split()]\nh = int(input())\nlo, hi = 1, max(piles)\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    if sum(-(-p // mid) for p in piles) <= h:\n        hi = mid\n    else:\n        lo = mid + 1\nprint(lo)"),
        ),
        lesson(
            "Three-sum with two pointers",
            """After sorting, a triple search becomes: fix one number, then run two pointers over the rest.

def three_sum(nums):
    nums.sort(); out = []
    for i, a in enumerate(nums):
        if i and a == nums[i - 1]: continue            # skip duplicate first numbers
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = a + nums[lo] + nums[hi]
            if s < 0: lo += 1
            elif s > 0: hi -= 1
            else: out.append([a, nums[lo], nums[hi]]); ... skip duplicates

Total O(n²) instead of O(n³).""",
            mcq("What is the complexity of the sort + two-pointer three-sum?", ["O(n²)", "O(n³)", "O(n)", "O(n log n)"], 0),
            mcq("Why sort first?", ["Pointers can move based on the sum", "To use less memory", "To remove zeros", "Python requires it"], 0),
            mcq("Why skip repeated first numbers?", ["To avoid duplicate triples", "To save memory", "To sort", "It is required by Python"], 0),
            run("Read numbers on one line. Print how many DIFFERENT triples (as value sets, unordered) sum to zero, using sorting and two pointers.", "python",
                [t("classic", stdin="-1 0 1 2 -1 -4"), t("none", stdin="1 2 3"), t("zeros", stdin="0 0 0 0")],
                ["2", "0", "1"],
                "nums = sorted(int(x) for x in input().split())\ncount = 0\nfor i, a in enumerate(nums):\n    if i and a == nums[i - 1]:\n        continue\n    lo, hi = i + 1, len(nums) - 1\n    while lo < hi:\n        s = a + nums[lo] + nums[hi]\n        if s < 0:\n            lo += 1\n        elif s > 0:\n            hi -= 1\n        else:\n            count += 1\n            lo += 1\n            while lo < hi and nums[lo] == nums[lo - 1]:\n                lo += 1\nprint(count)"),
        ),
    ),
    # ------------------------------------------------------------------ 11
    unit(
        "Unit 11 · Hashing in depth",
        lesson(
            "Grouping anagrams",
            """Two words are anagrams if they have the same letters. A canonical KEY makes them collide in a dictionary: sort the letters.

groups = {}
for w in words:
    groups.setdefault("".join(sorted(w)), []).append(w)

'eat', 'tea' and 'ate' all become 'aet'. Sorting costs O(k log k) per word of length k; a tuple of 26 letter counts is O(k).""",
            mcq("What key makes anagrams collide?", ["The sorted letters", "The length", "The first letter", "The last letter"], 0),
            mcq("What does setdefault(key, []) return for a new key?", ["A new empty list stored under key", "None", "An error", "0"], 0),
            mcq("Why is a canonical key powerful?", ["Equivalent things map to the same key", "It is faster than anything", "It sorts the dictionary", "It avoids memory"], 0),
            run("Read words on one line. Print the number of anagram groups with at least 2 words, then the size of the biggest group.", "python",
                [t("classic", stdin="eat tea tan ate nat bat"), t("none", stdin="a b c"), t("one", stdin="ab ba ab")],
                ["2\n3", "0\n1", "1\n3"],
                "words = input().split()\ngroups = {}\nfor w in words:\n    groups.setdefault(''.join(sorted(w)), []).append(w)\nbig = [g for g in groups.values() if len(g) >= 2]\nprint(len(big))\nprint(max(len(g) for g in groups.values()))"),
        ),
        lesson(
            "Prefix sums + hash maps",
            """To count subarrays whose sum equals k in ONE pass, keep a running prefix sum and a dictionary of how many times each prefix sum has appeared. A subarray ending here sums to k when (prefix - k) was seen before.

seen = {0: 1}; total = 0; count = 0
for x in nums:
    total += x
    count += seen.get(total - k, 0)
    seen[total] = seen.get(total, 0) + 1

O(n) instead of O(n²) for checking every pair.""",
            mcq("What does seen = {0: 1} represent?", ["The empty prefix", "A zero in the data", "A counter bug", "The answer"], 0),
            mcq("When does a subarray ending here sum to k?", ["When prefix - k was seen", "When prefix equals k", "When prefix is 0", "Always"], 0),
            mcq("What is the complexity?", ["O(n)", "O(n²)", "O(n log n)", "O(2^n)"], 0),
            run("Read numbers on line 1 and a target k on line 2. Print how many contiguous subarrays sum to k (numbers may be negative).", "python",
                [t("simple", stdin="1 1 1\n2"), t("negatives", stdin="1 -1 1 -1\n0"), t("none", stdin="5 6\n3")],
                ["2", "4", "0"],
                "nums = [int(x) for x in input().split()]\nk = int(input())\nseen = {0: 1}\ntotal = count = 0\nfor x in nums:\n    total += x\n    count += seen.get(total - k, 0)\n    seen[total] = seen.get(total, 0) + 1\nprint(count)"),
        ),
        lesson(
            "LRU cache with OrderedDict",
            """An LRU (least recently used) cache holds a fixed number of entries and evicts the one used longest ago. collections.OrderedDict remembers order and can move keys to the end in O(1):

from collections import OrderedDict
class LRU:
    def __init__(self, cap): self.cap, self.d = cap, OrderedDict()
    def get(self, k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        self.d[k] = v; self.d.move_to_end(k)
        if len(self.d) > self.cap: self.d.popitem(last=False)

Caches speed up repeated work: browsers, databases and CPUs all use them.""",
            mcq("What does an LRU cache evict?", ["The least recently used entry", "The newest entry", "The biggest value", "A random entry"], 0),
            mcq("What does move_to_end do?", ["Marks a key as most recently used", "Deletes the key", "Sorts the dict", "Copies it"], 0),
            mcq("What does popitem(last=False) remove?", ["The oldest entry", "The newest entry", "All entries", "A random one"], 0),
            run("Write class LRU(cap) with get(k) (-1 if missing) and put(k, v). The test prints get results after some puts.", "python",
                [t("evict", append="c = LRU(2)\nc.put(1, 1); c.put(2, 2)\nprint(c.get(1))\nc.put(3, 3)\nprint(c.get(2), c.get(3), c.get(1))"),
                 t("overwrite", append="c = LRU(1)\nc.put('a', 1); c.put('a', 2)\nprint(c.get('a'))")],
                ["1\n-1 3 1", "2"],
                "from collections import OrderedDict\n\nclass LRU:\n    def __init__(self, cap):\n        self.cap = cap\n        self.d = OrderedDict()\n    def get(self, k):\n        if k not in self.d:\n            return -1\n        self.d.move_to_end(k)\n        return self.d[k]\n    def put(self, k, v):\n        self.d[k] = v\n        self.d.move_to_end(k)\n        if len(self.d) > self.cap:\n            self.d.popitem(last=False)",
                starter="class LRU:\n    def __init__(self, cap):\n        pass\n", require=[r"OrderedDict|move_to_end"]),
        ),
    ),
    # ------------------------------------------------------------------ 12
    unit(
        "Unit 12 · Stacks & queues in depth",
        lesson(
            "Evaluating expressions",
            """Stacks evaluate arithmetic written in postfix (reverse Polish) notation: '3 4 + 2 *' means (3 + 4) * 2. Read tokens left to right: push numbers; for an operator pop two numbers, apply it, push the result.

stack = []
for tok in tokens:
    if tok in "+-*/":
        b, a = stack.pop(), stack.pop()
        stack.append(apply(tok, a, b))
    else:
        stack.append(int(tok))

Note the order: the FIRST pop is the right operand (b).""",
            mcq("What is '3 4 + 2 *' in normal notation?", ["(3 + 4) * 2", "3 + 4 * 2", "3 * 4 + 2", "3 + (4 * 2)"], 0),
            mcq("For an operator, what is the first pop?", ["The right operand", "The left operand", "The operator", "A bracket"], 0),
            mcq("What is left on the stack at the end?", ["The result", "Nothing", "The operators", "The last token"], 0),
            run("Read a postfix expression with + - * (integers, separated by spaces). Print its value.", "python",
                [t("basic", stdin="3 4 + 2 *"), t("order", stdin="10 2 8 * + 3 -"), t("single", stdin="42")],
                ["14", "23", "42"],
                "stack = []\nfor tok in input().split():\n    if tok in '+-*':\n        b, a = stack.pop(), stack.pop()\n        stack.append(a + b if tok == '+' else a - b if tok == '-' else a * b)\n    else:\n        stack.append(int(tok))\nprint(stack[0])"),
        ),
        lesson(
            "Sliding window maximum",
            """A deque can keep the indexes of useful candidates in DECREASING value order, so the maximum of the window is always at the front. Each index is added and removed at most once - O(n) overall.

dq = deque()
for i, x in enumerate(nums):
    while dq and nums[dq[-1]] <= x: dq.pop()      # smaller items can never be the max again
    dq.append(i)
    if dq[0] <= i - k: dq.popleft()               # front slid out of the window
    if i >= k - 1: out.append(nums[dq[0]])""",
            mcq("What does the deque keep in order?", ["Indexes with decreasing values", "All numbers sorted", "Only the maximum", "Random indexes"], 0),
            mcq("Why pop smaller items from the back?", ["They can never be the window max again", "To sort them", "To save memory only", "It is required"], 0),
            mcq("What is the total complexity?", ["O(n)", "O(n k)", "O(n²)", "O(n log n)"], 0),
            run("Read numbers on line 1 and window size k on line 2. Print the maximum of each window of k consecutive numbers, space-separated.", "python",
                [t("classic", stdin="1 3 -1 -3 5 3 6 7\n3"), t("k=1", stdin="4 2 7\n1"), t("whole", stdin="2 9 4\n3")],
                ["3 3 5 5 6 7", "4 2 7", "9"],
                "from collections import deque\nnums = [int(x) for x in input().split()]\nk = int(input())\ndq, out = deque(), []\nfor i, x in enumerate(nums):\n    while dq and nums[dq[-1]] <= x:\n        dq.pop()\n    dq.append(i)\n    if dq[0] <= i - k:\n        dq.popleft()\n    if i >= k - 1:\n        out.append(nums[dq[0]])\nprint(' '.join(map(str, out)))",
                require=[r"deque"]),
        ),
        lesson(
            "Min stack",
            """A MinStack supports push, pop and get_min all in O(1) by storing, with each item, the minimum so far:

class MinStack:
    def __init__(self): self.items = []          # (value, min_so_far)
    def push(self, x):
        m = min(x, self.items[-1][1]) if self.items else x
        self.items.append((x, m))
    def pop(self): return self.items.pop()[0]
    def get_min(self): return self.items[-1][1]

Trading a little extra memory for constant-time answers is a classic pattern.""",
            mcq("What does each stack entry store?", ["The value and the minimum so far", "Only the value", "Only the min", "An index"], 0),
            mcq("What is get_min's complexity?", ["O(1)", "O(n)", "O(log n)", "O(n²)"], 0),
            mcq("What does the extra memory buy?", ["Constant-time minimum", "Sorting", "Faster push only", "Nothing"], 0),
            run("Write class MinStack with push(x), pop() and get_min(). The test prints the min after several operations.", "python",
                [t("flow", append="s = MinStack()\ns.push(5); s.push(3); s.push(7)\nprint(s.get_min())\ns.pop()\nprint(s.get_min())\ns.pop()\nprint(s.get_min())"),
                 t("single", append="s = MinStack()\ns.push(2)\nprint(s.get_min(), s.pop())")],
                ["3\n3\n5", "2 2"],
                "class MinStack:\n    def __init__(self):\n        self.items = []\n    def push(self, x):\n        m = min(x, self.items[-1][1]) if self.items else x\n        self.items.append((x, m))\n    def pop(self):\n        return self.items.pop()[0]\n    def get_min(self):\n        return self.items[-1][1]",
                starter="class MinStack:\n    def __init__(self):\n        self.items = []\n"),
        ),
    ),
    # ------------------------------------------------------------------ 13
    unit(
        "Unit 13 · Linked lists in depth",
        lesson(
            "Reversing a linked list",
            """Reverse in place by walking the list and pointing each node back at the previous one:

def reverse(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev, head = head, nxt
    return prev

Always save head.next BEFORE overwriting it, or you lose the rest of the list. O(n) time, O(1) extra space.""",
            mcq("What is the extra space of the in-place reverse?", ["O(1)", "O(n)", "O(log n)", "O(n²)"], 0),
            mcq("Why save nxt = head.next first?", ["Otherwise the rest of the list is lost", "To count nodes", "To sort", "Python requires it"], 0),
            mcq("What does reverse return?", ["The new head (old tail)", "The old head", "None", "The length"], 0),
            run("Using the Node class provided in the program, write reverse(head). The test builds 1 -> 2 -> 3 and prints the reversed values.", "python",
                [t("three", append="head = Node(1, Node(2, Node(3)))\nr = reverse(head)\nout = []\nwhile r:\n    out.append(r.val); r = r.next\nprint(out)"), t("empty", append="print(reverse(None))"), t("single", append="r = reverse(Node(9))\nprint(r.val, r.next)")],
                ["[3, 2, 1]", "None", "9 None"],
                "class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse(head):\n    prev = None\n    while head:\n        nxt = head.next\n        head.next = prev\n        prev, head = head, nxt\n    return prev",
                starter="class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse(head):\n    pass\n"),
        ),
        lesson(
            "Fast and slow pointers",
            """Two pointers moving at different speeds solve classic list problems:

slow, fast = head, head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
# when fast reaches the end, slow is at the MIDDLE

If the list has a CYCLE, the fast pointer eventually laps the slow one and they meet (Floyd's algorithm): O(n) time, O(1) space - no set of visited nodes needed.""",
            mcq("Where is slow when fast reaches the end?", ["At the middle", "At the start", "At the end", "Past the end"], 0),
            mcq("How does Floyd's algorithm detect a cycle?", ["The fast pointer catches the slow one", "It counts nodes", "It sorts", "It reverses"], 0),
            mcq("What is its extra space?", ["O(1)", "O(n)", "O(log n)", "O(n²)"], 0),
            run("Using the Node class, write middle(head) returning the value of the middle node (the second of two middles for even lengths) and has_cycle(head) using fast/slow pointers.", "python",
                [t("middle", append="h = Node(1, Node(2, Node(3, Node(4, Node(5)))))\nprint(middle(h))"), t("even", append="print(middle(Node(1, Node(2, Node(3, Node(4))))))"),
                 t("cycle", append="a = Node(1); b = Node(2); c = Node(3)\na.next = b; b.next = c; c.next = b\nprint(has_cycle(a), has_cycle(Node(1, Node(2))))")],
                ["3", "3", "True False"],
                "class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef middle(head):\n    slow = fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n    return slow.val\n\ndef has_cycle(head):\n    slow = fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow is fast:\n            return True\n    return False",
                starter="class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef middle(head):\n    pass\n\ndef has_cycle(head):\n    pass\n"),
        ),
        lesson(
            "Merging sorted lists",
            """Merging two sorted linked lists splices nodes together without creating new ones. A DUMMY head node removes special cases:

def merge(a, b):
    dummy = tail = Node(0)
    while a and b:
        if a.val <= b.val: tail.next, a = a, a.next
        else: tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next

This is the heart of merge sort for linked lists.""",
            mcq("What does the dummy node avoid?", ["Special cases for an empty result", "Memory use", "Sorting", "Recursion"], 0),
            mcq("What does tail.next = a or b do?", ["Attaches whichever list is left over", "Deletes a", "Reverses b", "Copies values"], 0),
            mcq("What is the time complexity?", ["O(n + m)", "O(n m)", "O(log n)", "O(1)"], 0),
            run("Using the Node class, write merge(a, b) merging two sorted lists into one sorted list (reusing nodes). The test builds lists from Python lists and prints the merged values.", "python",
                [t("merge", append="def build(xs):\n    head = None\n    for x in reversed(xs):\n        head = Node(x, head)\n    return head\nr = merge(build([1, 4, 6]), build([2, 3, 7, 8]))\nout = []\nwhile r:\n    out.append(r.val); r = r.next\nprint(out)"),
                 t("empty", append="print(merge(None, None))")],
                ["[1, 2, 3, 4, 6, 7, 8]", "None"],
                "class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef merge(a, b):\n    dummy = tail = Node(0)\n    while a and b:\n        if a.val <= b.val:\n            tail.next, a = a, a.next\n        else:\n            tail.next, b = b, b.next\n        tail = tail.next\n    tail.next = a or b\n    return dummy.next",
                starter="class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef merge(a, b):\n    pass\n"),
        ),
    ),
    # ------------------------------------------------------------------ 14
    unit(
        "Unit 14 · Trees in depth",
        lesson(
            "Tree traversals",
            """Four ways to visit every node of a binary tree:

in-order    left, node, right      (a BST comes out sorted)
pre-order   node, left, right      (copy a tree)
post-order  left, right, node      (delete / evaluate a tree)
level-order row by row using a queue (BFS)

def inorder(n): return inorder(n.left) + [n.val] + inorder(n.right) if n else []

Depth-first orders use recursion (or a stack); level-order uses a queue.""",
            mcq("Which traversal returns a BST's values in sorted order?", ["In-order", "Pre-order", "Post-order", "Level-order"], 0),
            mcq("Which uses a queue?", ["Level-order", "In-order", "Pre-order", "Post-order"], 0),
            mcq("Which visits the root first?", ["Pre-order", "In-order", "Post-order", "None"], 0),
            run("Using the Node class provided, write inorder(n), preorder(n), postorder(n) and levelorder(n) returning lists of values. The test builds a small tree.", "python",
                [t("all", append="r = Node(1, Node(2, Node(4), Node(5)), Node(3))\nprint(inorder(r), preorder(r), postorder(r), levelorder(r))"), t("empty", append="print(inorder(None), levelorder(None))")],
                ["[4, 2, 5, 1, 3] [1, 2, 4, 5, 3] [4, 5, 2, 3, 1] [1, 2, 3, 4, 5]", "[] []"],
                "from collections import deque\n\nclass Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef inorder(n):\n    return inorder(n.left) + [n.val] + inorder(n.right) if n else []\n\ndef preorder(n):\n    return [n.val] + preorder(n.left) + preorder(n.right) if n else []\n\ndef postorder(n):\n    return postorder(n.left) + postorder(n.right) + [n.val] if n else []\n\ndef levelorder(n):\n    out, q = [], deque([n] if n else [])\n    while q:\n        x = q.popleft()\n        out.append(x.val)\n        if x.left:\n            q.append(x.left)\n        if x.right:\n            q.append(x.right)\n    return out",
                starter="class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef inorder(n):\n    pass\n\ndef preorder(n):\n    pass\n\ndef postorder(n):\n    pass\n\ndef levelorder(n):\n    pass\n"),
        ),
        lesson(
            "Height, balance & diameter",
            """Many tree properties are computed bottom-up by combining the answers from the children:

def height(n): return 0 if not n else 1 + max(height(n.left), height(n.right))

A tree is BALANCED if at every node the two sub-heights differ by at most 1 - this keeps operations O(log n). The DIAMETER is the longest path between any two nodes: at each node, height(left) + height(right), taking the best over all nodes.""",
            mcq("What is the height of an empty tree here?", ["0", "1", "-1", "None"], 0),
            mcq("Why does balance matter?", ["It keeps operations O(log n)", "It saves memory", "It sorts values", "It removes duplicates"], 0),
            mcq("What do bottom-up tree algorithms do?", ["Combine answers from the children", "Start at leaves only", "Sort nodes", "Delete nodes"], 0),
            run("Using the Node class, write height(n) and is_balanced(n) (heights of both children differ by at most 1 at EVERY node).", "python",
                [t("balanced", append="print(is_balanced(Node(1, Node(2), Node(3))), height(Node(1, Node(2, Node(4)), None)))"), t("unbalanced", append="r = Node(1, Node(2, Node(3, Node(4))), None)\nprint(is_balanced(r), height(r))"), t("empty", append="print(is_balanced(None), height(None))")],
                ["True 3", "False 4", "True 0"],
                "class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef height(n):\n    return 0 if not n else 1 + max(height(n.left), height(n.right))\n\ndef is_balanced(n):\n    if not n:\n        return True\n    return abs(height(n.left) - height(n.right)) <= 1 and is_balanced(n.left) and is_balanced(n.right)",
                starter="class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef height(n):\n    pass\n\ndef is_balanced(n):\n    pass\n"),
        ),
        lesson(
            "Binary search tree operations",
            """A BST keeps smaller values left and larger right, so search, insert and validate follow one path:

def insert(n, x):
    if not n: return Node(x)
    if x < n.val: n.left = insert(n.left, x)
    elif x > n.val: n.right = insert(n.right, x)
    return n

Average O(log n) per operation; a sorted insertion order degenerates into a linked list (O(n)). To VALIDATE a BST pass down allowed (low, high) bounds - checking only the children is not enough.""",
            mcq("What is the BST worst case?", ["A chain from sorted inserts, O(n)", "O(log n) always", "O(1)", "O(n²)"], 0),
            mcq("Why is checking only each node's children NOT enough to validate a BST?", ["A deep node can break an ancestor's bound", "It's too slow", "Children are random", "Python limits it"], 0),
            mcq("Where does a new value go?", ["Left if smaller, right if larger", "Always left", "Always right", "At the root"], 0),
            run("Using the Node class, write insert(n, x), contains(n, x) and is_bst(n, lo=None, hi=None) (strict: no duplicates allowed).", "python",
                [t("insert", append="r = None\nfor v in [5, 3, 8, 1, 4]:\n    r = insert(r, v)\nprint(contains(r, 4), contains(r, 7), is_bst(r))"), t("bad", append="bad = Node(5, Node(3, None, Node(6)), Node(8))\nprint(is_bst(bad))"), t("empty", append="print(contains(None, 1), is_bst(None))")],
                ["True False True", "False", "False True"],
                "class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef insert(n, x):\n    if not n:\n        return Node(x)\n    if x < n.val:\n        n.left = insert(n.left, x)\n    elif x > n.val:\n        n.right = insert(n.right, x)\n    return n\n\ndef contains(n, x):\n    while n:\n        if x == n.val:\n            return True\n        n = n.left if x < n.val else n.right\n    return False\n\ndef is_bst(n, lo=None, hi=None):\n    if not n:\n        return True\n    if (lo is not None and n.val <= lo) or (hi is not None and n.val >= hi):\n        return False\n    return is_bst(n.left, lo, n.val) and is_bst(n.right, n.val, hi)",
                starter="class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef insert(n, x):\n    pass\n\ndef contains(n, x):\n    pass\n\ndef is_bst(n, lo=None, hi=None):\n    pass\n"),
        ),
    ),
    # ------------------------------------------------------------------ 15
    unit(
        "Unit 15 · Heaps & intervals",
        lesson(
            "Top K with a heap",
            """To find the k largest of n items without sorting everything, keep a MIN-heap of size k: push each item and pop the smallest when the heap grows beyond k. The heap always holds the k largest seen so far - O(n log k).

import heapq
h = []
for x in nums:
    heapq.heappush(h, x)
    if len(h) > k: heapq.heappop(h)

h[0] is then the k-th largest. Python's heapq.nlargest(k, nums) does the same.""",
            mcq("Which heap finds the k LARGEST items efficiently?", ["A min-heap of size k", "A max-heap of size n", "A sorted list", "A stack"], 0),
            mcq("What is h[0] after processing all items with size k?", ["The k-th largest", "The largest", "The smallest overall", "The median"], 0),
            mcq("What is the complexity?", ["O(n log k)", "O(n²)", "O(k)", "O(n)"], 0),
            run("Read numbers on line 1 and k on line 2. Print the k-th largest number (k=1 is the maximum) using a heap of size k.", "python",
                [t("classic", stdin="3 2 1 5 6 4\n2"), t("duplicates", stdin="3 2 3 1 2 4 5 5 6\n4"), t("max", stdin="7 9 1\n1")],
                ["5", "4", "9"],
                "import heapq\nnums = [int(x) for x in input().split()]\nk = int(input())\nh = []\nfor x in nums:\n    heapq.heappush(h, x)\n    if len(h) > k:\n        heapq.heappop(h)\nprint(h[0])",
                require=[r"heapq"]),
        ),
        lesson(
            "Merging k sorted lists",
            """Merge k sorted lists with a heap holding the CURRENT front of each list. Pop the smallest, then push that list's next item:

heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
heapq.heapify(heap)
while heap:
    val, i, j = heapq.heappop(heap)
    out.append(val)
    if j + 1 < len(lists[i]): heapq.heappush(heap, (lists[i][j + 1], i, j + 1))

O(N log k) for N total items - far better than concatenating and sorting when k is small. (heapq.merge does this for you.)""",
            mcq("What does the heap hold?", ["The current front item of each list", "All items", "Only the largest", "Indexes"], 0),
            mcq("What is the complexity for N total items and k lists?", ["O(N log k)", "O(N k)", "O(N²)", "O(k)"], 0),
            mcq("Why store (value, list index, position) tuples?", ["To know where to continue from after popping", "To sort lists", "Python requires it", "To avoid duplicates"], 0),
            run("Read k on line 1, then k lines each with a sorted list of numbers. Print the merged sorted list as numbers separated by spaces, using a heap (do not call sorted/sort).", "python",
                [t("three", stdin="3\n1 4 5\n1 3 4\n2 6"), t("one", stdin="1\n5 6 7"), t("empty one", stdin="2\n1 2\n3")],
                ["1 1 2 3 4 4 5 6", "5 6 7", "1 2 3"],
                "import heapq\nk = int(input())\nlists = [[int(x) for x in input().split()] for _ in range(k)]\nheap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]\nheapq.heapify(heap)\nout = []\nwhile heap:\n    val, i, j = heapq.heappop(heap)\n    out.append(val)\n    if j + 1 < len(lists[i]):\n        heapq.heappush(heap, (lists[i][j + 1], i, j + 1))\nprint(' '.join(map(str, out)))",
                require=[r"heapq"], forbid=[r"\bsorted\s*\(", r"\.sort\s*\("]),
        ),
        lesson(
            "Merging intervals",
            """Overlapping intervals merge into one. Sort by start, then walk through: if the next start is at or before the current end, extend the end; otherwise begin a new interval.

intervals.sort()
merged = [intervals[0]]
for s, e in intervals[1:]:
    if s <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], e)
    else: merged.append([s, e])

O(n log n) because of the sort. Used by calendars, genome tools and schedulers.""",
            mcq("What do you sort the intervals by?", ["Start time", "End time", "Length", "Nothing"], 0),
            mcq("When do two intervals merge?", ["The next start is <= the current end", "They are equal", "They have the same length", "Never"], 0),
            mcq("What is the complexity?", ["O(n log n)", "O(n)", "O(n²)", "O(1)"], 0),
            run("Read n then n lines 'start end'. Print the merged intervals, each as 'start-end', separated by spaces, in order.", "python",
                [t("classic", stdin="4\n1 3\n2 6\n8 10\n15 18"), t("touching", stdin="2\n1 4\n4 5"), t("nested", stdin="3\n1 10\n2 3\n4 5")],
                ["1-6 8-10 15-18", "1-5", "1-10"],
                "n = int(input())\nintervals = sorted([int(x) for x in input().split()] for _ in range(n))\nmerged = [intervals[0]]\nfor s, e in intervals[1:]:\n    if s <= merged[-1][1]:\n        merged[-1][1] = max(merged[-1][1], e)\n    else:\n        merged.append([s, e])\nprint(' '.join(f'{s}-{e}' for s, e in merged))"),
        ),
    ),
)
