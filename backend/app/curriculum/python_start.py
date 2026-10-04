"""Python - gentle 'Start here' units for people who have never seen code. Everyday analogies, one new idea per lesson,
every word explained the first time it appears."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

START = [
    start_unit(
        1,
        "Start here · What is code?",
        lesson(
            "What is a program?",
            """You use programs every day - the calculator, your camera, a game. A PROGRAM is simply a list of instructions that a computer follows, one after another.

Think of a very obedient robot that does EXACTLY what you say, in order, and nothing else:

1. Say "Hello".
2. Say "Nice to meet you".

The robot says Hello first, then Nice to meet you. It never skips ahead, and it never guesses what you meant.

CODE is the way we write those instructions so the computer can understand them. There are many "languages" for writing code (like English and Spanish are languages for people). In this course we use one called PYTHON - it is popular because it reads almost like plain English.

You will not need to memorise anything. Each lesson explains one small idea, then lets you try it.

In this lesson you will learn: what a program is, and that a computer follows instructions in order.""",
            mcq("What is a program?", ["A list of instructions for a computer", "A kind of screen", "A type of cable", "A computer game only"], 0,
                "A program is a list of instructions that a computer follows."),
            mcq("In what order does a computer follow instructions?", ["One after another, from the top", "Randomly", "From the bottom up", "All at the same moment"], 0,
                "The computer starts at the top and works down, one instruction at a time."),
            mcq("What is Python?", ["A language for writing instructions for computers", "A kind of snake only", "A web browser", "A phone brand"], 0,
                "Python is a programming language - a way of writing code."),
            order("A robot follows these instructions. Put them in the order it will do them.", ["Say 'Hello'", "Say 'Nice to meet you'", "Say 'Goodbye'"],
                  "The robot does them top to bottom."),
        ),
        lesson(
            "Your first command: print",
            """The most useful first command in Python is print. It tells the computer: "Show this on the screen."

print("Hello!")

When the computer runs that line, you see:

Hello!

Let's look at the parts:
- print is the command (the word that tells the computer what to do).
- The round brackets ( ) hold what you want to show.
- The quotation marks " " tell the computer "this part is text".

Important: you only see the text inside the quotes - the quotes themselves are not shown.

You can show many things by writing many lines. The computer runs them from top to bottom:

print("Hello!")
print("I am learning Python.")

Don't worry about mistakes - the computer will just tell you something is wrong and you can try again.

In this lesson you will learn: how to make the computer show a message.""",
            mcq("What does print do?", ["Shows something on the screen", "Prints on paper", "Deletes text", "Saves a file"], 0,
                "In Python, print means 'show this on the screen'."),
            mcq("What will this show on the screen?", ["Good morning", "\"Good morning\"", "print", "Nothing"], 0,
                "The quotes only mark where the text starts and ends. They are not shown.", code='print("Good morning")'),
            mcq("How many lines will this show?", ["2", "1", "3", "0"], 0, "Each print command shows one line.", code='print("One")\nprint("Two")'),
            fill("Fill in the missing command so the computer shows Hi!", '___("Hi!")', "print", "The command that shows things is print."),
            run("Write one line that shows exactly: Hello, World!", "python", [t("Run")], ["Hello, World!"], 'print("Hello, World!")', starter="",
                hint='Type print( then your text in quotes, then ).  Like: print("Hello, World!")', explanation="print(\"...\") shows the text between the quotes."),
        ),
        lesson(
            "Words and numbers",
            """Computers treat words and numbers differently.

TEXT (words, sentences) must always be wrapped in quotes:
print("Hello")        shows Hello
print("Room 5")       shows Room 5

NUMBERS are written without quotes:
print(5)              shows 5
print(2.5)            shows 2.5   (a number with a decimal point)

What is the difference? The computer can do maths with numbers, but text is just letters.

