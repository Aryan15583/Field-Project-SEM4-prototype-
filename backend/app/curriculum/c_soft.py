"""C - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": r"""A C program always starts in a place called main. Everything inside main's curly brackets { } runs from top to bottom.

#include <stdio.h>

int main(void) {
    printf("Hello!\n");
    return 0;
}

Line by line:
- #include <stdio.h> teaches the computer about input and output (showing and reading things). Always put it at the top.
- int main(void) { ... } is the start point - the front door of your program.
- printf("Hello!\n"); shows the message. The \n inside the text means "go to a new line". printf does NOT move to a new line by itself, so you add \n when you want one.
- return 0; tells the computer "everything went fine".

Every instruction ends with a semicolon ;, like a full stop.

In this lesson you will learn: how a C program is laid out and how to show a message.""",
    "1/2": r"""Inside the text you give to printf, a backslash \ starts a SPECIAL CHARACTER (called an escape sequence):

\n    a new line
\t    a tab (a wide gap)
\"    a double quote mark inside the text
\\    one backslash
%%    a percent sign (a lone % has a special meaning in printf, so you double it)

Example: printf("Name:\tAda\n"); shows  Name:   Ada  and then moves to a new line.

Comments are notes for people that the computer ignores:

// a one-line note
/* a note that
   spans several lines */

In this lesson you will learn: special characters in text, and how to leave notes.""",
    "1/3": r"""C calculates with + - * / and % (the REMAINDER - what is left over after dividing).

If BOTH numbers are whole numbers, C does whole-number maths and throws away the decimals:

7 / 2     // 3     (not 3.5!)
7 % 2     // 1     (7 = 3 x 2 + 1)

To keep the decimals, make at least one number a decimal by writing .0:

7.0 / 2   // 3.5

To SHOW a number with printf you use a PLACEHOLDER - a gap in the text that is filled by the values listed after it:

%d    a whole number
%f    a decimal number  (%.2f means exactly 2 digits after the point)

printf("%d %.1f\n", 7 / 2, 7.0 / 2);      // shows: 3 3.5

The first value fills the first gap, the second value fills the second gap.

