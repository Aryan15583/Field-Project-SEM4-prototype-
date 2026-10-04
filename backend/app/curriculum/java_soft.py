"""Java - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """Every Java program sits inside a "frame". It always looks the same:

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello!");
    }
}

You don't need to understand every word yet. Here is the idea:
- class Main is the container for your program - like a box with a name.
- main is the START POINT: when you run the program, Java begins with the first line inside main and works down.
- System.out.println("Hello!"); is the instruction that shows the message Hello!.

Two rules: every instruction ends with a semicolon ;, and groups of instructions are wrapped in curly brackets { }.

For now, treat the frame like a template: copy it, then write your own instructions where println is.

In this lesson you will learn: the frame every Java program uses, and where your instructions go.""",
    "1/2": r"""You already know System.out.println shows text and then moves to a NEW LINE. There is a sibling, System.out.print, that shows text and STAYS on the same line:

System.out.print("A");
System.out.print("B");
System.out.println("C");      // shows ABC, then moves to a new line

Comments are notes for people (the computer ignores them):

// a one-line note
/* a note that
   spans many lines */

Special characters inside text start with a backslash \ (called an "escape"):

\n    a new line
\t    a tab (a wide gap)
\"    a quote mark inside the text

Example: System.out.println("Line 1\nLine 2"); shows two lines.

In this lesson you will learn: print versus println, comments, and special characters.""",
    "1/3": """Java is a calculator. The signs are + - * / and % (the REMAINDER - what is left over after dividing).

System.out.println(7 + 3);    // 10
System.out.println(7 % 2);    // 1     (7 = 3 x 2 + 1)

A famous surprise: when BOTH numbers are whole numbers (ints), division throws away the decimals:

System.out.println(7 / 2);    // 3     (not 3.5!)

To keep the decimals, make at least one number a decimal by writing .0:

System.out.println(7.0 / 2);  // 3.5

Java also has a toolbox called Math for bigger jobs:

Math.pow(2, 3)     // 8.0    2 to the power 3
Math.sqrt(16)      // 4.0    square root

(They give decimals, which is why you see .0.)

