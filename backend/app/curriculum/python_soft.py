"""Python - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """Python reads your program from the top to the bottom, one line at a time - like following a recipe.

The command print() shows something on the screen:

print("Hello!")     shows: Hello!
print(42)           shows: 42

Why are there quotes around Hello! but not around 42? Because Hello! is TEXT (programmers call text a "string") and quotes tell Python "this is words, not a command". Numbers don't need quotes.

The quotes are not shown - only what is inside them.

Two small rules to remember:
- Python cares about capital letters: print works, Print does not.
- Every opening bracket ( needs a closing bracket ).

In this lesson you will learn: how to show text and numbers with print().""",
    "1/2": """Sometimes you want to leave a NOTE in your code for people (including future-you). That is a COMMENT. It starts with a # sign, and Python ignores everything after it on that line:

# this note is for humans
print("Hi")      # this note is ignored too

You can write text with single quotes or double quotes - they work the same: 'Hi' and "Hi".

You can also JOIN pieces of text together with +. Joining text is called concatenation (a long word for "chaining together"):

print("Code" + "ingo")     shows: Codeingo

Notice there is no space - Python joins exactly what you give it. If you want a space, add one as text:

print("Good" + " " + "morning")     shows: Good morning

In this lesson you will learn: how to write notes, and how to join text.""",
    "1/3": """You already used + for maths. Python knows all the usual calculator signs:

