"""C - Expert section, part 2 (units 24-29): dynamic programming, error-handling idioms, memory safety, integers &
bits, generic code with void*, capstones. Runnable code targets C11."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .c_adv import STARTER, prog

STD = "#include <stdio.h>\n#include <stdlib.h>\n"
STR = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Dynamic programming",
        lesson(
            "Memoization",
            """Memoization stores each subproblem's answer so it is computed once - turning exponential recursion into linear time.

long long memo[91];                       // 0 = not computed yet (fib(0) handled by the base case)
long long fib(int n) {
    if (n < 2) return n;
    if (memo[n]) return memo[n];
    return memo[n] = fib(n - 1) + fib(n - 2);
}

Plain fib(50) makes ~40 billion calls; memoized it makes about 100. Use long long: fib(80) doesn't fit in int.""",
            mcq("What does memoization save?", ["Results of earlier calls", "Memory", "Source code", "Threads"], 0),
            mcq("Plain recursive fib(n) is roughly…", ["Exponential", "Linear", "Constant", "Logarithmic"], 0),
            mcq("Why a long long array?", ["Values grow beyond int", "Speed", "Alignment", "Style"], 0),
            run("Read n (up to 80) and print the nth Fibonacci number (fib(0)=0, fib(1)=1) using memoization.", "c",
                [t("small", stdin="10"), t("big", stdin="80"), t("zero", stdin="0")], ["55", "23416728348467685", "0"],
                prog('int n;\nscanf("%d", &n);\nprintf("%lld\\n", fib(n));',
                     before='long long memo[91];\n\nlong long fib(int n) {\n    if (n < 2) return n;\n    if (memo[n]) return memo[n];\n    return memo[n] = fib(n - 1) + fib(n - 2);\n}\n\n'),
                starter=STARTER, require=[r"memo|cache", r"long long"], fallback=[r"long long", r"memo|cache", r"fib\s*\("]),
        ),
        lesson(
            "Coin change table",
            """Bottom-up DP fills a table from the smallest subproblem. Fewest coins to make an amount:

int best[amount + 1];                         // variable-length array (C99)
best[0] = 0;
for (int a = 1; a <= amount; a++) {
    best[a] = INF;
    for (int i = 0; i < k; i++)
        if (coins[i] <= a && best[a - coins[i]] != INF && best[a - coins[i]] + 1 < best[a]) best[a] = best[a - coins[i]] + 1;
}

Greedy 'biggest coin first' fails for {1,3,4} and amount 6 (greedy 4+1+1, best 3+3). DP is always right. Time O(amount × coins). For big amounts allocate the table with malloc instead of the stack.""",
            mcq("Why can greedy fail?", ["Biggest-first isn't always optimal", "It is slow", "It overflows", "It needs recursion"], 0),
            mcq("What is best[0]?", ["0 coins", "1", "INF", "-1"], 0),
            mcq("When should the table use malloc?", ["For big amounts (the stack is limited)", "Always", "Never", "For small ones"], 0),
            run("Read k coin values then an amount. Print the fewest coins needed, or -1 if impossible.", "c",
                [t("greedy trap", stdin="3\n1 3 4\n6"), t("impossible", stdin="1\n5\n3"), t("zero", stdin="2\n2 5\n0")], ["2", "-1", "0"],
                prog('int k;\nscanf("%d", &k);\nint coins[50];\nfor (int i = 0; i < k; i++) scanf("%d", &coins[i]);\nint amount;\nscanf("%d", &amount);\nconst int INF = 1000000000;\nint *best = malloc((amount + 1) * sizeof *best);\nbest[0] = 0;\nfor (int a = 1; a <= amount; a++) {\n    best[a] = INF;\n    for (int i = 0; i < k; i++) {\n        if (coins[i] <= a && best[a - coins[i]] != INF && best[a - coins[i]] + 1 < best[a]) best[a] = best[a - coins[i]] + 1;\n    }\n}\nprintf("%d\\n", best[amount] == INF ? -1 : best[amount]);\nfree(best);',
                     includes=STD),
                starter=STARTER, require=[r"best|dp"], fallback=[r"for", r"best|dp", r"INF|1000000000"]),
        ),
        lesson(
            "Longest common subsequence",
            """LCS compares two strings with a 2-D table: dp[i][j] = best for the first i letters of A and first j of B.

if (a[i-1] == b[j-1]) dp[i][j] = dp[i-1][j-1] + 1;
else dp[i][j] = dp[i-1][j] > dp[i][j-1] ? dp[i-1][j] : dp[i][j-1];

Row 0 and column 0 are 0 (empty prefix). The answer is dp[n][m]. A subsequence keeps order but may skip letters (ACE is a subsequence of ABCDE). Used in diff tools and DNA alignment. Declare the table static or on the heap - a big 2-D local array can overflow the stack.""",
            mcq("What is the LCS of ABCDE and ACE?", ["ACE (length 3)", "ABC", "AE", "BD"], 0),
            mcq("What does dp[i][j] mean?", ["Best for first i letters of A and j of B", "Last match", "Count", "Edit distance"], 0),
            mcq("Why avoid a huge 2-D local array?", ["The stack is small", "It is illegal", "It is slow always", "It can't be indexed"], 0),
            run("Read two words and print the length of their longest common subsequence.", "c",
                [t("classic", stdin="abcde ace"), t("none", stdin="abc xyz"), t("same", stdin="code code")], ["3", "0", "4"],
                prog('char a[101], b[101];\nscanf("%100s %100s", a, b);\nint n = strlen(a), m = strlen(b);\nstatic int dp[101][101];\nfor (int i = 1; i <= n; i++) {\n    for (int j = 1; j <= m; j++) {\n        if (a[i - 1] == b[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;\n        else dp[i][j] = dp[i - 1][j] > dp[i][j - 1] ? dp[i - 1][j] : dp[i][j - 1];\n    }\n}\nprintf("%d\\n", dp[n][m]);',
                     includes="#include <stdio.h>\n#include <string.h>\n"),
                starter=STARTER, require=[r"dp\s*\[", r"strlen"], fallback=[r"dp\s*\[", r"strlen\s*\(", r"\[i\s*-\s*1\]"]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · Error handling idioms",
        lesson(
            "Return codes and out-parameters",
            """C has no exceptions, so functions report failure through their return value, and deliver results through pointer 'out-parameters':

int parse_int(const char *s, int *out) {     // returns 0 on success, -1 on failure
    char *end; long v = strtol(s, &end, 10);
    if (end == s || *end != '\\0') return -1;
    *out = (int)v;
    return 0;
}
int x; if (parse_int(text, &x) != 0) { /* handle the error */ }

ALWAYS check return values (malloc, fopen, scanf). Document what each function returns and keep the convention consistent across a module: 0 = success, negative = error is common.""",
            mcq("How does C report errors without exceptions?", ["Return codes and out-parameters", "try/catch", "throw", "assert only"], 0),
            mcq("Which calls must you check?", ["malloc, fopen, scanf and friends", "printf only", "Nothing", "return only"], 0),
            mcq("What is an out-parameter?", ["A pointer the function writes the result to", "A return type", "A macro", "A global"], 0),
            run("Write int parse_int(const char *s, int *out) returning 0 on success and -1 on failure. Read n tokens and print the sum of the valid ones and the number of invalid tokens, separated by a space.", "c",
                [t("mix", stdin="4\n10 x 5 7y"), t("good", stdin="2\n3 4")], ["15 2", "7 0"],
                prog('int n, sum = 0, bad = 0;\nscanf("%d", &n);\nwhile (n--) {\n    char tok[32];\n    int v;\n    scanf("%31s", tok);\n    if (parse_int(tok, &v) == 0) sum += v;\n    else bad++;\n}\nprintf("%d %d\\n", sum, bad);',
                     includes=STD,
                     before='int parse_int(const char *s, int *out) {\n    char *end;\n    long v = strtol(s, &end, 10);\n    if (end == s || *end != \'\\0\') return -1;\n    *out = (int)v;\n    return 0;\n}\n\n'),
                starter=STARTER, require=[r"parse_int", r"\*\s*out"], fallback=[r"parse_int\s*\(", r"\*\s*out", r"return\s+-1"]),
        ),
        lesson(
            "goto cleanup",
            """When a function acquires several resources, the cleanest C idiom is a single cleanup label at the end - each failure jumps there, and cleanup releases whatever was acquired:

int process(void) {
    int rc = -1;
    char *a = NULL, *b = NULL;
    a = malloc(100);  if (!a) goto done;
    b = malloc(100);  if (!b) goto done;
    ...
    rc = 0;
done:
    free(b);          // free(NULL) is safe
    free(a);
    return rc;
}

Initialise pointers to NULL first so cleanup is always safe. This is the one widely accepted use of goto - it avoids deeply nested ifs and duplicated cleanup code.""",
            mcq("Why initialise pointers to NULL first?", ["free(NULL) is safe in cleanup", "It's required", "To speed up malloc", "To avoid warnings only"], 0),
            mcq("What is goto cleanup good for?", ["One exit path that releases resources", "Loops", "Recursion", "Sorting"], 0),
            mcq("What does free(NULL) do?", ["Nothing, safely", "Crashes", "Frees everything", "Returns -1"], 0),
            run("Allocate two int arrays of size n with malloc using a single 'done:' cleanup label (free both there). Fill the first with 1..n, the second with squares, and print the sum of both arrays' elements. Read n.", "c",
                [t("three", stdin="3"), t("one", stdin="1")], ["20", "2"],
                prog('int n, rc = 1;\nint *a = NULL, *b = NULL;\nscanf("%d", &n);\na = malloc(n * sizeof *a);\nif (!a) goto done;\nb = malloc(n * sizeof *b);\nif (!b) goto done;\nlong long sum = 0;\nfor (int i = 0; i < n; i++) {\n    a[i] = i + 1;\n    b[i] = (i + 1) * (i + 1);\n    sum += a[i] + b[i];\n}\nprintf("%lld\\n", sum);\nrc = 0;\ndone:\nfree(b);\nfree(a);\nreturn rc;',
                     includes=STD),
                starter=STARTER, require=[r"goto\s+done", r"done\s*:"], fallback=[r"goto\s+\w+", r"\w+\s*:", r"free\s*\("]),
        ),
        lesson(
            "assert and defensive checks",
            """assert(cond) from <assert.h> aborts with file and line when cond is false - a tool for catching PROGRAMMER bugs (violated preconditions), not for handling bad user input.

assert(v != NULL);
assert(idx >= 0 && idx < v->len);

Compile with -DNDEBUG and every assert disappears, so NEVER put work with side effects inside one (assert(i++ < 5) changes behaviour between builds). Use return codes for expected failures (missing file, bad input) and assert for 'this can't happen'. C11 adds _Static_assert(sizeof(int) == 4, "int is 4 bytes") for compile-time checks.""",
            mcq("What is assert for?", ["Catching programmer bugs", "Validating user input", "Printing", "Looping"], 0),
            mcq("What happens to asserts with -DNDEBUG?", ["They are removed", "They get faster", "They become errors", "Nothing"], 0),
            mcq("Which is wrong inside an assert?", ["A side effect like i++", "A comparison", "A pointer check", "A range check"], 0),
            run("Write a safe get(const int *a, int n, int i) that asserts 0 <= i < n and returns a[i]. Read n numbers and q valid indexes and print the values at those indexes separated by spaces.", "c",
                [t("some", stdin="4\n10 20 30 40\n3\n3 0 2"), t("one", stdin="1\n5\n1\n0")], ["40 10 30", "5"],
                prog('int n, a[100];\nscanf("%d", &n);\nfor (int i = 0; i < n; i++) scanf("%d", &a[i]);\nint q;\nscanf("%d", &q);\nfor (int j = 0; j < q; j++) {\n    int i;\n    scanf("%d", &i);\n    printf("%s%d", j ? " " : "", get(a, n, i));\n}\nprintf("\\n");',
                     includes="#include <assert.h>\n#include <stdio.h>\n",
                     before='int get(const int *a, int n, int i) {\n    assert(i >= 0 && i < n);\n    return a[i];\n}\n\n'),
                starter=STARTER, require=[r"assert\s*\("], fallback=[r"assert\s*\(", r"get\s*\("]),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · Memory safety",
        lesson(
            "Buffer overflows",
            """Writing past the end of an array is undefined behaviour: it may crash, corrupt other variables or be exploited by attackers. C does NOT check bounds.

char buf[8];
strcpy(buf, "much too long");     // overflow! writes past buf
scanf("%s", buf);                 // overflow if the word is long

Safe habits: bound every read (scanf("%7s", buf), fgets(buf, sizeof buf, f)), use snprintf, always pass the buffer size, and compile with -fsanitize=address,undefined while testing - it reports the overflow immediately with a stack trace.""",
            mcq("What does writing past an array's end cause?", ["Undefined behaviour", "A compile error", "A safe wrap-around", "An exception"], 0),
            mcq("How do you limit scanf's %s?", ["scanf(\"%7s\", buf) for an 8-byte buffer", "Nothing is needed", "Use gets", "Use %w"], 0),
            mcq("Which tool detects overflows while testing?", ["-fsanitize=address", "-O3", "-pedantic only", "make"], 0),
            run("Read a word safely into an 8-byte buffer using a width limit (%7s) and print its length and then the word. Longer words are cut to 7 characters.", "c",
                [t("short", stdin="hello"), t("long", stdin="encyclopedia")], ["5 hello", "7 encyclo"],
                prog('char buf[8];\nscanf("%7s", buf);\nprintf("%zu %s\\n", strlen(buf), buf);',
                     includes="#include <stdio.h>\n#include <string.h>\n"),
                starter=STARTER, require=[r"%7s"], forbid=[r"gets\s*\(", r"scanf\s*\(\s*\"%s\""], fallback=[r"%7s", r"strlen"]),
        ),
        lesson(
            "Use-after-free and double free",
            """Two classic heap bugs:

free(p);  *p = 5;        // use-after-free: memory may be reused by someone else
free(p);  free(p);       // double free: corrupts the allocator's bookkeeping

Defence: set the pointer to NULL immediately after free (free(NULL) is a no-op, and a NULL dereference crashes loudly instead of silently corrupting memory).

free(p); p = NULL;

Also never return a pointer to a local variable - it dies when the function returns (dangling pointer). Ownership rule of thumb: whoever allocates documents who frees.""",
            mcq("Why set a pointer to NULL after free?", ["Double free becomes safe and use crashes loudly", "It frees memory twice", "It speeds malloc", "It's required by C"], 0),
            mcq("What is wrong with returning &local?", ["The local no longer exists", "Nothing", "It is slow", "It leaks"], 0),
            mcq("Is calling free twice on the same pointer safe?", ["No - it corrupts the heap", "Yes", "Only for ints", "Only with NULL check"], 0),
            run("Write void release(int **p) that frees *p and sets it to NULL. Allocate an int array of size n, fill with 1..n and print the sum, call release twice, then print whether the pointer is NULL (1 or 0).", "c",
                [t("four", stdin="4"), t("one", stdin="1")], ["10\n1", "1\n1"],
                prog('int n;\nscanf("%d", &n);\nint *a = malloc(n * sizeof *a);\nint sum = 0;\nfor (int i = 0; i < n; i++) {\n    a[i] = i + 1;\n    sum += a[i];\n}\nprintf("%d\\n", sum);\nrelease(&a);\nrelease(&a);\nprintf("%d\\n", a == NULL);',
                     includes=STD,
                     before='void release(int **p) {\n    free(*p);\n    *p = NULL;\n}\n\n'),
                starter=STARTER, require=[r"release", r"NULL"], fallback=[r"free\s*\(", r"=\s*NULL", r"release\s*\("]),
        ),
        lesson(
            "Ownership and leaks",
            """Every malloc needs exactly one free. A leak is memory you can no longer reach; a long-running program that leaks eventually dies.

Common leak sources: losing the pointer (p = malloc(..) twice), early returns before free, and overwriting a pointer with realloc's NULL result.

Ownership rules to document in comments:
- who allocates, who frees
- functions named *_new return an owned pointer; *_free consume it
- borrowed pointers (const char *) must not be freed or stored beyond the call

Tools: valgrind --leak-check=full ./prog or -fsanitize=leak report every unreachable block with the line that allocated it.""",
            mcq("What is a memory leak?", ["Memory you can no longer reach or free", "A buffer overflow", "A NULL pointer", "A stack overflow"], 0),
            mcq("What does the _new/_free naming convention document?", ["Ownership transfer", "Speed", "Types", "Threads"], 0),
            mcq("Which tool lists leaks with their allocation line?", ["valgrind / LeakSanitizer", "gcc -c", "make", "ls"], 0),
            run("Allocate each of n words with malloc in a loop (read with %31s), print the total number of characters, then free every word and the pointer array. Print 'freed' at the end.", "c",
                [t("three", stdin="3\nab cde f"), t("one", stdin="1\nhello")], ["6\nfreed", "5\nfreed"],
                prog('int n;\nscanf("%d", &n);\nchar **w = malloc(n * sizeof *w);\nsize_t total = 0;\nfor (int i = 0; i < n; i++) {\n    char buf[32];\n    scanf("%31s", buf);\n    w[i] = malloc(strlen(buf) + 1);\n    strcpy(w[i], buf);\n    total += strlen(w[i]);\n}\nprintf("%zu\\n", total);\nfor (int i = 0; i < n; i++) free(w[i]);\nfree(w);\nprintf("freed\\n");',
                     includes=STR),
                starter=STARTER, require=[r"malloc", r"free"], fallback=[r"malloc\s*\(", r"free\s*\(", r"for"]),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · Integers & arithmetic",
        lesson(
            "Fixed-width integers",
            """int's size varies by platform. <stdint.h> gives exact sizes: int8_t, int16_t, int32_t, int64_t and unsigned uint8_t ... uint64_t. Print them with the macros in <inttypes.h> (PRId64, PRIu64) or cast to long long and use %lld.

Overflow rules:
- UNSIGNED arithmetic wraps modulo 2^N (well defined)
- SIGNED overflow is undefined behaviour

<limits.h> has INT_MAX, LLONG_MAX, UINT_MAX. To multiply two ints safely, widen first: (long long)a * b.

Mixing signed and unsigned converts the signed value to unsigned: -1 < 1u is FALSE. Keep types consistent.""",
            mcq("What does unsigned overflow do?", ["Wraps around", "Is undefined", "Throws", "Saturates"], 0),
            mcq("What does signed overflow do?", ["Undefined behaviour", "Wraps safely", "Throws", "Saturates"], 0),
            mcq("How do you multiply two ints without overflow?", ["(long long)a * b", "a * b", "a << b", "(float)a * b"], 0),
            run("Read n numbers (each up to 2,000,000,000). Print their sum using int64_t and the largest value.", "c",
                [t("big", stdin="3\n2000000000 2000000000 2000000000"), t("small", stdin="2\n5 7")], ["6000000000\n2000000000", "12\n7"],
                prog('int n;\nscanf("%d", &n);\nint64_t sum = 0, best = INT64_MIN;\nwhile (n--) {\n    int64_t x;\n    scanf("%" SCNd64, &x);\n    sum += x;\n    if (x > best) best = x;\n}\nprintf("%" PRId64 "\\n%" PRId64 "\\n", sum, best);',
                     includes="#include <inttypes.h>\n#include <stdint.h>\n#include <stdio.h>\n"),
                starter=STARTER, require=[r"int64_t"], fallback=[r"int64_t|long long", r"PRId64|%lld"]),
        ),
        lesson(
            "gcd and modular exponentiation",
            """Euclid's algorithm computes the greatest common divisor in O(log n):

long long gcd(long long a, long long b) { return b == 0 ? a : gcd(b, a % b); }
lcm(a, b) = a / gcd(a, b) * b           // divide first to avoid overflow

When answers are huge, problems ask for the result modulo m. Reduce after every multiplication so numbers stay small. Fast exponentiation computes b^e mod m in O(log e) steps:

long long powmod(long long b, long long e, long long m) {
    long long r = 1; b %= m;
    while (e > 0) { if (e & 1) r = r * b % m; b = b * b % m; e >>= 1; }
    return r;
}""",
            mcq("What is gcd(12, 18)?", ["6", "36", "3", "2"], 0),
            mcq("Why compute lcm as a / gcd * b?", ["Dividing first avoids overflow", "It's faster", "It's required", "It rounds"], 0),
            mcq("How many steps does fast exponentiation take?", ["O(log e)", "O(e)", "O(1)", "O(e²)"], 0),
            run("Read b, e and m. Print b^e mod m by fast exponentiation (b, e up to 10^9, m up to 10^9+7).", "c",
                [t("small", stdin="2 10 1000"), t("big", stdin="3 200 1000000007"), t("zero exp", stdin="5 0 13")], ["24", "136318165", "1"],
                prog('long long b, e, m;\nscanf("%lld %lld %lld", &b, &e, &m);\nlong long r = 1 % m;\nb %= m;\nwhile (e > 0) {\n    if (e & 1) r = r * b % m;\n    b = b * b % m;\n    e >>= 1;\n}\nprintf("%lld\\n", r);'),
                starter=STARTER, require=[r"%"], fallback=[r"%\s*m", r"while", r"e\s*>>=\s*1|e\s*/=\s*2"]),
        ),
        lesson(
            "Bitsets with plain integers",
            """A uint64_t can hold a SET of up to 64 small numbers - one bit per member:

uint64_t set = 0;
set |= 1ULL << 5;          // add 5
set &= ~(1ULL << 5);       // remove 5
(set >> 5) & 1             // contains 5?
set & other                // intersection      set | other   union
__builtin_popcountll(set)  // size (GCC/Clang)

Always use 1ULL (not 1) when shifting past 31 bits - shifting a 32-bit int by 40 is undefined. Bitsets give O(1) set operations and are the basis of bitmask DP and compact flags.""",
            mcq("How do you add element k to a uint64_t set?", ["set |= 1ULL << k", "set += k", "set &= k", "set ^= k"], 0),
            mcq("Why 1ULL instead of 1?", ["1 is a 32-bit int - shifting past 31 is undefined", "It is faster", "It is shorter", "It looks better"], 0),
            mcq("What gives the set intersection?", ["a & b", "a | b", "a ^ b", "~a"], 0),
            run("Read two lists of numbers (each 0..63): 'n a1..an' then 'm b1..bm'. Store each as a uint64_t bitmask and print the size of the intersection and the size of the union.", "c",
                [t("overlap", stdin="3 1 2 3\n3 2 3 4"), t("disjoint", stdin="2 0 63\n1 5")], ["2 4", "0 3"],
                prog('uint64_t a = 0, b = 0;\nint n, x;\nscanf("%d", &n);\nwhile (n--) { scanf("%d", &x); a |= 1ULL << x; }\nscanf("%d", &n);\nwhile (n--) { scanf("%d", &x); b |= 1ULL << x; }\nprintf("%d %d\\n", __builtin_popcountll(a & b), __builtin_popcountll(a | b));',
                     includes="#include <stdint.h>\n#include <stdio.h>\n"),
                starter=STARTER, require=[r"1ULL\s*<<|1ull\s*<<|\(uint64_t\)\s*1\s*<<"], fallback=[r"<<", r"&", r"\|"]),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Generic code with void*",
        lesson(
            "void* and memcpy",
            """A void* can point at ANY type, which lets one function work on data of many types - at the price of manual size bookkeeping. memcpy and memcmp work on raw bytes:

void swap_any(void *a, void *b, size_t size) {
    unsigned char tmp[64];            // or malloc for large sizes
    memcpy(tmp, a, size); memcpy(a, b, size); memcpy(b, tmp, size);
}
swap_any(&x, &y, sizeof x);

You can't dereference or do arithmetic on a void*; cast to unsigned char * (bytes) or the real type first. This is how qsort and bsearch are written - they only know element SIZE, never the type.""",
            mcq("What can't you do with a void*?", ["Dereference it directly", "Assign it", "Pass it", "Compare to NULL"], 0),
            mcq("Which function copies raw bytes?", ["memcpy", "strcpy", "printf", "strlen"], 0),
            mcq("What does a generic function need besides the pointers?", ["The element size", "The type name", "A template", "A class"], 0),
            run("Write void swap_any(void *a, void *b, size_t size) and use it to swap two ints and two doubles. Read 'i1 i2 d1 d2' and print the swapped ints then the swapped doubles (1 decimal).", "c",
                [t("swap", stdin="1 2 3.5 4.5"), t("same", stdin="7 7 0.5 0.5")], ["2 1\n4.5 3.5", "7 7\n0.5 0.5"],
                prog('int a, b;\ndouble x, y;\nscanf("%d %d %lf %lf", &a, &b, &x, &y);\nswap_any(&a, &b, sizeof a);\nswap_any(&x, &y, sizeof x);\nprintf("%d %d\\n%.1f %.1f\\n", a, b, x, y);',
                     includes=STR,
                     before='void swap_any(void *a, void *b, size_t size) {\n    unsigned char tmp[64];\n    memcpy(tmp, a, size);\n    memcpy(a, b, size);\n    memcpy(b, tmp, size);\n}\n\n'),
                starter=STARTER, require=[r"void\s*\*", r"memcpy"], fallback=[r"void\s*\*", r"memcpy\s*\(", r"sizeof"]),
        ),
        lesson(
            "A generic dynamic array",
            """Store elements as raw bytes and track their size to build a vector that works for any type:

typedef struct { void *data; size_t elem, len, cap; } Vec;
void vec_init(Vec *v, size_t elem);
void vec_push(Vec *v, const void *item) {            // grows with realloc, then memcpy into the slot
    if (v->len == v->cap) { v->cap = v->cap ? v->cap * 2 : 4; v->data = realloc(v->data, v->cap * v->elem); }
    memcpy((char *)v->data + v->len * v->elem, item, v->elem);
    v->len++;
}
void *vec_at(const Vec *v, size_t i) { return (char *)v->data + i * v->elem; }

Pointer arithmetic needs a char * cast because void* has no element size. The cost of this generality: the compiler can no longer check types for you.""",
            mcq("Why cast to char * for arithmetic?", ["void* has no element size", "It's faster", "It's required for malloc", "It sorts"], 0),
            mcq("What does the Vec track besides the data?", ["Element size, length and capacity", "Only length", "A type name", "Nothing"], 0),
            mcq("What is lost with void* containers?", ["Compiler type checking", "Speed always", "Memory", "Portability"], 0),
            run("Implement the generic Vec (init, push, at, free). Read n doubles, push them, then print the sum and the maximum with 2 decimals.", "c",
                [t("three", stdin="3\n1.5 2.5 4"), t("one", stdin="1\n9")], ["8.00 4.00", "9.00 9.00"],
                prog('int n;\nscanf("%d", &n);\nVec v;\nvec_init(&v, sizeof(double));\nfor (int i = 0; i < n; i++) {\n    double x;\n    scanf("%lf", &x);\n    vec_push(&v, &x);\n}\ndouble sum = 0, best = *(double *)vec_at(&v, 0);\nfor (size_t i = 0; i < v.len; i++) {\n    double x = *(double *)vec_at(&v, i);\n    sum += x;\n    if (x > best) best = x;\n}\nprintf("%.2f %.2f\\n", sum, best);\nvec_free(&v);',
                     includes=STR,
                     before='typedef struct {\n    void *data;\n    size_t elem, len, cap;\n} Vec;\n\nvoid vec_init(Vec *v, size_t elem) {\n    v->data = NULL;\n    v->elem = elem;\n    v->len = v->cap = 0;\n}\n\nvoid vec_push(Vec *v, const void *item) {\n    if (v->len == v->cap) {\n        v->cap = v->cap ? v->cap * 2 : 4;\n        v->data = realloc(v->data, v->cap * v->elem);\n    }\n    memcpy((char *)v->data + v->len * v->elem, item, v->elem);\n    v->len++;\n}\n\nvoid *vec_at(const Vec *v, size_t i) {\n    return (char *)v->data + i * v->elem;\n}\n\nvoid vec_free(Vec *v) {\n    free(v->data);\n    v->data = NULL;\n    v->len = v->cap = 0;\n}\n\n'),
                starter=STARTER, require=[r"vec_push", r"vec_at", r"vec_init"], fallback=[r"vec_push\s*\(", r"memcpy\s*\(", r"realloc\s*\(", r"void\s*\*"]),
        ),
        lesson(
            "Generic find and map",
            """With a function pointer plus an element size you can write generic algorithms:

void *find_if(void *base, size_t n, size_t size, int (*pred)(const void *)) {
    for (size_t i = 0; i < n; i++) { void *p = (char *)base + i * size; if (pred(p)) return p; }
    return NULL;
}
void map(void *base, size_t n, size_t size, void (*f)(void *));

The caller supplies the behaviour; the algorithm supplies the loop. Returning NULL means 'not found'. This is C's version of templates and std::find_if - powerful, but you are responsible for matching types between the data and the callback.""",
            mcq("What does find_if return when nothing matches?", ["NULL", "-1", "The first element", "0"], 0),
            mcq("What does the algorithm know about the data?", ["Only its size", "Its type name", "Its class", "Its length in bytes only"], 0),
            mcq("What is the risk of generic C code?", ["A callback with the wrong type is not caught", "It is slow", "It is illegal", "It needs classes"], 0),
            run("Write generic find_if(void *base, size_t n, size_t size, int (*pred)(const void *)). Read n ints, then print the first negative number, or NONE; then print the first multiple of 5 or NONE.", "c",
                [t("mix", stdin="5\n3 -4 10 -1 7"), t("none", stdin="2\n1 2")], ["-4\n10", "NONE\nNONE"],
                prog('int n;\nscanf("%d", &n);\nint a[100];\nfor (int i = 0; i < n; i++) scanf("%d", &a[i]);\nint *neg = find_if(a, n, sizeof a[0], is_negative);\nint *m5 = find_if(a, n, sizeof a[0], is_mult5);\nif (neg) printf("%d\\n", *neg); else printf("NONE\\n");\nif (m5) printf("%d\\n", *m5); else printf("NONE\\n");',
                     before='void *find_if(void *base, size_t n, size_t size, int (*pred)(const void *)) {\n    for (size_t i = 0; i < n; i++) {\n        void *p = (char *)base + i * size;\n        if (pred(p)) return p;\n    }\n    return NULL;\n}\n\nint is_negative(const void *p) {\n    return *(const int *)p < 0;\n}\n\nint is_mult5(const void *p) {\n    return *(const int *)p % 5 == 0;\n}\n\n'),
                starter=STARTER, require=[r"find_if", r"void\s*\*"], fallback=[r"find_if\s*\(", r"\(\s*\*\s*pred\s*\)", r"void\s*\*"]),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Capstone projects",
        lesson(
            "Capstone: bank accounts",
            """Combine structs, arrays and error handling in one small system.

Design: an Account struct (id, balance) in an array; helper find(id) returns a pointer or NULL; each command validates input and prints a consistent ERROR. Keep each rule in ONE function - only withdraw() checks the balance - so changes stay local.""",
            mcq("Where should the 'enough funds' rule live?", ["In one withdraw function", "In every caller", "In main", "In the output code"], 0),
            mcq("What does find(id) return when missing?", ["NULL", "-1 always", "0", "An exception"], 0),
            mcq("Why print errors consistently?", ["Callers and tests can rely on the format", "It's shorter", "C requires it", "It hides bugs"], 0),
            run("Commands until 'end': 'open ID' (balance 0), 'deposit ID AMT', 'withdraw ID AMT', 'show ID'. Print 'ID: BALANCE' for show. Print ERROR for an unknown id or a withdrawal larger than the balance (balance unchanged).", "c",
                [t("flow", stdin="open a\ndeposit a 100\nwithdraw a 30\nshow a\nwithdraw a 500\nshow a\nshow z\nend"), t("empty", stdin="open x\nshow x\nend")],
                ["a: 70\nERROR\na: 70\nERROR", "x: 0"],
                prog('char cmd[16];\nwhile (scanf("%15s", cmd) == 1 && strcmp(cmd, "end") != 0) {\n    char id[16];\n    scanf("%15s", id);\n    if (strcmp(cmd, "open") == 0) {\n        strcpy(accts[used].id, id);\n        accts[used++].balance = 0;\n        continue;\n    }\n    long long amt = 0;\n    if (strcmp(cmd, "deposit") == 0 || strcmp(cmd, "withdraw") == 0) scanf("%lld", &amt);\n    Account *a = find(id);\n    if (!a) printf("ERROR\\n");\n    else if (strcmp(cmd, "deposit") == 0) a->balance += amt;\n    else if (strcmp(cmd, "withdraw") == 0) {\n        if (amt > a->balance) printf("ERROR\\n");\n        else a->balance -= amt;\n    } else printf("%s: %lld\\n", a->id, a->balance);\n}',
                     includes="#include <stdio.h>\n#include <string.h>\n",
                     before='typedef struct {\n    char id[16];\n    long long balance;\n} Account;\n\nAccount accts[100];\nint used = 0;\n\nAccount *find(const char *id) {\n    for (int i = 0; i < used; i++) {\n        if (strcmp(accts[i].id, id) == 0) return &accts[i];\n    }\n    return NULL;\n}\n\n'),
                starter=STARTER, require=[r"struct|typedef"], fallback=[r"typedef\s+struct|struct\s+\w+", r"strcmp", r"ERROR"]),
        ),
        lesson(
            "Capstone: inventory",
            """An inventory tracks stock levels and enforces simple business rules; the same shape powers carts, wallets and game state.

Plan before coding: list the commands, decide the data (item -> quantity), list the error cases (unknown item, not enough stock) and fix the output format. Implement one command at a time and test each. Keep items sorted (or sort before reporting) so the report is stable.""",
            mcq("What is a good first step?", ["List commands, data and error cases", "Write everything at once", "Pick colours", "Add threads"], 0),
            mcq("Why sort before reporting?", ["A stable, predictable output", "It's required by C", "It's faster", "To free memory"], 0),
            mcq("How should unknown items be handled?", ["Explicit, consistent error output", "Ignore silently", "Crash", "Create them silently"], 0),
            run("Commands until 'end': 'add ITEM QTY', 'remove ITEM QTY' and 'report'. remove prints SHORT when stock is insufficient or the item is unknown (no change). report prints items alphabetically as item=qty, space-separated (or EMPTY), dropping items at 0.", "c",
                [t("flow", stdin="add pen 10\nadd ink 4\nremove pen 3\nremove ink 9\nremove cap 1\nreport\nend"), t("empty", stdin="add a 2\nremove a 2\nreport\nend")],
                ["SHORT\nSHORT\nink=4 pen=7", "EMPTY"],
                prog('char cmd[16];\nwhile (scanf("%15s", cmd) == 1 && strcmp(cmd, "end") != 0) {\n    if (strcmp(cmd, "report") == 0) {\n        qsort(items, used, sizeof items[0], cmp);\n        int first = 1;\n        for (int i = 0; i < used; i++) {\n            if (items[i].qty == 0) continue;\n            printf("%s%s=%d", first ? "" : " ", items[i].name, items[i].qty);\n            first = 0;\n        }\n        printf(first ? "EMPTY\\n" : "\\n");\n        continue;\n    }\n    char name[16];\n    int q;\n    scanf("%15s %d", name, &q);\n    Item *it = find(name);\n    if (strcmp(cmd, "add") == 0) {\n        if (!it) {\n            it = &items[used++];\n            strcpy(it->name, name);\n            it->qty = 0;\n        }\n        it->qty += q;\n    } else if (!it || q > it->qty) {\n        printf("SHORT\\n");\n    } else {\n        it->qty -= q;\n    }\n}',
                     includes=STR,
                     before='typedef struct {\n    char name[16];\n    int qty;\n} Item;\n\nItem items[100];\nint used = 0;\n\nItem *find(const char *name) {\n    for (int i = 0; i < used; i++) {\n        if (strcmp(items[i].name, name) == 0) return &items[i];\n    }\n    return NULL;\n}\n\nint cmp(const void *a, const void *b) {\n    return strcmp(((const Item *)a)->name, ((const Item *)b)->name);\n}\n\n'),
                starter=STARTER, require=[r"struct|typedef"], fallback=[r"typedef\s+struct|struct\s+\w+", r"SHORT", r"EMPTY"]),
        ),
        lesson(
            "Capstone: state machine game",
            """A text adventure is a state machine: a current ROOM plus commands that move between rooms. In C, store the exits in a table indexed by room and direction:

int exits[ROOMS][DIRS];   // -1 = no exit, otherwise the destination room index

Separating the DATA (the table) from the ENGINE (the loop) means you can add rooms without touching the loop - the hallmark of a clean design. Enums give the rooms and directions readable names.""",
            mcq("What is the 'state' in a text adventure?", ["The current room", "The score only", "The command list", "The code"], 0),
            mcq("Why separate the table from the loop?", ["Add rooms without editing the engine", "It runs faster", "It's shorter", "C requires it"], 0),
            mcq("What does -1 in the table mean?", ["No exit", "A wall of text", "The start", "An error code in main"], 0),
            run("Rooms: hall (north->study, east->kitchen), study (south->hall), kitchen (west->hall). Start in hall. Read commands until 'quit'. 'go DIR' moves if an exit exists and prints 'You are in ROOM'; otherwise 'No exit'. 'where' prints the room name.", "c",
                [t("walk", stdin="go north\ngo north\nwhere\ngo south\ngo east\nwhere\nquit"), t("lost", stdin="go west\nwhere\nquit")],
                ["You are in study\nNo exit\nstudy\nYou are in hall\nYou are in kitchen\nkitchen", "No exit\nhall"],
                prog('int room = HALL;\nchar cmd[16];\nwhile (scanf("%15s", cmd) == 1 && strcmp(cmd, "quit") != 0) {\n    if (strcmp(cmd, "where") == 0) {\n        printf("%s\\n", names[room]);\n        continue;\n    }\n    char dir[16];\n    scanf("%15s", dir);\n    int d = strcmp(dir, "north") == 0 ? NORTH : strcmp(dir, "south") == 0 ? SOUTH : strcmp(dir, "east") == 0 ? EAST : WEST;\n    if (exits[room][d] < 0) {\n        printf("No exit\\n");\n    } else {\n        room = exits[room][d];\n        printf("You are in %s\\n", names[room]);\n    }\n}',
                     includes="#include <stdio.h>\n#include <string.h>\n",
                     before='enum { HALL, STUDY, KITCHEN, ROOMS };\nenum { NORTH, SOUTH, EAST, WEST, DIRS };\n\nconst char *names[ROOMS] = {"hall", "study", "kitchen"};\n\nint exits[ROOMS][DIRS] = {\n    /* hall    */ {STUDY, -1, KITCHEN, -1},\n    /* study   */ {-1, HALL, -1, -1},\n    /* kitchen */ {-1, -1, -1, HALL},\n};\n\n'),
                starter=STARTER, require=[r"exits|rooms"], fallback=[r"exits|rooms", r"No exit", r"quit"]),
        ),
        lesson(
            "Capstone: parking lot & library",
            """Two more designs to practise:

PARKING LOT - capacity N; 'park PLATE' fails with FULL when no space; 'leave PLATE' frees a spot; fee = hours × rate. An array of slots plus a capacity check is enough.

LIBRARY - a book can be borrowed by one user at a time; 'borrow BOOK USER' fails if it is out; 'return BOOK' makes it available. A struct array of {book, borrower} (borrower empty = available) is enough.

Both are small state machines with clear rules - exactly the shape of real backend services.""",
            mcq("What data tracks who has each book?", ["A struct with book and borrower", "An int", "A char", "A macro"], 0),
            mcq("What should 'park' do when the lot is full?", ["Report FULL without changing state", "Crash", "Park anyway", "Delete a car"], 0),
            mcq("What do both projects share?", ["Clear rules over a small state", "Threads", "Templates", "Networking"], 0),
            run("Library: commands until 'end': 'borrow BOOK USER' prints OK or OUT if already borrowed; 'return BOOK' prints RETURNED or 'NOT OUT'; 'who BOOK' prints the borrower or NONE.", "c",
                [t("flow", stdin="borrow dune ann\nborrow dune bob\nwho dune\nreturn dune\nwho dune\nreturn dune\nend"), t("simple", stdin="borrow a x\nwho a\nend")],
                ["OK\nOUT\nann\nRETURNED\nNONE\nNOT OUT", "OK\nx"],
                prog('char cmd[16];\nwhile (scanf("%15s", cmd) == 1 && strcmp(cmd, "end") != 0) {\n    char name[16];\n    scanf("%15s", name);\n    Book *b = find(name);\n    if (strcmp(cmd, "borrow") == 0) {\n        char user[16];\n        scanf("%15s", user);\n        if (b && b->user[0]) {\n            printf("OUT\\n");\n        } else {\n            if (!b) {\n                b = &books[used++];\n                strcpy(b->name, name);\n            }\n            strcpy(b->user, user);\n            printf("OK\\n");\n        }\n    } else if (strcmp(cmd, "return") == 0) {\n        if (b && b->user[0]) {\n            b->user[0] = \'\\0\';\n            printf("RETURNED\\n");\n        } else {\n            printf("NOT OUT\\n");\n        }\n    } else {\n        printf("%s\\n", b && b->user[0] ? b->user : "NONE");\n    }\n}',
                     includes="#include <stdio.h>\n#include <string.h>\n",
                     before='typedef struct {\n    char name[16];\n    char user[16];\n} Book;\n\nBook books[100];\nint used = 0;\n\nBook *find(const char *name) {\n    for (int i = 0; i < used; i++) {\n        if (strcmp(books[i].name, name) == 0) return &books[i];\n    }\n    return NULL;\n}\n\n'),
                starter=STARTER, require=[r"struct|typedef"], fallback=[r"typedef\s+struct|struct\s+\w+", r"strcmp", r"RETURNED"]),
        ),
    ),
)
