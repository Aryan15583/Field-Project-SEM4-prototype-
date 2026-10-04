"""Java - gentle 'Start here' units for people who have never seen code."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t
from .java_adv import MAIN, prog

START = [
    start_unit(
        1,
        "Start here · What is code?",
        lesson(
            "What is a program?",
            """Phones, games, banking apps - they all run PROGRAMS. A program is a list of instructions that a computer follows, one after another, from the top to the bottom. The computer is like a robot that does EXACTLY what you write - no guessing.

CODE is how we write instructions. Java is one language for writing them (just as English and Spanish are languages for people). Java is used for Android apps, websites' behind-the-scenes servers and much more.

Java wants every program wrapped in the same "frame". For now, simply COPY this frame and write your instructions in the middle - we'll explain the parts later:

public class Main {
    public static void main(String[] args) {
        // your instructions go here
    }
}

The line starting with // is a COMMENT - a note for people. The computer ignores it.

In this lesson you will learn: what a program is, and the frame every Java program sits in.""",
            mcq("What is a program?", ["A list of instructions for a computer", "A kind of screen", "A phone brand", "A cable"], 0, "A program is a list of instructions."),
            mcq("In what order does the computer follow instructions?", ["One after another, top to bottom", "Randomly", "Bottom to top", "All at once"], 0, "Top to bottom."),
            mcq("What does a line starting with // do?", ["It is a note the computer ignores", "It shows a message", "It stops the program", "It does maths"], 0, "// starts a comment."),
            order("Put the frame in the right order.", ["public class Main {", "    public static void main(String[] args) {", "        // your instructions", "    }", "}"], "The inner part (main) lives inside the outer part (class)."),
        ),
        lesson(
            "Showing a message",
            """To show something on the screen, use System.out.println:

System.out.println("Hello!");

When the computer runs it, you see:

Hello!

The parts:
- System.out.println is the command - it means "show this and then move to a new line".
- Round brackets ( ) hold what you want to show.
- Quote marks " " mean "this is text".
- The semicolon ; at the end is like a full stop - EVERY instruction ends with one.

Only the text inside the quotes appears - the quotes themselves are not shown.

Several instructions run top to bottom, each on its own line:

System.out.println("Hello!");
System.out.println("I am learning Java.");

Don't worry about mistakes - Java tells you what's wrong and you try again.

In this lesson you will learn: how to make the computer show a message.""",
            mcq("What does System.out.println do?", ["Shows something and moves to a new line", "Saves a file", "Deletes text", "Prints on paper"], 0, "println shows a message."),
            mcq("What will this show?", ["Good morning", "\"Good morning\"", "System.out.println", "Nothing"], 0, "The quotes only mark the text.", code='System.out.println("Good morning");'),
            mcq("What must every instruction end with?", ["A semicolon ;", "A full stop .", "A comma ,", "Nothing"], 0, "Java instructions end with ;"),
            fill("Fill in the missing word.", 'System.out.___("Hi!");', "println", "The command is println."),
            run("Show exactly: Hello, World!", "java", [t("Run")], ["Hello, World!"], prog('System.out.println("Hello, World!");'), starter=MAIN,
                fallback=[r'System\.out\.println\(\s*"Hello, World!"\s*\)\s*;'], hint='System.out.println("Hello, World!");'),
        ),
        lesson(
            "Words and numbers",
            """Computers treat words and numbers differently.

TEXT is wrapped in double quotes:   "Room 5"
NUMBERS have no quotes:             5      2.5

The computer can do maths with numbers:

System.out.println(2 + 3);      shows 5

With quotes it is only text, so nothing is calculated:

System.out.println("2 + 3");    shows 2 + 3

Java is picky about the KIND of each value, so it has names for them (you will use them when making boxes in the next lesson):

String   - text, like "hello"
int      - a whole number, like 7
double   - a number with decimals, like 2.5
boolean  - only true or false

