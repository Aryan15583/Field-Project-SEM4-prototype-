"""JavaScript - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """console.log() is how a JavaScript program SHOWS you something. Think of it as the program talking to you - very useful for checking what your code is doing.

console.log("Hello!");        shows: Hello!
console.log(42);              shows: 42
console.log("Sum:", 2 + 3);   shows: Sum: 5

You can give it several things separated by commas - they are shown with a space between them.

Two small habits:
- A statement (one instruction) normally ends with a semicolon ;, like a full stop.
- A COMMENT is a note for people that the computer ignores. // starts a one-line comment. For many lines, wrap them in /* and */.

In this lesson you will learn: how to show values and how to leave notes in your code.""",
    "1/2": """JavaScript is a good calculator, and it uses one kind of number for both whole numbers and decimals.

7 + 3     // 10    add
7 / 2     // 3.5   divide (decimals are kept)
7 % 2     // 1     the REMAINDER (what is left over after dividing)
2 ** 3    // 8     power (2 x 2 x 2)

Remainder example: share 7 sweets between 2 friends. Each gets 3, and 1 is left over - that is 7 % 2.

There is also a toolbox called Math with handy helpers:

Math.round(2.6)    // 3   nearest whole number
Math.floor(2.9)    // 2   always round DOWN
Math.max(4, 9)     // 9   the bigger of two

Just like at school, multiplication and division happen before addition and subtraction. Use brackets to choose the order.

In this lesson you will learn: the maths signs and the Math toolbox.""",
    "1/3": """Text is called a STRING. You can write it three ways: 'single quotes', "double quotes" or `backticks`. The first two are the same.

You can join strings with +:

"Code" + "ingo"     // "Codeingo"

Backticks are special - they let you put values INSIDE the text with ${ }. This is called a template literal, and it is much tidier than lots of +:

const name = "Ada";
console.log(`Hi ${name}, 2 + 2 = ${2 + 2}`);
shows: Hi Ada, 2 + 2 = 4

Whatever is inside ${ } is worked out and put into the sentence.

Strings also know things about themselves:

"hello".length          // 5   how many characters
"hi".toUpperCase()      // "HI"

In this lesson you will learn: how to write, join and look inside text.""",
    "2/1": """A variable is a labelled box that holds a value. JavaScript has two ways to make one:

let lives = 3;          // a box whose contents CAN change
lives = lives - 1;      // fine: lives is now 2

const name = "Ada";     // a box whose contents can NEVER be replaced
name = "Bob";           // ERROR - const forbids it

const is like writing a label in permanent marker: it protects you from changing something by accident.

A good habit: start with const, and switch to let only when you really need the value to change.

(In older code you may see var. It still works but has confusing rules - avoid it.)

In this lesson you will learn: the two ways to make a variable and when to use each.""",
    "2/2": """Every value has a TYPE - the kind of thing it is. JavaScript's main types:

  number     42, 3.14        (any number)
  string     "hi"            (text)
  boolean    true, false     (yes/no)
  undefined  a variable that has no value yet
  null       "intentionally empty" - you set it on purpose
  object     { } and [ ]     (groups of things)

Why does this matter? Because the computer treats each type differently. For example 5 + 5 is 10, but "5" + "5" is "55" (text joined together).

You can ask for the type with typeof:

typeof 42        // "number"
typeof "hi"      // "string"

The difference between undefined and null: undefined means "nothing was put here yet"; null means "I deliberately put nothing here".

In this lesson you will learn: the kinds of values JavaScript has.""",
    "2/3": """Sometimes a value is the wrong type, and you must convert it. A typical case: "42" in quotes is TEXT, not a number.

Number("42")      // 42      text to number
String(42)        // "42"    number to text
parseInt("7px")   // 7       reads the number at the start of the text

Comparing values: always use THREE equal signs, ===. It checks the value AND the type:

5 === "5"    // false  (a number is not text)

The two-sign version == tries to be helpful by converting types first, which leads to surprises:

