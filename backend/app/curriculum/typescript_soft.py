"""TypeScript - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """TypeScript is JavaScript with LABELS. A label (called a TYPE) says what kind of thing a variable holds - number, text, yes/no.

Imagine labelled moving boxes: a box marked "BOOKS" should not get kitchen plates. TypeScript is the person who stops you:

let age: number = 30;
age = "thirty";      // ERROR: "thirty" is text, but age is labelled as a number

The big benefit: the mistake is caught BEFORE the program runs, while you are still typing - not later when a user hits the bug.

When the program is finally built, the labels are removed, so they cost nothing. They only exist to help you.

In these lessons, a type error stops your program from running, exactly like in a real project.

In this lesson you will learn: what types are and why catching mistakes early is so valuable.""",
    "1/2": """The basic labels (types) are:

string      text              "hello"
number      any number        42, 3.14
boolean     true or false
null, undefined   two kinds of "nothing" (empty on purpose / not set yet)

You often don't have to write the label - TypeScript is smart and WORKS IT OUT from the value. This is called INFERENCE:

let name = "Ada";     // TypeScript decides: this is a string
name = 42;            // ERROR - you already said it holds text

Write the label yourself when you create a variable with no value yet, or when you want to be clear:

let total: number;
total = 0;

Two special types to know:
- any turns the checking OFF - avoid it, it defeats the purpose.
- unknown means "could be anything, check before using" - the safe choice.

In this lesson you will learn: the basic types and when TypeScript guesses them for you.""",
    "1/3": """A list gets a label for what is INSIDE it. number[] means "a list of numbers":

const scores: number[] = [90, 85];
scores.push("A");       // ERROR: "A" is text, but this list is for numbers

Every item must match the label.

A TUPLE is a list with a FIXED length where each position has its own type - perfect for a pair or small record:

const point: [number, number] = [3, 4];
const entry: [string, number] = ["Ada", 36];     // text first, then a number

You can unpack it into named variables:

const [name, age] = entry;      // name is a string, age is a number

Use an array for many items of the same kind; use a tuple for a small fixed group of different kinds.

In this lesson you will learn: how to label lists and fixed-size groups.""",
    "2/1": """A function is a little machine: values go IN (parameters) and a value comes OUT (the return value). In TypeScript you label both.

function add(a: number, b: number): number {
  return a + b;
}

Read it: "add takes a number a and a number b, and gives back a number." The part after the brackets (: number) labels what comes OUT.

Arrow function version:

const greet = (name: string): string => `Hi ${name}`;

TypeScript now protects every call: add("1", 2) is an error (text instead of a number), and add(1) is an error too (a number is missing).

If a function gives back nothing, label it void.

In this lesson you will learn: how to label what goes into and comes out of a function.""",
    "2/2": """Sometimes a parameter is optional, has a default, or there can be any number of them.

OPTIONAL - add a question mark. The value may be missing (then it is undefined):

function greet(name: string, greeting?: string) {
  return `${greeting ?? "Hello"}, ${name}!`;
}

(?? means "use this value, or the one on the right if it is missing".)

DEFAULT - give it a value to use when none is passed:

function pad(text: string, width = 10) { ... }

REST - three dots collect any number of values into a list:

function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}
sum(1, 2, 3);     // 6

One rule: optional parameters must come AFTER the required ones.

In this lesson you will learn: optional, default and "any number of" parameters.""",
    "2/3": """In JavaScript a function is a value, like a number or text - you can store it in a variable or hand it to another function. So functions have TYPES too. A function type is written like an arrow:

type MathOp = (a: number, b: number) => number;
const mul: MathOp = (a, b) => a * b;

Read the type: "takes two numbers, gives back a number."

A function that RECEIVES a function is very common. The one it receives is called a CALLBACK:

function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}
applyTwice((n) => n + 3, 1);     // 1 -> 4 -> 7

TypeScript guesses callback parameter types for you when it can (for example inside map and filter), so you often don't have to write them.

