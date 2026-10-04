"""C++ - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": r"""A C++ program always starts in a place called main. Everything inside main's curly brackets { } runs from top to bottom.

#include <iostream>

int main() {
    std::cout << "Hello!" << std::endl;
    return 0;
}

Line by line:
- #include <iostream> teaches the computer about input and output (showing and reading things). Always put it at the top.
- int main() { ... } is the start point - think of it as the front door of your program.
- std::cout is "the screen". The arrows << push things towards it.
- std::endl moves to a new line. (Writing "\n" inside the text does the same.)
- return 0; tells the computer "everything went fine".

Every instruction ends with a semicolon ;, like a full stop.

In this lesson you will learn: how a C++ program is laid out and how to show a message.""",
    "1/2": r"""You can push several things to the screen in one line by chaining the << arrows:

int age = 20;
std::cout << "Age: " << age << "\n";      // shows: Age: 20

Each << adds the next piece. Here we show a piece of text, then the value in age, then a new line.

Comments are notes for people (the computer ignores them):

// a one-line note
/* a note that
   spans several lines */

A time-saver: writing  using namespace std;  near the top lets you type cout instead of std::cout. It is handy in small programs (bigger projects avoid it to prevent name clashes).

In this lesson you will learn: how to show several things in one line, and how to leave notes.""",
    "1/3": """C++ calculates with + - * / and % (the REMAINDER - what is left after dividing).

7 + 3      // 10
7 % 2      // 1     (7 = 3 x 2 + 1) - works on whole numbers only

A famous surprise: if BOTH numbers are whole numbers, division throws away the decimals:

7 / 2      // 3     (not 3.5!)

To keep the decimals, make at least one number a decimal by writing .0:

7.0 / 2    // 3.5

For square roots and powers include the maths toolbox:

#include <cmath>
std::sqrt(16)      // 4
std::pow(2, 3)     // 8
std::abs(-5)       // 5