5 == "5"     // true   (surprise!)

So: use === to ask "are these the same?" and !== for "are they different?". Save yourself the confusion.

In this lesson you will learn: how to convert between types and compare safely.""",
    "3/1": """A comparison asks a yes/no question and the answer is true or false:

5 > 3        // true    is 5 bigger than 3?
5 <= 5       // true    is 5 smaller than or equal to 5?
"a" !== "b"  // true    are they different?

You can combine questions with three small signs:

&&   AND - both must be true
||   OR  - at least one must be true
!    NOT - flips true to false and false to true

Example - is someone a teenager?

age >= 13 && age <= 19

That reads: "age is 13 or more AND age is 19 or less". Both must be true.

These true/false answers are what the next lesson uses to make decisions.

In this lesson you will learn: how to ask yes/no questions and combine them.""",
    "3/2": """An if statement lets your program choose. The question goes in round brackets ( ), and the instructions to follow go in curly brackets { }.

if (temp > 25) {
  console.log("Hot");
} else if (temp > 15) {
  console.log("Nice");
} else {
  console.log("Cold");
}

Read it from the top, like a list of questions:
- IF the temperature is above 25: show Hot.
- ELSE IF it is above 15: show Nice.
- ELSE (none of the above): show Cold.

JavaScript tries each question in order and runs ONLY the first one that is true, then skips the rest.

In this lesson you will learn: how to make a program choose between several paths.""",
    "3/3": """When you compare ONE value against MANY possible answers, a long chain of if/else gets tiring. switch is a neater way:

switch (day) {
  case "sat":
  case "sun":
    console.log("Weekend");
    break;
  default:
    console.log("Weekday");
}

Read it: "look at day. If it is sat OR sun (two cases stacked together), show Weekend. For anything else (default), show Weekday."

The word break ends that case. Without it JavaScript keeps going into the next case - a classic beginner trap!

There is also a one-line shortcut for choosing between two values, called the TERNARY. It reads "condition ? value if true : value if false":

const label = age >= 18 ? "adult" : "minor";

In this lesson you will learn: two tidy ways of choosing.""",
    "4/1": """A loop repeats instructions. The for loop has three parts inside the brackets, separated by semicolons:

for (let i = 0; i < 3; i++) {
  console.log(i);
}

1. START: let i = 0 - make a counter that begins at 0.
2. CONDITION: i < 3 - keep going while this is true.
3. STEP: i++ - after each round, add 1 to the counter.

So i is 0, then 1, then 2, and when it reaches 3 the condition is false and the loop stops. It shows 0, 1, 2.

(Programmers count from 0 - a funny habit you will get used to!)

The instructions between { } are repeated each round.

In this lesson you will learn: how to repeat instructions a set number of times.""",
    "4/2": """A while loop keeps repeating AS LONG AS its question is true. You don't say how many times - it stops when the question becomes false.

let n = 3;
while (n > 0) {
  console.log(n);
  n--;
}

Step by step: n is 3 (shown), becomes 2 (shown), becomes 1 (shown), becomes 0 - and 0 > 0 is false, so it stops. It shows 3, 2, 1.

n-- means "take 1 away from n".

The golden rule: make sure something changes inside the loop so the question eventually turns false. If nothing changes, the loop never ends and the program gets stuck (an "infinite loop").

In this lesson you will learn: how to repeat until something changes.""",
    "4/3": """Two commands let you control a loop from the inside:

break     = leave the loop completely, right now.
continue  = skip the rest of this round and jump to the next.

for (let i = 1; i <= 10; i++) {
  if (i === 5) break;          // at 5, stop everything
  if (i % 2 === 0) continue;   // even? skip the log
  console.log(i);              // shows 1 and 3
}

Step by step: 1 is shown. 2 is even - skipped. 3 shown. 4 skipped. At 5 the loop stops, so nothing more is shown.

(i % 2 === 0 asks "is the remainder 0 when dividing by 2?" - that is how you test for an even number.)

