"""Starter curriculum. Loaded once, when the database has no courses."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Course, Exercise, Lesson, Unit

Q = r"""(['"])"""  # opening quote; close with \1 (or \2... when nested groups are used)


def mcq(prompt, options, index, explanation="", hint="", code=None):
    return {"kind": "mcq", "prompt": prompt, "code": code, "data": {"options": options}, "solution": {"index": index},
            "explanation": explanation, "hint": hint}


def fill(prompt, code, accepted, explanation="", hint=""):
    return {"kind": "fill", "prompt": prompt, "code": code, "data": {}, "solution": {"accepted": accepted},
            "explanation": explanation, "hint": hint}


def order(prompt, lines, explanation="", hint=""):
    return {"kind": "order", "prompt": prompt, "code": None, "data": {"lines": lines}, "solution": {},
            "explanation": explanation, "hint": hint}


def code(prompt, patterns, example, starter="", explanation="", hint="", forbid=None):
    return {"kind": "code", "prompt": prompt, "code": None, "data": {"starter": starter},
            "solution": {"patterns": patterns, "example": example, "forbid": forbid or []},
            "explanation": explanation, "hint": hint}


CURRICULUM = [
    {
        "slug": "python", "title": "Python", "icon": "🐍",
        "description": "The friendliest first language - readable, powerful and everywhere.",
        "units": [
            {"title": "Unit 1 · First steps", "lessons": [
                {"title": "Hello, Python", "intro": "Python runs your code line by line. The print() function shows a value on the screen.\n\nprint(\"Hello!\")  # shows Hello!", "exercises": [
                    mcq("What does this code show?", ["Hi", "\"Hi\"", "print Hi", "An error"], 0,
                        "print() shows the text itself, without the quotes.", "Quotes mark text - they aren't printed.", code='print("Hi")'),
                    fill("Complete the code so it shows a greeting.", '___("Hello, World!")', ["print"],
                         "print is the built-in function that displays output.", "Which function displays output?"),
                    code("Write one line that prints exactly: Hello, World!",
                         [r"^\s*print\(\s*" + Q + r"Hello, World!\1\s*\)\s*$"], 'print("Hello, World!")',
                         explanation="Text goes inside quotes, and the quotes go inside print( ).",
                         hint="Use print( ) with the text in quotes."),
                    mcq("Which symbol starts a comment in Python?", ["#", "//", "/*", "--"], 0,
                        "Everything after # on a line is ignored by Python.", "It's also called a hash."),
                ]},
                {"title": "Variables", "intro": "A variable is a named box that stores a value.\n\nscore = 10\nscore = score + 5  # now 15", "exercises": [
                    mcq("What is printed?", ["5", "7", "x + 2", "52"], 1, "x starts at 5, then becomes 5 + 2 = 7.",
                        "Work through it one line at a time.", code="x = 5\nx = x + 2\nprint(x)"),
                    fill("Store the text \"Ada\" in a variable called name.", 'name ___ "Ada"', ["="],
                         "A single = assigns a value to a variable.", "It's the assignment operator."),
                    order("Put the lines in order so the program prints 21.", ["age = 20", "age = age + 1", "print(age)"],
                          "A variable must be created before it's changed or printed.", "Create -> update -> print."),
                    mcq("Which is a valid variable name?", ["2cool", "my_score", "my-score", "class"], 1,
                        "Names can't start with a digit, contain '-', or be keywords like class.", "Underscores are allowed."),
                ]},
            ]},
            {"title": "Unit 2 · Making decisions & repeating", "lessons": [
                {"title": "If statements", "intro": "if runs code only when a condition is True. Indentation shows which lines belong to it.\n\nif age >= 18:\n    print(\"Adult\")\nelse:\n    print(\"Minor\")", "exercises": [
                    mcq("What is printed?", ["yes", "no", "yes then no", "nothing"], 0, "3 > 2 is True, so the if-branch runs.",
                        "Is 3 greater than 2?", code='if 3 > 2:\n    print("yes")\nelse:\n    print("no")'),
                    fill("Check whether score is greater than or equal to 50.", "if score ___ 50:", [">="],
                         ">= means 'greater than or equal to'.", "Two characters: a comparison plus equals."),
                    order("Order the program so it prints Hot.", ["temp = 30", "if temp > 25:", '    print("Hot")', "else:", '    print("Nice")'],
                          "The variable comes first, then the if, its body, the else and its body.", "else always follows the if block."),
                    code('Write an if statement: when x equals 10, print "ten".',
                         [r"^if\s+x\s*==\s*10\s*:\s*$", r"^\s+print\(\s*" + Q + r"ten\1\s*\)\s*$"],
                         'if x == 10:\n    print("ten")', explanation="Use == to compare and indent the body.",
                         hint="Remember: == compares, = assigns. Don't forget the colon and indentation."),
                ]},
                {"title": "Loops", "intro": "for loops repeat code for each item. range(n) counts from 0 up to n-1.\n\nfor i in range(3):\n    print(i)  # 0, 1, 2", "exercises": [
                    mcq("What does this print?", ["1 2 3", "0 1 2", "0 1 2 3", "3"], 1, "range(3) produces 0, 1 and 2.",
                        "range starts at 0 by default.", code="for i in range(3):\n    print(i)"),
                    fill("Loop over every fruit in the list.", "for fruit ___ fruits:", ["in"], "for ... in ... walks through each item.",
                         "A two-letter keyword."),
                    code("Write a for loop that prints the numbers 1 to 5.",
                         [r"^for\s+\w+\s+in\s+range\(\s*1\s*,\s*6\s*\)\s*:\s*$", r"^\s+print\(\s*\w+\s*\)\s*$"],
                         "for n in range(1, 6):\n    print(n)", explanation="range(1, 6) stops before 6.",
                         hint="range(start, stop) - the stop value is not included."),
                    mcq("What does break do inside a loop?", ["Skips one iteration", "Exits the loop immediately", "Restarts the loop", "Crashes the program"], 1,
                        "break leaves the loop straight away; continue skips to the next iteration.", "Think 'break out'."),
                ]},
            ]},
        ],
    },
    {
        "slug": "javascript", "title": "JavaScript", "icon": "⚡",
        "description": "The language of the web - make pages interactive.",
        "units": [
            {"title": "Unit 1 · Basics", "lessons": [
                {"title": "console.log", "intro": "console.log() prints values to the browser console.\n\nconsole.log(\"Hi\");", "exercises": [
                    fill("Print a message to the console.", 'console.___("Hello");', ["log"], "console.log writes to the console.", "Starts with l."),
                    code("Print exactly: Hello, JS!", [r"^\s*console\.log\(\s*(['\"`])Hello, JS!\1\s*\)\s*;?\s*$"], 'console.log("Hello, JS!");',
                         hint="console.log( ) with the text in quotes."),
                    mcq("What does console.log(2 + 3) print?", ["23", "5", "2 + 3", "undefined"], 1, "Numbers are added before printing.", "It's arithmetic."),
                    mcq("Which ends a statement in JavaScript (optional but common)?", [";", ".", ":", "!"], 0, "Semicolons end statements.", "Same as C and Java."),
                ]},
                {"title": "let & const", "intro": "let creates a variable you can change; const creates one you can't reassign.\n\nlet lives = 3;\nconst name = \"Ada\";", "exercises": [
                    mcq("Which keyword declares a variable that can't be reassigned?", ["let", "var", "const", "fixed"], 2,
                        "const bindings can't be reassigned.", "Short for 'constant'."),
                    fill("Declare a changeable variable count set to 0.", "___ count = 0;", ["let"], "let allows reassignment.", "Three letters."),
                    mcq("What happens?", ["Prints 2", "TypeError: Assignment to constant variable", "Prints 1", "Nothing"], 1,
                        "Reassigning a const throws a TypeError.", "Can a constant change?", code="const x = 1;\nx = 2;"),
                    order("Order the code so it logs 6.", ["let total = 1;", "total = total + 5;", "console.log(total);"],
                          "Declare, update, then log.", "Declaration always comes first."),
                ]},
            ]},
            {"title": "Unit 2 · Functions & arrays", "lessons": [
                {"title": "Functions", "intro": "Functions package reusable code.\n\nfunction greet(name) {\n  return \"Hi \" + name;\n}\nconst double = (n) => n * 2;", "exercises": [
                    mcq("What does double(4) return?", ["4", "8", "\"44\"", "undefined"], 1, "The arrow function returns n * 2.",
                        "Multiply by two.", code="const double = (n) => n * 2;"),
                    fill("Send a value back from a function.", "function five() {\n  ___ 5;\n}", ["return"], "return gives a value back to the caller.", "Six letters."),
                    code("Write a function add(a, b) that returns a + b (any style).",
                         [r"(function\s+add\s*\(\s*a\s*,\s*b\s*\)|add\s*=\s*\(\s*a\s*,\s*b\s*\)\s*=>)", r"(return\s+a\s*\+\s*b|=>\s*a\s*\+\s*b)"],
                         "function add(a, b) {\n  return a + b;\n}", hint="function add(a, b) { ... } and return the sum."),
                    order("Order a function that logs a greeting.", ["function hello() {", '  console.log("hello");', "}", "hello();"],
                          "Define the function, then call it.", "The call comes last."),
                ]},
                {"title": "Arrays", "intro": "Arrays hold ordered lists. Indexes start at 0.\n\nconst langs = [\"JS\", \"Python\"];\nlangs.push(\"C\");\nlangs[0]; // \"JS\"", "exercises": [
                    mcq("What is nums[1]?", ["10", "20", "30", "undefined"], 1, "Indexes start at 0, so [1] is the second item.",
                        "Count from zero.", code="const nums = [10, 20, 30];"),
                    fill("Add \"C\" to the end of the array.", 'langs.___("C");', ["push"], "push appends to the end.", "Push it on!"),
                    mcq("What does [1, 2, 3].length return?", ["2", "3", "4", "undefined"], 1, "length counts the items.", "How many items?"),
                    code("Create a const array named colors with \"red\" and \"blue\".",
                         [r"const\s+colors\s*=\s*\[\s*(['\"])red\1\s*,\s*(['\"])blue\2\s*\]"], 'const colors = ["red", "blue"];',
                         hint="Square brackets, items separated by commas."),
                ]},
            ]},
        ],
    },
    {
        "slug": "java", "title": "Java", "icon": "☕",
        "description": "Strongly-typed and object-oriented - powers Android and big backends.",
        "units": [{"title": "Unit 1 · Java foundations", "lessons": [
            {"title": "Your first program", "intro": "Every Java program starts in a main method inside a class.\n\npublic class Main {\n  public static void main(String[] args) {\n    System.out.println(\"Hi\");\n  }\n}", "exercises": [
                order("Order the lines to make a valid program.",
                      ["public class Main {", "  public static void main(String[] args) {", '    System.out.println("Hello");', "  }", "}"],
                      "Class wraps method; method wraps statements.", "Braces open before they close."),
                fill("Print a line in Java.", 'System.out.___("Hi");', ["println"], "println prints and adds a newline.", "print + line."),
                mcq("Which method does Java run first?", ["start()", "main()", "run()", "init()"], 1, "The JVM starts at main.", "Same as C."),
                mcq("Java statements end with…", [";", ":", ".", "nothing"], 0, "Every statement ends in a semicolon.", "Like JavaScript."),
            ]},
            {"title": "Types & variables", "intro": "Java variables have a type.\n\nint age = 20;\ndouble price = 9.99;\nString name = \"Ada\";\nboolean ok = true;", "exercises": [
                mcq("Which type stores whole numbers?", ["double", "int", "String", "boolean"], 1, "int holds integers.", "Short for integer."),
                fill("Declare text.", '___ city = "Pune";', ["String"], "String (capital S) holds text.", "Capitalised type."),
                mcq("What is 7 / 2 in Java (both ints)?", ["3.5", "3", "4", "Error"], 1, "Integer division drops the remainder.", "ints can't hold decimals."),
                code("Declare a boolean named isReady set to true.", [r"^\s*boolean\s+isReady\s*=\s*true\s*;\s*$"], "boolean isReady = true;",
                     hint="type name = value;"),
            ]},
        ]}],
    },
    {
        "slug": "cpp", "title": "C++", "icon": "⚙️",
        "description": "Fast, close-to-the-metal - games, engines and competitive coding.",
        "units": [{"title": "Unit 1 · C++ basics", "lessons": [
            {"title": "Output with cout", "intro": "#include <iostream>\nint main() {\n  std::cout << \"Hi\" << std::endl;\n}", "exercises": [
                fill("Complete the output statement.", 'std::cout ___ "Hello";', ["<<"], "<< sends data to the output stream.", "Two arrows."),
                mcq("Which header gives you std::cout?", ["<stdio.h>", "<iostream>", "<string>", "<cmath>"], 1, "iostream = input/output streams.", "io + stream."),
                order("Order a minimal program.", ["#include <iostream>", "int main() {", '  std::cout << "Hi";', "  return 0;", "}"],
                      "Includes first, then main.", "return goes at the end of main."),
                mcq("What does main return on success by convention?", ["1", "0", "-1", "true"], 1, "0 means success.", "Zero errors."),
            ]},
            {"title": "Variables & if", "intro": "int x = 5;\nif (x > 3) {\n  std::cout << \"big\";\n}", "exercises": [
                mcq("What is printed?", ["big", "small", "bigsmall", "nothing"], 1, "2 > 3 is false, so else runs.", "Is 2 greater than 3?",
                    code='int x = 2;\nif (x > 3) std::cout << "big";\nelse std::cout << "small";'),
                fill("Conditions in C++ go inside…", "if ___x > 0) { }", ["("], "Conditions are wrapped in parentheses.", "A bracket type."),
                code("Declare an int named lives with value 3.", [r"^\s*int\s+lives\s*=\s*3\s*;\s*$"], "int lives = 3;", hint="int name = value;"),
                mcq("Which operator checks equality?", ["=", "==", "===", ":="], 1, "== compares; = assigns.", "Two characters."),
            ]},
        ]}],
    },
    {
        "slug": "c", "title": "C", "icon": "🔧",
        "description": "The classic systems language behind operating systems.",
        "units": [{"title": "Unit 1 · C basics", "lessons": [
            {"title": "printf", "intro": "#include <stdio.h>\nint main(void) {\n  printf(\"Hi\\n\");\n  return 0;\n}", "exercises": [
                fill("Print formatted text in C.", '___("Hello\\n");', ["printf"], "printf = print formatted.", "print + f."),
                mcq("What does \\n do?", ["Prints n", "New line", "Tab", "Ends program"], 1, "\\n is the newline escape.", "n for newline."),
                mcq("Which header declares printf?", ["<iostream>", "<stdio.h>", "<stdlib.h>", "<string.h>"], 1, "Standard I/O.", "std + io."),
                code("Print exactly Hello, C! followed by a newline.", [r"^\s*printf\(\s*\"Hello, C!\\n\"\s*\)\s*;\s*$"], 'printf("Hello, C!\\n");',
                     hint="Double quotes only in C, and end with \\n."),
            ]},
            {"title": "Format specifiers", "intro": "int age = 20;\nprintf(\"%d\\n\", age);   // integer\nprintf(\"%f\\n\", 3.14); // float\nprintf(\"%s\\n\", \"hi\");  // string", "exercises": [
                mcq("Which specifier prints an int?", ["%s", "%d", "%f", "%c"], 1, "%d = decimal integer.", "d for decimal."),
                fill("Print a string variable name.", 'printf("___\\n", name);', ["%s"], "%s prints a string.", "s for string."),
                mcq("What prints?", ["x", "5", "%d", "0"], 1, "%d is replaced by x's value.", "The placeholder is filled in.", code='int x = 5;\nprintf("%d", x);'),
                mcq("Which prints a single character?", ["%c", "%ch", "%s", "%x"], 0, "%c = char.", "c for char."),
            ]},
        ]}],
    },
    {
        "slug": "sql", "title": "SQL", "icon": "🗄️",
        "description": "Ask databases questions and get answers.",
        "units": [{"title": "Unit 1 · Querying data", "lessons": [
            {"title": "SELECT", "intro": "SELECT picks columns FROM a table.\n\nSELECT name, age FROM students;\nSELECT * FROM students;  -- all columns", "exercises": [
                fill("Get every column from users.", "SELECT ___ FROM users;", ["*"], "* means all columns.", "A star."),
                mcq("Which keyword names the table?", ["WHERE", "FROM", "INTO", "TABLE"], 1, "SELECT ... FROM table.", "Where is the data from?"),
                code("Select the name column from the students table.", [r"(?i)^\s*select\s+name\s+from\s+students\s*;?\s*$"], "SELECT name FROM students;",
                     hint="SELECT column FROM table;"),
                order("Order the query.", ["SELECT title", "FROM books", "ORDER BY title;"], "SELECT, FROM, then ORDER BY.", "Sorting comes last."),
            ]},
            {"title": "WHERE", "intro": "WHERE filters rows.\n\nSELECT * FROM students WHERE age >= 18;", "exercises": [
                fill("Only rows where city is Mumbai.", "SELECT * FROM users ___ city = 'Mumbai';", ["WHERE", "where"], "WHERE filters rows.", "Filtering keyword."),
                mcq("Which combines two conditions that must BOTH be true?", ["OR", "AND", "NOT", "BOTH"], 1, "AND requires both.", "Both = ..."),
                mcq("Text values in SQL are written in…", ["single quotes", "backticks", "no quotes", "brackets"], 0, "'Mumbai' - single quotes.", "Standard SQL uses '...'."),
                code("Select all columns from products where price < 100.", [r"(?i)^\s*select\s+\*\s+from\s+products\s+where\s+price\s*<\s*100\s*;?\s*$"],
                     "SELECT * FROM products WHERE price < 100;", hint="SELECT * FROM table WHERE condition;"),
            ]},
        ]}],
    },
    {
        "slug": "html-css", "title": "HTML & CSS", "icon": "🎨",
        "description": "Build and style web pages.",
        "units": [{"title": "Unit 1 · Web page basics", "lessons": [
            {"title": "HTML tags", "intro": "HTML uses tags to structure content.\n\n<h1>Title</h1>\n<p>A paragraph.</p>\n<a href=\"https://example.com\">Link</a>", "exercises": [
                mcq("Which tag makes the largest heading?", ["<h6>", "<h1>", "<head>", "<title>"], 1, "h1 is the top-level heading.", "Lower number = bigger."),
                fill("Close the paragraph.", "<p>Hello___", ["</p>"], "Closing tags start with </.", "Slash + tag name."),
                mcq("Which attribute sets a link's destination?", ["src", "href", "link", "to"], 1, "href = hypertext reference.", "h..."),
                code("Write a link to https://codeingo.dev with the text Codeingo.",
                     [r"^\s*<a\s+href=\"https://codeingo\.dev\"\s*>\s*Codeingo\s*</a>\s*$"], '<a href="https://codeingo.dev">Codeingo</a>',
                     hint="<a href=\"...\">text</a>"),
            ]},
            {"title": "CSS selectors", "intro": "CSS styles elements.\n\np { color: blue; }\n.card { padding: 8px; }\n#logo { width: 40px; }", "exercises": [
                mcq("Which selector targets class=\"card\"?", ["#card", ".card", "card", "*card"], 1, ". = class, # = id.", "Dot."),
                fill("Make h1 text green.", "h1 { ___: green; }", ["color"], "color sets text colour.", "American spelling."),
                mcq("Which selects id=\"logo\"?", [".logo", "#logo", "logo", "@logo"], 1, "# selects an id.", "Hash."),
                code("Write a rule making all p elements have font-size 16px.", [r"^\s*p\s*\{\s*font-size\s*:\s*16px\s*;?\s*\}\s*$"],
                     "p { font-size: 16px; }", hint="selector { property: value; }"),
            ]},
        ]}],
    },
]


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(Course.id).limit(1)):
        return
    for ci, c in enumerate(CURRICULUM):
        course = Course(slug=c["slug"], title=c["title"], description=c["description"], icon=c["icon"], position=ci)
        for ui, u in enumerate(c["units"]):
            unit = Unit(title=u["title"], position=ui)
            for li, l in enumerate(u["lessons"]):
                lesson = Lesson(title=l["title"], intro=l["intro"], position=li, xp_reward=10)
                for ei, e in enumerate(l["exercises"]):
                    lesson.exercises.append(Exercise(position=ei, **e))
                unit.lessons.append(lesson)
            course.units.append(unit)
        db.add(course)
    db.commit()