print(2 + 3)          shows 5     (maths!)
print("2 + 3")        shows 2 + 3 (it is just text, so nothing is calculated)

Programmers have names for these two kinds of things:
- text is called a STRING (like a string of letters)
- whole numbers are called INTEGERS, and numbers with decimals are FLOATS

You don't need to remember the names yet - just the idea: quotes mean text, no quotes mean a number.

In this lesson you will learn: the difference between text and numbers.""",
            mcq("Which one is text?", ["\"Hello\"", "42", "3.14", "7"], 0, "Anything inside quotes is text."),
            mcq("What does this show?", ["5", "2 + 3", "23", "An error"], 0, "No quotes, so Python does the maths: 2 + 3 = 5.", code="print(2 + 3)"),
            mcq("What does this show?", ["2 + 3", "5", "23", "An error"], 0, "The quotes make it text, so nothing is calculated.", code='print("2 + 3")'),
            fill("Make Python add the numbers (no quotes needed).", "print(4 ___ 6)", "+", "The + sign adds."),
            run("Show the result of 10 + 5 (it should show 15).", "python", [t("Run")], ["15"], "print(10 + 5)", hint="No quotes: print(10 + 5)"),
        ),
        lesson(
            "Boxes with names (variables)",
            """Often you want the computer to REMEMBER something. For that we use a VARIABLE: a box with a name on it that holds a value.

age = 12

Read it as: "put 12 into a box called age". The = sign here does not mean "equals" like in maths - it means "store this value".

Now whenever you write age, the computer uses what is inside the box:

print(age)       shows 12

You can change what is in the box at any time:

age = 12
age = 13         the box now holds 13
print(age)       shows 13

Boxes can hold text too:

name = "Maya"
print(name)      shows Maya

Notice: no quotes around name in print(name) - we want the CONTENTS of the box, not the word "name".

Choosing good names helps: score, price, name - not x or thing.

In this lesson you will learn: how to store a value with a name and use it later.""",
            mcq("What does age = 12 do?", ["Stores 12 in a box called age", "Shows 12", "Deletes age", "Compares two things"], 0, "= means 'store this value'."),
            mcq("What does this show?", ["13", "12", "age", "Nothing"], 0, "The box first holds 12, then it is replaced by 13.", code="age = 12\nage = 13\nprint(age)"),
            mcq("What does this show?", ["Maya", "name", "\"Maya\"", "An error"], 0, "print(name) shows what is inside the box called name.", code='name = "Maya"\nprint(name)'),
            fill("Store the number 50 in a variable called score.", "score ___ 50", "=", "Use a single = to store a value."),
            run("Store your favourite number in a variable called number (use 7) and show it.", "python", [t("Run")], ["7"], "number = 7\nprint(number)", require=[r"number\s*=", r"print"],
                hint="First line: number = 7. Second line: print(number)"),
        ),
    ),
    start_unit(
        2,
        "Start here · Making the computer think",
        lesson(
            "Doing maths",
            """Python is a super calculator. These are the signs (called OPERATORS):

+   add            print(8 + 2)    shows 10
-   subtract       print(8 - 2)    shows 6
*   multiply       print(8 * 2)    shows 16   (use * instead of ×)
/   divide         print(8 / 2)    shows 4.0

Just like in school, multiplication and division happen BEFORE addition and subtraction. Use round brackets to choose what goes first:

print(2 + 3 * 4)       shows 14     (3 * 4 first)
print((2 + 3) * 4)     shows 20     (the brackets first)

You can do maths with variables too:

price = 5
amount = 3
print(price * amount)  shows 15

