"""JavaScript - gentle 'Start here' units for people who have never seen code."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

START = [
    start_unit(
        1,
        "Start here · What is code?",
        lesson(
            "What is JavaScript?",
            """Every time a web page reacts to you - a menu that opens, a game, a like button that turns red - JavaScript is working behind the scenes.

A PROGRAM is a list of instructions for a computer. CODE is how we write those instructions. JavaScript is one of the languages we can write them in (like English and French are languages for people).

A computer is like a super-fast robot that does EXACTLY what you tell it, one instruction after another, from the top to the bottom. It never guesses what you meant.

Here is a tiny JavaScript instruction:

console.log("Hello!");

It tells the computer: "Show the message Hello!". You don't need to understand every symbol yet - we will take each piece slowly in the next lessons.

In this lesson you will learn: what JavaScript is for, and that computers follow instructions in order.""",
            mcq("What is a program?", ["A list of instructions for a computer", "A kind of screen", "A web browser", "A cable"], 0, "A program is a list of instructions."),
            mcq("In what order does a computer follow instructions?", ["One after another, from the top", "Randomly", "Bottom to top", "All at once"], 0, "It starts at the top and works down."),
            mcq("What is JavaScript mainly used for?", ["Making web pages interactive", "Printing paper", "Charging phones", "Cleaning files"], 0, "It runs in your browser and makes pages react to you."),
            order("A robot follows these instructions. Put them in the order it does them.", ["Say 'Hello'", "Say 'How are you?'", "Say 'Goodbye'"], "Top to bottom."),
        ),
        lesson(
            "Your first command: console.log",
            """To make the computer show something, we use console.log.

console.log("Hello!");

When it runs, you see:

Hello!

The parts:
- console.log is the command - it means "show this".
- The round brackets ( ) hold what you want to show.
- The quote marks " " tell the computer "this is text".
- The semicolon ; at the end is like a full stop - it ends the instruction.

You only see the text inside the quotes - the quotes are not shown.

Several instructions run from top to bottom:

console.log("Hello!");
console.log("I am learning JavaScript.");

The "console" is just a place where a program writes messages. In this course the Output box under your code is the console.

In this lesson you will learn: how to make the computer show a message.""",
            mcq("What does console.log do?", ["Shows something in the console (the output)", "Saves a file", "Deletes text", "Prints on paper"], 0, "console.log shows a message."),
            mcq("What will this show?", ["Good morning", "\"Good morning\"", "console.log", "Nothing"], 0, "The quotes only mark the text. They are not shown.", code='console.log("Good morning");'),
            mcq("How many lines will this show?", ["2", "1", "3", "0"], 0, "Each console.log shows one line.", code='console.log("One");\nconsole.log("Two");'),
            fill("Fill in the missing word.", 'console.___("Hi!");', "log", "The command is console.log."),
            run("Write one line that shows exactly: Hello, World!", "javascript", [t("Run")], ["Hello, World!"], 'console.log("Hello, World!");', starter="",
                hint='console.log("Hello, World!");'),
        ),
        lesson(
            "Words and numbers",
            """Computers treat words and numbers differently.

TEXT must be wrapped in quote marks:
console.log("Room 5");     shows Room 5

NUMBERS have no quotes:
console.log(5);            shows 5
console.log(2.5);          shows 2.5

The computer can do maths with numbers:

console.log(2 + 3);        shows 5

But with quotes it is just text, so nothing is calculated:

console.log("2 + 3");      shows 2 + 3

Programmers call text a STRING (a string of letters) and numbers NUMBERS. You don't need the names yet - just remember: quotes mean text, no quotes mean a number.

In this lesson you will learn: the difference between text and numbers.""",
            mcq("Which one is text?", ["\"Hello\"", "42", "3.14", "7"], 0, "Anything in quotes is text."),
            mcq("What does this show?", ["5", "2 + 3", "23", "An error"], 0, "No quotes: the computer adds 2 + 3.", code="console.log(2 + 3);"),
            mcq("What does this show?", ["2 + 3", "5", "23", "An error"], 0, "In quotes it is only text.", code='console.log("2 + 3");'),
            fill("Make JavaScript add the numbers.", "console.log(4 ___ 6);", "+", "+ adds."),
            run("Show the result of 10 + 5 (it should show 15).", "javascript", [t("Run")], ["15"], "console.log(10 + 5);", hint="No quotes: console.log(10 + 5);"),
        ),
        lesson(
            "Boxes with names (variables)",
            """Often we want the computer to REMEMBER something. We use a VARIABLE: a box with a name that holds a value.

let age = 12;

