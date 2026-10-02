"""C projects - one at the end of each section (added to units 8, 12 and 16)."""
from .c_adv import STARTER, prog
from .dsl import project, run, t

# ------------------------------------------------------------------ Beginner: temperature log
TEMP_INC = "#include <stdio.h>\n#include <stdlib.h>\n"
READ = '''int n;
if (scanf("%d", &n) != 1 || n <= 0) return 0;
double *t = malloc((size_t)n * sizeof *t);
if (!t) return 1;
for (int i = 0; i < n; i++) scanf("%lf", &t[i]);
double min = t[0], max = t[0], sum = 0;
for (int i = 0; i < n; i++) {
    if (t[i] < min) min = t[i];
    if (t[i] > max) max = t[i];
    sum += t[i];
}
double avg = sum / n;
printf("min %.1f max %.1f avg %.1f\\n", min, max, avg);
'''
ABOVE = '''int above = 0;
for (int i = 0; i < n; i++)
    if (t[i] > avg) above++;
printf("days above average: %d\\n", above);
'''
STREAK = '''int best = 1, run = 1;
for (int i = 1; i < n; i++) {
    run = t[i] > t[i - 1] ? run + 1 : 1;
    if (run > best) best = run;
}
printf("longest warming streak: %d days\\n", best);
'''
T1 = prog(READ + "free(t);", includes=TEMP_INC)
T2 = prog(READ + ABOVE + "free(t);", includes=TEMP_INC)
T3 = prog(READ + ABOVE + STREAK + "free(t);", includes=TEMP_INC)
WEEK = "7\n12.5 14 13 15.5 17 18 9"

BEGINNER = project(
    "Project: Temperature log",
    "Analyse a week of temperatures using a dynamically allocated array:\n\n1. Read the readings with malloc and print "
    "min, max and average.\n2. Count the days above average.\n3. Find the longest warming streak.\n\nInput: the number "
    "of readings, then the readings.",
    run("Step 1 - Read n, malloc an array of n doubles, read the readings and print 'min X max Y avg Z' (1 decimal). "
        "Free the memory.", "c", [t("week", stdin=WEEK), t("one", stdin="1\n-3")],
        ["min 9.0 max 18.0 avg 14.1", "min -3.0 max -3.0 avg -3.0"], T1, starter=STARTER, require=[r"malloc", r"free\s*\("],
        fallback=[r"malloc", r"free\s*\(", r"%\.1f"]),
    run("Step 2 - Also print 'days above average: K'.", "c", [t("week", stdin=WEEK), t("one", stdin="1\n-3")],
        ["min 9.0 max 18.0 avg 14.1\ndays above average: 3", "min -3.0 max -3.0 avg -3.0\ndays above average: 0"],
        T2, starter=T1, carry=True, fallback=[r"days above average"]),
    run("Step 3 - Finally print 'longest warming streak: K days' - the most consecutive readings that each rise.", "c",
        [t("week", stdin=WEEK), t("one", stdin="1\n-3")],
        ["min 9.0 max 18.0 avg 14.1\ndays above average: 3\nlongest warming streak: 4 days",
         "min -3.0 max -3.0 avg -3.0\ndays above average: 0\nlongest warming streak: 1 days"],
        T3, starter=T2, carry=True, fallback=[r"warming streak"]),
)

# ------------------------------------------------------------------ Intermediate: contacts book
CB_INC = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
CONTACT = '''typedef struct {
    char name[32];
    char phone[16];
} Contact;

'''
CMP = '''static int by_name(const void *a, const void *b) {
    return strcmp(((const Contact *)a)->name, ((const Contact *)b)->name);
}

'''
LOAD = '''Contact book[100];
int n = 0;
char name[32], phone[16];
while (n < 100 && scanf("%31s", name) == 1 && strcmp(name, "---") != 0) {
    if (scanf("%15s", phone) != 1) break;
    snprintf(book[n].name, sizeof book[n].name, "%s", name);
    snprintf(book[n].phone, sizeof book[n].phone, "%s", phone);
    n++;
}
printf("%d contacts\\n", n);
'''
SORT = '''qsort(book, (size_t)n, sizeof book[0], by_name);
for (int i = 0; i < n; i++) printf("%-10s %s\\n", book[i].name, book[i].phone);
'''
LOOKUP = '''while (scanf("%31s", name) == 1) {
    Contact key;
    snprintf(key.name, sizeof key.name, "%s", name);
    Contact *hit = bsearch(&key, book, (size_t)n, sizeof book[0], by_name);
    printf("%s: %s\\n", name, hit ? hit->phone : "not found");
}
'''
CB1 = prog(LOAD, includes=CB_INC, before=CONTACT)
CB2 = prog(LOAD + SORT, includes=CB_INC, before=CONTACT + CMP)
CB3 = prog(LOAD + SORT + LOOKUP, includes=CB_INC, before=CONTACT + CMP)
BOOK = "zoe 555-0101\nada 555-0199\nbo 555-0123\n---\nbo\nmax\nada"