In this lesson you will learn: how to make Python add, subtract, multiply and divide.""",
            mcq("Which sign multiplies?", ["*", "x", "×", "^"], 0, "On a computer, multiplication is written with a star: *."),
            mcq("What does this show?", ["14", "20", "10", "24"], 0, "Multiplication first: 3 * 4 = 12, then 2 + 12 = 14.", code="print(2 + 3 * 4)"),
            mcq("What does this show?", ["20", "14", "9", "60"], 0, "Brackets first: (2 + 3) = 5, then 5 * 4 = 20.", code="print((2 + 3) * 4)"),
            mcq("What does this show?", ["15", "8", "53", "An error"], 0, "price * amount is 5 * 3.", code="price = 5\namount = 3\nprint(price * amount)"),
            run("A pack has 6 pencils. You buy 4 packs. Show how many pencils you have (24).", "python", [t("Run")], ["24"], "print(6 * 4)", hint="Use the * sign: 6 * 4"),
        ),
        lesson(
            "Yes or no questions (True and False)",
            """Computers are great at answering yes-or-no questions. In Python, the answer is either True or False.

print(5 > 3)       shows True    (is 5 bigger than 3? yes)
print(5 < 3)       shows False   (is 5 smaller than 3? no)
print(5 == 5)      shows True    (are they the same? yes)
print(5 != 5)      shows False   (are they different? no)

The signs that ask questions:

>    is bigger than
<    is smaller than
>=   is bigger than or equal to
<=   is smaller than or equal to
==   is the same as   (TWO equal signs!)
!=   is not the same as

Why two equal signs? Because one = already means "store a value". To ASK whether two things are equal, we use ==.

In this lesson you will learn: how to ask the computer a yes-or-no question.""",
            mcq("What does this show?", ["True", "False", "7", "An error"], 0, "7 is bigger than 3, so the answer is True.", code="print(7 > 3)"),
            mcq("What does this show?", ["False", "True", "10", "An error"], 0, "10 is not smaller than 4, so False.", code="print(10 < 4)"),
            mcq("Which sign asks 'are these two the same?'", ["==", "=", "!=", "=>"], 0, "Two equal signs ask the question. One equal sign stores a value."),
            mcq("What does this show?", ["True", "False", "5", "Nothing"], 0, "5 and 5 are the same.", code="print(5 == 5)"),
            fill("Ask whether 3 is smaller than 9.", "print(3 ___ 9)", "<", "< means 'is smaller than'."),
        ),
        lesson(
            "If this, then that",
            """Now we can let the computer MAKE A DECISION. We use the word if:

weather = "rain"
if weather == "rain":
    print("Take an umbrella")

Read it as: "IF the weather is the same as rain, THEN show: Take an umbrella."

Look closely at the shape:
- the if line ends with a colon  :
- the line below is pushed in a little (4 spaces) - this is called INDENTATION. It tells Python "this line belongs to the if".

If the answer is False, Python skips the pushed-in lines.

We can also say what to do OTHERWISE, with else:

if weather == "rain":
    print("Take an umbrella")
else:
    print("Wear sunglasses")

Only one of the two happens.

In this lesson you will learn: how a program chooses between two paths.""",
            mcq("What does this show?", ["Take an umbrella", "Wear sunglasses", "Both", "Nothing"], 0, "weather IS rain, so the first path runs.",
                code='weather = "rain"\nif weather == "rain":\n    print("Take an umbrella")\nelse:\n    print("Wear sunglasses")'),
            mcq("What does this show?", ["Wear sunglasses", "Take an umbrella", "Both", "Nothing"], 0, "weather is not rain, so the else path runs.",
                code='weather = "sun"\nif weather == "rain":\n    print("Take an umbrella")\nelse:\n    print("Wear sunglasses")'),
            mcq("What does the pushed-in (indented) line mean?", ["It belongs to the if above it", "It is a mistake", "It is a comment", "It runs first"], 0,
                "Indentation shows which lines belong to the if."),
            fill("Complete the missing word for 'otherwise'.", 'age = 10\nif age >= 18:\n    print("Adult")\n___:\n    print("Child")', "else", "else is the 'otherwise' path."),
            run("The temperature is 30. Show Hot if it is above 25, otherwise show Cool.", "python", [t("Run")], ["Hot"],
                'temperature = 30\nif temperature > 25:\n    print("Hot")\nelse:\n    print("Cool")', starter="temperature = 30\n", require=[r"if", r"else"],
                hint='if temperature > 25: (then a pushed-in print("Hot")), then else: with print("Cool").'),
        ),
        lesson(
            "Doing it again and again (loops)",
            """Suppose you want to show "Hello" five times. Writing five lines is boring - and impossible if it is a million times!

