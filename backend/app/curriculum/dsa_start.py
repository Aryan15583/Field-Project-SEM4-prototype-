"""Algorithms - gentle 'Start here' units for people who have never programmed. Everyday analogies first, tiny
Python only at the end of each idea. Every word is explained the first time it appears."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

START = [
    start_unit(
        1,
        "Start here · What is an algorithm?",
        lesson(
            "A recipe for solving problems",
            """Welcome! You don't need to know anything about coding to start here.

An ALGORITHM is just a fancy word for a set of steps that solves a problem - like a recipe.

Making a cup of tea is an algorithm:
1. Boil some water.
2. Put a tea bag in a cup.
3. Pour the water in.
4. Wait three minutes.
5. Take the tea bag out.

Computers can't think for themselves. They only follow steps - so before we teach a computer anything, we first learn to write down good steps. That is all "algorithms" means.

In this lesson you will learn: what an algorithm is, and why the ORDER of the steps matters.""",
            mcq("In everyday words, what is an algorithm?", ["A list of steps that solves a problem", "A kind of computer", "A secret code", "A type of game"], 0,
                "An algorithm is a recipe: a clear list of steps to get something done."),
            mcq("Which of these is an algorithm?", ["The steps for tying your shoelaces", "A photo of your shoes", "The colour of your shoes", "The price of your shoes"], 0,
                "Only the steps for doing something are an algorithm."),
            order("Put the tea-making steps in the right order.", ["Boil the water", "Put a tea bag in a cup", "Pour the water into the cup", "Wait three minutes", "Take the tea bag out"],
                  "If you poured the water before boiling it, you would get cold tea - order matters!"),
            mcq("Why does the order of the steps matter?", ["Doing them in the wrong order gives a wrong result", "It doesn't matter at all", "Only computers care about order", "Order only matters for tea"], 0,
                "Steps are done one after another, so swapping them can break the whole recipe."),
        ),
        lesson(
            "Be exact: computers are very literal",
            """A friend can understand "make me a sandwich". A computer can't - it needs EXACT steps and takes everything literally.

Imagine telling a robot: "Put the butter on the bread." The robot has no idea what butter is, where the bread is, or which way up the knife goes!

So a good algorithm is:
- Clear - every step means only one thing.
- In order - step 2 comes after step 1.
- Finished - it must end at some point and give an answer.

Let's practise by writing steps for finding the tallest person in a small group:
1. Pick the first person as "tallest so far".
2. Look at the next person. If they are taller, they become "tallest so far".
3. Keep going until nobody is left.
4. The "tallest so far" is the answer.

In this lesson you will learn: what makes steps "exact enough" for a computer.""",
            mcq("Which instruction is clear enough for a computer?", ["Add 2 and 3, then show the result", "Do the maths thing", "Just make it work", "Figure it out"], 0,
                "A computer needs a precise instruction. 'Add 2 and 3' means exactly one thing."),
            mcq("In the 'tallest person' recipe, who is 'tallest so far' at the very beginning?", ["The first person", "The last person", "Nobody", "The shortest person"], 0,
                "We start by trusting the first person, then compare everyone else against them."),
            mcq("A group has people of heights 150, 180, 165 (cm). Following the recipe, who ends up as 'tallest so far'?", ["The 180 person", "The 150 person", "The 165 person", "All of them"], 0,
                "150 first. 180 is taller, so 180 takes over. 165 is not taller than 180, so 180 stays."),
            mcq("What must every algorithm eventually do?", ["Finish and give an answer", "Run forever", "Skip steps", "Ask for help"], 0,
                "An algorithm that never ends isn't solving anything."),
        ),
        lesson(
            "Making choices: if this, then that",
            """Real life is full of choices:

IF it is raining, THEN take an umbrella. OTHERWISE, leave it at home.

Algorithms make choices the same way. A choice is a question with a yes-or-no answer, followed by what to do in each case.

Example - deciding what to wear:
- If it is cold: wear a coat.
- Otherwise: wear a T-shirt.

Only ONE of the two paths happens each time.

A computer does this with a little code. In Python (the language we use here) it looks almost like English:

temperature = 5
if temperature < 10:
    print("Wear a coat")
else:
    print("Wear a T-shirt")