In this lesson you will learn: how to describe functions as types and pass them around.""",
    "3/1": """When you have an object with specific details, an INTERFACE describes its SHAPE - a checklist of what must be there.

interface User {
  id: number;
  name: string;
  email: string;
}

const u: User = { id: 1, name: "Ada", email: "ada@example.com" };

TypeScript now checks that the object matches the checklist:
- a missing property is an error,
- an extra unknown property is an error,
- a property with the wrong type is an error.

Think of a form with required boxes - you can't submit it half-filled.

You can use an interface for function parameters and return values too, so functions can say exactly what kind of object they expect.

In this lesson you will learn: how to describe the exact shape of an object.""",
    "3/2": """Not every property has to be required, and some should never change.

interface Profile {
  readonly id: number;    // can't be changed after the object is made
  name: string;
  bio?: string;           // the ? makes it OPTIONAL
}

const p: Profile = { id: 1, name: "Ada" };    // fine: bio can be left out
p.id = 2;                                     // ERROR: id is read-only

An optional property may be missing, so reading it gives undefined. Reading something inside it could crash, so use ?. - the "safe dot":

console.log(p.bio?.length);     // undefined (no crash) if bio is missing

For lists that must not change, use readonly: a readonly number[] cannot be added to.

In this lesson you will learn: optional properties and values that can't be changed.""",
    "3/3": """A TYPE ALIAS gives a name to any type, so you don't repeat long descriptions:

type ID = number | string;                   // "a number or a text"
type Point = { x: number; y: number };
type Pair<T> = [T, T];                       // a pair of the same kind of thing

You can build bigger types from smaller ones.

Interfaces can EXTEND each other - the new one has everything the old one had, plus more:

interface Animal { name: string }
interface Dog extends Animal { breed: string }      // Dog has name AND breed

Type aliases combine with & ("and"), called an intersection - the result has all the parts:

type Timestamped = { createdAt: string };
type Post = Point & Timestamped;                     // x, y AND createdAt

In this lesson you will learn: how to name types and combine them.""",
    "4/1": """A UNION type says "this can be ONE of these types". You write it with a vertical bar |, which you can read as "or":

let id: number | string;
id = 42;        // fine
id = "A-42";    // fine
id = true;      // ERROR: not a number or a string

A catch: with a union, you can only do things that work for ALL the options. id.toUpperCase() is an error, because numbers have no toUpperCase. First you must check which one you have (that is called narrowing - the next lesson).

Unions are brilliant for fixed sets of choices:

type Size = "S" | "M" | "L";

A variable of type Size can only be exactly "S", "M" or "L" - a typo like "XL" is caught immediately.

In this lesson you will learn: how to say "one of these".""",
    "4/2": """With a union, you often need to find out WHICH one you have before using it. Checking this is called NARROWING, and TypeScript follows your checks.

function show(id: number | string) {
  if (typeof id === "string") {
    return id.toUpperCase();    // inside this block TypeScript knows: id is a string
  }
  return id.toFixed(2);         // out here it knows: id must be a number
}

Read it: "if it is text, shout it; otherwise it must be a number, show two decimals."

Other ways to narrow:
- x === null  or  x === undefined   (is it empty?)
- Array.isArray(x)                  (is it a list?)
- "prop" in obj                     (does it have this property?)
- x instanceof Date                 (is it a date?)

In this lesson you will learn: how to check which type you have so TypeScript lets you use it.""",
    "4/3": """A very useful pattern: give every kind of object a "kind" label with a fixed text value. TypeScript can then tell them apart.

type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; w: number; h: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "rect":   return s.w * s.h;
  }
}

Inside case "circle", TypeScript knows the shape has a radius. Inside case "rect", it knows about w and h. And if you forget a kind, it can warn you!

This is called a DISCRIMINATED union ("discriminate" = tell apart). Real apps use it for states like "loading", "success" and "error", where each state carries different information.

In this lesson you will learn: how to model "one of several different shapes" safely.""",
}