A LOOP repeats instructions for you:

for i in range(5):
    print("Hello")

Read it as: "repeat 5 times: show Hello".

Once again, notice the colon : at the end of the first line and the pushed-in line below it - the pushed-in lines are the ones that get repeated.

The loop also keeps a counter (here called i). It starts at 0:

for i in range(3):
    print(i)

shows:
0
1
2

(Programmers start counting at 0 - a funny habit that you will get used to!)

Loops let you do big jobs with small code: adding up numbers, checking every item in a list, drawing a pattern.

In this lesson you will learn: how to repeat instructions without writing them again and again.""",
            mcq("What does a loop do?", ["Repeats instructions", "Stops the program", "Makes a choice", "Stores a value"], 0, "A loop repeats the pushed-in lines."),
            mcq("How many times does this show Hi?", ["3", "2", "4", "1"], 0, "range(3) means three times.", code='for i in range(3):\n    print("Hi")'),
            mcq("What does this show (one number per line)?", ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3", "3, 2, 1"], 0, "The counter starts at 0 and goes up for each repeat.",
                code="for i in range(3):\n    print(i)"),
            fill("Repeat 4 times.", 'for i in ___(4):\n    print("Go")', "range", "range(4) means four times."),
            run("Show the word Python 3 times, each on its own line, using a loop.", "python", [t("Run")], ["Python\nPython\nPython"],
                'for i in range(3):\n    print("Python")', require=[r"for", r"range"], hint='for i in range(3): then a pushed-in print("Python")'),
        ),
        lesson(
            "Lists: many things in one place",
            """What if you want to keep ALL your friends' names? One box per name would be messy. A LIST holds many values in one box, in order:

friends = ["Ana", "Ben", "Cy"]

Each item has a position number called an INDEX. The first is 0 (remember - counting starts at 0!):

print(friends[0])    shows Ana
print(friends[1])    shows Ben
print(friends[2])    shows Cy

Handy things you can do:

len(friends)             how many items? (3)
friends.append("Dee")    add Dee to the end

And a loop can visit every item - very powerful together:

for name in friends:
    print("Hi " + name)

shows:
Hi Ana
Hi Ben
Hi Cy

(The + here joins two pieces of text together.)

In this lesson you will learn: how to hold many things in one list and go through them.""",
            mcq("What is friends[0] in this list?", ["Ana", "Ben", "Cy", "0"], 0, "Index 0 is the first item.", code='friends = ["Ana", "Ben", "Cy"]'),
            mcq("What does len(friends) give for a list of 3 names?", ["3", "2", "0", "Ana"], 0, "len tells you how many items are in the list."),
            mcq("What does this show?", ["Hi Ana, then Hi Ben", "Hi Hi", "Ana Ben", "Nothing"], 0, "The loop visits each name in turn.",
                code='friends = ["Ana", "Ben"]\nfor name in friends:\n    print("Hi " + name)'),
            fill("Add \"Dee\" to the end of the list.", 'friends = ["Ana", "Ben"]\nfriends.___("Dee")', "append", "append adds an item to the end."),
            run("Make a list called fruits with apple and pear, then show each fruit on its own line using a loop.", "python", [t("Run")], ["apple\npear"],
                'fruits = ["apple", "pear"]\nfor fruit in fruits:\n    print(fruit)', require=[r"fruits", r"for"], hint="Loop with: for fruit in fruits:"),
        ),
    ),
]