In this lesson you will learn: Java's maths signs and the whole-number division surprise.""",
    "2/1": """In Java, every variable (a labelled box) must say what KIND of thing it holds. Java checks this strictly.

int age = 20;           // int: whole numbers
double price = 9.99;    // double: numbers with decimals
char grade = 'A';       // char: ONE character, in single quotes
boolean ok = true;      // boolean: true or false
long big = 9000000000L; // long: a very large whole number (note the L)

Think of boxes of different shapes: a box made for numbers will not accept text. If you try, Java refuses before the program even runs - that protects you from mistakes.

int can hold up to about 2 billion. For bigger numbers, use long.

In this lesson you will learn: the basic kinds of values and how to make a variable for each.""",
    "2/2": """Text in Java is a String (with a capital S). Join strings with +:

String name = "Ada";
String msg = "Hi " + name + "!";      // Hi Ada!

A String knows things about itself. You ask with a dot:

name.length()          // 3        how many characters
name.toUpperCase()     // "ADA"
name.charAt(0)         // 'A'      the character at position 0 (counting starts at 0)

An important trap: to check whether two strings contain the same text, use .equals(), NOT ==:

name.equals("Ada")     // true

(== checks whether they are literally the same object in memory, which is not what you usually want.)

In this lesson you will learn: how to work with text, and how to compare it properly.""",
    "2/3": """Sometimes you must change a value from one kind to another. This is called CASTING - you put the new kind in brackets in front:

double d = 9.8;
int i = (int) d;                // 9   (the decimals are chopped off, not rounded)
double avg = (double) 7 / 2;    // 3.5

Converting text to a number is different - use the helpers:

Integer.parseInt("42")          // 42
Double.parseDouble("3.5")       // 3.5

A CONSTANT is a value that must never change. Mark it with final and write its name in CAPITALS:

final double PI = 3.14159;

If you try to change it later, Java gives an error.

In this lesson you will learn: how to convert between kinds of numbers, turn text into numbers, and make constants.""",
    "3/1": """if lets your program choose. The question goes in round brackets ( ), and the instructions go in curly brackets { }:

if (score >= 50) {
    System.out.println("Pass");
} else if (score >= 40) {
    System.out.println("Almost");
} else {
    System.out.println("Fail");
}

Read it from the top, like a list of questions:
- IF the score is 50 or more: show Pass.
- ELSE IF it is 40 or more: show Almost.
- ELSE (none of the above): show Fail.

Java tries each question in order and runs only the first one that is true.

The comparison signs: == (equal) != (different) < > <= >=

In this lesson you will learn: how to make your program choose between paths.""",
    "3/2": """One question is sometimes not enough. Three small signs combine questions:

&&   AND - BOTH must be true
||   OR  - AT LEAST ONE must be true
!    NOT - flips true to false

if (age >= 13 && age <= 19) { ... }
Reads: "age is 13 or more AND 19 or less" - a teenager.

if (day.equals("Sat") || day.equals("Sun")) { ... }
Reads: "the day is Saturday OR Sunday" - the weekend.

Real-life examples:
- "You can ride if you are tall enough AND have a ticket" - and.
- "Take a coat if it is cold OR raining" - or.
- "Go out if it is NOT raining" - not.

In this lesson you will learn: how to combine yes/no questions.""",
    "3/3": """When one value could be MANY different things, a long chain of if/else is tiring. switch is neater: it looks at one value and picks the matching branch.

String name = switch (day) {
    case 1 -> "Mon";
    case 2 -> "Tue";
    default -> "Other";
};

Read it: "look at day. If it is 1, the answer is Mon. If it is 2, Tue. For anything else (default), Other."

This is the modern arrow form. There is an older form, with a colon and the word break:

case 1:
    ...
    break;

In the older form, break is needed to stop - otherwise Java keeps running into the next case, which is called fall-through (a classic beginner trap).

In this lesson you will learn: a tidy way to choose between many possibilities.""",
    "4/1": """A while loop repeats AS LONG AS its question is true:

int n = 3;
while (n > 0) {
    System.out.println(n);
    n--;
}

Step by step: n is 3 (shown) then becomes 2 (shown) then 1 (shown) then 0 - the question n > 0 is now false, so the loop stops. It shows 3, 2, 1.

n-- means "take 1 away from n". n++ means "add 1 to n".

The golden rule: change something inside the loop so the question eventually turns false. If nothing changes, the loop never ends and the program gets stuck - an "infinite loop".

In this lesson you will learn: how to repeat instructions while something is true.""",
    "4/2": """A for loop packs the three parts of a counting loop on one line:

for (int i = 1; i <= 5; i++) {
    System.out.println(i);
}

1. START: int i = 1 - make a counter that begins at 1.
2. CONDITION: i <= 5 - keep going while this is true.
3. STEP: i++ - after each round, add 1.

It shows 1, 2, 3, 4, 5.

Variations:
- Count down: for (int i = 10; i > 0; i--)
- Jump in 2s: for (int i = 0; i < 10; i += 2)   (i += 2 means "add 2 to i")

Use for when you know how many times to repeat; use while when you are waiting for something to change.

In this lesson you will learn: how to repeat a set number of times.""",
    "4/3": """Loops can go INSIDE other loops. The inner loop runs completely for each round of the outer loop - like a clock where the minute hand goes all the way round for each step of the hour hand.

for (int row = 1; row <= 3; row++) {
    for (int col = 1; col <= row; col++) {
        System.out.print("*");
    }
    System.out.println();
}

This draws a triangle:
*
**
***

Row 1 prints one star, row 2 prints two, row 3 prints three. After each row, println() starts a new line.

Two control commands:
- break leaves the innermost loop immediately.
- continue skips the rest of this round and goes to the next one.

In this lesson you will learn: how to put loops inside loops to make patterns.""",
    "5/1": """A METHOD is a mini-program with a name that you can use again and again - like a recipe card. (In some languages these are called functions.)

static void greet(String name) {
    System.out.println("Hi " + name);
}

Parts:
- static - for now, always write this for methods inside Main.
- void - this method does not give anything back.
- greet - its name.
- (String name) - a PARAMETER: a blank that the caller fills in.
- The lines in { } are what it does.

Defining a method does not run it. To USE it, CALL it from main:

greet("Ada");     // Hi Ada

Why? You write the steps ONCE and reuse them anywhere. If you need to fix something, you fix it in one place.

In this lesson you will learn: how to write your own reusable commands.""",
    "5/2": """A method can hand a result BACK with return. The type of the result goes before the method's name:

static int square(int n) {
    return n * n;
}

int s = square(5);        // s is now 25

Read the first line: "square takes a whole number n and gives back a whole number."

A yes/no method returns a boolean:

static boolean isEven(int n) { return n % 2 == 0; }

Compare: println SHOWS a value to the person; return GIVES it back to the program, which can then store it or calculate with it.

In this lesson you will learn: how methods take values in and send a result back.""",
    "5/3": """Java lets you give several methods the SAME NAME, as long as their parameters are different. This is called OVERLOADING.

static int area(int side) { return side * side; }          // a square
static int area(int w, int h) { return w * h; }            // a rectangle

area(4)       // 16   (one number -> the square version)
area(3, 5)    // 15   (two numbers -> the rectangle version)

Java looks at the values you pass and picks the right method automatically.

Why is it useful? You can use one natural name for the same idea ("area") instead of inventing areaSquare, areaRectangle and so on.

In this lesson you will learn: how to reuse a name for similar methods.""",
    "6/1": """An ARRAY holds a fixed number of values, all of the same kind, in a row of numbered boxes. The numbering (the INDEX) starts at 0.

int[] nums = {4, 8, 15};
nums[0]         // 4      the first
nums[1] = 99;   // replace the second one
nums.length     // 3      how many (no brackets after length!)

Make an empty array of a certain size:

int[] empty = new int[5];     // five boxes, each holding 0

The valid positions are 0 up to length - 1. Asking for nums[3] in a 3-item array is an error, because positions are 0, 1, 2.

An array's size can NOT change once it is created. (The next lessons show a flexible list.)

In this lesson you will learn: how to store many values of one kind and use any one.""",
    "6/2": """To do something with every item of an array, use a loop.

Use a counting loop when you need the POSITION as well:

for (int i = 0; i < nums.length; i++) {
    System.out.println(i + ": " + nums[i]);
}

Use the "for-each" loop when you only care about the values - it is shorter and safer:

int sum = 0;
for (int n : nums) {
    sum += n;
}

Read for (int n : nums) as "for each number n in nums". sum += n means "add n to sum".

In this lesson you will learn: two ways to go through an array.""",
    "6/3": """An array has a fixed size. An ArrayList is a FLEXIBLE list that grows and shrinks.

import java.util.ArrayList;

ArrayList<String> names = new ArrayList<>();
names.add("Ada");              // put on the end
names.add("Bo");
names.get(0);                  // "Ada"    get by position
names.size();                  // 2        how many
names.remove("Bo");            // take it out
names.contains("Ada");         // true     is it in there?

The part in angle brackets <String> says what the list holds. For numbers you write <Integer> (not int) - the "wrapper" version of int that lists need.

The import line at the top brings in the ArrayList tool.

In this lesson you will learn: how to use a list that can grow.""",
    "7/1": """So far you have used values like numbers and text. A CLASS lets you create your OWN kind of thing. It is a blueprint (like the plan for a house), and an OBJECT is one real thing built from it.

class Dog {
    String name;
    void bark() {
        System.out.println(name + " says woof");
    }
}

The blueprint says: every Dog has a name and can bark. To build a real dog, use new:

Dog d = new Dog();
d.name = "Rex";
d.bark();         // Rex says woof

The dot (d.name, d.bark()) means "the name of THIS dog", "make THIS dog bark". You can build many dogs, each with its own name.

(Only one class per file may be marked public; the others are written without it.)

In this lesson you will learn: how to make blueprints and build objects from them.""",
    "7/2": """Setting up each new object by hand (d.name = ...) is tiring. A CONSTRUCTOR is a special method that runs automatically when you build an object, and sets it up. It has the same name as the class and no return type.

class Point {
    int x, y;
    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

Point p = new Point(3, 4);

Inside, this means "the object being built". this.x is the object's own x field; plain x is the value that was passed in. So this.x = x means "store the incoming x in my x".

Now every Point is created with its x and y already set - no half-finished objects.

In this lesson you will learn: how to set up an object the moment it is created.""",
    "7/3": """If anyone can change an object's data directly, mistakes happen: someone could set a bank balance to -1000. ENCAPSULATION means hiding the data and letting the outside world use only controlled methods.

class Account {
    private double balance;
    public double getBalance() { return balance; }
    public void deposit(double amt) {
        if (amt > 0) balance += amt;
    }
}

- private means "only this class may touch it".
- public means "anyone may use it".
- getBalance() is a GETTER - it lets people read the balance.
- deposit() is controlled - it refuses negative amounts.

Now nobody can set a negative balance directly. Think of a bank: you can't walk into the vault, you go through the teller.

In this lesson you will learn: how to protect data inside an object.""",
    "8/1": """INHERITANCE lets one class build on another, so you don't write the same things twice. The new class EXTENDS the old one and gets all its fields and methods for free.

class Animal {
    String name;
    String sound() { return "..."; }
}

class Cat extends Animal {
    @Override
    String sound() { return "Meow"; }
}

A Cat IS an Animal (so it has a name) and it REPLACES (overrides) the sound method with its own version. @Override is a safety label: Java checks you really are replacing something.

Because a Cat is an Animal, you can store it in an Animal variable:

Animal a = new Cat();

This is very useful: you can treat many different animals the same way.

In this lesson you will learn: how a class can inherit from another and change its behaviour.""",
    "8/2": """An INTERFACE is a PROMISE: a list of methods a class agrees to provide, without saying how.

interface Greeter {
    String greet(String name);
}

class Friendly implements Greeter {
    public String greet(String name) {
        return "Hi " + name + "!";
    }
}

Greeter says "anything that is a Greeter can greet(name)". Friendly implements (keeps) the promise by writing the method.

Why? Other code can just ask for "a Greeter" without caring which exact class it is - you can swap in different ones later.

A class can extend only ONE other class, but it can implement MANY interfaces.

In this lesson you will learn: how to describe what a class can do without describing how.""",
    "8/3": """Things go wrong while a program runs: the user types letters instead of a number, or you divide by zero. Java raises an EXCEPTION and the program stops. try/catch lets you handle it politely:

try {
    int n = Integer.parseInt(text);
    System.out.println(100 / n);
} catch (NumberFormatException e) {
    System.out.println("Not a number");
} catch (ArithmeticException e) {
    System.out.println("Can't divide by zero");
}

Read it: "TRY this. If the text is not a number, do the first catch. If you divide by zero, do the second."

You can also raise your own error when something is not acceptable:

throw new IllegalArgumentException("Bad age");

Why? So the problem is reported clearly where it happens, instead of causing confusing trouble later.

In this lesson you will learn: how to handle errors without crashing, and raise your own.""",
}