In this lesson you will learn: C's maths signs, whole-number division and printf placeholders.""",
    "2/1": r"""In C every variable (a labelled box) must say what KIND of thing it holds:

int count = 3;          // a whole number
double price = 9.99;    // a number with decimals
char letter = 'A';      // ONE character, in single quotes
long big = 3000000000L; // a very large whole number (note the L)

Think of boxes of different shapes: a box made for whole numbers won't take text. C checks this before the program even runs.

Older C had no true/false kind. To use bool, true and false, add this line at the top:

#include <stdbool.h>

In this lesson you will learn: the basic kinds of values and how to make a variable for each.""",
    "2/2": r"""printf uses PLACEHOLDERS to know how to show each value. A placeholder starts with %:

%d    a whole number (int)         %ld   a long number
%f    a decimal (double)           %.2f  a decimal with exactly 2 digits after the point
%c    one character                %s    a piece of text (string)

You can also set a WIDTH - how much room the value takes. This is how you line things up in columns:

%5d    room for 5 characters, number pushed to the RIGHT
%-5d   room for 5 characters, number pushed to the LEFT

printf("%-6s|%4d\n", "Ada", 36);     // shows: Ada   |  36

Read it: show the text Ada in 6 spaces (left side), then a bar |, then the number 36 in 4 spaces (right side).

In this lesson you will learn: how to show different kinds of values neatly.""",
    "2/3": r"""A CONSTANT is a value that must never change. C has two ways to make one:

#define MAX_USERS 100          // every MAX_USERS in the code is replaced by 100
const double PI = 3.14159;     // a variable that cannot be changed

By tradition, constants are written in CAPITALS.

CASTING means changing a value from one kind to another. Put the new kind in brackets in front of the value:

int a = 7, b = 2;
double avg = (double) a / b;      // 3.5
int whole = (int) 9.9;            // 9   (chopped, not rounded)

Why cast a to double? Because int divided by int would give 3. Turning one of them into a double keeps the decimals.

In this lesson you will learn: how to make constants and convert between kinds of numbers.""",
    "3/1": r"""So far your programs only SHOW things. scanf lets the user type something in. You tell it what kind of value to expect (with a placeholder) and WHERE to put it (the variable's address, written with &).

int age;
scanf("%d", &age);          // reads a whole number into age

double price;
scanf("%lf", &price);       // %lf means a decimal (note: lf, not f, for scanf)

For a word (text), you give an array, which needs no &:

char name[50];
scanf("%49s", name);        // reads one word; the 49 stops it overflowing the box

Why the &? scanf must change YOUR variable, so it needs to know where it lives - its address. (You will understand this fully in the Pointers unit.)

In this lesson you will learn: how to read what the user types.""",
    "3/2": r"""if lets your program choose. The question goes in round brackets ( ) and the instructions go in curly brackets { }.

if (n % 2 == 0) {
    printf("even\n");
} else {
    printf("odd\n");
}

Read it: "IF n divided by 2 leaves remainder 0, show even; ELSE show odd."

A fact about C: there is no separate true/false. The number 0 means FALSE and any other number means TRUE. (A comparison like n > 3 gives 1 if yes, 0 if no.)

You can chain more questions with else if, and combine questions with:

&&   AND - both must be true
||   OR  - at least one must be true
!    NOT - flips true and false

Remember: == (two signs) ASKS "are these equal?"; = (one sign) STORES a value.

In this lesson you will learn: how to make your program choose.""",
    "3/3": r"""When one value could be MANY different things, a long chain of if/else is tiring. switch is a neater way:

switch (choice) {
    case 1:
        printf("Start\n");
        break;
    case 2:
        printf("Stop\n");
        break;
    default:
        printf("Unknown\n");
}

Read it: "look at choice. If it is 1, show Start. If it is 2, show Stop. For anything else (default), show Unknown."

Don't forget break at the end of each case! Without it the program keeps running into the next case (a classic mistake called fall-through).

switch works with whole numbers and single characters, not with text or decimals.

In this lesson you will learn: a tidy way to choose between many possibilities.""",
    "4/1": r"""A while loop repeats AS LONG AS its question is true. The question is checked BEFORE each round:

int n = 3;
while (n > 0) {
    printf("%d ", n);
    n--;
}

This shows 3 2 1. (n-- takes 1 away from n each round, so the loop eventually ends.)

A do-while loop does the same but checks AFTER each round, so it always runs at least once. Notice the semicolon at the very end:

do {
    ...
} while (condition);

The golden rule: make sure something changes inside the loop so the question eventually turns false. Otherwise the loop never ends.

In this lesson you will learn: how to repeat while something is true.""",
    "4/2": r"""A for loop packs the three parts of a counting loop on one line:

for (int i = 0; i < n; i++) { ... }

1. START: int i = 0 - a counter that begins at 0.
2. CONDITION: i < n - keep going while this is true.
3. STEP: i++ - after each round, add 1.

With n = 3 it runs for i = 0, 1, 2 - three times. (Programmers count from 0.)

You can change the steps. This counts down by 2:

for (int i = 10; i > 0; i -= 2)      // 10, 8, 6, 4, 2

(i -= 2 means "take 2 away from i".)

Use for when you know how many times to repeat; use while when you are waiting for something to change.

In this lesson you will learn: how to repeat a set number of times.""",
    "4/3": r"""Two commands control a loop from the inside:
- break leaves the innermost loop immediately.
- continue skips the rest of this round and goes to the next.

Loops can also go INSIDE other loops. The inner loop runs completely for each round of the outer loop - like the minute hand going all the way round for each step of the hour hand. This is how you make tables and grids:

for (int r = 1; r <= 3; r++) {
    for (int c = 1; c <= 3; c++) {
        printf("%d ", r * c);
    }
    printf("\n");
}

This prints a small multiplication table:
1 2 3
2 4 6
3 6 9

After each row, printf("\n") starts a new line.

In this lesson you will learn: how to stop or skip loops, and how to nest loops.""",
    "5/1": r"""A FUNCTION is a mini-program with a name that you can use again and again - like a recipe card.

int square(int n) {
    return n * n;
}

Parts, left to right:
- int - the kind of value it gives BACK.
- square - its name.
- (int n) - a PARAMETER: a blank that the caller fills in.
- return n * n; - sends the result back.

Use it by CALLING it from main:

int main(void) {
    printf("%d\n", square(5));      // 25
    return 0;
}

A function that gives nothing back is marked void.

Why bother? You write the steps ONCE and reuse them, and if you need a fix you change it in one place.

In this lesson you will learn: how to write your own reusable commands.""",
    "5/2": r"""C reads your file from the top down. If you call a function that is written BELOW, C doesn't know it yet and complains. The fix is a PROTOTYPE: a one-line promise placed at the top, saying what the function looks like.

int cube(int n);                       // the promise (prototype)

int main(void) { printf("%d", cube(3)); }

int cube(int n) { return n * n * n; }  // the real function, below

SCOPE means "where a variable can be seen". A variable made inside a function is LOCAL: it exists only inside that function and vanishes when the function ends.

There is one trick: marking a local variable static makes it REMEMBER its value between calls, instead of starting fresh each time.

In this lesson you will learn: how to declare functions before using them, and where variables live.""",
    "5/3": r"""RECURSION is when a function calls ITSELF to solve a smaller version of the same problem. Like Russian nesting dolls: to open the big one, open the smaller one inside, and so on until you reach the tiny one that doesn't open.

int factorial(int n) {
    if (n <= 1) return 1;            // base case: the tiny doll - stop here
    return n * factorial(n - 1);     // recursive case: a smaller problem
}

(factorial(4) means 4 x 3 x 2 x 1 = 24.)

Two parts are ALWAYS needed:
1. A BASE CASE - the answer you know without more work. Without it the function calls itself forever.
2. A RECURSIVE CASE - a call to itself with a SMALLER problem.

Trace factorial(3): 3 * factorial(2) = 3 * (2 * factorial(1)) = 3 * (2 * 1) = 6.

In this lesson you will learn: how a function can solve a problem by calling itself.""",
    "6/1": r"""An ARRAY is a row of numbered boxes of the same kind. The size is fixed when you create it, and numbering (the INDEX) starts at 0:

int nums[5] = {4, 8, 15, 16, 23};
nums[0]      // 4      the first
nums[4]      // 23     the last - always size minus 1

IMPORTANT: C does NOT check that you stay inside the array. Asking for nums[5] reads memory that is not yours - the result is unpredictable (this is called undefined behaviour). You must keep track of the size yourself.

Go through an array with a loop that stops at the size:

for (int i = 0; i < 5; i++) printf("%d ", nums[i]);

In this lesson you will learn: how to store many values of one kind, safely.""",
    "6/2": r"""C has no special text type. A "string" is just an ARRAY OF CHARACTERS ending with a special invisible marker '\0' (called the null terminator), so the computer knows where the text stops.

char name[] = "Ada";        // really: 'A', 'd', 'a', '\0'  - that is 4 boxes!
printf("%s\n", name);       // shows Ada
name[0] = 'E';              // now it spells Eda

To go through a string, loop until you meet the marker:

for (int i = 0; name[i] != '\0'; i++) { ... }

Remember: the array needs ONE extra box for the marker. "Ada" has 3 letters but needs 4 boxes.

In this lesson you will learn: how text is stored in C and how to walk through it.""",
    "6/3": r"""The toolbox for text is called string.h. Include it first:

#include <string.h>

strlen(s)          // how many characters (not counting the '\0' marker)
strcpy(dst, src)   // copy src into dst  (dst must be BIG ENOUGH!)
strcat(dst, src)   // glue src onto the end of dst
strcmp(a, b)       // compare: 0 means equal; a negative or positive number means different

Two warnings:
1. strcpy and strcat don't check sizes. If the destination box is too small, they write past its end and cause bugs and security holes. Always make sure it is big enough.
2. NEVER compare strings with == in C. That compares their addresses (where they live), not their letters. Use strcmp(a, b) == 0 instead.

In this lesson you will learn: the standard tools for text, and their dangers.""",
    "7/1": r"""Every variable lives at an ADDRESS in the computer's memory - like a house on a street. A POINTER is a variable that stores an address instead of a normal value.

int x = 10;
int *p = &x;           // & means "the address of x"; p now points to x
printf("%d\n", *p);    // 10   * means "the value AT that address"
*p = 25;               // change the value there: x is now 25

Two signs to remember:
- &x  = "where does x live?"
- *p  = "what is stored where p points?"

NULL means "points to nothing" - a pointer that is not aimed anywhere. Using a NULL pointer crashes the program, so check before you use a pointer you are unsure about.

Pointers are the heart of C. They feel strange at first - that is normal!

In this lesson you will learn: what a pointer is and how to read and change a value through it.""",
    "7/2": r"""When you pass a value to a function, C gives the function a COPY. Changing the copy leaves your original untouched:

To let a function change YOUR variables, pass their ADDRESSES (pointers):

void swap(int *a, int *b) {
    int tmp = *a;      // remember what a points to
    *a = *b;           // put b's value where a points
    *b = tmp;          // put the remembered value where b points
}

swap(&x, &y);          // pass the addresses of x and y

After this call x and y have traded values.

Now you can see why scanf needs the & in scanf("%d", &age): scanf has to change YOUR age, so it needs to know where it lives.

In this lesson you will learn: how functions can change the caller's variables.""",
    "7/3": r"""Arrays and pointers are close cousins. The NAME of an array acts like a pointer to its first box:

int a[3] = {10, 20, 30};
int *p = a;            // p points to the first element, same as &a[0]
*(p + 1)               // 20    "one box further along" - same as a[1]

Adding 1 to a pointer moves it to the NEXT box (C knows how big each box is).

When you give an array to a function, the function only receives that pointer - it does NOT know how long the array is. So always pass the length as well:

int sum(const int *a, int n);

(const promises the function will only read the numbers, not change them.)

In this lesson you will learn: how arrays and pointers are connected, and how to pass arrays to functions.""",
    "8/1": r"""A STRUCT groups several related values into ONE new kind of thing - like a form with several fields.

struct Point {
    int x;
    int y;
};

struct Point p = {3, 4};
printf("%d\n", p.x);       // 3    the dot picks one field

The dot means "the x of THIS point". Each Point you create has its own x and y.

Writing "struct Point" every time is long. typedef gives it a shorter name:

typedef struct { char name[20]; int age; } Person;
Person ada = {"Ada", 36};

Now Person works like int or double - a new kind of box you invented.

In this lesson you will learn: how to bundle related values together under one name.""",
    "8/2": r"""A normal array has a fixed size decided when you write the program. But sometimes you only know the size WHILE the program runs (for example, the number the user types). For that you ask the computer for memory - this is called allocating on the "heap".

#include <stdlib.h>
int *a = malloc(n * sizeof(int));      // ask for room for n ints
if (a == NULL) { /* the computer had no memory to give */ }
...
free(a);                               // ALWAYS give it back when you are done

malloc says "please lend me this many bytes" and gives back a pointer to them. sizeof(int) is how big one int is.

The two rules:
- Forgetting free means the memory is never returned: a MEMORY LEAK.
- Using the memory AFTER free is a serious bug - it may belong to someone else by then.

In this lesson you will learn: how to ask for memory at run time and give it back.""",
    "8/3": r"""Now we combine everything you've learned: structs, arrays, pointers and functions working together.

typedef struct { char item[32]; double price; int qty; } Line;

double total(const Line *lines, int n) {
    double t = 0;
    for (int i = 0; i < n; i++) t += lines[i].price * lines[i].qty;
    return t;
}

Read it: "A Line is one row of a receipt - an item name, a price and a quantity. total takes a list of Lines and how many there are, adds up price times quantity for each, and gives back the sum."

A few things to notice:
- lines[i].price - pick the i-th Line, then its price field.
- const promises the function only READS the lines, never changes them.
- We pass the array's length n, since a function can't tell how long an array is.

This is what real C programs look like: small, clear pieces working together.

In this lesson you will learn: how the pieces of C fit together in a real program.""",
}