print(7 + 3)     # 10    add
print(7 - 3)     # 4     subtract
print(7 * 3)     # 21    multiply (a star)
print(7 / 2)     # 3.5   divide (the answer can have decimals)
print(7 // 2)    # 3     divide and keep only the WHOLE part
print(7 % 2)     # 1     the REMAINDER (what is left over)
print(2 ** 3)    # 8     power (2 x 2 x 2)

Remainder example: share 7 sweets between 2 friends. Each gets 3 (7 // 2) and 1 is left over (7 % 2).

Order of work: just like at school, multiplication and division happen first, then addition and subtraction. Use brackets to choose: (2 + 3) * 4.

The % sign is handy later - for example, a number is even when number % 2 is 0.

In this lesson you will learn: the maths signs, including whole-number division and remainders.""",
    "2/1": """In "Start here" you met variables: a labelled box that holds a value. Let's look at them properly.

score = 10

means "put 10 in the box called score". The = sign means STORE, not "equals".

You can use the box in a calculation and store the answer back in the same box:

score = score + 5

Read it right-to-left: "take what is in score (10), add 5 (15), and put the result back into score." Now score is 15.

print(score)      shows 15

Naming rules:
- Use letters, digits and the underscore _ (no spaces!).
- A name can't start with a digit: 1score is not allowed.
- Programmers write names in snake_case: high_score, first_name.
- Pick names that explain themselves: price is better than p.

In this lesson you will learn: how to store, change and reuse values.""",
    "2/2": """Every value has a TYPE - the kind of thing it is. It matters because the computer treats each kind differently.

  int     whole numbers          42
  float   numbers with decimals  3.14
  str     text (a "string")      "hi"
  bool    True or False          True

You can ask Python: type(42) tells you int.

A very common trap: "20" in quotes is TEXT, not a number. You cannot do maths with it until you convert it:

age = "20"             # text
print(int(age) + 1)    # 21   int() turns text into a whole number

And the other way - to join a number to text, turn the number into text with str():

print("Age: " + str(21))     shows: Age: 21

Conversion helpers: int() whole number, float() decimal number, str() text.

In this lesson you will learn: the kinds of values and how to convert between them.""",
    "2/3": """So far your programs only show things. Let's make them listen! The command input() waits for the user to type something and press Enter, then gives you what they typed.

name = input()
print("Hello, " + name)

If the user types Maya, the program shows Hello, Maya.

Important: input() ALWAYS gives you TEXT, even if the person types digits. So to do maths, convert it:

age = int(input())
print(age + 1)

If the user types 20, you get 21. Without int() you would be trying to add 1 to the text "20", which doesn't work.

(You can also show a question first: input("Your name? "), but in these lessons the program just waits quietly for the answer.)

In this lesson you will learn: how to read what the user types and use it.""",
    "3/1": """Joining text with + gets messy when you mix in numbers. An F-STRING is a neat shortcut. Put the letter f just before the opening quote, and write variables inside curly brackets { }:

name = "Ada"
age = 36
print(f"{name} is {age} years old")

shows: Ada is 36 years old

Python swaps each { } for the value inside. You can even do a calculation inside the brackets:

print(f"Next year: {age + 1}")      shows: Next year: 37

Showing decimals neatly: add :.2f after the value for exactly two digits after the decimal point.

print(f"{3.14159:.2f}")     shows: 3.14

(The f in .2f means "float" - a decimal number.)

In this lesson you will learn: how to put values into sentences easily.""",
    "3/2": """A piece of text is a row of characters, each in its own numbered slot. The numbering starts at 0, not 1:

word = "Python"
 P y t h o n
 0 1 2 3 4 5

word[0]      # 'P'      the first character
word[2]      # 't'

Negative numbers count from the END: word[-1] is the last character ('n').

A SLICE takes a piece of the text: word[start:stop]. It starts AT start but stops BEFORE stop:

word[0:3]    # 'Pyt'    characters 0, 1, 2
word[2:]     # 'thon'   from 2 to the end

len(word) tells you how many characters there are (6).

Think of it like cutting a ribbon: the cut at "stop" happens just before that character.

In this lesson you will learn: how to pick out single characters and pieces of text.""",
    "3/3": """Text comes with built-in helpers called METHODS - little tools you call with a dot after the text:

s = "  Hello World  "
s.strip()               # 'Hello World'   removes spaces at both ends
s.upper()               # '  HELLO WORLD  '   capital letters
s.lower()               # small letters
s.replace("World", "Py")    # swaps one piece for another
"a,b,c".split(",")      # ['a', 'b', 'c']   cuts text into a list at each comma
"-".join(["a", "b"])    # 'a-b'             glues a list into text
"Hello".count("l")      # 2   how many times does "l" appear?

An important detail: these tools give you a NEW piece of text - the original is not changed. If you want to keep the result, store it in a variable:

clean = s.strip()

In this lesson you will learn: the most useful tools for working with text.""",
    "4/1": """A COMPARISON asks a yes/no question and the answer is True or False (a "boolean"):

5 > 3        # True    is 5 bigger than 3?
5 == 5       # True    are they equal?
5 != 3       # True    are they different?
4 <= 3       # False   is 4 smaller than or equal to 3?

Remember the two kinds of "equals":
- one = STORES a value in a box.
- two == ASKS whether two things are equal.

Also: capital letters count. "a" == "A" is False, because to the computer they are different characters.

These True/False answers are what the next lesson uses to make decisions.

In this lesson you will learn: how to ask the computer yes/no questions.""",
    "4/2": """if lets your program choose what to do. The pushed-in (indented) lines belong to the if. Four spaces is the standard.

temp = 30
if temp > 25:
    print("Hot")
elif temp > 15:
    print("Nice")
else:
    print("Cold")

Read it from the top, like a list of questions:
- IF it is above 25: show Hot.
- ELSE IF (elif) it is above 15: show Nice.
- ELSE (nothing above was true): show Cold.

Python tries each question from the top and runs ONLY the first one that is True, then skips the rest. With temp = 30, only "Hot" is shown (even though 30 > 15 is also true).

Don't forget the colon : at the end of each if/elif/else line.

In this lesson you will learn: how to make a program choose between several paths.""",
    "4/3": """Sometimes one question isn't enough. You can combine questions with three small words:

and   BOTH must be true
or    AT LEAST ONE must be true
not   flips True to False and False to True

age = 20
has_ticket = True
if age >= 18 and has_ticket:
    print("Enter")

Read it as: "if the person is 18 or older AND has a ticket, let them in". If either part is false, they stay out.

Real-life examples:
- "Take an umbrella if it is raining OR the forecast says rain" - or.
- "You can drive if you are 18+ AND have a licence" - and.
- "Go outside if NOT raining" - not.

In this lesson you will learn: how to combine yes/no questions.""",
    "5/1": """A while loop says: "keep repeating as long as this is true."

count = 1
while count <= 3:
    print(count)
    count = count + 1

Step by step:
- count is 1. Is 1 <= 3? Yes - show 1, then make count 2.
- 2 <= 3? Yes - show 2, count becomes 3.
- 3 <= 3? Yes - show 3, count becomes 4.
- 4 <= 3? No - the loop stops.

The most important rule: change something inside the loop so the question eventually becomes False. If nothing changes, the loop never ends! (That is called an infinite loop - the program gets stuck.)

count += 1 is a shorter way to write count = count + 1.

In this lesson you will learn: how to repeat while something is still true.""",
    "5/2": """A for loop goes through things one at a time. Often you want a certain number of repeats, and range() gives you the numbers:

for i in range(3):
    print(i)        # shows 0, then 1, then 2

range(3) means "three numbers, starting at 0". Other forms:

range(1, 6)        # 1, 2, 3, 4, 5   (it stops BEFORE 6)
range(0, 10, 2)    # 0, 2, 4, 6, 8   (the last number is the step size)

The "stops before" rule is the same as slicing text.

You can also loop over the letters of text:

for ch in "hi":
    print(ch)       # h, then i

Choose for when you know what to go through, and while when you are waiting for something to become true.

In this lesson you will learn: how to repeat a set number of times, or once for each item.""",
    "5/3": """Two commands let you control a loop from the inside:

break  = stop the loop completely, right now.
continue = skip the rest of this round and go straight to the next one.

for n in range(1, 10):
    if n == 5:
        break          # when n reaches 5, leave the loop
    if n % 2 == 0:
        continue       # even number? skip the print
    print(n)

This shows 1 and 3. Step by step: 1 is odd - shown. 2 is even - skipped. 3 shown. 4 skipped. At 5 the loop breaks, so nothing more is shown.

(n % 2 == 0 asks "is the remainder 0 when dividing by 2?" - that is how you test for an even number.)

Use break when you have found what you are looking for, so you stop wasting time.

In this lesson you will learn: how to stop a loop early or skip a round.""",
    "6/1": """A list holds many values in one box, in order. You write it in square brackets, with commas between items:

fruits = ["apple", "banana", "cherry"]

Each item has a position number called an INDEX, starting at 0:

fruits[0]       # 'apple'
fruits[1]       # 'banana'
fruits[-1]      # 'cherry'   (-1 means the last one)
len(fruits)     # 3          how many items

Lists can be changed. To replace the second item:

fruits[1] = "kiwi"

A list can hold anything, even a mix: [1, "two", 3.0]. Lists are what you use for shopping lists, scores, names - anything with many items.

In this lesson you will learn: how to keep many values together and pick any one.""",
    "6/2": """Lists come with useful tools (methods) for changing them:

nums = [3, 1, 2]
nums.append(4)       # add to the END:        [3, 1, 2, 4]
nums.insert(0, 9)    # add at a position:     [9, 3, 1, 2, 4]
nums.remove(1)       # remove the VALUE 1:    [9, 3, 2, 4]
last = nums.pop()    # take off and return the last item (4)
nums.sort()          # put in order

And some ready-made helpers that work on a whole list:

sum(nums)     # add everything up
max(nums)     # the biggest
min(nums)     # the smallest
3 in nums     # is 3 in the list? True or False

Think of a list as a toolbox: append to add, remove to take out, sort to tidy up.

In this lesson you will learn: how to add, remove and organise items in a list.""",
    "6/3": """To do something for every item in a list, loop straight over the list:

for name in ["Ada", "Alan"]:
    print("Hi " + name)

Python hands you each item in turn - no need to count positions.

Python also has a shortcut for BUILDING a new list from an old one, called a LIST COMPREHENSION. It looks odd at first, but read it like a sentence:

squares = [n * n for n in range(5)]
# "n times n, for each n in range(5)"  ->  [0, 1, 4, 9, 16]

evens = [n for n in nums if n % 2 == 0]
# "n, for each n in nums, but only if n is even"

It is just a for loop and an if squeezed into one line. If it looks confusing, write the long loop first - it does the same job.

In this lesson you will learn: how to go through a list and how to build new lists from old ones.""",
    "7/1": """A list finds things by position (0, 1, 2...). A DICTIONARY finds things by a NAME, called a KEY - like a real dictionary where you look up a word to find its meaning, or a phone book where you look up a name to find a number.

ages = {"Ada": 36, "Alan": 41}

Each entry is key: value. Look one up with square brackets:

ages["Ada"]            # 36

Add or change an entry:

ages["Grace"] = 85

Check whether a key is there:

"Ada" in ages          # True

If you look up a key that is missing you get an error. A safer way gives a default instead:

ages.get("Bob", 0)     # 0

In this lesson you will learn: how to store and look up information by name.""",
    "7/2": """You can loop over a dictionary in three ways:

for name in ages:                  # the keys (names)
for age in ages.values():          # just the values
for name, age in ages.items():     # both together
    print(f"{name}: {age}")

A very common use is COUNTING: how many times does each word appear?

counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1

Read it: "get the count so far for this word (or 0 if new), add 1, and store it back." After going through ["a", "b", "a"] you get {"a": 2, "b": 1}.

In this lesson you will learn: how to go through a dictionary and how to count things with one.""",
    "7/3": """Two more containers:

A TUPLE is like a list that cannot be changed - useful for a fixed pair or group, such as a point on a map:

point = (3, 4)
x, y = point            # "unpacking": x is 3, y is 4

A SET is a bag of UNIQUE values with no order. Duplicates disappear automatically:

colors = {"red", "blue", "red"}     # just red and blue
set([1, 1, 2])                      # {1, 2}   - a handy way to remove duplicates

Sets can combine, like overlapping circles:

a | b     everything in either (union)
a & b     only what is in both (intersection)
a - b     in a but not in b (difference)

In this lesson you will learn: tuples for fixed groups, and sets for unique values.""",
    "8/1": """A FUNCTION is a mini-program with a name that you can use again and again - like a recipe card you can follow whenever you like.

def greet(name):
    print(f"Hello, {name}!")

Parts:
- def means "I am defining a function".
- greet is its name.
- name in brackets is a PARAMETER - a blank the caller fills in.
- The pushed-in lines are what the function does.

Defining a function does not run it. To use it, CALL it by name:

greet("Ada")     # Hello, Ada!
greet("Alan")    # Hello, Alan!

Why bother? You write the steps ONCE and reuse them, and if you need a fix you change it in one place.

In this lesson you will learn: how to write your own reusable commands.""",
    "8/2": """A function can hand a result BACK to whoever called it. That is what return does:

def area(w, h):
    return w * h

size = area(3, 4)       # size is now 12

Compare: print SHOWS a value to the person; return GIVES the value back to the program so it can use it (store it, calculate with it).

Parameters can have DEFAULT values, used when the caller doesn't provide one:

def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Ada")           # 'Hello, Ada!'
greet("Ada", "Hi")     # 'Hi, Ada!'

In this lesson you will learn: how functions give back results, and how to set default values.""",
    "8/3": """Things go wrong: the user types letters where you wanted a number, or you divide by zero. When that happens Python raises an EXCEPTION and the program stops with an error message.

You can PREPARE for trouble with try/except - "try this; if it goes wrong in this way, do that instead":

try:
    n = int(input())
    print(10 / n)
except ValueError:
    print("That's not a number")
except ZeroDivisionError:
    print("Can't divide by zero")

If the user types abc, int() fails with a ValueError, and the program prints a friendly message instead of crashing.

Common exceptions and what causes them:
- ValueError - the right kind of value but unusable ("abc" as a number)
- ZeroDivisionError - dividing by zero
- KeyError - a dictionary key that is missing
- IndexError - a list position that doesn't exist
- TypeError - mixing types that don't go together

In this lesson you will learn: how to handle mistakes without crashing.""",
}