Read it out loud: "If the temperature is less than 10, show 'Wear a coat'; otherwise show 'Wear a T-shirt'." The word print just means "show this on the screen". The < sign means "is less than".

In this lesson you will learn: how a program chooses between two paths.""",
            mcq("In 'IF it is raining THEN take an umbrella', what is the question being asked?", ["Is it raining?", "Do I have an umbrella?", "What day is it?", "Where am I?"], 0,
                "The part after IF is always a yes-or-no question."),
            mcq("What does this code show?", ["Wear a coat", "Wear a T-shirt", "Both messages", "Nothing"], 0,
                "The temperature is 5, which IS less than 10, so the first path runs.", code='temperature = 5\nif temperature < 10:\n    print("Wear a coat")\nelse:\n    print("Wear a T-shirt")'),
            mcq("What does this code show?", ["Wear a T-shirt", "Wear a coat", "Both messages", "Nothing"], 0,
                "25 is NOT less than 10, so the 'else' (otherwise) path runs.", code='temperature = 25\nif temperature < 10:\n    print("Wear a coat")\nelse:\n    print("Wear a T-shirt")'),
            fill("The sign < means 'is less than'. Complete the word that means 'otherwise'.", 'if age < 18:\n    print("Child")\n___:\n    print("Adult")', "else",
                 "else is the path taken when the if-question is NO."),
            run("The number of points is 7. Write code that shows Pass if points is 5 or more, otherwise shows Fail. (Use >= for 'is 5 or more'.)", "python", [t("Run")], ["Pass"],
                'points = 7\nif points >= 5:\n    print("Pass")\nelse:\n    print("Fail")',
                starter='points = 7\n', require=[r"if", r"else"], hint='Use if points >= 5: then print("Pass"), then else: and print("Fail").'),
        ),
        lesson(
            "Repeating things (loops)",
            """Imagine you have to say "Hello" to 5 people. You don't write 5 different recipes - you write ONE step and say "do it 5 times".

That is a LOOP: doing the same thing again and again.

In Python:

for number in range(3):
    print("Hello")

This shows "Hello" three times. Read it as: "repeat 3 times: show Hello".

Why are loops so useful? Because a computer never gets bored. Counting to a million, checking every name in a list, adding up all your shopping prices - loops do these in a blink.

We can also use the counter that the loop keeps:

for number in range(3):
    print(number)

This shows 0, then 1, then 2. (Computers usually start counting at 0, not 1 - that is normal and you will get used to it!)

In this lesson you will learn: how to repeat a step many times without writing it many times.""",
            mcq("What is a loop for?", ["Repeating steps many times", "Making a choice", "Stopping a program", "Saving a file"], 0,
                "A loop repeats the same steps again and again."),
            mcq("How many times does this show Hi?", ["4", "3", "5", "1"], 0, "range(4) means 'four times'.", code='for i in range(4):\n    print("Hi")'),
            mcq("What does this code show (one number per line)?", ["0, 1, 2", "1, 2, 3", "3, 2, 1", "0, 1, 2, 3"], 0,
                "range(3) counts three times, starting at 0: 0, 1, 2.", code="for i in range(3):\n    print(i)"),
            fill("Make the loop repeat 5 times.", 'for i in ___(5):\n    print("Go!")', "range", "range(5) means five times."),
            run("Show the word Hello three times, each on its own line, using a loop.", "python", [t("Run")], ["Hello\nHello\nHello"],
                'for i in range(3):\n    print("Hello")', require=[r"for", r"range"], hint='for i in range(3): then, on the next line indented, print("Hello").'),
        ),
    ),
    start_unit(
        2,
        "Start here · Lists, searching and speed",
        lesson(
            "Lists: a row of boxes",
            """Most problems involve MANY things - a list of names, scores, prices. Computers store these in a LIST.

Think of a row of numbered boxes, each holding one thing:

  box 0     box 1     box 2     box 3
 [ "Ana" ] [ "Ben" ] [ "Cy"  ] [ "Dee" ]

In Python:

names = ["Ana", "Ben", "Cy", "Dee"]
print(names[0])       # Ana   (the first box is number 0)
print(names[2])       # Cy
print(len(names))     # 4     (len means: how many things?)

