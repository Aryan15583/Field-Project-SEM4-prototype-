"""Algorithms - plain-language rewrites of the Beginner lesson texts. Keyed "<unit>/<lesson>" (Start-here units not
counted); only the explanation changes - the questions stay the same."""

INTROS = {
    "1/1": """You met algorithms in "Start here" - a set of steps that solves a problem. Now let's look at one real algorithm closely.

PROBLEM: find the biggest number in a list, for example [4, 9, 2].

THE STEPS (like a recipe):
1. Take the first number and call it the "best so far".
2. Look at each of the other numbers one by one. If a number is bigger than the best so far, it becomes the new best so far.
3. When there are no numbers left, the best so far is the answer.

Try it on [4, 9, 2]: best = 4. See 9 - bigger, so best = 9. See 2 - not bigger. Answer: 9.

In Python it looks like this (read it line by line - it is just the three steps):

def biggest(nums):
    best = nums[0]
    for n in nums[1:]:
        if n > best:
            best = n
    return best

Two things make an algorithm GOOD:
- Correct: it gives the right answer for EVERY input - even an empty list or a list with just one number. Always ask "what could break this?"
- Efficient: it doesn't do pointless extra work.

In this lesson you will learn: how to turn a plain-English recipe into code, and to check it with tricky inputs.""",
    "1/2": """When we compare two recipes, we ask: "which one takes fewer steps?" We count STEPS rather than seconds, because a fast and a slow computer give different seconds but the same number of steps.

The number of steps usually depends on how much data there is. Call the amount of data n (for example n = the number of items in a list).

ONE LOOP - you look at every item once, so you do about n steps:

for x in items:
    total += x

TWO LOOPS INSIDE EACH OTHER - for each item you look at every item again. That is n x n steps. With 10 items that is 100 steps; with 1,000 items it is 1,000,000!

for a in items:
    for b in items:
        ...

TWO LOOPS ONE AFTER ANOTHER just add up: n + n = 2n steps, which is still about n.

HALVING - if each step throws away half of the work (like the guessing game), you finish very fast. 1,000 items need only about 10 steps, because you can halve 1,000 about 10 times before reaching 1.

In this lesson you will learn: how to count steps, and why loops inside loops grow so fast.""",
    "1/3": """Counting every single step is tiring. Programmers use a short-hand called BIG-O. It answers: "As the data gets bigger, how fast does the work grow?"

Big-O only cares about the BIG picture, so it ignores small details like "+ 5" or "x 3".

Here are the common ones, from fastest to slowest. (Don't memorise - just notice the pattern.)

  O(1)       "constant"   - the work doesn't grow at all. Example: grabbing item number 5 from a list.
  O(log n)   "logarithmic" - grows very slowly. Example: guessing a number by halving (binary search).
  O(n)       "linear"     - grows in step with the data. Example: one loop over everything.
  O(n log n)              - a bit more than linear. Example: good sorting.
  O(n²)      "quadratic"  - grows very fast. Example: a loop inside a loop.

You say it out loud as "big-O of n" or "order n".

Dropping the small stuff: 3n + 5 steps is just O(n) - when n is huge, the "3" and the "5" don't change the big picture. And n² + n is O(n²) - the n² part dominates.

The rule of thumb: the further up the list, the faster for big data.

In this lesson you will learn: how to describe an algorithm's speed with a single short label.""",
    "2/1": """An ARRAY is just a row of boxes holding values, one after another. In Python the everyday array is called a LIST:

nums = [3, 1, 4]

Because the boxes sit side by side and are numbered (0, 1, 2...), the computer can jump straight to any box - nums[2] is instant. That is why "get item i" is O(1).

Now a clever trick. Suppose someone keeps asking: "what is the total of the numbers from position a up to b?" Adding them up each time is slow if there are many questions.

The PREFIX SUM trick: do some work ONCE, answer every question instantly. Make a second list where each box holds the running total so far:

nums   = [3, 1, 4]
prefix = [0, 3, 4, 8]      (0, then 0+3, then 3+1, then 4+4)

To get the total of any stretch, subtract two prefix values. Total of the numbers from position 1 up to (not including) position 3 is prefix[3] - prefix[1] = 8 - 3 = 5. Check: 1 + 4 = 5. Yes!

Building it:

prefix = [0]
for n in nums:
    prefix.append(prefix[-1] + n)

(prefix[-1] means "the last item in the list".)

In this lesson you will learn: how a little prepared work lets you answer "total of this stretch" instantly.""",
    "2/2": """The TWO POINTERS idea: instead of one finger moving through a list, use TWO fingers - often one at each end - moving toward each other. This can replace a slow loop-inside-a-loop.

EXAMPLE 1: is a word a palindrome (reads the same backwards, like "level")?
Put one finger on the first letter (i) and one on the last (j). Compare them. If they differ, it is not a palindrome. If they match, move both inward and repeat.

i, j = 0, len(s) - 1
while i < j:
    if s[i] != s[j]:
        return False
    i += 1
    j -= 1
return True

(len(s) - 1 is the position of the last letter, since counting starts at 0. i += 1 means "move the left finger one step right".)

EXAMPLE 2: in a list that is already SORTED from small to big, find two numbers that add up to a target.
- If the two numbers add up to too little, move the left finger right (to a bigger number).
- If they add up to too much, move the right finger left (to a smaller number).
- Stop when the total is exactly right.

Because every step moves a finger, you finish in about n steps instead of trying every pair.

In this lesson you will learn: how two moving fingers can solve problems quickly.""",
    "2/3": """Imagine a window frame sliding along a row of numbers. It always shows exactly k neighbours. A SLIDING WINDOW keeps the total of what is inside the window.

PROBLEM: in [2, 1, 5, 1, 3, 2], find the biggest total of 3 numbers next to each other.

SLOW WAY: add up every group of 3 from scratch. Lots of repeated adding.

SMART WAY: when the window slides one step right, ONE number leaves on the left and ONE number enters on the right. So just fix the total: add the new one, subtract the old one.

window = sum(nums[:k])          # total of the first k numbers
best = window
for i in range(k, len(nums)):
    window += nums[i] - nums[i - k]   # add the new number, drop the old one
    best = max(best, window)

(nums[:k] means "the first k numbers". max(a, b) gives the bigger of two.)

Each number is added once and removed once, so the work is about n steps - much faster than adding every group again.

In this lesson you will learn: how to slide a window over data while keeping a running total.""",
    "3/1": """Question: "Have I seen this name before?" With a list you must look at every item - slow for big lists.

A SET answers it instantly. A set is a bag of unique items: no duplicates, and the computer can check "is it in here?" almost immediately (it does this with a trick called hashing - think of a library where every book has a label telling you exactly which shelf it is on).

seen = set()
seen.add(3)         # put 3 in the bag
3 in seen           # True
7 in seen           # False

Adding something that is already there changes nothing - sets never hold duplicates.

Sets can also combine, like circles in a Venn diagram:

a | b    everything in either (union)
a & b    only what is in both (intersection)
a - b    in a but not in b (difference)

One rule: things in a set must be "unchangeable" - numbers, text and tuples are fine, lists are not.

In this lesson you will learn: how a set checks "have I seen this?" in an instant.""",
    "3/2": """A DICTIONARY (called a dict) is like a real dictionary or a phone book: you look something up by a KEY (the word, the name) and get back a VALUE (the meaning, the number).

ages = {"Ana": 12, "Ben": 14}
ages["Ana"]           # 12

Looking up is almost instant, however big it is.

A very common job is COUNTING: how many times does each word appear? Keep a dict from word to count. Each time you see a word, add one to its count:

counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

counts.get(word, 0) means "the count so far, or 0 if I have not seen this word yet". Then we add 1 and store it back.

Python has a ready-made helper that does this counting for you:

from collections import Counter
Counter("banana")       # counts: a 3, n 2, b 1

In this lesson you will learn: how to use a dictionary to count things.""",
    "3/3": """A famous puzzle: you have a list of numbers and a target number. Find two numbers in the list that add up to the target.

Example: numbers [2, 7, 11, 15], target 9. Answer: 2 and 7 (they are in position 0 and 1).

SLOW WAY: try every pair of numbers. With a big list that is a loop inside a loop - very slow.

SMART WAY: go through the numbers once. For each number, ask: "what number would I need to add to make the target?" (target minus this number). Have I already seen that number? A dict remembers the numbers we have seen so far and their positions.

seen = {}
for i, n in enumerate(nums):
    need = target - n
    if need in seen:
        return (seen[need], i)
    seen[n] = i

(enumerate gives you the position i and the number n together.)

Try it: 2 comes first - need 7, not seen yet, remember 2. Then 7 - need 2, it is in seen! Found.

One pass through the list, so it is fast.

In this lesson you will learn: how remembering what you have seen turns a slow search into a fast one.""",
    "4/1": """A STACK is like a pile of plates. You can only add a plate on TOP, and only take the plate from the TOP. The last plate you put on is the first one you take off. This is called LIFO: Last In, First Out.

In Python a plain list works as a stack:

stack = []
stack.append("a")    # put on top (called "push")
stack.append("b")
stack.pop()          # take off the top: gives "b" (the last one in)
stack[-1]            # just look at the top without taking it

Where do you see stacks in real life?
- Undo in an editor (the last thing you did is undone first).
- The Back button in a browser.
- Checking that brackets match, like (a [b] c).

In this lesson you will learn: how a stack works and why "last in, first out" is so useful.""",
    "4/2": """A QUEUE is a line at a shop: the person who joined FIRST is served FIRST. This is called FIFO: First In, First Out.

You could use a list, but removing from the FRONT of a list makes all the others shuffle along - slow for big lists. Python has a better tool called deque (say "deck"):

from collections import deque
q = deque()
q.append("Ada")     # Ada joins the back of the line
q.append("Bo")
q.popleft()         # the person at the FRONT leaves: gives "Ada"

popleft takes from the front instantly.

Queues are used for: waiting lines, printing jobs one after another, and exploring things level by level (you will see this later).

In this lesson you will learn: how a queue works, and why deque is the right tool.""",
    "4/3": """This is a neat stack trick. PROBLEM: for each number in a list, find the next number to its right that is BIGGER. If there is none, answer -1.

Example: [2, 1, 5] -> [5, 5, -1]. (After 2 comes 1, then 5 which is bigger. After 1, the next bigger is 5. After 5, nothing bigger.)

THE IDEA: walk along the list. Keep a stack of positions that are still WAITING for a bigger number. When a new number arrives and it is bigger than the waiting ones, it is the answer for each of them - take them off the stack one by one and write down the answer. Then put the new number's position on the stack to wait.

result = [-1] * len(nums)         # start with -1 everywhere
stack = []
for i, n in enumerate(nums):
    while stack and nums[stack[-1]] < n:
        result[stack.pop()] = n
    stack.append(i)

(while stack and ... means "keep going while the stack is not empty and the top is smaller than n".)

Each position goes onto the stack once and comes off once, so the whole thing is fast.

In this lesson you will learn: how a stack can solve "next bigger" problems in one pass.""",
}