Read it as: "make a box called age and put 12 in it". The word let means "make a new box". The = sign here means "store this value" - it is not the "equals" from maths.

Now use the box by writing its name:

console.log(age);      shows 12

You can put something new in the box any time:

let age = 12;
age = 13;              the box now holds 13
console.log(age);      shows 13

Boxes can hold text too:

let name = "Maya";
console.log(name);     shows Maya

Notice: no quotes around name in console.log(name) - we want what is INSIDE the box.

(You may also see const - it makes a box whose value never changes. We will meet it later.)

In this lesson you will learn: how to store a value with a name and use it again.""",
            mcq("What does let age = 12; do?", ["Makes a box called age holding 12", "Shows 12", "Deletes age", "Compares things"], 0, "let makes a new box and = stores the value."),
            mcq("What does this show?", ["13", "12", "age", "Nothing"], 0, "The box first holds 12, then 13.", code="let age = 12;\nage = 13;\nconsole.log(age);"),
            mcq("What does this show?", ["Maya", "name", "\"Maya\"", "An error"], 0, "console.log(name) shows what is inside the box.", code='let name = "Maya";\nconsole.log(name);'),
            fill("Store 50 in a box called score.", "let score ___ 50;", "=", "= stores a value."),
            run("Store 7 in a variable called number and show it.", "javascript", [t("Run")], ["7"], "let number = 7;\nconsole.log(number);", require=[r"number\s*=", r"console\.log"],
                hint="let number = 7; then console.log(number);"),
        ),
    ),
    start_unit(
        2,
        "Start here · Making the computer think",
        lesson(
            "Doing maths",
            """JavaScript is a super calculator:

+   add            console.log(8 + 2);    shows 10
-   subtract       console.log(8 - 2);    shows 6
*   multiply       console.log(8 * 2);    shows 16   (a star, not ×)
/   divide         console.log(8 / 2);    shows 4

Just like at school, multiplication and division happen BEFORE addition and subtraction. Round brackets let you choose what goes first:

console.log(2 + 3 * 4);       shows 14
console.log((2 + 3) * 4);     shows 20

Maths works with variables too:

let price = 5;
let amount = 3;
console.log(price * amount);  shows 15

In this lesson you will learn: how to add, subtract, multiply and divide.""",
            mcq("Which sign multiplies?", ["*", "x", "×", "^"], 0, "Multiplication is written with a star."),
            mcq("What does this show?", ["14", "20", "10", "24"], 0, "3 * 4 first = 12, then + 2.", code="console.log(2 + 3 * 4);"),
            mcq("What does this show?", ["20", "14", "9", "60"], 0, "Brackets first: 5 * 4.", code="console.log((2 + 3) * 4);"),
            mcq("What does this show?", ["15", "8", "53", "An error"], 0, "5 * 3.", code="let price = 5;\nlet amount = 3;\nconsole.log(price * amount);"),
            run("A pack has 6 pencils and you buy 4 packs. Show how many pencils you have (24).", "javascript", [t("Run")], ["24"], "console.log(6 * 4);", hint="console.log(6 * 4);"),
        ),
        lesson(
            "Yes or no questions (true and false)",
            """Computers are great at yes-or-no questions. The answer is always true or false.

console.log(5 > 3);       shows true    (is 5 bigger than 3? yes)
console.log(5 < 3);       shows false   (is 5 smaller than 3? no)
console.log(5 === 5);     shows true    (are they the same? yes)
console.log(5 !== 5);     shows false   (are they different? no)

The signs that ask questions:

>     is bigger than
<     is smaller than
>=    is bigger than or equal to
<=    is smaller than or equal to
===   is the same as   (THREE equal signs!)
!==   is not the same as

One = stores a value. To ASK whether two things are the same we use three: ===.

In this lesson you will learn: how to ask the computer a yes-or-no question.""",
            mcq("What does this show?", ["true", "false", "7", "An error"], 0, "7 is bigger than 3.", code="console.log(7 > 3);"),
            mcq("What does this show?", ["false", "true", "10", "An error"], 0, "10 is not smaller than 4.", code="console.log(10 < 4);"),
            mcq("Which sign asks 'are these two the same?'", ["===", "=", "!==", "=>"], 0, "Three equal signs ask; one equal sign stores."),
            fill("Ask whether 3 is smaller than 9.", "console.log(3 ___ 9);", "<", "< means smaller than."),
        ),
        lesson(
            "If this, then that",
            """Now the computer can make a DECISION with the word if:

let weather = "rain";
if (weather === "rain") {
    console.log("Take an umbrella");
}

Read it as: "IF the weather is rain, THEN show: Take an umbrella."

The question goes in round brackets. The instructions to do go between curly brackets { }. If the answer is false, the computer skips them.