The number in the square brackets is called the INDEX - it says which box you want. And remember: counting starts at 0!

You can also add something to the end:

names.append("Eli")   # now there are 5 names

In this lesson you will learn: how to hold lots of things in one list and pick any one of them.""",
            mcq("In ['red', 'green', 'blue'], what is at index 0?", ["red", "green", "blue", "Nothing"], 0, "The first box is always index 0."),
            mcq("What does this show?", ["Cy", "Ben", "Dee", "Ana"], 0, "Index 0 is Ana, 1 is Ben, 2 is Cy.", code='names = ["Ana", "Ben", "Cy", "Dee"]\nprint(names[2])'),
            mcq("What does len(names) tell you?", ["How many things are in the list", "The first thing", "The last thing", "The biggest thing"], 0,
                "len is short for 'length' - how many items there are."),
            fill("Show the first item of the list.", 'fruits = ["apple", "pear", "plum"]\nprint(fruits[___])', "0", "The first item has index 0."),
            run("Make a list called colors holding red, green and blue, then show the second one (green).", "python", [t("Run")], ["green"],
                'colors = ["red", "green", "blue"]\nprint(colors[1])', require=[r"\[", r"colors"], hint='Index 1 is the second box.'),
        ),
        lesson(
            "Searching: finding something in a list",
            """How do you find a name in an unsorted list? You look at the first, then the second, then the third... until you find it. This is called a LINEAR SEARCH ("linear" means "one after another, in a line").

Looking for "Cy" in ["Ana", "Ben", "Cy", "Dee"]:
- Is box 0 "Cy"? No.
- Is box 1 "Cy"? No.
- Is box 2 "Cy"? Yes! Found it at index 2.

If you reach the end without finding it, then it is not in the list.

In Python, a loop does exactly that:

names = ["Ana", "Ben", "Cy", "Dee"]
for name in names:
    if name == "Cy":
        print("Found!")

(Notice == with TWO equal signs means "is equal to". One = is something else - it stores a value.)

In this lesson you will learn: the simplest way to find an item - by checking one at a time.""",
            mcq("Linear search looks at the items…", ["One after another", "At random", "Only the last one", "Only the middle one"], 0,
                "It starts at the beginning and checks each item in turn."),
            mcq("Searching for 8 in [3, 5, 8, 1]. How many items do we check before finding it?", ["3", "2", "4", "1"], 0,
                "We check 3, then 5, then 8 - found on the third check."),
            mcq("What does the sign == mean?", ["Is equal to", "Store a value", "Is bigger than", "Add"], 0,
                "Two equal signs ask 'are these the same?'. One equal sign stores a value."),
            mcq("The item is NOT in the list. What does linear search do at the end?", ["Checks everything, then finds nothing", "Finds it anyway", "Stops after one check", "Crashes"], 0,
                "It has to look at every single item before it can say 'not here'."),
            run("Show Found! if the number 7 is in the list [3, 7, 9], otherwise show Not found. (Use a loop and ==.)", "python", [t("Run")], ["Found!"],
                'numbers = [3, 7, 9]\nfound = False\nfor n in numbers:\n    if n == 7:\n        found = True\nif found:\n    print("Found!")\nelse:\n    print("Not found")',
                starter='numbers = [3, 7, 9]\n', require=[r"for", r"=="], hint='Loop over numbers; when n == 7, remember it. After the loop, print the right message.'),
        ),
        lesson(
            "Putting things in order (sorting)",
            """Sorting means arranging things in order - smallest to biggest, or A to Z.

How would you sort a hand of playing cards? Most people do this:
1. Pick up the cards one by one.
2. For each new card, slide it into the right place among the cards you already hold.