INTERMEDIATE = project(
    "Project: Contacts book",
    "Build a phone book with structs, qsort and bsearch:\n\n1. Load 'name phone' pairs into an array of structs (until "
    "a line '---').\n2. Sort and print them alphabetically.\n3. Answer lookups with binary search.",
    run("Step 1 - typedef struct Contact { name, phone }. Read pairs until '---' (or the input ends) into an array and "
        "print 'N contacts'. Copy strings safely with snprintf.", "c", [t("book", stdin=BOOK)], ["3 contacts"], CB1,
        starter=STARTER, require=[r"typedef\s+struct"], fallback=[r"typedef\s+struct", r"snprintf"]),
    run("Step 2 - Sort with qsort by name and print each as name padded to 10 characters, a space, then the phone "
        "(printf \"%-10s %s\").", "c", [t("book", stdin=BOOK)],
        ["3 contacts\nada        555-0199\nbo         555-0123\nzoe        555-0101"], CB2, starter=CB1, carry=True,
        fallback=[r"qsort\s*\(", r"%-10s"]),
    run("Step 3 - After '---', read names until the input ends and print 'name: phone' or 'name: not found', using "
        "bsearch on the sorted array.", "c", [t("book", stdin=BOOK)],
        ["3 contacts\nada        555-0199\nbo         555-0123\nzoe        555-0101\nbo: 555-0123\nmax: not found\nada: 555-0199"],
        CB3, starter=CB2, carry=True, require=[r"bsearch"], fallback=[r"bsearch\s*\(", r"not found"]),
)

# ------------------------------------------------------------------ Advanced: RPN calculator
RPN_INC = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
STACK = '''typedef struct {
    long items[64];
    int top;
} Stack;

static int push(Stack *s, long v) {
    if (s->top == 64) return 0;
    s->items[s->top++] = v;
    return 1;
}

static int pop(Stack *s, long *out) {
    if (s->top == 0) return 0;
    *out = s->items[--s->top];
    return 1;
}

'''
EVAL1 = '''static long eval(char *line) {
    Stack s = {.top = 0};
    for (char *tok = strtok(line, " \\n"); tok; tok = strtok(NULL, " \\n")) {
        if (strlen(tok) == 1 && strchr("+-*", tok[0])) {
            long b, a;
            pop(&s, &b);
            pop(&s, &a);
            push(&s, tok[0] == '+' ? a + b : tok[0] == '-' ? a - b : a * b);
        } else {
            push(&s, strtol(tok, NULL, 10));
        }
    }
    long result = 0;
    pop(&s, &result);
    return result;
}

'''
EVAL2 = '''/* returns 1 and stores the value on success, 0 on any error */
static int eval(char *line, long *result) {
    Stack s = {.top = 0};
    for (char *tok = strtok(line, " \\n"); tok; tok = strtok(NULL, " \\n")) {
        if (strlen(tok) == 1 && strchr("+-*/", tok[0])) {
            long b, a;
            if (!pop(&s, &b) || !pop(&s, &a)) return 0;
            if (tok[0] == '/' && b == 0) return 0;
            push(&s, tok[0] == '+' ? a + b : tok[0] == '-' ? a - b : tok[0] == '*' ? a * b : a / b);
        } else {
            char *end;
            long v = strtol(tok, &end, 10);
            if (*end != '\\0' || !push(&s, v)) return 0;
        }
    }
    return s.top == 1 && pop(&s, result);
}

'''
R1 = prog('''char line[256];
if (fgets(line, sizeof line, stdin)) printf("%ld\\n", eval(line));''', includes=RPN_INC, before=STACK + EVAL1)
R2 = prog('''char line[256];
long value;
if (fgets(line, sizeof line, stdin)) {
    if (eval(line, &value)) printf("%ld\\n", value);
    else printf("error\\n");
}''', includes=RPN_INC, before=STACK + EVAL2)
R3 = prog('''char line[256];
long value;
int ok = 0, bad = 0;
while (fgets(line, sizeof line, stdin)) {
    if (strspn(line, " \\n") == strlen(line)) continue;
    if (eval(line, &value)) {
        printf("%ld\\n", value);
        ok++;
    } else {
        printf("error\\n");
        bad++;
    }
}
printf("%d ok, %d errors\\n", ok, bad);''', includes=RPN_INC, before=STACK + EVAL2)

ADVANCED = project(
    "Project: RPN calculator",
    "Reverse Polish Notation puts the operator after its operands: '3 4 + 2 *' means (3 + 4) * 2. It's evaluated with a "
    "stack - the same trick compilers and calculators use.\n\n1. Evaluate one expression with + - *.\n2. Add / and "
    "error handling.\n3. Process many lines and summarise.",
    run("Step 1 - Implement a stack (struct with an array and top) and evaluate one line: numbers are pushed; + - * pop "
        "two values and push the result. Print the result.", "c",
        [t("basic", stdin="3 4 + 2 *"), t("negative", stdin="5 9 -")], ["14", "-4"], R1, starter=STARTER,
        require=[r"struct"], fallback=[r"push\s*\(", r"pop\s*\(", r"strtok"]),
    run("Step 2 - Add '/' and print 'error' for division by zero, too few operands, junk tokens, or anything other than "
        "exactly one value left.", "c",
        [t("divide", stdin="20 4 /"), t("by zero", stdin="1 0 /"), t("underflow", stdin="1 +"), t("leftover", stdin="1 2"),
         t("junk", stdin="2 x +")], ["5", "error", "error", "error", "error"], R2, starter=R1, carry=True,
        fallback=[r"'/'", r"error"]),
    run("Step 3 - Evaluate every non-empty line until the input ends, then print 'K ok, E errors'.", "c",
        [t("lines", stdin="3 4 +\n\n1 0 /\n2 3 4 * +\n")], ["7\nerror\n14\n2 ok, 1 errors"], R3, starter=R2, carry=True,
        fallback=[r"while\s*\(\s*fgets", r"ok, %d errors"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
