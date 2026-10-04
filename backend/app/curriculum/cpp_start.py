"""C++ - gentle 'Start here' units for people who have never seen code."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t
from .cpp_adv import STARTER, prog

START = [
    start_unit(
        1,
        "Start here · What is code?",
        lesson(
            "What is a program?",
            """Games, phone apps, even your car's screen run PROGRAMS. A program is a list of instructions that a computer follows one after another, top to bottom. The computer is like a robot that does EXACTLY what you write - it never guesses.

CODE is how we write those instructions. C++ is one language for it (like English or French for people). It is very fast, so it powers games, browsers and many tools.

Every C++ program sits in the same frame. For now, COPY it and write your instructions in the middle - the parts are explained later:

#include <iostream>

int main() {
    // your instructions go here
    return 0;
}

A line starting with // is a COMMENT - a note for people that the computer ignores.

In this lesson you will learn: what a program is, and the frame every C++ program sits in.""",
            mcq("What is a program?", ["A list of instructions for a computer", "A kind of screen", "A phone brand", "A cable"], 0, "A program is a list of instructions."),
            mcq("In what order does the computer follow instructions?", ["One after another, top to bottom", "Randomly", "Bottom to top", "All at once"], 0, "Top to bottom."),
            mcq("What does a line starting with // do?", ["It is a note the computer ignores", "It shows a message", "It stops the program", "It does maths"], 0, "// starts a comment."),
            order("Put the frame in order.", ["#include <iostream>", "int main() {", "    // your instructions", "    return 0;", "}"], "include first, then main with your instructions inside."),
        ),
        lesson(
            "Showing a message",
            """To show something on the screen use std::cout and the << sign (think of it as an arrow pushing the message to the screen):

std::cout << "Hello!" << std::endl;

You see:

Hello!

The parts:
- std::cout is "the screen" (the output).
- << pushes things to it.
- Quote marks " " mean "this is text".
- std::endl moves to a new line (you can also write "\\n" inside the text).
- The semicolon ; at the end is like a full stop - EVERY instruction ends with one.

Several things can be pushed in one line:

std::cout << "Score: " << 10 << std::endl;     shows Score: 10

The line #include <iostream> at the top is what teaches the computer about std::cout - leave it there.

In this lesson you will learn: how to make the computer show a message.""",
            mcq("What does std::cout do?", ["Shows things on the screen", "Reads a file", "Deletes text", "Saves a file"], 0, "cout is the output (screen)."),
            mcq("What does this show?", ["Good morning", "\"Good morning\"", "std::cout", "Nothing"], 0, "The quotes only mark the text.", code='std::cout << "Good morning" << std::endl;'),
            mcq("What must every instruction end with?", ["A semicolon ;", "A full stop .", "A comma ,", "Nothing"], 0, "C++ instructions end with ;"),
            fill("Fill in the arrow that pushes text to the screen.", 'std::cout ___ "Hi!";', "<<", "<< pushes values to cout."),
            run("Show exactly: Hello, World!", "cpp", [t("Run")], ["Hello, World!"], prog('std::cout << "Hello, World!" << std::endl;'), starter=STARTER,
                fallback=[r'cout\s*<<\s*"Hello, World!"'], hint='std::cout << "Hello, World!" << std::endl;'),
        ),
        lesson(
            "Words and numbers",
            """Computers treat words and numbers differently.

TEXT is wrapped in double quotes:   "Room 5"
NUMBERS have no quotes:             5      2.5

The computer can do maths with numbers:

std::cout << 2 + 3;        shows 5

With quotes it is only text:

std::cout << "2 + 3";      shows 2 + 3

C++ is picky about the KIND of each value. The names you will use when making boxes next lesson:

int      - a whole number, like 7
double   - a number with decimals, like 2.5
std::string - text, like "hello"  (needs #include <string>)
bool     - only true or false

In this lesson you will learn: the difference between text and numbers, and C++'s names for them.""",
            mcq("Which one is text?", ["\"Hello\"", "42", "3.14", "7"], 0, "Text is in quotes."),
            mcq("What does this show?", ["5", "2 + 3", "23", "An error"], 0, "No quotes: the computer adds.", code="std::cout << 2 + 3;"),
            mcq("Which C++ name is for whole numbers?", ["int", "double", "bool", "string"], 0, "int = integer."),
            mcq("Which C++ name is for numbers with decimals?", ["double", "int", "bool", "char"], 0, "double holds decimals."),
            run("Show the result of 10 + 5 (15).", "cpp", [t("Run")], ["15"], prog("std::cout << 10 + 5 << std::endl;"), starter=STARTER, fallback=[r"10\s*\+\s*5"], hint="std::cout << 10 + 5 << std::endl;"),
        ),
        lesson(
            "Boxes with names (variables)",
            """A VARIABLE is a box with a name that holds a value, so the computer can remember it.

int age = 12;

Read it as: "make a box for a whole number (int), call it age, and put 12 in it". The = sign means "store this value" (it isn't the maths 'equals').

Use the box by writing its name:

std::cout << age;       shows 12

Change what is inside later:

age = 13;               the box now holds 13

Text goes in a std::string box:

std::string name = "Maya";
std::cout << name;      shows Maya

No quotes around name in cout << name - we want what is INSIDE the box.

In this lesson you will learn: how to store a value with a name and use it again.""",
            mcq("What does int age = 12; do?", ["Makes a whole-number box called age holding 12", "Shows 12", "Deletes age", "Compares"], 0, "int says the kind of box; = stores."),
            mcq("What does this show?", ["13", "12", "age", "Nothing"], 0, "The box was changed to 13.", code="int age = 12;\nage = 13;\nstd::cout << age;"),
            mcq("Which line makes a box for text?", ["std::string name = \"Maya\";", "int name = \"Maya\";", "name = Maya;", "text name = Maya;"], 0, "Text goes in std::string, with quotes."),
            fill("Make a whole-number box called score holding 50.", "___ score = 50;", "int", "int is for whole numbers."),
            run("Make an int called number with the value 7 and show it.", "cpp", [t("Run")], ["7"], prog("int number = 7;\nstd::cout << number << std::endl;"), starter=STARTER,
                fallback=[r"int\s+number\s*=\s*7\s*;", r"cout\s*<<\s*number"], hint="int number = 7; then std::cout << number;"),
        ),
    ),
    start_unit(
        2,
        "Start here · Making the computer think",
        lesson(
            "Doing maths",
            """C++ is a super calculator:

+  add          std::cout << 8 + 2;     shows 10
-  subtract     std::cout << 8 - 2;     shows 6
*  multiply     std::cout << 8 * 2;     shows 16   (a star, not ×)
/  divide       std::cout << 8 / 2;     shows 4

One surprise: with whole numbers (int), division throws away the decimal part:

std::cout << 7 / 2;      shows 3     (not 3.5)

Use a decimal number to keep it:

std::cout << 7 / 2.0;    shows 3.5

The remainder after dividing is %:

std::cout << 7 % 2;      shows 1

Just like at school, * and / happen before + and -. Round brackets choose what goes first.

In this lesson you will learn: how to do maths, and the whole-number division surprise.""",
            mcq("Which sign multiplies?", ["*", "x", "×", "^"], 0, "A star."),
            mcq("What does this show?", ["3", "3.5", "4", "2"], 0, "Whole-number division drops the decimals.", code="std::cout << 7 / 2;"),
            mcq("What does this show?", ["1", "3", "0", "7"], 0, "% is the remainder: 7 = 3 * 2 + 1.", code="std::cout << 7 % 2;"),
            mcq("What does this show?", ["14", "20", "10", "24"], 0, "3 * 4 first.", code="std::cout << 2 + 3 * 4;"),
            run("A pack has 6 pencils and you buy 4 packs. Show how many (24).", "cpp", [t("Run")], ["24"], prog("std::cout << 6 * 4 << std::endl;"), starter=STARTER, fallback=[r"6\s*\*\s*4"], hint="std::cout << 6 * 4;"),
        ),
        lesson(
            "Yes or no questions",
            """Computers are great at yes-or-no questions. The answer is a bool: true or false (shown as 1 and 0 when printed).

std::cout << (5 > 3);     shows 1   (true: is 5 bigger than 3? yes)
std::cout << (5 < 3);     shows 0   (false)
std::cout << (5 == 5);    shows 1   (are they the same? yes)
std::cout << (5 != 5);    shows 0   (are they different? no)

The signs that ask questions:

>    is bigger than          <    is smaller than
>=   is bigger or equal      <=   is smaller or equal
==   is the same as  (TWO equal signs)      !=   is not the same as

One = stores a value. To ASK whether two things are equal, use two: ==. Put the question in round brackets when you print it.

In this lesson you will learn: how to ask the computer a yes-or-no question.""",
            mcq("What does this show (1 means true, 0 means false)?", ["1", "0", "7", "An error"], 0, "7 is bigger than 3, so true = 1.", code="std::cout << (7 > 3);"),
            mcq("What does this show?", ["0", "1", "10", "An error"], 0, "10 is not smaller than 4: false = 0.", code="std::cout << (10 < 4);"),
            mcq("Which sign asks 'are these two the same?'", ["==", "=", "!=", "=>"], 0, "Two equal signs ask."),
            fill("Ask whether 3 is smaller than 9.", "std::cout << (3 ___ 9);", "<", "< is 'smaller than'."),
        ),
        lesson(
            "If this, then that",
            """Now the computer can DECIDE with the word if:

int temperature = 30;
if (temperature > 25) {
    std::cout << "Hot";
}

Read it as: "IF the temperature is above 25, THEN show Hot."

The question goes in round brackets ( ). The instructions to do go between curly brackets { }. If the answer is false, they are skipped.

To say what to do OTHERWISE, add else:

if (temperature > 25) {
    std::cout << "Hot";
} else {
    std::cout << "Cool";
}

Only ONE of the two happens.

In this lesson you will learn: how a program chooses between two paths.""",
            mcq("What does this show?", ["Hot", "Cool", "Both", "Nothing"], 0, "30 is above 25.", code='int t = 30;\nif (t > 25) {\n    std::cout << "Hot";\n} else {\n    std::cout << "Cool";\n}'),
            mcq("What does this show?", ["Cool", "Hot", "Both", "Nothing"], 0, "10 is not above 25, so else runs.", code='int t = 10;\nif (t > 25) {\n    std::cout << "Hot";\n} else {\n    std::cout << "Cool";\n}'),
            fill("Fill in the word for 'otherwise'.", 'if (age >= 18) {\n    std::cout << "Adult";\n} ___ {\n    std::cout << "Child";\n}', "else", "else is the otherwise path."),
            run("The points are 7. Show Pass if points is 5 or more, otherwise Fail.", "cpp", [t("Run")], ["Pass"],
                prog('int points = 7;\nif (points >= 5) {\n    std::cout << "Pass" << std::endl;\n} else {\n    std::cout << "Fail" << std::endl;\n}'), starter=STARTER,
                fallback=[r"if\s*\(", r"else"], hint="if (points >= 5) { ... } else { ... }"),
        ),
        lesson(
            "Doing it again and again (loops)",
            """To show "Hello" five times you could write five lines - but a million times is impossible. A LOOP repeats for you:

for (int i = 0; i < 5; i++) {
    std::cout << "Hello" << std::endl;
}

Read it as: "start i at 0; keep going while i is less than 5; add 1 to i each time". That is 5 repeats (i is 0, 1, 2, 3, 4). The lines between { } repeat.

You can use the counter too:

for (int i = 0; i < 3; i++) {
    std::cout << i << std::endl;
}

shows 0, 1, 2. (Programmers start counting at 0 - a funny habit you will get used to!) i++ means "add 1 to i".

In this lesson you will learn: how to repeat instructions without writing them again and again.""",
            mcq("What does a loop do?", ["Repeats instructions", "Stops the program", "Makes a choice", "Stores a value"], 0, "A loop repeats the lines in { }."),
            mcq("How many times does this show Hi?", ["3", "2", "4", "1"], 0, "i is 0, 1, 2.", code='for (int i = 0; i < 3; i++) {\n    std::cout << "Hi\\n";\n}'),
            mcq("What does i++ do?", ["Adds 1 to i", "Subtracts 1", "Shows i", "Resets i"], 0, "i++ means i becomes i + 1."),
            run("Show the word Hello 3 times, each on its own line, using a loop.", "cpp", [t("Run")], ["Hello\nHello\nHello"],
                prog('for (int i = 0; i < 3; i++) {\n    std::cout << "Hello" << std::endl;\n}'), starter=STARTER, fallback=[r"for\s*\("], hint='for (int i = 0; i < 3; i++) { std::cout << "Hello" << std::endl; }'),
        ),
    ),
]