In this lesson you will learn: C++'s maths signs and the whole-number division surprise.""",
    "2/1": """In C++ every variable (a labelled box) must say what KIND of thing it holds:

int age = 20;           // a whole number
double price = 9.99;    // a number with decimals
char grade = 'A';       // ONE character, in single quotes
bool ok = true;         // true or false

Think of boxes of different shapes: a box made for whole numbers won't accept text. C++ checks this before the program even runs.

A time-saver: auto lets the computer figure out the kind from the value:

auto x = 3.5;           // C++ decides: this is a double

In this lesson you will learn: the basic kinds of values and how to make a variable for each.""",
    "2/2": """Text in C++ is a std::string. You must include the string tool first:

#include <string>

std::string name = "Ada";
name.length()          // 3       how many characters
name + " Lovelace"     // "Ada Lovelace"   joining two strings
name[0]                // 'A'     the first character (counting starts at 0)
name.substr(1, 2)      // "da"    a piece: start at 1, take 2 characters

To read a whole LINE of text (with spaces) from the keyboard:

std::getline(std::cin, name);

(Plain cin >> name would stop at the first space.)

In this lesson you will learn: how to store and work with text.""",
    "2/3": """Sometimes you must turn one kind of number into another. This is called CASTING. In C++ you write static_cast<kind>(value):

int total = 7, count = 2;
double avg = static_cast<double>(total) / count;    // 3.5
int whole = static_cast<int>(9.9);                  // 9  (chopped, not rounded)

Why cast total to double? Because int divided by int would give 3. Turning one of them into a double keeps the decimals.

A CONSTANT is a value that must never change. Add const in front:

const double PI = 3.14159;

If you try to change it later, the compiler gives an error. That is useful - it protects you from accidents.

In this lesson you will learn: how to convert between kinds of numbers and make constants.""",
    "3/1": """So far your programs only SHOW things. cin lets the user type something in. It uses the arrows the other way round (>>) - the value flows from the keyboard INTO your variable:

int a, b;
std::cin >> a >> b;          // reads two numbers
std::cout << a + b;

If the user types 3 4 (with a space or a new line between), a becomes 3 and b becomes 4, and the program shows 7.

Note: cin >> stops reading at a space. So when reading text it reads one WORD at a time.

Memory trick: cout << pushes OUT to the screen, cin >> pulls IN from the keyboard. The arrows point the way the data flows.

In this lesson you will learn: how to read what the user types.""",
    "3/2": """if lets your program choose. The question goes in round brackets ( ), and the instructions go in curly brackets { }:

int n = 7;
if (n % 2 == 0) {
    std::cout << "even";
} else {
    std::cout << "odd";
}

Read it: "IF n divided by 2 leaves remainder 0, show even; ELSE show odd." With n = 7 the remainder is 1, so it shows odd.

You can chain more questions with else if, and combine questions with:

&&   AND - both must be true
||   OR  - at least one must be true
!    NOT - flips true and false

Remember: == (two signs) ASKS "are these equal?"; = (one sign) STORES a value.

In this lesson you will learn: how to make your program choose.""",
    "3/3": """When one value could be MANY different things, a long chain of if/else is tiring. switch is a neater way to choose:

switch (op) {
    case '+': std::cout << a + b; break;
    case '-': std::cout << a - b; break;
    default:  std::cout << "?";
}

Read it: "look at op. If it is +, show the sum. If it is -, show the difference. Otherwise (default), show a question mark."

The word break ends each case. Without it the program keeps running into the next case - a classic beginner trap called fall-through. (switch works with whole numbers and single characters.)

A one-line shortcut for choosing between two values is the TERNARY: condition ? value-if-true : value-if-false.

std::string s = n > 0 ? "pos" : "not pos";

In this lesson you will learn: tidy ways of choosing between possibilities.""",
    "4/1": """A while loop repeats AS LONG AS its question is true. The question is checked BEFORE each round:

int n = 3;
while (n > 0) {
    std::cout << n-- << " ";
}

This shows 3 2 1. (n-- shows n, then takes 1 away.)

A do-while loop does the same but checks AFTER each round, so it always runs at least once - perfect for "ask until the answer is acceptable":

do {
    std::cin >> x;
} while (x < 0);       // keep asking until x is 0 or more

The golden rule: make sure something changes inside the loop so the question eventually turns false. Otherwise the loop never ends.

In this lesson you will learn: how to repeat while something is true.""",
    "4/2": """A for loop packs the three parts of a counting loop on one line:

for (int i = 1; i <= 5; i++) {
    std::cout << i << " ";
}

1. START: int i = 1 - a counter that begins at 1.
2. CONDITION: i <= 5 - keep going while this is true.
3. STEP: i++ - after each round, add 1.

It shows 1 2 3 4 5.

Variations: count down with i--, or jump in 2s with i += 2 (add 2 to i).

Use for when you know how many times to repeat; use while when you are waiting for something to change.

In this lesson you will learn: how to repeat a set number of times.""",
    "4/3": r"""Two commands control a loop from the inside:
- break leaves the innermost loop immediately.
- continue skips the rest of this round and goes to the next.

Loops can also go INSIDE other loops. The inner loop runs completely for each round of the outer loop - like the minute hand going all the way round for each step of the hour hand. This is how you draw grids:

for (int r = 0; r < 3; r++) {
    for (int c = 0; c < 4; c++) {
        std::cout << '#';
    }
    std::cout << '\n';
}

This draws 3 rows of 4 hashes:
####
####
####

After each row, '\n' starts a new line.

In this lesson you will learn: how to stop or skip loops, and how to nest loops for grids.""",
    "5/1": """A FUNCTION is a mini-program with a name that you can use again and again - like a recipe card.

int square(int n) {
    return n * n;
}

Parts, left to right:
- int - the kind of value it gives BACK.
- square - its name.
- (int n) - a PARAMETER: a blank that the caller fills in.
- return n * n; - sends the result back.

Use it by CALLING it from main:

int main() {
    std::cout << square(5);      // 25
}

The function must be written BEFORE main (so the computer already knows it), or you promise it earlier with a one-line "prototype".

A function that gives nothing back is marked void.

In this lesson you will learn: how to write your own reusable commands.""",
    "5/2": """Normally when you pass a value to a function, the function gets a COPY. Changing the copy does not change your original:

If you want the function to change YOUR variable, pass it BY REFERENCE by adding & after the type:

void addOne(int& x) {
    x++;
}

int n = 5;
addOne(n);         // n is now 6

The & means "don't copy - work on the real one". Think of lending your actual notebook instead of a photocopy.

Another good use: big objects (like long text) are slow to copy. Pass them as a const reference - no copy, and the function is not allowed to change them:

void show(const std::string& s)

In this lesson you will learn: how functions can change the caller's variable or avoid copying.""",
    "5/3": """OVERLOADING means several functions can share the SAME NAME, as long as their parameters differ. C++ picks the right one from what you pass:

double area(double r) { return 3.14159 * r * r; }     // a circle
int area(int w, int h) { return w * h; }              // a rectangle

area(2.0)     // uses the circle version
area(3, 5)    // uses the rectangle version

DEFAULT values let the caller leave a parameter out:

void greet(std::string name = "friend") {
    std::cout << "Hi " << name;
}
greet();          // Hi friend
greet("Ada");     // Hi Ada

In this lesson you will learn: how to reuse a function name and set default values.""",
    "6/1": """An array has a fixed size. A std::vector is a FLEXIBLE list that grows and shrinks. Include it first:

#include <vector>

std::vector<int> nums = {4, 8, 15};
nums.push_back(16);     // add to the END
nums.size()             // 4        how many
nums[0]                 // 4        the first (counting starts at 0)
nums.back()             // 16       the last
nums.pop_back();        // remove the last

The <int> in angle brackets says what the vector holds. For text you would write std::vector<std::string>.

Vectors are the everyday list of C++ - fast, flexible and safe.

In this lesson you will learn: how to keep a growing list of values.""",
    "6/2": """To do something with every item of a vector, use a RANGE-BASED for loop. Read it as "for each x in nums":

for (int x : nums) {
    std::cout << x << " ";
}

If you want to CHANGE the items, add & so you work on the real items and not copies:

for (auto& x : nums) x *= 2;      // doubles every item (x *= 2 means x = x * 2)

The <algorithm> toolbox does common jobs for you:

#include <algorithm>
std::sort(v.begin(), v.end());        // sort
std::max_element(...), std::count(...), std::reverse(...)

(begin() and end() mean "the start and the end of the vector".)

In this lesson you will learn: how to go through a vector and use ready-made tools.""",
    "6/3": """std::string has many helpful tools. Here are the common ones (the dot after the text means "ask this text to..."):

std::string s = "hello world";
s.find("world")            // 6    where does it start? (npos if it isn't there)
s.replace(0, 5, "HELLO")   // swap 5 characters from position 0 -> "HELLO world"
s.substr(6)                // "world"   the piece from position 6 on

For single characters and conversions:

std::toupper(c)            // one character to a capital (needs <cctype>)
std::to_string(42)         // the number 42 as text "42"
std::stoi("42")            // the text "42" as the number 42

Remember: positions start at 0, so "hello world" has its w at position 6.

In this lesson you will learn: how to search, change and convert text.""",
    "7/1": """So far you have used values like numbers and text. A CLASS lets you create your OWN kind of thing. It is a blueprint (like the plan for a house); an OBJECT is one real thing built from it.

class Dog {
public:
    std::string name;
    void bark() {
        std::cout << name << " says woof\n";
    }
};

The blueprint says: every Dog has a name and can bark. (public means "anyone may use these".) To build a real dog:

Dog d;
d.name = "Rex";
d.bark();          // Rex says woof

The dot means "this dog's name", "make this dog bark". You can build many dogs, each with its own name.

Careful: a class definition ends with a semicolon ; after the closing bracket - easy to forget!

In this lesson you will learn: how to make blueprints and build objects.""",
    "7/2": """Setting up each new object by hand is tiring. A CONSTRUCTOR is a special function that runs automatically when you build an object and sets it up. It has the same name as the class and no return type.

class Point {
public:
    int x, y;
    Point(int x, int y) : x(x), y(y) {}
};

Point p(3, 4);

The part after the colon, x(x), y(y), is the "member initializer list". Read x(x) as "set my x to the incoming x". It is the tidy, preferred way to set up an object.

Now every Point is created with x and y already set - no half-finished objects.

In this lesson you will learn: how to set up an object the moment it is created.""",
    "7/3": """INHERITANCE lets one class build on another so you don't repeat yourself. The new class gets everything the old one has and can add or change things.

class Shape {
public:
    virtual double area() const { return 0; }
    virtual ~Shape() = default;
};

class Square : public Shape {
    double s;
public:
    Square(double s) : s(s) {}
    double area() const override { return s * s; }
};

- A Square IS a Shape.
- virtual in Shape means "a child class may replace this method with its own version".
- override in Square says "this is my own version" (the compiler checks you really are replacing something).

This lets you treat many different shapes in one way: ask any Shape for its area, and each one answers in its own way. (The virtual ~Shape() line is a safety detail for cleanup - always include it with virtual methods.)

In this lesson you will learn: how a class can inherit from another and change its behaviour.""",
    "8/1": """Every value in your program lives at an ADDRESS in the computer's memory - like a house on a street. A POINTER is a variable that stores an address instead of a normal value.

int x = 10;
int* p = &x;         // & means "the address of x"; p now points to x
std::cout << *p;     // 10   * means "the value AT that address"
*p = 20;             // change the value at that address: x is now 20

Two signs to remember:
- &x  = "where does x live?"
- *p  = "what is at the place p points to?"

nullptr means "points to nothing" - a pointer that is not aimed anywhere yet.

Pointers are everywhere in real C++ code, but modern C++ prefers safer tools (references and smart pointers, which you will meet soon).

In this lesson you will learn: what a pointer is and how to read and change a value through it.""",
    "8/2": """A std::map is like a dictionary or a phone book: you look something up by a KEY (a name) and get a VALUE (a number). It keeps its keys in sorted order.

#include <map>

std::map<std::string, int> ages;
ages["Ada"] = 36;               // add or change
ages.count("Bob")               // 0 -> Bob is not in the map (1 means present)

To go through every entry:

for (const auto& [name, age] : ages) {
    std::cout << name << " " << age << "\n";
}

(Read the loop as: "for each name-and-age pair in ages". The & avoids copying.)

There is a faster version called std::unordered_map that does not keep the keys sorted - use it when you don't care about order.

In this lesson you will learn: how to store and look up information by name.""",
    "8/3": """Older C++ made you reserve memory yourself with new and give it back with delete. Forgetting to delete causes a "memory leak"; deleting twice crashes. SMART POINTERS do the cleanup for you automatically when the pointer goes out of scope (when the { } it lives in ends). This clever idea is called RAII.

#include <memory>
auto p = std::make_unique<int>(42);
std::cout << *p;            // 42
// no delete needed - it is freed automatically

unique_ptr means ONE owner of the thing.

If several parts of a program must share something, use std::shared_ptr. It counts how many owners there are and frees the object when the LAST owner goes away.

The rule for modern C++: don't write new and delete yourself - let smart pointers do it.

In this lesson you will learn: how to manage memory safely without cleaning up by hand.""",
}