That is a real algorithm (it's called insertion sort)! Here is the same idea with numbers - sorting [4, 2, 5, 1]:

hold: [4]
take 2 -> goes before 4 -> [2, 4]
take 5 -> goes at the end -> [2, 4, 5]
take 1 -> goes at the start -> [1, 2, 4, 5]

Python can sort for you in one word:

numbers = [4, 2, 5, 1]
numbers.sort()
print(numbers)     # [1, 2, 4, 5]

Why learn the manual way? Because the same ideas help you solve harder problems later.

In this lesson you will learn: what sorting is, and one natural way to do it.""",
            mcq("What does sorting do?", ["Puts items in order", "Deletes items", "Counts items", "Finds the biggest only"], 0, "Sorting arranges items smallest to biggest (or A to Z)."),
            mcq("Sort [3, 1, 2] smallest to biggest. What do you get?", ["[1, 2, 3]", "[3, 2, 1]", "[2, 1, 3]", "[1, 3, 2]"], 0, "1 is smallest, then 2, then 3."),
            order("Put these steps of 'sorting a hand of cards' in order.", ["Pick up the first card", "Pick up the next card", "Slide it into the right place in your hand", "Repeat until no cards are left"],
                  "You build the sorted hand one card at a time."),
            fill("Ask Python to sort the list.", "scores = [9, 4, 7]\nscores.___()\nprint(scores)", "sort", ".sort() sorts the list in place: [4, 7, 9]."),
        ),
        lesson(
            "How much work is it? (speed in plain words)",
            """Imagine looking for a name in a phone book with 10 names, then one with 1,000,000 names. Searching one-by-one takes MUCH longer for the big one.

When we compare algorithms we ask: "If there is 10 times more data, how much longer does it take?"

- If the work grows by the same amount (10 times more names -> about 10 times more work): that is called LINEAR growth.
- If the work stays nearly the same no matter how much data: that is the best case.
- If the work grows much faster than the data (10 times more data -> 100 times more work): that is slow and gets worse quickly.

Computers are fast, but "slow growth" algorithms can still take hours when the data is huge. So we try to pick algorithms that grow gently.

You don't need any maths for this - just the idea: "As the data gets bigger, how fast does the work grow?"

In this lesson you will learn: why we care about how an algorithm behaves with BIG data.""",
            mcq("Searching a list one-by-one: you double the number of items. The work becomes about…", ["Double", "The same", "Half", "Ten times more"], 0,
                "More items to check = proportionally more work. That's linear growth."),
            mcq("Which growth is best for big data?", ["Barely grows", "Grows a little", "Grows a lot", "Grows enormously"], 0, "We want the work to grow as slowly as possible."),
            mcq("Why do we compare how work GROWS rather than timing it in seconds?", ["Seconds depend on the computer; growth does not", "Seconds are illegal", "Computers can't count time", "Growth is always faster"], 0,
                "A fast and a slow computer give different seconds, but the same growth pattern."),
        ),
        lesson(
            "The guessing game: finding things fast",
            """Play this game: "I'm thinking of a number from 1 to 100. Guess it - I'll say higher or lower."

A clever player guesses 50 first. "Higher" - so the answer is 51-100. Then 75. "Lower" - so now 51-74. Every guess cuts the possibilities in HALF. In about 7 guesses you always win!

This is called BINARY SEARCH. ("Binary" means "two" - each step splits into two halves and throws one away.)

The one rule: it only works if the list is already SORTED. If a list is sorted, you can jump to the middle and instantly know which half to ignore.

Compare for a sorted list of 1,000,000 numbers:
- one-by-one search: up to 1,000,000 checks
- binary search: about 20 checks!

That is the power of a good algorithm - the same problem, solved enormously faster, just by being clever.

In this lesson you will learn: how halving the problem makes searching super fast.""",
            mcq("In the guessing game (1-100), what is the smartest first guess?", ["50", "1", "100", "A random number"], 0, "50 splits the range into two equal halves."),
            mcq("Each binary-search step does what to the possible answers?", ["Cuts them in half", "Doubles them", "Adds one", "Changes nothing"], 0, "After each guess, half of the numbers are ruled out."),
            mcq("What must be true about the list for binary search to work?", ["It is sorted", "It has no numbers", "It is very short", "It is empty"], 0, "Only a sorted list tells you which half to ignore."),
            mcq("Roughly how many guesses can find a number from 1 to 1,000,000 with binary search?", ["About 20", "About 1,000", "About 500,000", "1,000,000"], 0,
                "Halving a million over and over reaches 1 in about 20 steps."),
            order("Put the steps of one round of the guessing game in order.", ["Guess the middle number", "Hear 'higher' or 'lower'", "Throw away the half that can't contain the answer", "Guess the middle of what is left"],
                  "Guess, learn, shrink the range, repeat."),
        ),
    ),
]