In this lesson you will learn: how to stop a loop early or skip a round.""",
    "5/1": """A FUNCTION is a mini-program with a name. You write the steps once, then use it whenever you like - like a recipe card.

function greet(name) {
  return "Hi " + name;
}

console.log(greet("Ada"));    // Hi Ada

Parts:
- function says "I am defining a function".
- greet is its name.
- name in the brackets is a PARAMETER - a blank for the caller to fill in.
- return gives a result BACK to the place that called the function.

Defining does not run it. To use it, CALL it by name with a value in the brackets: greet("Ada").

If a function has no return, it gives back undefined (nothing).

In this lesson you will learn: how to write your own reusable commands.""",
    "5/2": """There is a shorter way to write functions, called an ARROW FUNCTION. It uses => (an arrow) instead of the word function:

const double = (n) => n * 2;
const add = (a, b) => a + b;

Read the first: "double is a function that takes n and gives back n times 2."

When the function is just one expression, you can leave out the curly brackets and the word return - the value is given back automatically.

For several steps, use curly brackets and write return yourself:

const greet = (name) => {
  const msg = `Hi ${name}`;
  return msg;
};

Arrow functions are very common in modern JavaScript, especially for short helpers.

In this lesson you will learn: the short way to write functions.""",
    "5/3": """SCOPE means "where a variable can be seen". A variable made inside curly brackets { } lives ONLY inside them. Outside, it does not exist:

if (true) {
  const secret = 42;
}
console.log(secret);    // ERROR: secret is not defined here

Think of { } as a room: what is in the room stays in the room. This keeps different parts of a program from interfering with each other.

Functions can also have DEFAULT values for their parameters, used when the caller gives nothing:

function greet(name = "friend") {
  return `Hi ${name}`;
}
greet();            // "Hi friend"
greet("Ada");       // "Hi Ada"

In this lesson you will learn: where variables live, and how to give parameters default values.""",
    "6/1": """An ARRAY holds many values in one box, in order. You write it in square brackets with commas between items:

const langs = ["JS", "Python", "C"];

Each item has a position number called an INDEX, starting at 0:

langs[0]                    // "JS"
langs.length                // 3   (how many items)
langs[langs.length - 1]     // "C"  (the last one)
langs[1] = "Go";            // replace the second item

Why "length - 1" for the last item? Because counting starts at 0, so the last position is one less than the count.

Arrays are what you use for shopping lists, scores, names - anything with many items.

In this lesson you will learn: how to keep many values together and pick any one.""",
    "6/2": """Arrays come with handy tools called METHODS:

const a = [3, 1, 2];
a.push(4);          // add to the END         -> [3, 1, 2, 4]
a.pop();            // remove the LAST item   -> [3, 1, 2]
a.includes(2);      // is 2 in there?         true
a.indexOf(1);       // where is 1?            position 1
a.slice(0, 2);      // a copy of a piece      [3, 1]
a.join("-");        // glue into text         "3-1-2"

To sort numbers, use a small rule that says how to compare two of them:

[...a].sort((x, y) => x - y);     // [1, 2, 3]

(The three dots ... make a copy first, because sort changes the array it is called on.)

In this lesson you will learn: how to add, remove, find and sort items in an array.""",
    "6/3": """Three powerful tools handle a whole array without you writing a loop. Each one takes a small function and applies it to every item.

const nums = [1, 2, 3, 4];

map - TRANSFORM every item into something new:
nums.map(n => n * 2);               // [2, 4, 6, 8]

filter - KEEP only the items that pass a test:
nums.filter(n => n % 2 === 0);      // [2, 4]   (the even ones)

reduce - COMBINE everything into one value:
nums.reduce((sum, n) => sum + n, 0);    // 10   (the 0 is where the total starts)

There is also forEach, which just does something with each item (like showing it).

map and filter give you a NEW array and leave the original alone - so you never lose your data by accident.

In this lesson you will learn: how to change, filter and add up arrays in one line.""",
    "7/1": """An array finds things by position. An OBJECT finds things by NAME - a bundle of related facts about one thing, like a profile card:

const user = { name: "Ada", age: 36 };

Each entry is key: value. Read a value with a dot or with square brackets:

user.name         // "Ada"
user["age"]       // 36

Change or add entries any time:

user.city = "London";     // adds a new fact
delete user.age;          // removes one

Object.keys(user) gives you a list of the names: ["name", "city"].

Use an object when one thing has several different details (name, age, city), and an array when you have many similar things.

In this lesson you will learn: how to group related facts together under names.""",
    "7/2": """An object can hold FUNCTIONS too. A function stored in an object is called a METHOD - it is something the object can DO.

Inside a method, the word this means "the object I belong to". That is how a method reads or changes the object's own data:

const counter = {
  count: 0,
  increment() {
    this.count++;
    return this.count;
  },
};

counter.increment();    // 1
counter.increment();    // 2

Read it: "counter has a number called count, and a method increment that adds 1 to its own count."

Why is this useful? It keeps data and the actions on that data together - like a real object (a kettle holds water and can boil it).

In this lesson you will learn: how objects can have their own actions.""",
    "7/3": """Two shortcuts make working with objects and arrays tidier.

DESTRUCTURING pulls values out into their own variables in one line:

const { name, age } = user;            // name and age variables from the object
const [first, second] = [10, 20];      // first is 10, second is 20

The SPREAD operator (three dots) copies things. It is great for making a changed copy without touching the original:

const copy = { ...user, age: 37 };     // same as user, but with age 37

JSON is a text format for sending data between programs - it looks like an object, but it is just text:

JSON.stringify({ a: 1 })       // '{"a":1}'     object -> text
JSON.parse('{"a":1}').a        // 1             text -> object

Whenever a website talks to a server, it usually sends JSON.

In this lesson you will learn: shortcuts for unpacking and copying data, and what JSON is.""",
    "8/1": """Strings come with many built-in tools (methods). They never change the original - they give you a NEW string:

"Hello".toLowerCase()            // "hello"
"  hi  ".trim()                  // "hi"       removes the spaces at the ends
"a,b,c".split(",")               // ["a", "b", "c"]   cuts into an array
"banana".replaceAll("a", "o")    // "bonono"
"hello".includes("ell")          // true       is that piece inside?
"hello".slice(1, 3)              // "el"       a piece: from 1, stopping before 3
"hi".repeat(3)                   // "hihihi"

You can chain them: " HELLO ".trim().toLowerCase() gives "hello".

(Positions start at 0, and a slice stops just BEFORE its end number.)

In this lesson you will learn: the most useful tools for working with text.""",
    "8/2": """Imagine you need many dogs, each with its own name that can speak. Writing an object for each is repetitive. A CLASS is a BLUEPRINT for making objects of the same kind - like a cookie cutter.

class Dog {
  constructor(name) {
    this.name = name;
  }
  speak() {
    return `${this.name} says woof`;
  }
}

const rex = new Dog("Rex");
rex.speak();       // "Rex says woof"

Parts:
- class Dog is the blueprint.
- constructor runs when you make a new one; it sets up the new dog's data (this.name is the dog's own name).
- speak is a method - something every dog can do.
- new Dog("Rex") makes one actual dog from the blueprint.

You can make as many dogs as you like, each with its own name.

In this lesson you will learn: how to make blueprints for objects.""",
    "8/3": """When something goes wrong, JavaScript THROWS an error and the program stops. try/catch lets you handle it politely - "try this; if it fails, do that instead".

try {
  JSON.parse("not json");
} catch (err) {
  console.log("Bad data:", err.name);
}

If anything inside try fails, the program jumps to catch (with the error stored in err) instead of crashing.

You can also THROW your own error when something is not acceptable:

throw new Error("Age must be positive");

Why? So the problem is reported clearly at the exact moment it happens, instead of causing a confusing failure later.

In this lesson you will learn: how to handle errors without crashing and raise your own.""",
}
