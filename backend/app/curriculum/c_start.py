"""C - gentle 'Start here' units for people who have never seen code."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t
from .c_adv import STARTER, prog

START = [
    start_unit(
        1,
        "Start here · What is code?",
        lesson(
            "What is a program?",
            """Phones, TVs, washing machines, even cars run PROGRAMS. A program is a list of instructions that a computer follows one after another, top to bottom. The computer is like a robot that does EXACTLY what you write - it never guesses.

CODE is how we write those instructions. C is one of the oldest and most important languages (like Latin for languages, almost everything else grew from it). It is used inside operating systems and small devices.

Every C program sits in the same frame. For now, COPY it and write your instructions in the middle - the parts are explained later:

#include <stdio.h>

int main(void) {
    // your instructions go here
    return 0;
}

A line starting with // is a COMMENT - a note for people that the computer ignores.

In this lesson you will learn: what a program is, and the frame every C program sits in.""",
            mcq("What is a program?", ["A list of instructions for a computer", "A kind of screen", "A phone brand", "A cable"], 0, "A program is a list of instructions."),
            mcq("In what order does the computer follow instructions?", ["One after another, top to bottom", "Randomly", "Bottom to top", "All at once"], 0, "Top to bottom."),
            mcq("What does a line starting with // do?", ["It is a note the computer ignores", "It shows a message", "It stops the program", "It does maths"], 0, "// starts a comment."),
            order("Put the frame in order.", ["#include <stdio.h>", "int main(void) {", "    // your instructions", "    return 0;", "}"], "include first, then main with your instructions inside."),
        ),
        lesson(
            "Showing a message",
            """To show something on the screen use printf (short for "print formatted"):

printf("Hello!\\n");

You see:

Hello!

The parts:
- printf is the command - "show this".
- Round brackets ( ) hold what to show.
- Quote marks " " mean "this is text".
- \\n means "go to a new line". printf does NOT move to a new line by itself, so we add \\n.
- The semicolon ; ends the instruction - EVERY instruction ends with one.

Several instructions run top to bottom:

printf("Hello!\\n");
printf("I am learning C.\\n");

The line #include <stdio.h> at the top is what teaches the computer about printf - leave it there.

In this lesson you will learn: how to make the computer show a message.""",
            mcq("What does printf do?", ["Shows something on the screen", "Reads a file", "Deletes text", "Saves a file"], 0, "printf shows output."),
            mcq("What does \\n do inside the text?", ["Moves to a new line", "Shows the letter n", "Ends the program", "Does maths"], 0, "\\n is a new line."),
            mcq("What must every instruction end with?", ["A semicolon ;", "A full stop .", "A comma ,", "Nothing"], 0, "C instructions end with ;"),
            fill("Fill in the missing word.", '___("Hi!\\n");', "printf", "The command is printf."),
            run("Show exactly: Hello, World!", "c", [t("Run")], ["Hello, World!"], prog('printf("Hello, World!\\n");'), starter=STARTER,
                fallback=[r'printf\(\s*"Hello, World!'], hint='printf("Hello, World!\\n");'),
        ),
        lesson(
            "Words and numbers",
            """Computers treat words and numbers differently.

TEXT is wrapped in double quotes:   "Room 5"
NUMBERS have no quotes:             5      2.5

To show a number with printf we use a PLACEHOLDER inside the text. A placeholder is a gap that gets filled by a value you list after the comma:

printf("%d\\n", 5);          shows 5      (%d = a whole number goes here)
printf("%f\\n", 2.5);        shows 2.500000   (%f = a decimal number)
printf("Score: %d\\n", 10);  shows Score: 10

You can even do maths there:

printf("%d\\n", 2 + 3);      shows 5

C names the KINDS of values:

int     - a whole number, like 7
double  - a number with decimals, like 2.5
char    - one single letter, like 'A' (in single quotes)