In this lesson you will learn: the difference between text and numbers, and Java's names for them.""",
            mcq("Which one is text?", ["\"Hello\"", "42", "3.14", "7"], 0, "Anything in quotes is text."),
            mcq("What does this show?", ["5", "2 + 3", "23", "An error"], 0, "No quotes: the computer adds.", code="System.out.println(2 + 3);"),
            mcq("Which Java name is for whole numbers?", ["int", "String", "double", "boolean"], 0, "int = integer = whole number."),
            mcq("Which Java name is for text?", ["String", "int", "double", "boolean"], 0, "String holds text."),
            run("Show the result of 10 + 5 (15).", "java", [t("Run")], ["15"], prog("System.out.println(10 + 5);"), starter=MAIN, fallback=[r"println\(\s*10\s*\+\s*5\s*\)"], hint="System.out.println(10 + 5);"),
        ),
        lesson(
            "Boxes with names (variables)",
            """A VARIABLE is a box with a name that holds a value, so the computer can remember it.

int age = 12;

Read it as: "make a box for a whole number (int), call it age, and put 12 in it". The = sign here means "store this value" (it isn't the maths 'equals').

Use the box by writing its name:

System.out.println(age);     shows 12

Change what is inside later - but not the kind of thing:

age = 13;                    the box now holds 13

Text goes in a String box:

String name = "Maya";
System.out.println(name);    shows Maya

Notice there are no quotes around name in println(name) - we want what is INSIDE the box.

In this lesson you will learn: how to store a value with a name and use it again.""",
            mcq("What does int age = 12; do?", ["Makes a whole-number box called age holding 12", "Shows 12", "Deletes age", "Compares"], 0, "int says what kind of box, = stores the value."),
            mcq("What does this show?", ["13", "12", "age", "Nothing"], 0, "The box is changed to 13.", code="int age = 12;\nage = 13;\nSystem.out.println(age);"),
            mcq("Which line makes a box for text?", ["String name = \"Maya\";", "int name = \"Maya\";", "name = Maya;", "text name = Maya;"], 0, "Text goes in a String box, with quotes."),
            fill("Make a whole-number box called score holding 50.", "___ score = 50;", "int", "int is for whole numbers."),
            run("Make an int called number with the value 7 and show it.", "java", [t("Run")], ["7"], prog("int number = 7;\nSystem.out.println(number);"), starter=MAIN,
                fallback=[r"int\s+number\s*=\s*7\s*;", r"println\(\s*number\s*\)"], hint="int number = 7; then System.out.println(number);"),
        ),
    ),
    start_unit(
        2,
        "Start here · Making the computer think",
        lesson(
            "Doing maths",
            """Java is a super calculator:

+   add            System.out.println(8 + 2);    shows 10
-   subtract       System.out.println(8 - 2);    shows 6
*   multiply       System.out.println(8 * 2);    shows 16   (a star, not ×)
/   divide         System.out.println(8 / 2);    shows 4

One surprise: with int (whole numbers), division throws away the decimal part:

System.out.println(7 / 2);      shows 3   (not 3.5)

Use a double (a number that can have decimals) to keep it:

System.out.println(7 / 2.0);    shows 3.5

The remainder after dividing is %:

System.out.println(7 % 2);      shows 1

Just like at school, * and / happen before + and -. Round brackets choose what goes first.

In this lesson you will learn: how to do maths, and the whole-number division surprise.""",
            mcq("Which sign multiplies?", ["*", "x", "×", "^"], 0, "A star."),
            mcq("What does this show?", ["3", "3.5", "4", "2"], 0, "Whole-number division drops the decimals: 7 / 2 is 3.", code="System.out.println(7 / 2);"),
            mcq("What does this show?", ["1", "3", "0", "7"], 0, "% gives the remainder: 7 = 3 * 2 + 1.", code="System.out.println(7 % 2);"),
            mcq("What does this show?", ["14", "20", "10", "24"], 0, "3 * 4 first.", code="System.out.println(2 + 3 * 4);"),
            run("A pack has 6 pencils and you buy 4 packs. Show how many pencils you have (24).", "java", [t("Run")], ["24"], prog("System.out.println(6 * 4);"), starter=MAIN, fallback=[r"6\s*\*\s*4"], hint="System.out.println(6 * 4);"),
        ),
        lesson(
            "Yes or no questions",
            """Computers are great at yes-or-no questions. The answer is a boolean: true or false.

System.out.println(5 > 3);      shows true    (is 5 bigger than 3? yes)
System.out.println(5 < 3);      shows false
System.out.println(5 == 5);     shows true    (are they the same? yes)
System.out.println(5 != 5);     shows false   (are they different? no)

The signs that ask questions:

>    is bigger than          <    is smaller than
>=   is bigger or equal      <=   is smaller or equal
==   is the same as  (TWO equal signs)      !=   is not the same as

One = stores a value. To ASK whether two things are equal, use two: ==.

In this lesson you will learn: how to ask the computer a yes-or-no question.""",
            mcq("What does this show?", ["true", "false", "7", "An error"], 0, "7 is bigger than 3.", code="System.out.println(7 > 3);"),
            mcq("What does this show?", ["false", "true", "10", "An error"], 0, "10 is not smaller than 4.", code="System.out.println(10 < 4);"),
            mcq("Which sign asks 'are these two the same?'", ["==", "=", "!=", "=>"], 0, "Two equal signs ask."),
            fill("Ask whether 3 is smaller than 9.", "System.out.println(3 ___ 9);", "<", "< is 'smaller than'."),
        ),
        lesson(
            "If this, then that",
            """Now the computer can DECIDE with the word if:

int temperature = 30;
if (temperature > 25) {
    System.out.println("Hot");
}

Read it as: "IF the temperature is above 25, THEN show Hot."

The question goes in round brackets ( ). The instructions to do go between curly brackets { }. If the answer is false, the computer skips them.

To say what to do OTHERWISE, add else:

if (temperature > 25) {
    System.out.println("Hot");
} else {
    System.out.println("Cool");
}

Only ONE of the two happens.

In this lesson you will learn: how a program chooses between two paths.""",
            mcq("What does this show?", ["Hot", "Cool", "Both", "Nothing"], 0, "30 is above 25.", code='int t = 30;\nif (t > 25) {\n    System.out.println("Hot");\n} else {\n    System.out.println("Cool");\n}'),
            mcq("What does this show?", ["Cool", "Hot", "Both", "Nothing"], 0, "10 is not above 25, so else runs.", code='int t = 10;\nif (t > 25) {\n    System.out.println("Hot");\n} else {\n    System.out.println("Cool");\n}'),
            fill("Fill in the word for 'otherwise'.", 'if (age >= 18) {\n    System.out.println("Adult");\n} ___ {\n    System.out.println("Child");\n}', "else", "else is the otherwise path."),
            run("The points are 7. Show Pass if points is 5 or more, otherwise Fail.", "java", [t("Run")], ["Pass"],
                prog('int points = 7;\nif (points >= 5) {\n    System.out.println("Pass");\n} else {\n    System.out.println("Fail");\n}'), starter=MAIN,
                fallback=[r"if\s*\(", r"else"], hint='if (points >= 5) { ... } else { ... }'),
        ),
        lesson(
            "Doing it again and again (loops)",
            """To show "Hello" five times you could write five lines - but a million times is impossible. A LOOP repeats for you:

for (int i = 0; i < 5; i++) {
    System.out.println("Hello");
}

Read it as: "start i at 0; keep going while i is less than 5; add 1 to i each time". That is 5 repeats (i is 0, 1, 2, 3, 4). The lines between { } are repeated.

You can use the counter, too:

for (int i = 0; i < 3; i++) {
    System.out.println(i);
}

shows 0, 1, 2. (Programmers start counting at 0 - a funny habit you will get used to!) i++ means "add 1 to i".

In this lesson you will learn: how to repeat instructions without writing them again and again.""",
            mcq("What does a loop do?", ["Repeats instructions", "Stops the program", "Makes a choice", "Stores a value"], 0, "A loop repeats the lines inside { }."),
            mcq("How many times does this show Hi?", ["3", "2", "4", "1"], 0, "i is 0, 1, 2.", code='for (int i = 0; i < 3; i++) {\n    System.out.println("Hi");\n}'),
            mcq("What does i++ do?", ["Adds 1 to i", "Subtracts 1", "Shows i", "Resets i"], 0, "i++ means i becomes i + 1."),
            run("Show the word Hello 3 times, each on its own line, using a loop.", "java", [t("Run")], ["Hello\nHello\nHello"],
                prog('for (int i = 0; i < 3; i++) {\n    System.out.println("Hello");\n}'), starter=MAIN, fallback=[r"for\s*\("], hint='for (int i = 0; i < 3; i++) { System.out.println("Hello"); }'),
        ),
    ),
]
