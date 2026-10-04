"""TypeScript - gentle 'Start here' unit: what types are and why they help, in everyday words."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

START = [
    start_unit(
        1,
        "Start here · What are types?",
        lesson(
            "JavaScript with labels",
            """If you have never coded: a PROGRAM is a list of instructions for a computer, and JavaScript is a popular language for writing them. (If JavaScript is new to you, the JavaScript course is a friendly place to start - but you can also learn TypeScript directly here.)

TypeScript is JavaScript with LABELS added. A label says what kind of thing each box holds.

Imagine moving house. You write on each box: "KITCHEN", "BOOKS", "FRAGILE". Now nobody puts a book in the kitchen box by mistake.

TypeScript does that for your code:

let age: number = 30;

This says: "age is a box for a NUMBER". If you later try to put text in it, TypeScript warns you BEFORE the program runs:

age = "thirty";   // warning: this box is for numbers!

The labels disappear when the program finally runs, so they cost nothing - they are just there to catch mistakes early.

In this lesson you will learn: what TypeScript adds to JavaScript, and why labels help.""",
            mcq("What does TypeScript add to JavaScript?", ["Labels (types) that catch mistakes early", "A new screen", "More colours", "Faster internet"], 0, "Types are labels that describe what each value is."),
            mcq("In 'let age: number = 30;' what does ': number' mean?", ["age is a box for numbers", "age is text", "age is empty", "age is a list"], 0, "It labels the box as number-only."),
            mcq("When does TypeScript warn you about a wrong type?", ["Before the program runs", "Never", "After the user sees it", "Only on Fridays"], 0, "That is the whole point: catch mistakes early."),
        ),
        lesson(
            "The basic labels: string, number, boolean",
            """There are three labels you will use all the time:

string    - text, written in quotes:           let name: string = "Maya";
number    - any number (whole or decimal):     let price: number = 4.5;
boolean   - only true or false:                let isOpen: boolean = true;

TypeScript can often GUESS the label from the value, so you can skip writing it:

let city = "Paris";       // TypeScript knows this is a string

If you do write a label and the value doesn't match, you get a warning:

let year: number = "2024";   // warning: "2024" is text, not a number

Quotes are the clue: "2024" with quotes is text; 2024 without quotes is a number.

In this lesson you will learn: the three most common types.""",
            mcq("Which label fits the value true?", ["boolean", "string", "number", "list"], 0, "true and false are boolean values."),
            mcq("Which label fits \"hello\"?", ["string", "number", "boolean", "date"], 0, "Anything in quotes is a string."),
            mcq("Which line gives a TypeScript warning?", ["let year: number = \"2024\";", "let year: number = 2024;", "let year = 2024;", "let year: string = \"2024\";"], 0, "\"2024\" is text, but the label says number."),
            fill("Label this box so it only holds text.", 'let name: ___ = "Maya";', "string", "string is the label for text."),
            run("Make a number called score with the value 10, then show it. Use the label : number.", "typescript", [t("Run")], ["10"], "const score: number = 10;\nconsole.log(score);",
                require=[r"score\s*:\s*number"], hint="const score: number = 10;"),
        ),
        lesson(
            "Labels for lists and functions",
            """Lists get a label too. A list of numbers is written number[]:

let scores: number[] = [10, 20, 30];

Now TypeScript refuses to let you add text into it by mistake.

A FUNCTION is a small reusable machine: you give it something, it gives something back. You label what goes IN and what comes OUT:

function double(n: number): number {
    return n * 2;
}

Read it as: "double takes a number n and gives back a number". The part after the brackets (: number) labels what comes back.

console.log(double(4));   shows 8

If you called double("hello"), TypeScript would warn you straight away - you gave it text where a number was expected.

In this lesson you will learn: how to label lists and function inputs and outputs.""",
            mcq("How do you label a list of text values?", ["string[]", "string", "list", "text"], 0, "Put [] after the type of the items."),
            mcq("In 'function double(n: number): number', what does the last ': number' label?", ["What the function gives back", "What it takes in", "Its name", "Nothing"], 0, "The label after the brackets is the output type."),
            mcq("What does double(4) give?", ["8", "4", "2", "16"], 0, "4 * 2.", code="function double(n: number): number {\n    return n * 2;\n}"),
            run("Write a function add(a: number, b: number): number that returns the sum, then show add(2, 3).", "typescript", [t("Run")], ["5"],
                "function add(a: number, b: number): number {\n    return a + b;\n}\nconsole.log(add(2, 3));", require=[r"add\s*\(\s*a\s*:\s*number"], hint="return a + b;"),
        ),
    ),
]
