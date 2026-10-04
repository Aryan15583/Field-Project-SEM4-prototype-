"""C - Expert section, part 1 (units 17-23): modular design, dynamic arrays, function pointers, parsing, data
structures, trees, algorithms. Runnable code targets C11."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .c_adv import STARTER, prog

IO = "#include <stdio.h>\n"
STD = "#include <stdio.h>\n#include <stdlib.h>\n"
STR = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Modular design",
        lesson(
            "Structs as modules",
            """Good C groups data with the functions that operate on it. A struct plus functions taking a pointer to it is C's version of a class:

typedef struct { int *data; int len, cap; } Vec;
void vec_init(Vec *v);
void vec_push(Vec *v, int x);
void vec_free(Vec *v);

Convention: a prefix per module (vec_), an init that sets up the struct, a free that releases everything, and the struct passed by pointer so functions can modify it and large structs aren't copied.""",
            mcq("Why pass a struct by pointer?", ["To modify it and avoid copying", "Structs can't be passed by value", "It's required", "To hide it"], 0),
            mcq("What does the vec_ prefix achieve?", ["Namespacing - C has no namespaces", "Speed", "Type safety", "Nothing"], 0),
            mcq("Which function pair should every module with allocation have?", ["init and free", "get and set", "open and read", "min and max"], 0),
            run("Write a Counter struct {int count, step;} with counter_init(Counter *c, int step), counter_tick(Counter *c) and counter_value(const Counter *c). Read step and n; call tick n times and print the value.", "c",
                [t("step3", stdin="3 4"), t("zero", stdin="5 0")], ["12", "0"],
                prog('int step, n;\nscanf("%d %d", &step, &n);\nCounter c;\ncounter_init(&c, step);\nfor (int i = 0; i < n; i++) counter_tick(&c);\nprintf("%d\\n", counter_value(&c));',
                     before='typedef struct {\n    int count;\n    int step;\n} Counter;\n\nvoid counter_init(Counter *c, int step) {\n    c->count = 0;\n    c->step = step;\n}\n\nvoid counter_tick(Counter *c) {\n    c->count += c->step;\n}\n\nint counter_value(const Counter *c) {\n    return c->count;\n}\n\n'),
                starter=STARTER, require=[r"counter_init", r"counter_tick", r"counter_value"], fallback=[r"typedef\s+struct", r"counter_init\s*\(", r"->"]),
        ),
        lesson(
            "static, extern and headers",
            """Large C programs are split across files:

- a header (.h) DECLARES the public functions and types: int vec_len(const Vec *v);
- the source (.c) DEFINES them
- static on a file-level function or variable makes it PRIVATE to that file (internal linkage)
- extern declares a global that is defined in another file

Always protect headers from double inclusion:
#ifndef VEC_H
#define VEC_H
...
#endif

Mark helper functions static: it documents intent, avoids name clashes and lets the compiler inline them.""",
            mcq("What does static on a file-scope function mean?", ["Private to that file", "Constant", "Runs once", "Allocated on stack"], 0),
            mcq("What does an include guard prevent?", ["Double inclusion of a header", "Buffer overflow", "Null pointers", "Recursion"], 0),
            mcq("What goes in a header file?", ["Declarations of the public interface", "All the code", "Only main", "Object files"], 0),
            run("Use a static helper: write static int clamp(int x, int lo, int hi) and a public function score(int raw) that clamps raw into 0..100. Read n numbers and print each clamped score on one line separated by spaces.", "c",
                [t("mix", stdin="4\n-5 50 120 100"), t("one", stdin="1\n7")], ["0 50 100 100", "7"],
                prog('int n;\nscanf("%d", &n);\nfor (int i = 0; i < n; i++) {\n    int raw;\n    scanf("%d", &raw);\n    printf("%s%d", i ? " " : "", score(raw));\n}\nprintf("\\n");',
                     before='static int clamp(int x, int lo, int hi) {\n    if (x < lo) return lo;\n    if (x > hi) return hi;\n    return x;\n}\n\nint score(int raw) {\n    return clamp(raw, 0, 100);\n}\n\n'),
                starter=STARTER, require=[r"static\s+int\s+clamp"], fallback=[r"static\s+int\s+clamp", r"score\s*\("]),
        ),
        lesson(
            "Opaque types",
            """An opaque type hides its fields from users: the header only forward-declares the struct and exposes functions on a pointer.

typedef struct Stack Stack;              // header: users can't see the fields
Stack *stack_new(void);
void stack_push(Stack *s, int x);
void stack_free(Stack *s);

The .c file defines struct Stack { ... }. Users can't touch the fields, so the implementation can change without breaking them (encapsulation). The price: every instance is heap-allocated, so the module needs a matching _free.""",
            mcq("What does an opaque type hide?", ["The struct's fields", "The functions", "The header", "The name"], 0),
            mcq("Why must opaque types be heap allocated?", ["Users don't know their size", "They are huge", "C requires it", "They're global"], 0),
            mcq("What must pair with stack_new?", ["stack_free", "stack_copy", "main", "stack_print"], 0),
            run("Implement an integer stack with array storage and the API stack_new, stack_push, stack_pop, stack_empty, stack_free (capacity 100). Read n commands ('push x' or 'pop'); print popped values, or EMPTY when popping an empty stack.", "c",
                [t("mix", stdin="5\npush 1\npush 2\npop\npop\npop"), t("empty", stdin="1\npop")], ["2\n1\nEMPTY", "EMPTY"],
                prog('int n;\nscanf("%d", &n);\nStack *s = stack_new();\nwhile (n--) {\n    char cmd[8];\n    scanf("%7s", cmd);\n    if (cmd[1] == \'u\') {\n        int x;\n        scanf("%d", &x);\n        stack_push(s, x);\n    } else if (stack_empty(s)) {\n        printf("EMPTY\\n");\n    } else {\n        printf("%d\\n", stack_pop(s));\n    }\n}\nstack_free(s);',
                     includes=STD,
                     before='typedef struct Stack Stack;\n\nstruct Stack {\n    int data[100];\n    int top;\n};\n\nStack *stack_new(void) {\n    Stack *s = malloc(sizeof *s);\n    s->top = 0;\n    return s;\n}\n\nvoid stack_push(Stack *s, int x) {\n    s->data[s->top++] = x;\n}\n\nint stack_pop(Stack *s) {\n    return s->data[--s->top];\n}\n\nint stack_empty(const Stack *s) {\n    return s->top == 0;\n}\n\nvoid stack_free(Stack *s) {\n    free(s);\n}\n\n'),
                starter=STARTER, require=[r"stack_new", r"stack_free", r"malloc"], fallback=[r"typedef\s+struct\s+Stack", r"malloc\s*\(", r"free\s*\("]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Dynamic arrays",
        lesson(
            "A growable vector with realloc",
            """realloc resizes a heap block, keeping its contents. Doubling the capacity when full makes appends O(1) amortised:

if (v->len == v->cap) {
    int ncap = v->cap ? v->cap * 2 : 4;
    int *p = realloc(v->data, ncap * sizeof *p);
    if (!p) { /* keep v->data valid, report error */ return -1; }
    v->data = p; v->cap = ncap;
}
v->data[v->len++] = x;

NEVER assign realloc's result straight to the old pointer - on failure you'd lose it (memory leak). Use a temporary, check for NULL, then assign.""",
            mcq("Why double the capacity?", ["Appends become O(1) amortised", "It's required", "To save memory", "To align data"], 0),
            mcq("Why use a temporary pointer with realloc?", ["On failure the old block must stay reachable", "It's faster", "Syntax", "To avoid free"], 0),
            mcq("What does realloc return on failure?", ["NULL", "The old pointer", "0 bytes", "An error code"], 0),
            run("Read integers until EOF into a dynamic array that starts at capacity 2 and doubles with realloc. Print how many were read and their sum.", "c",
                [t("five", stdin="1 2 3 4 5"), t("none", stdin="")], ["5 15", "0 0"],
                prog('int *a = NULL;\nint len = 0, cap = 0, x;\nwhile (scanf("%d", &x) == 1) {\n    if (len == cap) {\n        int ncap = cap ? cap * 2 : 2;\n        int *p = realloc(a, ncap * sizeof *p);\n        if (!p) { free(a); return 1; }\n        a = p;\n        cap = ncap;\n    }\n    a[len++] = x;\n}\nlong long sum = 0;\nfor (int i = 0; i < len; i++) sum += a[i];\nprintf("%d %lld\\n", len, sum);\nfree(a);',
                     includes=STD),
                starter=STARTER, require=[r"realloc", r"free"], fallback=[r"realloc\s*\(", r"free\s*\(", r"scanf"]),
        ),
        lesson(
            "2-D arrays on the heap",
            """A matrix of R rows and C columns can be ONE block indexed manually (fast, simple to free):

int *m = malloc(R * C * sizeof *m);
m[r * C + c] = 7;            // row-major indexing
free(m);

or an array of row pointers (allows ragged rows, needs a free per row):

int **m = malloc(R * sizeof *m);
for (int r = 0; r < R; r++) m[r] = calloc(C, sizeof **m);
...  for (r) free(m[r]);  free(m);

calloc zero-initialises. Always free in the reverse of allocation order, and check R*C doesn't overflow.""",
            mcq("What is row-major indexing?", ["m[r * C + c]", "m[c * R + r]", "m[r][c] only", "m[r + c]"], 0),
            mcq("What does calloc add over malloc?", ["Zeroed memory", "Larger blocks", "Thread safety", "Alignment"], 0),
            mcq("How many free calls does an int** matrix need?", ["R + 1", "1", "R", "C"], 0),
            run("Read R and C then R×C numbers into a single malloc'd block. Print the sum of each row, one per line.", "c",
                [t("2x3", stdin="2 3\n1 2 3\n4 5 6"), t("1x1", stdin="1 1\n9")], ["6\n15", "9"],
                prog('int R, C;\nscanf("%d %d", &R, &C);\nint *m = malloc((size_t)R * C * sizeof *m);\nfor (int i = 0; i < R * C; i++) scanf("%d", &m[i]);\nfor (int r = 0; r < R; r++) {\n    int sum = 0;\n    for (int c = 0; c < C; c++) sum += m[r * C + c];\n    printf("%d\\n", sum);\n}\nfree(m);',
                     includes=STD),
                starter=STARTER, require=[r"malloc|calloc", r"free"], fallback=[r"malloc\s*\(|calloc\s*\(", r"free\s*\(", r"\*\s*C|C\s*\*"]),
        ),
        lesson(
            "Arrays of strings",
            """An array of strings is an array of char pointers:

char *words[100];                  // 100 pointers - each must point at its own storage
words[i] = strdup(buf);            // POSIX: malloc + copy  (or malloc(strlen+1) + strcpy)
...
for (i) free(words[i]);

Common mistake: storing the address of the SAME buffer each time - every entry then shows the last word read. Copy each string into its own allocation. Sort with qsort and a comparator that calls strcmp on the dereferenced pointers.

int cmp(const void *a, const void *b) { return strcmp(*(char *const *)a, *(char *const *)b); }""",
            mcq("What is the classic bug when reading words in a loop?", ["Storing the same buffer address for each", "Using strcmp", "Using qsort", "Calling free"], 0),
            mcq("What does a char *words[100] hold?", ["100 pointers", "100 strings inline", "100 chars", "A matrix"], 0),
            mcq("What must you free for strdup'd strings?", ["Each string", "Only the array", "Nothing", "The buffer"], 0),
            run("Read n words, store each in its own malloc'd copy, sort them alphabetically with qsort and print them one per line, then free everything.", "c",
                [t("fruit", stdin="3\npear apple fig"), t("one", stdin="1\nsolo")], ["apple\nfig\npear", "solo"],
                prog('int n;\nscanf("%d", &n);\nchar **w = malloc(n * sizeof *w);\nfor (int i = 0; i < n; i++) {\n    char buf[64];\n    scanf("%63s", buf);\n    w[i] = malloc(strlen(buf) + 1);\n    strcpy(w[i], buf);\n}\nqsort(w, n, sizeof *w, cmp_str);\nfor (int i = 0; i < n; i++) {\n    printf("%s\\n", w[i]);\n    free(w[i]);\n}\nfree(w);',
                     includes=STR,
                     before='int cmp_str(const void *a, const void *b) {\n    return strcmp(*(char *const *)a, *(char *const *)b);\n}\n\n'),
                starter=STARTER, require=[r"qsort", r"strcmp", r"free"], fallback=[r"qsort\s*\(", r"strcmp\s*\(", r"free\s*\("]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Function pointers",
        lesson(
            "Callbacks",
            """A function pointer stores the address of a function so you can pass behaviour as an argument:

int add(int a, int b) { return a + b; }
int (*op)(int, int) = add;          // pointer to a function taking two ints and returning int
printf("%d", op(2, 3));             // 5

typedef int (*BinOp)(int, int);     // typedef makes it readable
int apply(BinOp f, int a, int b) { return f(a, b); }
apply(add, 2, 3);

The standard library uses this in qsort and bsearch - they call YOUR comparison function.""",
            mcq("What does int (*op)(int, int) declare?", ["A pointer to a function (int,int) returning int", "A function returning a pointer", "An int pointer", "An array"], 0),
            mcq("Which std function takes a callback?", ["qsort", "printf", "strlen", "malloc"], 0),
            mcq("Why typedef a function pointer type?", ["The syntax is hard to read otherwise", "It is faster", "It is required", "To avoid &"], 0),
            run("Write add, sub and mul functions and a function apply(BinOp f, int a, int b). Read 'op a b' (op is a, s or m) and print the result using the matching function pointer.", "c",
                [t("add", stdin="a 3 4"), t("sub", stdin="s 3 10"), t("mul", stdin="m 6 7")], ["7", "-7", "42"],
                prog('char op;\nint a, b;\nscanf(" %c %d %d", &op, &a, &b);\nBinOp f = op == \'a\' ? add : op == \'s\' ? sub : mul;\nprintf("%d\\n", apply(f, a, b));',
                     before='typedef int (*BinOp)(int, int);\n\nint add(int a, int b) { return a + b; }\nint sub(int a, int b) { return a - b; }\nint mul(int a, int b) { return a * b; }\n\nint apply(BinOp f, int a, int b) {\n    return f(a, b);\n}\n\n'),
                starter=STARTER, require=[r"\(\s*\*\s*\w+\s*\)\s*\("], fallback=[r"\(\s*\*\s*\w+\s*\)\s*\(", r"apply\s*\("]),
        ),
        lesson(
            "Dispatch tables",
            """An array of function pointers replaces a long if/else or switch with a table lookup:

typedef struct { const char *name; int (*fn)(int, int); } Op;
Op ops[] = { {"add", add}, {"sub", sub}, {"mul", mul} };
for (size_t i = 0; i < sizeof ops / sizeof ops[0]; i++)
    if (strcmp(ops[i].name, cmd) == 0) return ops[i].fn(a, b);

Adding a command is then ONE line in the table. This pattern powers command interpreters, state machines and plugin systems. sizeof ops / sizeof ops[0] computes the element count.""",
            mcq("What does a dispatch table replace?", ["Long if/else or switch chains", "Loops", "Arrays", "Structs"], 0),
            mcq("How do you count elements of a static array?", ["sizeof arr / sizeof arr[0]", "strlen(arr)", "arr.length", "len(arr)"], 0),
            mcq("How many edits to add a new command to the table?", ["One new line in the table", "A new function in every file", "Rewrite main", "None"], 0),
            run("Build a dispatch table of {name, function} for add, sub, mul, max. Read 'name a b' and print the result, or UNKNOWN if the name is not in the table.", "c",
                [t("max", stdin="max 4 9"), t("mul", stdin="mul 6 7"), t("unknown", stdin="pow 2 3")], ["9", "42", "UNKNOWN"],
                prog('char name[16];\nint a, b;\nscanf("%15s %d %d", name, &a, &b);\nfor (size_t i = 0; i < sizeof ops / sizeof ops[0]; i++) {\n    if (strcmp(ops[i].name, name) == 0) {\n        printf("%d\\n", ops[i].fn(a, b));\n        return 0;\n    }\n}\nprintf("UNKNOWN\\n");',
                     includes=STR,
                     before='int add(int a, int b) { return a + b; }\nint sub(int a, int b) { return a - b; }\nint mul(int a, int b) { return a * b; }\nint mx(int a, int b) { return a > b ? a : b; }\n\ntypedef struct {\n    const char *name;\n    int (*fn)(int, int);\n} Op;\n\nstatic const Op ops[] = {{"add", add}, {"sub", sub}, {"mul", mul}, {"max", mx}};\n\n'),
                starter=STARTER, require=[r"sizeof", r"strcmp"], fallback=[r"typedef\s+struct", r"sizeof", r"strcmp\s*\("]),
        ),
        lesson(
            "qsort with custom comparators",
            """qsort(base, count, size, compare) sorts any array. The comparator receives two const void* and returns <0, 0 or >0:

typedef struct { char name[16]; int score; } P;
int by_score_desc(const void *a, const void *b) {
    const P *x = a, *y = b;
    if (x->score != y->score) return y->score - x->score;     // watch overflow for huge values - use comparisons
    return strcmp(x->name, y->name);
}
qsort(people, n, sizeof people[0], by_score_desc);

Cast the void pointers back to the real type inside the comparator. For ints prefer (a > b) - (a < b) over subtraction (which can overflow).""",
            mcq("What does a comparator return for 'a before b'?", ["A negative number", "A positive number", "0", "1 always"], 0),
            mcq("Why avoid a - b for ints in comparators?", ["It can overflow", "It is slow", "It is illegal", "It sorts descending"], 0),
            mcq("What are the comparator's parameters?", ["const void * pointers to elements", "ints", "indices", "strings"], 0),
            run("Read n lines 'name score'. Print the names ordered by score descending, ties alphabetically (qsort with a struct comparator).", "c",
                [t("ties", stdin="4\nbo 80\nada 90\ncy 80\ndee 70"), t("one", stdin="1\nsolo 5")], ["ada\nbo\ncy\ndee", "solo"],
                prog('int n;\nscanf("%d", &n);\nP p[100];\nfor (int i = 0; i < n; i++) scanf("%15s %d", p[i].name, &p[i].score);\nqsort(p, n, sizeof p[0], by_score_desc);\nfor (int i = 0; i < n; i++) printf("%s\\n", p[i].name);',
                     includes=STR,
                     before='typedef struct {\n    char name[16];\n    int score;\n} P;\n\nint by_score_desc(const void *a, const void *b) {\n    const P *x = a, *y = b;\n    if (x->score != y->score) return (y->score > x->score) - (y->score < x->score);\n    return strcmp(x->name, y->name);\n}\n\n'),
                starter=STARTER, require=[r"qsort"], fallback=[r"qsort\s*\(", r"const\s+void\s*\*", r"strcmp"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Strings & parsing",
        lesson(
            "strtol and error checking",
            """atoi can't report errors (it returns 0 for both '0' and 'abc'). strtol can:

char *end;
errno = 0;
long v = strtol(s, &end, 10);
if (end == s)        { /* no digits at all */ }
else if (*end != '\\0') { /* trailing junk like '12abc' */ }
else if (errno == ERANGE) { /* out of range */ }

end points at the first character NOT converted. Valid input means end != s, *end == '\\0' and errno unchanged. Use strtod for doubles. Always validate user input before trusting it.""",
            mcq("What is wrong with atoi?", ["It can't tell '0' from invalid text", "It's slow", "It's removed", "It needs a loop"], 0),
            mcq("What does end point at after strtol?", ["The first unconverted character", "The start", "The last digit", "NULL"], 0),
            mcq("How do you detect trailing junk?", ["*end != '\\0'", "end == NULL", "errno == 0", "v == 0"], 0),
            run("Read n tokens. For each print the integer value if the whole token is a valid decimal integer, otherwise BAD (use strtol and check end).", "c",
                [t("mix", stdin="4\n42 -7 12abc xyz"), t("one", stdin="1\n0")], ["42\n-7\nBAD\nBAD", "0"],
                prog('int n;\nscanf("%d", &n);\nwhile (n--) {\n    char tok[64];\n    scanf("%63s", tok);\n    char *end;\n    long v = strtol(tok, &end, 10);\n    if (end == tok || *end != \'\\0\') printf("BAD\\n");\n    else printf("%ld\\n", v);\n}',
                     includes=STD),
                starter=STARTER, require=[r"strtol", r"end"], fallback=[r"strtol\s*\(", r"\*\s*end", r"BAD"]),
        ),
        lesson(
            "Tokenizing with strtok and sscanf",
            """strtok splits a string on delimiter characters - it MODIFIES the string and keeps hidden state, so use it on a copy and don't nest calls:

char *tok = strtok(line, ",");
while (tok) { ...; tok = strtok(NULL, ","); }

sscanf parses fixed layouts: sscanf(line, "%15[^,],%d,%lf", name, &qty, &price) returns how many fields matched - check it equals the expected count. %[^,] reads everything up to a comma; the number after % limits the length so it can't overflow the buffer.""",
            mcq("What does strtok do to its input string?", ["Modifies it (writes NUL bytes)", "Nothing", "Copies it", "Frees it"], 0),
            mcq("What does sscanf return?", ["The number of fields matched", "The string length", "Always 0", "A pointer"], 0),
            mcq("What does %15[^,] read?", ["Up to 15 chars until a comma", "15 digits", "A comma", "The rest of the line"], 0),
            run("Read n lines 'item,qty,price' (e.g. apple,2,1.50). Skip lines that do not parse into all three fields (check sscanf's return). Print the total qty*price with 2 decimals and then the number of skipped lines.", "c",
                [t("one bad", stdin="3\napple,2,1.50\nbad,x,2\npear,1,0.75"), t("good", stdin="1\nfig,4,2.5")], ["3.75\n1", "10.00\n0"],
                prog('int n;\nscanf("%d ", &n);\ndouble total = 0;\nint bad = 0;\nwhile (n--) {\n    char line[128], name[32];\n    int qty;\n    double price;\n    if (!fgets(line, sizeof line, stdin)) break;\n    if (sscanf(line, "%31[^,],%d,%lf", name, &qty, &price) == 3) total += qty * price;\n    else bad++;\n}\nprintf("%.2f\\n%d\\n", total, bad);'),
                starter=STARTER, require=[r"sscanf"], fallback=[r"sscanf\s*\(", r"==\s*3", r"fgets"]),
        ),
        lesson(
            "A word-frequency counter",
            """Putting strings and structs together: count how often each word appears.

typedef struct { char word[32]; int count; } Entry;
Entry table[1000]; int used = 0;
// for each word: linear search for it; if found count++, else add a new entry

Linear search is fine for small inputs (O(words × distinct)); a hash table scales better. Sorting the final table with qsort gives a report. Lower-case words first with tolower so 'The' and 'the' are the same.""",
            mcq("What is the cost of the linear-search table?", ["O(words × distinct)", "O(1)", "O(log n)", "O(n!)"], 0),
            mcq("Which function lower-cases a char?", ["tolower", "lower", "strlwr", "downcase"], 0),
            mcq("What scales better than a linear table?", ["A hash table", "Another array", "A bigger buffer", "Recursion"], 0),
            run("Read words until EOF (lower-case them) and print each distinct word with its count in alphabetical order as 'word count', one per line.", "c",
                [t("repeats", stdin="b A c a b a"), t("one", stdin="solo")], ["a 3\nb 2\nc 1", "solo 1"],
                prog('Entry table[1000];\nint used = 0;\nchar w[32];\nwhile (scanf("%31s", w) == 1) {\n    for (char *p = w; *p; p++) *p = (char)tolower((unsigned char)*p);\n    int i;\n    for (i = 0; i < used; i++) {\n        if (strcmp(table[i].word, w) == 0) { table[i].count++; break; }\n    }\n    if (i == used) {\n        strcpy(table[used].word, w);\n        table[used].count = 1;\n        used++;\n    }\n}\nqsort(table, used, sizeof table[0], cmp_entry);\nfor (int i = 0; i < used; i++) printf("%s %d\\n", table[i].word, table[i].count);',
                     includes="#include <ctype.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n",
                     before='typedef struct {\n    char word[32];\n    int count;\n} Entry;\n\nint cmp_entry(const void *a, const void *b) {\n    return strcmp(((const Entry *)a)->word, ((const Entry *)b)->word);\n}\n\n'),
                starter=STARTER, require=[r"strcmp", r"tolower"], fallback=[r"strcmp\s*\(", r"tolower\s*\(", r"qsort|count"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Data structures",
        lesson(
            "Queue as a ring buffer",
            """A ring (circular) buffer is a fixed-size queue with O(1) push and pop and no shifting:

typedef struct { int data[N]; int head, count; } Queue;
void push(Queue *q, int x) { q->data[(q->head + q->count) % N] = x; q->count++; }
int pop(Queue *q)          { int x = q->data[q->head]; q->head = (q->head + 1) % N; q->count--; return x; }

The modulo wraps indexes round to the start. Check count before push (full) and pop (empty). Used in keyboards, network drivers and audio buffers.""",
            mcq("What does the modulo do in a ring buffer?", ["Wraps the index back to the start", "Counts items", "Sorts", "Frees memory"], 0),
            mcq("What are push and pop costs?", ["O(1)", "O(n)", "O(log n)", "O(n²)"], 0),
            mcq("What must you check before pop?", ["That count > 0", "That head == 0", "That N is even", "Nothing"], 0),
            run("Implement a ring-buffer queue of capacity 4. Read commands until 'end': 'push x' prints FULL when full, otherwise nothing; 'pop' prints the front value or EMPTY.", "c",
                [t("flow", stdin="push 1\npush 2\npop\npush 3\npush 4\npush 5\npush 6\npop\nend"), t("empty", stdin="pop\nend")], ["1\nFULL\n2", "EMPTY"],
                prog('Queue q = {{0}, 0, 0};\nchar cmd[8];\nwhile (scanf("%7s", cmd) == 1 && cmd[0] != \'e\') {\n    if (cmd[1] == \'u\') {\n        int x;\n        scanf("%d", &x);\n        if (q.count == N) printf("FULL\\n");\n        else {\n            q.data[(q.head + q.count) % N] = x;\n            q.count++;\n        }\n    } else if (q.count == 0) {\n        printf("EMPTY\\n");\n    } else {\n        printf("%d\\n", q.data[q.head]);\n        q.head = (q.head + 1) % N;\n        q.count--;\n    }\n}',
                     before='#define N 4\n\ntypedef struct {\n    int data[N];\n    int head, count;\n} Queue;\n\n'),
                starter=STARTER, require=[r"%\s*N|%\s*4"], fallback=[r"%\s*N|%\s*4", r"head", r"count"]),
        ),
        lesson(
            "Hash tables",
            """A hash table maps keys to values in average O(1). A hash function turns the key into an index; collisions (two keys, one slot) are handled by CHAINING - each slot holds a linked list.

unsigned hash(const char *s) { unsigned h = 5381; while (*s) h = h * 33 + (unsigned char)*s++; return h; }
size_t slot = hash(key) % TABLE_SIZE;

Lookup: hash, go to the slot, walk the list comparing keys with strcmp. A good hash spreads keys evenly; a bad one sends everything to one slot and degrades to O(n). Real tables also grow when the load factor gets high.""",
            mcq("What is a hash collision?", ["Two keys mapping to the same slot", "A crash", "A full table", "A sorted list"], 0),
            mcq("How does chaining resolve collisions?", ["Each slot holds a linked list", "It overwrites", "It rehashes forever", "It errors"], 0),
            mcq("What is average lookup cost?", ["O(1)", "O(n)", "O(log n)", "O(n²)"], 0),
            run("Implement a chained hash table (size 16) from string to int. Read n commands: 'set key v' or 'get key' (print the value, or MISSING). Use the djb2 hash.", "c",
                [t("flow", stdin="5\nset a 1\nset b 2\nset a 9\nget a\nget z"), t("one", stdin="2\nset x 5\nget x")], ["9\nMISSING", "5"],
                prog('int n;\nscanf("%d", &n);\nNode *table[SIZE] = {0};\nwhile (n--) {\n    char cmd[8], key[32];\n    scanf("%7s %31s", cmd, key);\n    unsigned slot = hash(key) % SIZE;\n    Node *p = table[slot];\n    while (p && strcmp(p->key, key) != 0) p = p->next;\n    if (cmd[0] == \'s\') {\n        int v;\n        scanf("%d", &v);\n        if (p) p->value = v;\n        else {\n            p = malloc(sizeof *p);\n            strcpy(p->key, key);\n            p->value = v;\n            p->next = table[slot];\n            table[slot] = p;\n        }\n    } else if (p) {\n        printf("%d\\n", p->value);\n    } else {\n        printf("MISSING\\n");\n    }\n}\nfor (int i = 0; i < SIZE; i++) {\n    while (table[i]) {\n        Node *next = table[i]->next;\n        free(table[i]);\n        table[i] = next;\n    }\n}',
                     includes=STR,
                     before='#define SIZE 16\n\ntypedef struct Node {\n    char key[32];\n    int value;\n    struct Node *next;\n} Node;\n\nunsigned hash(const char *s) {\n    unsigned h = 5381;\n    while (*s) h = h * 33 + (unsigned char)*s++;\n    return h;\n}\n\n'),
                starter=STARTER, require=[r"hash", r"malloc", r"free"], fallback=[r"hash\s*\(", r"malloc\s*\(", r"struct\s+Node", r"strcmp"]),
        ),
        lesson(
            "Binary heap",
            """A binary heap stores a complete binary tree in an array: for index i the children are 2i+1 and 2i+2, the parent is (i-1)/2. In a MIN-heap every parent <= its children, so a[0] is the minimum.

push: put the value at the end, then 'sift up' while it is smaller than its parent.
pop: take a[0], move the last element to the root, then 'sift down' - swap with the smaller child until the order holds.

push and pop are O(log n); peek is O(1). Heaps power priority queues, Dijkstra's algorithm and heap sort.""",
            mcq("Where is a heap's minimum?", ["a[0]", "The last element", "The middle", "Anywhere"], 0),
            mcq("What are the children of index i?", ["2i+1 and 2i+2", "i+1 and i+2", "i/2", "2i and 3i"], 0),
            mcq("What does pop do after removing the root?", ["Moves the last element to the root and sifts down", "Sorts the array", "Deletes the heap", "Shifts all left"], 0),
            run("Implement a min-heap with push and pop. Read n numbers then k, push all numbers and print the k smallest in ascending order (by popping k times).", "c",
                [t("classic", stdin="6\n5 2 9 1 7 3\n3"), t("all", stdin="2\n8 4\n2")], ["1 2 3", "4 8"],
                prog('int n;\nscanf("%d", &n);\nint h[1000], size = 0;\nfor (int i = 0; i < n; i++) {\n    int x;\n    scanf("%d", &x);\n    int c = size++;\n    h[c] = x;\n    while (c > 0 && h[(c - 1) / 2] > h[c]) {\n        int p = (c - 1) / 2, tmp = h[p];\n        h[p] = h[c];\n        h[c] = tmp;\n        c = p;\n    }\n}\nint k;\nscanf("%d", &k);\nfor (int j = 0; j < k; j++) {\n    printf("%d%s", h[0], j + 1 < k ? " " : "\\n");\n    h[0] = h[--size];\n    int i = 0;\n    while (1) {\n        int l = 2 * i + 1, r = l + 1, m = i;\n        if (l < size && h[l] < h[m]) m = l;\n        if (r < size && h[r] < h[m]) m = r;\n        if (m == i) break;\n        int tmp = h[i];\n        h[i] = h[m];\n        h[m] = tmp;\n        i = m;\n    }\n}'),
                starter=STARTER, require=[r"2\s*\*\s*i\s*\+\s*1|\(\s*c\s*-\s*1\s*\)\s*/\s*2"], fallback=[r"2\s*\*\s*\w+\s*\+\s*1|-\s*1\s*\)\s*/\s*2", r"while"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Trees",
        lesson(
            "Binary search tree",
            """A BST keeps smaller keys on the left and larger on the right, so search, insert and delete take O(height) - O(log n) when balanced.

typedef struct Node { int key; struct Node *left, *right; } Node;
Node *insert(Node *root, int key) {
    if (!root) { Node *n = calloc(1, sizeof *n); n->key = key; return n; }
    if (key < root->key) root->left = insert(root->left, key);
    else if (key > root->key) root->right = insert(root->right, key);
    return root;
}

Returning the (possibly new) root and assigning the result keeps insertion simple. Duplicates are ignored here.""",
            mcq("Where do smaller keys go in a BST?", ["Left", "Right", "Root", "Anywhere"], 0),
            mcq("What is search cost in a balanced BST?", ["O(log n)", "O(n)", "O(1)", "O(n²)"], 0),
            mcq("Why return the root from insert?", ["A new node may become the root", "To print it", "Required by C", "To free it"], 0),
            run("Read n numbers into a BST (ignore duplicates) and print its in-order traversal (sorted order) separated by spaces, then free the tree.", "c",
                [t("mix", stdin="6\n5 2 8 2 9 1"), t("one", stdin="1\n4")], ["1 2 5 8 9", "4"],
                prog('int n;\nscanf("%d", &n);\nNode *root = NULL;\nwhile (n--) {\n    int x;\n    scanf("%d", &x);\n    root = insert(root, x);\n}\nint first = 1;\ninorder(root, &first);\nprintf("\\n");\nfree_tree(root);',
                     includes=STD,
                     before='typedef struct Node {\n    int key;\n    struct Node *left, *right;\n} Node;\n\nNode *insert(Node *root, int key) {\n    if (!root) {\n        Node *n = calloc(1, sizeof *n);\n        n->key = key;\n        return n;\n    }\n    if (key < root->key) root->left = insert(root->left, key);\n    else if (key > root->key) root->right = insert(root->right, key);\n    return root;\n}\n\nvoid inorder(const Node *r, int *first) {\n    if (!r) return;\n    inorder(r->left, first);\n    printf("%s%d", *first ? "" : " ", r->key);\n    *first = 0;\n    inorder(r->right, first);\n}\n\nvoid free_tree(Node *r) {\n    if (!r) return;\n    free_tree(r->left);\n    free_tree(r->right);\n    free(r);\n}\n\n'),
                starter=STARTER, require=[r"insert", r"inorder|in_order"], fallback=[r"struct\s+Node", r"insert\s*\(", r"left", r"right"]),
        ),
        lesson(
            "Tree height and recursion",
            """Most tree operations are naturally recursive: do something at the node, then recurse into the children.

int height(const Node *r) { if (!r) return 0; int l = height(r->left), rr = height(r->right); return 1 + (l > rr ? l : rr); }
int count(const Node *r) { return r ? 1 + count(r->left) + count(r->right) : 0; }

The base case (NULL -> 0) makes every call terminate. Recursion depth equals the tree height, so a degenerate (list-shaped) tree with a million nodes can overflow the stack - another reason to keep trees balanced.""",
            mcq("What is the base case for tree recursion?", ["NULL node", "A leaf's parent", "The root", "A value of 0"], 0),
            mcq("What does height return for an empty tree?", ["0", "1", "-1", "NULL"], 0),
            mcq("What risks a stack overflow?", ["Very deep (unbalanced) trees", "Wide trees", "Small trees", "Empty trees"], 0),
            run("Read n numbers into a BST (ignore duplicates). Print the number of nodes, the height (empty = 0) and the smallest key, one per line.", "c",
                [t("mix", stdin="5\n5 3 8 1 4"), t("chain", stdin="3\n1 2 3")], ["5\n3\n1", "3\n3\n1"],
                prog('int n;\nscanf("%d", &n);\nNode *root = NULL;\nwhile (n--) {\n    int x;\n    scanf("%d", &x);\n    root = insert(root, x);\n}\nNode *m = root;\nwhile (m->left) m = m->left;\nprintf("%d\\n%d\\n%d\\n", count(root), height(root), m->key);',
                     includes=STD,
                     before='typedef struct Node {\n    int key;\n    struct Node *left, *right;\n} Node;\n\nNode *insert(Node *root, int key) {\n    if (!root) {\n        Node *n = calloc(1, sizeof *n);\n        n->key = key;\n        return n;\n    }\n    if (key < root->key) root->left = insert(root->left, key);\n    else if (key > root->key) root->right = insert(root->right, key);\n    return root;\n}\n\nint height(const Node *r) {\n    if (!r) return 0;\n    int l = height(r->left), rr = height(r->right);\n    return 1 + (l > rr ? l : rr);\n}\n\nint count(const Node *r) {\n    return r ? 1 + count(r->left) + count(r->right) : 0;\n}\n\n'),
                starter=STARTER, require=[r"height", r"count"], fallback=[r"height\s*\(", r"count\s*\(", r"left"]),
        ),
        lesson(
            "BST search and range queries",
            """Searching follows one path: compare, then go left or right. Because of the ordering, a RANGE query can skip whole subtrees:

void range(const Node *r, int lo, int hi) {
    if (!r) return;
    if (lo < r->key) range(r->left, lo, hi);        // left subtree may hold keys in range
    if (lo <= r->key && r->key <= hi) visit(r);
    if (r->key < hi) range(r->right, lo, hi);       // right subtree may hold keys in range
}

Only subtrees that can contain matches are visited, so a range query costs O(height + results).""",
            mcq("Why can a range query skip subtrees?", ["The BST ordering rules out whole subtrees", "Recursion skips them", "Memory limits", "It can't"], 0),
            mcq("What is a range query's cost?", ["O(height + results)", "O(n)", "O(1)", "O(n²)"], 0),
            mcq("When do we go left in range()?", ["When lo < key", "Always", "When hi > key", "Never"], 0),
            run("Read n numbers into a BST (ignore duplicates), then lo and hi. Print every key in [lo, hi] in ascending order separated by spaces (or NONE), using a pruned in-order traversal.", "c",
                [t("some", stdin="6\n5 2 8 1 9 6\n2 8"), t("none", stdin="2\n1 2\n5 9")], ["2 5 6 8", "NONE"],
                prog('int n;\nscanf("%d", &n);\nNode *root = NULL;\nwhile (n--) {\n    int x;\n    scanf("%d", &x);\n    root = insert(root, x);\n}\nint lo, hi, found = 0;\nscanf("%d %d", &lo, &hi);\nrange(root, lo, hi, &found);\nprintf("%s", found ? "\\n" : "NONE\\n");',
                     includes=STD,
                     before='typedef struct Node {\n    int key;\n    struct Node *left, *right;\n} Node;\n\nNode *insert(Node *root, int key) {\n    if (!root) {\n        Node *n = calloc(1, sizeof *n);\n        n->key = key;\n        return n;\n    }\n    if (key < root->key) root->left = insert(root->left, key);\n    else if (key > root->key) root->right = insert(root->right, key);\n    return root;\n}\n\nvoid range(const Node *r, int lo, int hi, int *found) {\n    if (!r) return;\n    if (lo < r->key) range(r->left, lo, hi, found);\n    if (lo <= r->key && r->key <= hi) {\n        printf("%s%d", *found ? " " : "", r->key);\n        *found = 1;\n    }\n    if (r->key < hi) range(r->right, lo, hi, found);\n}\n\n'),
                starter=STARTER, require=[r"range", r"lo", r"hi"], fallback=[r"range\s*\(", r"left", r"right", r"NONE"]),
        ),
    ),
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Algorithms in C",
        lesson(
            "Merge sort",
            """Merge sort splits an array, sorts both halves and merges them - O(n log n), stable, needing a temporary buffer.

void msort(int *a, int *tmp, int lo, int hi) {         // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) / 2;
    msort(a, tmp, lo, mid); msort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    memcpy(a + lo, tmp + lo, (hi - lo) * sizeof *a);
}""",
            mcq("What is merge sort's time complexity?", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 0),
            mcq("Why does it need tmp?", ["To hold merged results before copying back", "To count", "To free memory", "It doesn't"], 0),
            mcq("Why is <= used when merging?", ["It keeps equal items in order (stable)", "It's faster", "It avoids overflow", "It's required"], 0),
            run("Read n then n integers and sort them with your own merge sort (no qsort); print them separated by spaces.", "c",
                [t("mix", stdin="6\n5 2 9 1 5 6"), t("one", stdin="1\n7")], ["1 2 5 5 6 9", "7"],
                prog('int n;\nscanf("%d", &n);\nint *a = malloc(n * sizeof *a), *tmp = malloc(n * sizeof *tmp);\nfor (int i = 0; i < n; i++) scanf("%d", &a[i]);\nmsort(a, tmp, 0, n);\nfor (int i = 0; i < n; i++) printf("%d%s", a[i], i + 1 < n ? " " : "\\n");\nfree(a);\nfree(tmp);',
                     includes=STR,
                     before='void msort(int *a, int *tmp, int lo, int hi) {\n    if (hi - lo < 2) return;\n    int mid = (lo + hi) / 2;\n    msort(a, tmp, lo, mid);\n    msort(a, tmp, mid, hi);\n    int i = lo, j = mid, k = lo;\n    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];\n    while (i < mid) tmp[k++] = a[i++];\n    while (j < hi) tmp[k++] = a[j++];\n    memcpy(a + lo, tmp + lo, (hi - lo) * sizeof *a);\n}\n\n'),
                starter=STARTER, require=[r"msort|merge"], forbid=[r"qsort"], fallback=[r"msort|mergesort|merge_sort", r"mid", r"while"]),
        ),
        lesson(
            "Binary search",
            """Binary search halves a sorted range each step - O(log n):

int lo = 0, hi = n - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;      // (lo + hi) / 2 can overflow
    if (a[mid] == x) return mid;
    if (a[mid] < x) lo = mid + 1; else hi = mid - 1;
}
return -1;

The library version is bsearch(&key, a, n, sizeof a[0], cmp). The same loop shape finds the first element >= x ('lower bound') by shrinking hi to mid instead of returning.""",
            mcq("Why write lo + (hi - lo) / 2?", ["Avoids integer overflow", "It's faster", "It's required", "It rounds up"], 0),
            mcq("Binary search needs the data to be…", ["Sorted", "Unique", "Small", "Positive"], 0),
            mcq("What is the std function?", ["bsearch", "bfind", "search", "lookup"], 0),
            run("Read n sorted integers then q queries. For each query print its index (0-based) or -1. Write the loop yourself (no bsearch).", "c",
                [t("some", stdin="5\n1 3 5 7 9\n3\n7 4 1"), t("one", stdin="1\n4\n2\n4 5")], ["3\n-1\n0", "0\n-1"],
                prog('int n;\nscanf("%d", &n);\nint a[1000];\nfor (int i = 0; i < n; i++) scanf("%d", &a[i]);\nint q;\nscanf("%d", &q);\nwhile (q--) {\n    int x, lo = 0, hi = n - 1, ans = -1;\n    scanf("%d", &x);\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (a[mid] == x) { ans = mid; break; }\n        if (a[mid] < x) lo = mid + 1; else hi = mid - 1;\n    }\n    printf("%d\\n", ans);\n}'),
                starter=STARTER, require=[r"while", r"mid"], forbid=[r"bsearch"], fallback=[r"while\s*\(\s*lo\s*<=\s*hi", r"mid"]),
        ),
        lesson(
            "BFS on a grid",
            """Breadth-first search with a queue finds the fewest steps in an unweighted grid. In C a plain array works as the queue:

int qr[MAX], qc[MAX], head = 0, tail = 0;
dist[sr][sc] = 0;  qr[tail] = sr; qc[tail++] = sc;
while (head < tail) {
    int r = qr[head], c = qc[head++];
    for (int d = 0; d < 4; d++) {
        int nr = r + dr[d], nc = c + dc[d];
        if (in bounds && grid[nr][nc] != '#' && dist[nr][nc] == -1) { dist[nr][nc] = dist[r][c] + 1; qr[tail] = nr; qc[tail++] = nc; }
    }
}

Each cell enters the queue at most once, so MAX = rows × columns is enough. Distances start at -1 (unvisited).""",
            mcq("What does BFS guarantee in an unweighted grid?", ["Fewest steps", "Most steps", "A random path", "Cycles only"], 0),
            mcq("How big must the array queue be?", ["rows × columns", "rows", "columns", "4"], 0),
            mcq("What does dist == -1 mean here?", ["Not yet visited", "A wall", "The goal", "Start"], 0),
            run("Read R and C then R rows ('.' open, '#' wall, 'S' start, 'E' end). Print the fewest steps (up/down/left/right) from S to E, or -1 if unreachable.", "c",
                [t("open", stdin="3 4\nS...\n.##.\n...E"), t("blocked", stdin="2 3\nS#E\n.#."), t("adjacent", stdin="1 2\nSE")], ["5", "-1", "1"],
                prog('int R, C, sr = 0, sc = 0, er = 0, ec = 0;\nchar g[30][30];\nint dist[30][30];\nscanf("%d %d", &R, &C);\nfor (int r = 0; r < R; r++) {\n    scanf("%29s", g[r]);\n    for (int c = 0; c < C; c++) {\n        dist[r][c] = -1;\n        if (g[r][c] == \'S\') { sr = r; sc = c; }\n        if (g[r][c] == \'E\') { er = r; ec = c; }\n    }\n}\nint qr[900], qc[900], head = 0, tail = 0;\nint dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};\ndist[sr][sc] = 0;\nqr[tail] = sr;\nqc[tail++] = sc;\nwhile (head < tail) {\n    int r = qr[head], c = qc[head++];\n    for (int d = 0; d < 4; d++) {\n        int nr = r + dr[d], nc = c + dc[d];\n        if (nr >= 0 && nr < R && nc >= 0 && nc < C && g[nr][nc] != \'#\' && dist[nr][nc] == -1) {\n            dist[nr][nc] = dist[r][c] + 1;\n            qr[tail] = nr;\n            qc[tail++] = nc;\n        }\n    }\n}\nprintf("%d\\n", dist[er][ec]);'),
                starter=STARTER, require=[r"head", r"tail"], fallback=[r"head", r"tail", r"dist"]),
        ),
    ),
)