To say what to do OTHERWISE, add else:

if (weather === "rain") {
    console.log("Take an umbrella");
} else {
    console.log("Wear sunglasses");
}

Only ONE of the two happens.

In this lesson you will learn: how a program chooses between two paths.""",
            mcq("What does this show?", ["Take an umbrella", "Wear sunglasses", "Both", "Nothing"], 0, "The weather is rain, so the first path runs.",
                code='let weather = "rain";\nif (weather === "rain") {\n    console.log("Take an umbrella");\n} else {\n    console.log("Wear sunglasses");\n}'),
            mcq("What does this show?", ["Wear sunglasses", "Take an umbrella", "Both", "Nothing"], 0, "The weather is not rain, so else runs.",
                code='let weather = "sun";\nif (weather === "rain") {\n    console.log("Take an umbrella");\n} else {\n    console.log("Wear sunglasses");\n}'),
            fill("Fill in the word for 'otherwise'.", 'if (age >= 18) {\n    console.log("Adult");\n} ___ {\n    console.log("Child");\n}', "else", "else is the otherwise path."),
            run("The temperature is 30. Show Hot if it is above 25, otherwise show Cool.", "javascript", [t("Run")], ["Hot"],
                'let temperature = 30;\nif (temperature > 25) {\n    console.log("Hot");\n} else {\n    console.log("Cool");\n}', starter="let temperature = 30;\n", require=[r"if", r"else"],
                hint='if (temperature > 25) { ... } else { ... }'),
        ),
        lesson(
            "Doing it again and again (loops)",
            """To show "Hello" five times you could write five lines - but a million times is impossible. A LOOP repeats for you:

for (let i = 0; i < 5; i++) {
    console.log("Hello");
}

Read it as: "start i at 0; keep going while i is less than 5; add 1 to i each time". That makes 5 repeats (i is 0, 1, 2, 3, 4). The instructions between { } are repeated.

You can use the counter i too:

for (let i = 0; i < 3; i++) {
    console.log(i);
}

shows 0, then 1, then 2. (Programmers start counting at 0 - a funny habit you will get used to!)

i++ is a short way of saying "add 1 to i".

In this lesson you will learn: how to repeat instructions without writing them again and again.""",
            mcq("What does a loop do?", ["Repeats instructions", "Stops the program", "Makes a choice", "Stores a value"], 0, "A loop repeats what is inside { }."),
            mcq("How many times does this show Hi?", ["3", "2", "4", "1"], 0, "i is 0, 1, 2 - three times.", code='for (let i = 0; i < 3; i++) {\n    console.log("Hi");\n}'),
            mcq("What does i++ do?", ["Adds 1 to i", "Subtracts 1", "Shows i", "Resets i"], 0, "i++ means i becomes i + 1."),
            run("Show the word Hello 3 times, each on its own line, using a loop.", "javascript", [t("Run")], ["Hello\nHello\nHello"],
                'for (let i = 0; i < 3; i++) {\n    console.log("Hello");\n}', require=[r"for"], hint='for (let i = 0; i < 3; i++) { console.log("Hello"); }'),
        ),
        lesson(
            "Lists: many things in one place",
            """A LIST (called an ARRAY in JavaScript) holds many values in one box, in order:

let friends = ["Ana", "Ben", "Cy"];

Each item has a position number called an INDEX. The first is 0:

console.log(friends[0]);    shows Ana
console.log(friends[1]);    shows Ben

Handy things:

friends.length             how many items? (3)
friends.push("Dee");       add Dee to the end

A loop can visit every item:

for (let i = 0; i < friends.length; i++) {
    console.log("Hi " + friends[i]);
}

The + joins two pieces of text.

In this lesson you will learn: how to keep many things in one list and go through them.""",
            mcq("What is friends[0]?", ["Ana", "Ben", "Cy", "0"], 0, "Index 0 is the first item.", code='let friends = ["Ana", "Ben", "Cy"];'),
            mcq("What is friends.length for three names?", ["3", "2", "0", "Ana"], 0, ".length tells you how many items there are."),
            fill("Add \"Dee\" to the end of the list.", 'let friends = ["Ana", "Ben"];\nfriends.___("Dee");', "push", "push adds to the end."),
            run("Make a list called fruits with apple and pear, then show each fruit on its own line using a loop.", "javascript", [t("Run")], ["apple\npear"],
                'let fruits = ["apple", "pear"];\nfor (let i = 0; i < fruits.length; i++) {\n    console.log(fruits[i]);\n}', require=[r"fruits", r"for"], hint="Loop with i from 0 up to fruits.length."),
        ),
    ),
]