In this lesson you will learn: how to show numbers, and C's names for kinds of values.""",
            mcq("What is %d a placeholder for?", ["A whole number", "Text", "A decimal", "A letter"], 0, "%d = integer (digits)."),
            mcq("What does this show?", ["Score: 10", "Score: %d", "Score: ", "An error"], 0, "The 10 fills the %d gap.", code='printf("Score: %d\\n", 10);'),
            mcq("What does this show?", ["5", "2 + 3", "23", "An error"], 0, "The computer adds, then fills the gap.", code='printf("%d\\n", 2 + 3);'),
            mcq("Which C name is for whole numbers?", ["int", "double", "char", "float"], 0, "int = integer."),
            run("Show the result of 10 + 5 (15).", "c", [t("Run")], ["15"], prog('printf("%d\\n", 10 + 5);'), starter=STARTER, fallback=[r"10\s*\+\s*5"], hint='printf("%d\\n", 10 + 5);'),
        ),
        lesson(
            "Boxes with names (variables)",
            """A VARIABLE is a box with a name that holds a value, so the computer can remember it.

int age = 12;

Read it as: "make a box for a whole number (int), call it age, and put 12 in it". The = sign means "store this value" (it isn't the maths 'equals').

Use the box by writing its name:

printf("%d\\n", age);      shows 12

Change what is inside later:

age = 13;                 the box now holds 13

For decimal numbers use double and the placeholder %f (or %.2f for two digits after the point):

double price = 4.5;
printf("%.2f\\n", price);   shows 4.50

In this lesson you will learn: how to store a value with a name and use it again.""",
            mcq("What does int age = 12; do?", ["Makes a whole-number box called age holding 12", "Shows 12", "Deletes age", "Compares"], 0, "int is the kind of box; = stores."),
            mcq("What does this show?", ["13", "12", "age", "Nothing"], 0, "The box was changed to 13.", code='int age = 12;\nage = 13;\nprintf("%d\\n", age);'),
            mcq("What does %.2f do?", ["Shows a decimal with 2 digits after the point", "Shows 2 numbers", "Shows text", "Rounds to whole"], 0, "%.2f formats decimals with two places."),
            fill("Make a whole-number box called score holding 50.", "___ score = 50;", "int", "int is for whole numbers."),
            run("Make an int called number with the value 7 and show it.", "c", [t("Run")], ["7"], prog('int number = 7;\nprintf("%d\\n", number);'), starter=STARTER,
                fallback=[r"int\s+number\s*=\s*7\s*;", r"printf\("], hint='int number = 7; then printf("%d\\n", number);'),
        ),
    ),
    start_unit(
        2,
        "Start here · Making the computer think",
        lesson(
            "Doing maths",
            """C is a super calculator:

+  add          printf("%d\\n", 8 + 2);    shows 10
-  subtract     printf("%d\\n", 8 - 2);    shows 6
*  multiply     printf("%d\\n", 8 * 2);    shows 16   (a star, not ×)
/  divide       printf("%d\\n", 8 / 2);    shows 4

One surprise: with whole numbers (int), division throws away the decimal part:

printf("%d\\n", 7 / 2);      shows 3     (not 3.5)

Use a decimal number to keep it:

printf("%.1f\\n", 7 / 2.0);  shows 3.5

The remainder after dividing is %:

printf("%d\\n", 7 % 2);      shows 1

Just like at school, * and / happen before + and -. Round brackets choose what goes first.

In this lesson you will learn: how to do maths, and the whole-number division surprise.""",
            mcq("Which sign multiplies?", ["*", "x", "×", "^"], 0, "A star."),
            mcq("What does this show?", ["3", "3.5", "4", "2"], 0, "Whole-number division drops the decimals.", code='printf("%d\\n", 7 / 2);'),
            mcq("What does this show?", ["1", "3", "0", "7"], 0, "% is the remainder: 7 = 3 * 2 + 1.", code='printf("%d\\n", 7 % 2);'),
            mcq("What does this show?", ["14", "20", "10", "24"], 0, "3 * 4 first.", code='printf("%d\\n", 2 + 3 * 4);'),
            run("A pack has 6 pencils and you buy 4 packs. Show how many (24).", "c", [t("Run")], ["24"], prog('printf("%d\\n", 6 * 4);'), starter=STARTER, fallback=[r"6\s*\*\s*4"], hint='printf("%d\\n", 6 * 4);'),
        ),
        lesson(
            "Yes or no questions",
            """Computers are great at yes-or-no questions. In C the answer is a number: 1 means yes (true) and 0 means no (false).

printf("%d\\n", 5 > 3);     shows 1   (is 5 bigger than 3? yes)
printf("%d\\n", 5 < 3);     shows 0   (no)
printf("%d\\n", 5 == 5);    shows 1   (are they the same? yes)
printf("%d\\n", 5 != 5);    shows 0   (are they different? no)

The signs that ask questions:

>    is bigger than          <    is smaller than
>=   is bigger or equal      <=   is smaller or equal
==   is the same as  (TWO equal signs)      !=   is not the same as

One = stores a value. To ASK whether two things are equal, use two: ==.

In this lesson you will learn: how to ask the computer a yes-or-no question.""",
            mcq("What does this show (1 = true, 0 = false)?", ["1", "0", "7", "An error"], 0, "7 is bigger than 3.", code='printf("%d\\n", 7 > 3);'),
            mcq("What does this show?", ["0", "1", "10", "An error"], 0, "10 is not smaller than 4.", code='printf("%d\\n", 10 < 4);'),
            mcq("Which sign asks 'are these two the same?'", ["==", "=", "!=", "=>"], 0, "Two equal signs ask."),
            fill("Ask whether 3 is smaller than 9.", 'printf("%d\\n", 3 ___ 9);', "<", "< is 'smaller than'."),
        ),
        lesson(
            "If this, then that",
            """Now the computer can DECIDE with the word if:

int temperature = 30;
if (temperature > 25) {
    printf("Hot\\n");
}

Read it as: "IF the temperature is above 25, THEN show Hot."

The question goes in round brackets ( ). The instructions to do go between curly brackets { }. If the answer is no, they are skipped.

To say what to do OTHERWISE, add else:

if (temperature > 25) {
    printf("Hot\\n");
} else {
    printf("Cool\\n");
}

Only ONE of the two happens.

In this lesson you will learn: how a program chooses between two paths.""",
            mcq("What does this show?", ["Hot", "Cool", "Both", "Nothing"], 0, "30 is above 25.", code='int t = 30;\nif (t > 25) {\n    printf("Hot\\n");\n} else {\n    printf("Cool\\n");\n}'),
            mcq("What does this show?", ["Cool", "Hot", "Both", "Nothing"], 0, "10 is not above 25, so else runs.", code='int t = 10;\nif (t > 25) {\n    printf("Hot\\n");\n} else {\n    printf("Cool\\n");\n}'),
            fill("Fill in the word for 'otherwise'.", 'if (age >= 18) {\n    printf("Adult\\n");\n} ___ {\n    printf("Child\\n");\n}', "else", "else is the otherwise path."),
            run("The points are 7. Show Pass if points is 5 or more, otherwise Fail.", "c", [t("Run")], ["Pass"],
                prog('int points = 7;\nif (points >= 5) {\n    printf("Pass\\n");\n} else {\n    printf("Fail\\n");\n}'), starter=STARTER, fallback=[r"if\s*\(", r"else"], hint="if (points >= 5) { ... } else { ... }"),
        ),
        lesson(
            "Doing it again and again (loops)",
            """To show "Hello" five times you could write five lines - but a million times is impossible. A LOOP repeats for you:

for (int i = 0; i < 5; i++) {
    printf("Hello\\n");
}

Read it as: "start i at 0; keep going while i is less than 5; add 1 to i each time". That is 5 repeats (i is 0, 1, 2, 3, 4). The lines between { } repeat.

You can use the counter too:

for (int i = 0; i < 3; i++) {
    printf("%d\\n", i);
}

shows 0, 1, 2. (Programmers start counting at 0 - a funny habit you will get used to!) i++ means "add 1 to i".

In this lesson you will learn: how to repeat instructions without writing them again and again.""",
            mcq("What does a loop do?", ["Repeats instructions", "Stops the program", "Makes a choice", "Stores a value"], 0, "A loop repeats the lines in { }."),
            mcq("How many times does this show Hi?", ["3", "2", "4", "1"], 0, "i is 0, 1, 2.", code='for (int i = 0; i < 3; i++) {\n    printf("Hi\\n");\n}'),
            mcq("What does i++ do?", ["Adds 1 to i", "Subtracts 1", "Shows i", "Resets i"], 0, "i++ means i becomes i + 1."),
            run("Show the word Hello 3 times, each on its own line, using a loop.", "c", [t("Run")], ["Hello\nHello\nHello"],
                prog('for (int i = 0; i < 3; i++) {\n    printf("Hello\\n");\n}'), starter=STARTER, fallback=[r"for\s*\("], hint='for (int i = 0; i < 3; i++) { printf("Hello\\n"); }'),
        ),
    ),
]
