"""C++ - Expert section, part 2 (units 24-29): dynamic programming, idioms & patterns, enums/optional/variant,
bits & numbers, exceptions & lambdas, capstones. Runnable code targets C++17."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .cpp_adv import STARTER, prog

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Dynamic programming",
        lesson(
            "Memoization",
            """Memoization stores the result of each subproblem so it is computed once - turning exponential recursion into linear time.

std::unordered_map<int, long long> memo;
long long fib(int n) {
    if (n < 2) return n;
    auto it = memo.find(n);
    if (it != memo.end()) return it->second;
    return memo[n] = fib(n - 1) + fib(n - 2);
}

Plain fib(50) makes ~40 billion calls; memoized it makes about 100. Use long long: fib(80) overflows int.""",
            mcq("What does memoization save?", ["Results of earlier calls", "Memory", "Source code", "Threads"], 0),
            mcq("Plain recursive fib(n) is roughly…", ["Exponential", "Linear", "Constant", "Logarithmic"], 0),
            mcq("Why use long long for fib(80)?", ["int would overflow", "It is faster", "It is required for maps", "To print it"], 0),
            run("Read n (up to 80) and print the nth Fibonacci number (fib(0)=0, fib(1)=1) using memoization.", "cpp",
                [t("small", stdin="10"), t("big", stdin="80"), t("zero", stdin="0")], ["55", "23416728348467685", "0"],
                prog('int n;\nstd::cin >> n;\nstd::cout << fib(n) << "\\n";',
                     includes="#include <iostream>\n#include <unordered_map>\n",
                     before='std::unordered_map<int, long long> memo;\n\nlong long fib(int n) {\n    if (n < 2) return n;\n    auto it = memo.find(n);\n    if (it != memo.end()) return it->second;\n    return memo[n] = fib(n - 1) + fib(n - 2);\n}\n\n'),
                starter=STARTER, require=[r"memo|cache", r"long long"], fallback=[r"unordered_map|map|vector", r"long long", r"memo|cache"]),
        ),
        lesson(
            "Coin change table",
            """Bottom-up DP fills a table from the smallest subproblem. Fewest coins to make an amount:

const int INF = 1e9;
std::vector<int> best(amount + 1, INF);
best[0] = 0;
for (int a = 1; a <= amount; a++)
    for (int c : coins)
        if (c <= a && best[a - c] != INF) best[a] = std::min(best[a], best[a - c] + 1);

Greedy 'biggest coin first' fails for coins {1,3,4} and amount 6 (greedy 4+1+1 = 3 coins, best 3+3 = 2). DP is always right. Time O(amount × coins).""",
            mcq("Why can greedy fail for coin change?", ["Biggest-first isn't always optimal", "It is slow", "It overflows", "It needs recursion"], 0),
            mcq("What is best[0]?", ["0 coins", "1", "INF", "-1"], 0),
            mcq("What is the time cost?", ["O(amount × coins)", "O(2^amount)", "O(coins)", "O(amount!)"], 0),
            run("Read k coin values then an amount. Print the fewest coins needed, or -1 if impossible.", "cpp",
                [t("greedy trap", stdin="3\n1 3 4\n6"), t("impossible", stdin="1\n5\n3"), t("zero", stdin="2\n2 5\n0")], ["2", "-1", "0"],
                prog('int k;\nstd::cin >> k;\nstd::vector<int> coins(k);\nfor (auto& c : coins) std::cin >> c;\nint amount;\nstd::cin >> amount;\nconst int INF = 1e9;\nstd::vector<int> best(amount + 1, INF);\nbest[0] = 0;\nfor (int a = 1; a <= amount; a++)\n    for (int c : coins)\n        if (c <= a && best[a - c] != INF) best[a] = std::min(best[a], best[a - c] + 1);\nstd::cout << (best[amount] == INF ? -1 : best[amount]) << "\\n";',
                     includes="#include <algorithm>\n#include <iostream>\n#include <vector>\n"),
                starter=STARTER, require=[r"std::min|min\("], fallback=[r"min\(", r"vector\s*<\s*int\s*>", r"for"]),
        ),
        lesson(
            "Longest common subsequence",
            """LCS compares two strings with a 2-D table: dp[i][j] = best for the first i letters of A and first j of B.

if (a[i-1] == b[j-1]) dp[i][j] = dp[i-1][j-1] + 1;
else dp[i][j] = std::max(dp[i-1][j], dp[i][j-1]);

Row 0 and column 0 are 0 (empty prefix). The answer is dp[n][m]. A subsequence keeps order but may skip letters (ACE is a subsequence of ABCDE). Used in diff tools and DNA alignment. Memory can drop to two rows when you only need the length.""",
            mcq("What is the LCS of ABCDE and ACE?", ["ACE (length 3)", "ABC", "AE", "BD"], 0),
            mcq("What does dp[i][j] mean?", ["Best for first i letters of A and j of B", "Last match", "Count of letters", "Edit distance"], 0),
            mcq("When letters match, we take…", ["Diagonal + 1", "Max of neighbours", "0", "Left + above"], 0),
            run("Read two words and print the length of their longest common subsequence.", "cpp",
                [t("classic", stdin="abcde ace"), t("none", stdin="abc xyz"), t("same", stdin="code code")], ["3", "0", "4"],
                prog('std::string a, b;\nstd::cin >> a >> b;\nstd::vector<std::vector<int>> dp(a.size() + 1, std::vector<int>(b.size() + 1, 0));\nfor (size_t i = 1; i <= a.size(); i++) {\n    for (size_t j = 1; j <= b.size(); j++) {\n        if (a[i - 1] == b[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;\n        else dp[i][j] = std::max(dp[i - 1][j], dp[i][j - 1]);\n    }\n}\nstd::cout << dp[a.size()][b.size()] << "\\n";',
                     includes="#include <algorithm>\n#include <iostream>\n#include <string>\n#include <vector>\n"),
                starter=STARTER, require=[r"vector\s*<\s*(std::)?vector", r"max\("], fallback=[r"vector\s*<\s*std::vector|vector\s*<\s*vector", r"max\(", r"\[i\s*-\s*1\]"]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · Idioms & patterns",
        lesson(
            "std::function and Strategy",
            """std::function<R(Args)> holds ANY callable - a function pointer, lambda or functor - so behaviour becomes a value you can store and pass around (the Strategy pattern).

std::map<std::string, std::function<double(double, double)>> ops = {
    {"add", [](double a, double b) { return a + b; }},
    {"mul", [](double a, double b) { return a * b; }},
};
ops["add"](2, 3);

It costs a little (type erasure); for hot loops prefer templates, for configuration tables std::function is ideal.""",
            mcq("What can std::function hold?", ["Any callable with a matching signature", "Only lambdas", "Only functions", "Only classes"], 0),
            mcq("Which pattern does a map of operations resemble?", ["Strategy", "Singleton", "Builder", "Factory"], 0),
            mcq("When is a template better than std::function?", ["Hot loops needing speed", "Storing in maps", "Never", "Always"], 0),
            run("Build a map from operator name to std::function<long long(long long,long long)> for add, sub, mul. Read 'op a b' and print the result, or UNKNOWN if the operator is not in the map.", "cpp",
                [t("mul", stdin="mul 6 7"), t("sub", stdin="sub 3 10"), t("unknown", stdin="pow 2 3")], ["42", "-7", "UNKNOWN"],
                prog('std::map<std::string, std::function<long long(long long, long long)>> ops = {\n    {"add", [](long long a, long long b) { return a + b; }},\n    {"sub", [](long long a, long long b) { return a - b; }},\n    {"mul", [](long long a, long long b) { return a * b; }},\n};\nstd::string op;\nlong long a, b;\nstd::cin >> op >> a >> b;\nauto it = ops.find(op);\nif (it == ops.end()) std::cout << "UNKNOWN\\n";\nelse std::cout << it->second(a, b) << "\\n";',
                     includes="#include <functional>\n#include <iostream>\n#include <map>\n#include <string>\n"),
                starter=STARTER, require=[r"std::function"], fallback=[r"std::function", r"map\s*<"]),
        ),
        lesson(
            "Fluent builders",
            """A builder object lets you configure something step by step. Each setter returns *this by reference so calls chain:

class Request {
public:
    Request& url(std::string u) { url_ = std::move(u); return *this; }
    Request& header(std::string h) { headers_.push_back(std::move(h)); return *this; }
    std::string str() const;
};
Request r; r.url("a.com").header("x").header("y");

Returning a reference (not a copy) keeps the chain on the same object. The trailing underscore is a common style for private members.""",
            mcq("What do chaining setters return?", ["*this by reference", "void", "A copy", "nullptr"], 0),
            mcq("Why return a reference instead of a copy?", ["The chain edits the same object", "References are faster to type", "Copies are illegal", "To hide data"], 0),
            mcq("What does the trailing underscore usually signal?", ["A private data member", "A macro", "A template", "A keyword"], 0),
            run("Write class Pizza with chainable size(s), cheese(bool) and topping(s) and a const str() that returns 'SIZE pizza, cheese: yes|no, toppings: a,b' (toppings: none if empty). Read a size, a cheese flag (yes/no) and n toppings, then print.", "cpp",
                [t("full", stdin="large yes 2 olives ham"), t("plain", stdin="small no 0")], ["large pizza, cheese: yes, toppings: olives,ham", "small pizza, cheese: no, toppings: none"],
                prog('std::string size, c;\nint n;\nstd::cin >> size >> c >> n;\nPizza p;\np.size(size).cheese(c == "yes");\nwhile (n--) {\n    std::string t;\n    std::cin >> t;\n    p.topping(t);\n}\nstd::cout << p.str() << "\\n";',
                     includes="#include <iostream>\n#include <string>\n#include <vector>\n",
                     before='class Pizza {\npublic:\n    Pizza& size(std::string s) {\n        size_ = std::move(s);\n        return *this;\n    }\n    Pizza& cheese(bool c) {\n        cheese_ = c;\n        return *this;\n    }\n    Pizza& topping(std::string t) {\n        toppings_.push_back(std::move(t));\n        return *this;\n    }\n    std::string str() const {\n        std::string t;\n        for (const auto& x : toppings_) t += (t.empty() ? "" : ",") + x;\n        if (t.empty()) t = "none";\n        return size_ + " pizza, cheese: " + (cheese_ ? "yes" : "no") + ", toppings: " + t;\n    }\n\nprivate:\n    std::string size_;\n    bool cheese_ = false;\n    std::vector<std::string> toppings_;\n};\n\n'),
                starter=STARTER, require=[r"return\s+\*this", r"Pizza&"], fallback=[r"return\s+\*this", r"Pizza\s*&", r"str\s*\(\s*\)\s*const"]),
        ),
        lesson(
            "Observer with callbacks",
            """A subject stores a list of callbacks and calls each one when something happens:

class Subject {
public:
    void subscribe(std::function<void(const std::string&)> f) { listeners_.push_back(std::move(f)); }
    void set(const std::string& v) { for (auto& f : listeners_) f(v); }
private:
    std::vector<std::function<void(const std::string&)>> listeners_;
};

Lambdas make subscribers one-liners. Careful: a lambda capturing a local by reference must not outlive that local.""",
            mcq("What does the subject know about its listeners?", ["Only the callback signature", "Their classes", "Their fields", "Nothing"], 0),
            mcq("What is the danger of capturing a local by reference in a stored lambda?", ["It dangles after the local dies", "It is slow", "It copies", "Nothing"], 0),
            mcq("Which container stores several callbacks?", ["std::vector<std::function<...>>", "int", "std::string", "std::optional"], 0),
            run("Implement the Subject. Read n words; subscribe two listeners (one prints 'A:word', the other 'B:LENGTH') then call set for each word.", "cpp",
                [t("two", stdin="2\nhi code"), t("one", stdin="1\nok")], ["A:hi\nB:2\nA:code\nB:4", "A:ok\nB:2"],
                prog('int n;\nstd::cin >> n;\nSubject s;\ns.subscribe([](const std::string& v) { std::cout << "A:" << v << "\\n"; });\ns.subscribe([](const std::string& v) { std::cout << "B:" << v.size() << "\\n"; });\nwhile (n--) {\n    std::string w;\n    std::cin >> w;\n    s.set(w);\n}',
                     includes="#include <functional>\n#include <iostream>\n#include <string>\n#include <vector>\n",
                     before='class Subject {\npublic:\n    void subscribe(std::function<void(const std::string&)> f) { listeners_.push_back(std::move(f)); }\n    void set(const std::string& v) {\n        for (auto& f : listeners_) f(v);\n    }\n\nprivate:\n    std::vector<std::function<void(const std::string&)>> listeners_;\n};\n\n'),
                starter=STARTER, require=[r"subscribe", r"std::function"], fallback=[r"subscribe", r"std::function", r"listeners"]),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · enum class, optional & variant",
        lesson(
            "enum class",
            """Plain enums leak their names into the surrounding scope and convert silently to int. enum class is scoped and type-safe:

enum class Color { Red, Green, Blue };
Color c = Color::Green;            // must qualify
// int n = c;                      // error - needs static_cast<int>(c)

switch (c) { case Color::Red: ... case Color::Green: ... case Color::Blue: ... }   // compiler warns if you miss one

You can pick the underlying type: enum class Level : uint8_t { Low, High };. Always prefer enum class.""",
            mcq("How do you name an enum class value?", ["Color::Red", "Red", "Color.Red", "Color->Red"], 0),
            mcq("Does enum class convert to int implicitly?", ["No - use static_cast", "Yes", "Only in switch", "Only for 0"], 0),
            mcq("Why prefer enum class over plain enum?", ["Scoped names and type safety", "It's shorter", "It's faster", "It supports strings"], 0),
            run("Define enum class Light {Red, Green, Yellow} with a function next(Light) returning the following light in the cycle Red->Green->Yellow->Red, and a name(Light) function. Read n and print the light after n steps from Red.", "cpp",
                [t("three", stdin="3"), t("four", stdin="4"), t("zero", stdin="0")], ["Red", "Green", "Red"],
                prog('int n;\nstd::cin >> n;\nLight l = Light::Red;\nwhile (n--) l = next(l);\nstd::cout << name(l) << "\\n";',
                     includes="#include <iostream>\n#include <string>\n",
                     before='enum class Light { Red, Green, Yellow };\n\nLight next(Light l) {\n    switch (l) {\n        case Light::Red: return Light::Green;\n        case Light::Green: return Light::Yellow;\n        case Light::Yellow: return Light::Red;\n    }\n    return Light::Red;\n}\n\nstd::string name(Light l) {\n    switch (l) {\n        case Light::Red: return "Red";\n        case Light::Green: return "Green";\n        case Light::Yellow: return "Yellow";\n    }\n    return "";\n}\n\n'),
                starter=STARTER, require=[r"enum\s+class"], fallback=[r"enum\s+class\s+Light", r"switch", r"Light::"]),
        ),
        lesson(
            "std::optional",
            """std::optional<T> says 'maybe a value' in the type, instead of magic return values like -1 or nullptr:

std::optional<int> find(const std::vector<int>& v, int x) {
    for (size_t i = 0; i < v.size(); i++) if (v[i] == x) return (int)i;
    return std::nullopt;
}
if (auto idx = find(v, 5)) std::cout << *idx;        // has_value() / operator bool, then * to read
int safe = find(v, 9).value_or(-1);

Calling .value() on an empty optional throws std::bad_optional_access; dereferencing with * on empty is undefined behaviour - check first.""",
            mcq("What does value_or(-1) do?", ["Returns the value or -1 when empty", "Sets -1", "Throws if empty", "Returns a pointer"], 0),
            mcq("How do you return 'no value'?", ["std::nullopt", "nullptr", "-1 always", "void"], 0),
            mcq("What does *opt do on an empty optional?", ["Undefined behaviour", "Returns 0", "Throws always", "Returns nullopt"], 0),
            run("Write std::optional<int> indexOf(const std::vector<int>&, int). Read n numbers then q queries and print each index or NONE (use value checks, not -1).", "cpp",
                [t("some", stdin="4\n5 8 5 2\n3\n8 9 5"), t("one", stdin="1\n4\n1\n4")], ["1\nNONE\n0", "0"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> v(n);\nfor (auto& x : v) std::cin >> x;\nint q;\nstd::cin >> q;\nwhile (q--) {\n    int x;\n    std::cin >> x;\n    auto idx = indexOf(v, x);\n    if (idx) std::cout << *idx << "\\n";\n    else std::cout << "NONE\\n";\n}',
                     includes="#include <iostream>\n#include <optional>\n#include <vector>\n",
                     before='std::optional<int> indexOf(const std::vector<int>& v, int x) {\n    for (size_t i = 0; i < v.size(); i++) {\n        if (v[i] == x) return static_cast<int>(i);\n    }\n    return std::nullopt;\n}\n\n'),
                starter=STARTER, require=[r"std::optional", r"nullopt"], fallback=[r"std::optional", r"nullopt"]),
        ),
        lesson(
            "std::variant",
            """std::variant<A, B, C> holds exactly ONE of several types - a type-safe union.

std::variant<int, std::string> v = 42;
v = std::string("hi");
if (std::holds_alternative<int>(v)) std::get<int>(v);
if (auto* s = std::get_if<std::string>(&v)) std::cout << *s;      // nullptr if the type doesn't match
std::visit([](auto&& x) { std::cout << x; }, v);                  // call a lambda on whatever it holds

std::get<T> throws std::bad_variant_access on the wrong type. variant replaces tagged unions and some inheritance hierarchies.""",
            mcq("How many values can a variant hold at once?", ["Exactly one", "All of them", "Two", "None"], 0),
            mcq("What does get_if return on a type mismatch?", ["nullptr", "An exception", "0", "A copy"], 0),
            mcq("What does std::visit do?", ["Calls a callable on the held value", "Prints the type", "Resets the variant", "Copies it"], 0),
            run("Read n tokens. Each token is stored as std::variant<int, std::string> (an int when it is all digits, otherwise a string). Print 'int:VALUE' or 'str:VALUE' for each, using holds_alternative or get_if.", "cpp",
                [t("mix", stdin="3\n42 hello 7"), t("one", stdin="1\nabc")], ["int:42\nstr:hello\nint:7", "str:abc"],
                prog('int n;\nstd::cin >> n;\nwhile (n--) {\n    std::string tok;\n    std::cin >> tok;\n    bool digits = !tok.empty() && std::all_of(tok.begin(), tok.end(), [](unsigned char c) { return std::isdigit(c); });\n    std::variant<int, std::string> v;\n    if (digits) v = std::stoi(tok);\n    else v = tok;\n    if (std::holds_alternative<int>(v)) std::cout << "int:" << std::get<int>(v) << "\\n";\n    else std::cout << "str:" << std::get<std::string>(v) << "\\n";\n}',
                     includes="#include <algorithm>\n#include <cctype>\n#include <iostream>\n#include <string>\n#include <variant>\n"),
                starter=STARTER, require=[r"std::variant"], fallback=[r"std::variant", r"holds_alternative|get_if|std::get"]),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · Bits & numbers",
        lesson(
            "Bit manipulation",
            """Integers are bit patterns, and bit operators are fast and powerful:

a & b   AND     a | b   OR     a ^ b   XOR     ~a   NOT
a << k  shift left (multiply by 2^k)     a >> k  shift right

Test bit i: (x >> i) & 1.   Set it: x | (1 << i).   Clear it: x & ~(1 << i).   Toggle it: x ^ (1 << i).
x & (x - 1) clears the lowest set bit, so x is a power of two exactly when x > 0 and (x & (x - 1)) == 0.
GCC offers __builtin_popcount(x) to count set bits, and <bitset> has std::bitset<N> with count().""",
            mcq("What does x << 3 do?", ["Multiplies by 8", "Divides by 8", "Adds 3", "Rotates"], 0),
            mcq("How do you test bit i of x?", ["(x >> i) & 1", "x | i", "x ^ i", "x << i"], 0),
            mcq("What does a ^ a equal?", ["0", "a", "1", "-a"], 0),
            run("Read n numbers. Print how many are powers of two (positive with exactly one set bit).", "cpp",
                [t("some", stdin="6\n1 2 3 4 6 8"), t("none", stdin="2\n0 -4")], ["4", "0"],
                prog('int n;\nstd::cin >> n;\nint count = 0;\nwhile (n--) {\n    long long x;\n    std::cin >> x;\n    if (x > 0 && (x & (x - 1)) == 0) count++;\n}\nstd::cout << count << "\\n";'),
                starter=STARTER, require=[r"&"], fallback=[r"&\s*\(", r"x\s*-\s*1|popcount|bitset"]),
        ),
        lesson(
            "Integer limits and overflow",
            """Fixed-size integers WRAP (unsigned) or are undefined behaviour (signed) when they overflow:

#include <climits>  #include <limits>
INT_MAX                                  // 2147483647
std::numeric_limits<long long>::max()    // 9223372036854775807

int a = INT_MAX; a + 1;                  // signed overflow: undefined behaviour!
long long big = 1LL * a * a;             // widen BEFORE multiplying (1LL * ...)

Use long long for sums and products of large inputs, and unsigned only for bit tricks (mixing signed and unsigned causes surprises like -1 < 1u being false).""",
            mcq("What is signed integer overflow in C++?", ["Undefined behaviour", "Wraps safely", "An exception", "Saturates"], 0),
            mcq("How do you multiply two ints without overflow?", ["1LL * a * b", "a * b", "(float)a * b", "a << b"], 0),
            mcq("What is std::numeric_limits<int>::max()?", ["The largest int value", "Zero", "The size of int", "A macro for pi"], 0),
            run("Read n numbers (each up to 2,000,000,000). Print their sum using a type that cannot overflow for 100000 of them, and the largest value.", "cpp",
                [t("big", stdin="3\n2000000000 2000000000 2000000000"), t("small", stdin="2\n5 7")], ["6000000000\n2000000000", "12\n7"],
                prog('int n;\nstd::cin >> n;\nlong long sum = 0, best = std::numeric_limits<long long>::min();\nwhile (n--) {\n    long long x;\n    std::cin >> x;\n    sum += x;\n    if (x > best) best = x;\n}\nstd::cout << sum << "\\n" << best << "\\n";',
                     includes="#include <iostream>\n#include <limits>\n"),
                starter=STARTER, require=[r"long long"], fallback=[r"long long", r"numeric_limits|LLONG_MIN"]),
        ),
        lesson(
            "gcd, lcm and modular arithmetic",
            """C++17's <numeric> has std::gcd and std::lcm. Euclid's algorithm computes gcd in O(log n):

long long g(long long a, long long b) { return b == 0 ? a : g(b, a % b); }

When answers are huge, problems ask for the result 'modulo m' (often 1,000,000,007). Reduce after every multiplication so numbers stay small:

long long powmod(long long b, long long e, long long m) {
    long long r = 1; b %= m;
    while (e > 0) { if (e & 1) r = r * b % m; b = b * b % m; e >>= 1; }
    return r;
}

Fast exponentiation takes O(log e) steps instead of e.""",
            mcq("What is gcd(12, 18)?", ["6", "36", "3", "2"], 0),
            mcq("Why reduce modulo after each multiplication?", ["Numbers stay small and don't overflow", "It's required syntax", "To sort", "To round"], 0),
            mcq("How many steps does fast exponentiation take?", ["O(log e)", "O(e)", "O(1)", "O(e²)"], 0),
            run("Read b, e and m. Print b^e mod m computed by fast exponentiation (b, e up to 10^9, m up to 10^9+7).", "cpp",
                [t("small", stdin="2 10 1000"), t("big", stdin="3 200 1000000007"), t("zero exp", stdin="5 0 13")], ["24", "136318165", "1"],
                prog('long long b, e, m;\nstd::cin >> b >> e >> m;\nlong long r = 1 % m;\nb %= m;\nwhile (e > 0) {\n    if (e & 1) r = r * b % m;\n    b = b * b % m;\n    e >>= 1;\n}\nstd::cout << r << "\\n";'),
                starter=STARTER, require=[r"%"], fallback=[r"%\s*m", r"while", r"e\s*>>=\s*1|e\s*/=\s*2"]),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Exceptions & lambdas",
        lesson(
            "Exceptions",
            """C++ exceptions separate error handling from normal flow:

struct InsufficientFunds : std::runtime_error { using std::runtime_error::runtime_error; };
throw InsufficientFunds("need 30 more");
try { ... } catch (const InsufficientFunds& e) { std::cout << e.what(); } catch (const std::exception& e) { ... }

Catch by const reference (never by value - slicing). Derive your own types from std::exception or std::runtime_error. RAII guarantees destructors run while the stack unwinds, so resources are released. Mark functions that cannot throw as noexcept.""",
            mcq("How should exceptions be caught?", ["By const reference", "By value", "By pointer always", "By rvalue"], 0),
            mcq("What does what() return?", ["The error message", "The line number", "The type", "A code"], 0),
            mcq("What happens to local objects during unwinding?", ["Their destructors run", "They leak", "They're copied", "They're frozen"], 0),
            run("Write struct InsufficientFunds deriving from std::runtime_error and withdraw(balance, amount) that throws it with message 'Insufficient: need X more'. Read balance and amount; print the new balance or the exception message.", "cpp",
                [t("ok", stdin="100 30"), t("short", stdin="50 80")], ["70", "Insufficient: need 30 more"],
                prog('int balance, amount;\nstd::cin >> balance >> amount;\ntry {\n    std::cout << withdraw(balance, amount) << "\\n";\n} catch (const InsufficientFunds& e) {\n    std::cout << e.what() << "\\n";\n}',
                     includes="#include <iostream>\n#include <stdexcept>\n#include <string>\n",
                     before='struct InsufficientFunds : std::runtime_error {\n    using std::runtime_error::runtime_error;\n};\n\nint withdraw(int balance, int amount) {\n    if (amount > balance) throw InsufficientFunds("Insufficient: need " + std::to_string(amount - balance) + " more");\n    return balance - amount;\n}\n\n'),
                starter=STARTER, require=[r"throw", r"catch"], fallback=[r"runtime_error|exception", r"throw\s+", r"catch\s*\("]),
        ),
        lesson(
            "Lambda captures",
            """A lambda can use variables from the surrounding scope if you CAPTURE them:

[=]            capture everything by copy
[&]            capture everything by reference
[x, &y]        x by copy, y by reference
[this]         capture the object
[](int a) { ... }    capture nothing

By-copy captures are const unless the lambda is mutable. Capturing by reference is fine for short-lived lambdas (std::sort comparators) but dangerous for lambdas that outlive the variable.

int threshold = 3;
auto big = [threshold](int x) { return x > threshold; };""",
            mcq("What does [&] capture?", ["Everything used, by reference", "Nothing", "Only this", "By copy"], 0),
            mcq("Is a by-copy capture modifiable by default?", ["No (const unless mutable)", "Yes", "Only ints", "Only in sort"], 0),
            mcq("When is capture-by-reference dangerous?", ["When the lambda outlives the variable", "In sort", "Always", "Never"], 0),
            run("Read n numbers and a threshold t. Using std::count_if with a lambda that captures t, print how many numbers are strictly greater than t, then print the sum of those numbers using a second lambda capturing a running total by reference.", "cpp",
                [t("mix", stdin="5\n1 5 9 3 7\n4"), t("none", stdin="2\n1 2\n5")], ["3\n21", "0\n0"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> v(n);\nfor (auto& x : v) std::cin >> x;\nint t;\nstd::cin >> t;\nauto cnt = std::count_if(v.begin(), v.end(), [t](int x) { return x > t; });\nint sum = 0;\nstd::for_each(v.begin(), v.end(), [&sum, t](int x) { if (x > t) sum += x; });\nstd::cout << cnt << "\\n" << sum << "\\n";',
                     includes="#include <algorithm>\n#include <iostream>\n#include <vector>\n"),
                starter=STARTER, require=[r"\[[^\]]*t[^\]]*\]"], fallback=[r"count_if", r"\[[^\]]*\]\s*\("]),
        ),
        lesson(
            "std::array, tuple and tie",
            """std::array<T, N> is a fixed-size array with the vector-like interface (size(), begin(), at()) and no heap allocation.

std::tuple<std::string, int, double> row{"ada", 36, 4.5};
auto& [name, age, gpa] = row;               // structured binding
std::get<1>(row);                           // 36
std::tie(a, b) = std::make_pair(1, 2);      // assign to existing variables

A function can return several values as a pair/tuple instead of out-parameters:
std::pair<int,int> minmax(...) and then auto [lo, hi] = minmax(...);

Tuples compare lexicographically, so std::tie(a.x, a.y) < std::tie(b.x, b.y) is a one-line comparator.""",
            mcq("How do you read several return values at once?", ["Structured bindings: auto [a, b] = f();", "Pointers only", "Globals", "Macros"], 0),
            mcq("How are tuples compared?", ["Lexicographically", "By size", "By address", "They can't be"], 0),
            mcq("Does std::array allocate on the heap?", ["No", "Yes", "Only large", "Only if const"], 0),
            run("Write a function minMax(const std::vector<int>&) returning std::pair<int,int>, then read n numbers and print 'min max' using a structured binding (n >= 1).", "cpp",
                [t("mix", stdin="5\n4 -2 9 0 3"), t("one", stdin="1\n7")], ["-2 9", "7 7"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> v(n);\nfor (auto& x : v) std::cin >> x;\nauto [lo, hi] = minMax(v);\nstd::cout << lo << " " << hi << "\\n";',
                     includes="#include <algorithm>\n#include <iostream>\n#include <utility>\n#include <vector>\n",
                     before='std::pair<int, int> minMax(const std::vector<int>& v) {\n    auto [mn, mx] = std::minmax_element(v.begin(), v.end());\n    return {*mn, *mx};\n}\n\n'),
                starter=STARTER, require=[r"std::pair|tuple", r"auto\s*\["], fallback=[r"std::pair|tuple", r"auto\s*\["]),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Capstone projects",
        lesson(
            "Capstone: bank accounts",
            """Combine classes, maps and error handling in one small system.

Design: a Bank keeps accounts in an unordered_map by id; each operation validates input and reports errors consistently; main parses commands. Keep each rule in ONE place so changes stay local - e.g. only withdraw() checks the balance.""",
            mcq("Where should the 'enough funds' rule live?", ["In one withdraw function", "In every caller", "In main", "In the output code"], 0),
            mcq("Which container finds an account by id fastest?", ["unordered_map", "vector scan", "stack", "queue"], 0),
            mcq("Why print errors consistently?", ["Callers and tests can rely on the format", "It's shorter", "It is required by C++", "It hides bugs"], 0),
            run("Commands until 'end': 'open ID' (balance 0), 'deposit ID AMT', 'withdraw ID AMT', 'show ID'. Print 'ID: BALANCE' for show. Print 'ERROR' for an unknown id or a withdrawal larger than the balance (balance unchanged).", "cpp",
                [t("flow", stdin="open a\ndeposit a 100\nwithdraw a 30\nshow a\nwithdraw a 500\nshow a\nshow z\nend"), t("empty", stdin="open x\nshow x\nend")],
                ["a: 70\nERROR\na: 70\nERROR", "x: 0"],
                prog('std::unordered_map<std::string, long long> acc;\nstd::string cmd;\nwhile (std::cin >> cmd && cmd != "end") {\n    std::string id;\n    std::cin >> id;\n    if (cmd == "open") {\n        acc[id] = 0;\n    } else {\n        long long amt = 0;\n        if (cmd == "deposit" || cmd == "withdraw") std::cin >> amt;\n        auto it = acc.find(id);\n        if (it == acc.end()) {\n            std::cout << "ERROR\\n";\n        } else if (cmd == "deposit") {\n            it->second += amt;\n        } else if (cmd == "withdraw") {\n            if (amt > it->second) std::cout << "ERROR\\n";\n            else it->second -= amt;\n        } else {\n            std::cout << id << ": " << it->second << "\\n";\n        }\n    }\n}',
                     includes="#include <iostream>\n#include <string>\n#include <unordered_map>\n"),
                starter=STARTER, require=[r"map\s*<"], fallback=[r"map\s*<", r"deposit", r"withdraw", r"ERROR"]),
        ),
        lesson(
            "Capstone: inventory",
            """An inventory tracks stock levels and enforces simple business rules; the same shape powers carts, wallets and game state.

Plan before coding: list the commands, decide the data (item -> quantity), list the error cases (unknown item, not enough stock) and fix the output format. Implement one command at a time and test each. A std::map keeps the report alphabetical for free.""",
            mcq("What is a good first step?", ["List commands, data and error cases", "Write everything at once", "Pick colours", "Add threads"], 0),
            mcq("Which map type gives alphabetical iteration?", ["std::map", "std::unordered_map", "std::vector", "std::stack"], 0),
            mcq("How should unknown items be handled?", ["Explicit, consistent error output", "Ignore silently", "Crash", "Create them silently"], 0),
            run("Commands until 'end': 'add ITEM QTY', 'remove ITEM QTY' and 'report'. remove prints 'SHORT' when stock is insufficient or the item is unknown (no change). report prints items alphabetically as item=qty, space-separated (or EMPTY), dropping items at 0.", "cpp",
                [t("flow", stdin="add pen 10\nadd ink 4\nremove pen 3\nremove ink 9\nremove cap 1\nreport\nend"), t("empty", stdin="add a 2\nremove a 2\nreport\nend")],
                ["SHORT\nSHORT\nink=4 pen=7", "EMPTY"],
                prog('std::map<std::string, int> stock;\nstd::string cmd;\nwhile (std::cin >> cmd && cmd != "end") {\n    if (cmd == "add") {\n        std::string item;\n        int q;\n        std::cin >> item >> q;\n        stock[item] += q;\n    } else if (cmd == "remove") {\n        std::string item;\n        int q;\n        std::cin >> item >> q;\n        auto it = stock.find(item);\n        if (it == stock.end() || q > it->second) std::cout << "SHORT\\n";\n        else if (q == it->second) stock.erase(it);\n        else it->second -= q;\n    } else {\n        std::string out;\n        for (const auto& [k, v] : stock) out += (out.empty() ? "" : " ") + k + "=" + std::to_string(v);\n        std::cout << (out.empty() ? "EMPTY" : out) << "\\n";\n    }\n}',
                     includes="#include <iostream>\n#include <map>\n#include <string>\n"),
                starter=STARTER, require=[r"map\s*<"], fallback=[r"map\s*<", r"SHORT", r"EMPTY"]),
        ),
        lesson(
            "Capstone: state machine game",
            """A text adventure is a state machine: a current ROOM plus commands that move between rooms. Store exits as map<room, map<direction, room>> and loop reading commands until 'quit'.

Separating the DATA (the room map) from the ENGINE (the loop) means you can add rooms without touching the loop - the hallmark of a clean design.""",
            mcq("What is the 'state' in a text adventure?", ["The current room", "The score only", "The command list", "The code"], 0),
            mcq("Why separate the room data from the loop?", ["Add rooms without editing the engine", "It runs faster", "It's shorter", "C++ requires it"], 0),
            mcq("Which structure stores exits?", ["map<string, map<string, string>>", "int[]", "string", "optional"], 0),
            run("Rooms: hall (north->study, east->kitchen), study (south->hall), kitchen (west->hall). Start in hall. Read commands until 'quit'. 'go DIR' moves if an exit exists and prints 'You are in ROOM'; otherwise 'No exit'. 'where' prints the room name.", "cpp",
                [t("walk", stdin="go north\ngo north\nwhere\ngo south\ngo east\nwhere\nquit"), t("lost", stdin="go west\nwhere\nquit")],
                ["You are in study\nNo exit\nstudy\nYou are in hall\nYou are in kitchen\nkitchen", "No exit\nhall"],
                prog('std::map<std::string, std::map<std::string, std::string>> rooms = {\n    {"hall", {{"north", "study"}, {"east", "kitchen"}}},\n    {"study", {{"south", "hall"}}},\n    {"kitchen", {{"west", "hall"}}},\n};\nstd::string room = "hall", cmd;\nwhile (std::cin >> cmd && cmd != "quit") {\n    if (cmd == "where") {\n        std::cout << room << "\\n";\n    } else {\n        std::string dir;\n        std::cin >> dir;\n        auto it = rooms[room].find(dir);\n        if (it == rooms[room].end()) {\n            std::cout << "No exit\\n";\n        } else {\n            room = it->second;\n            std::cout << "You are in " << room << "\\n";\n        }\n    }\n}',
                     includes="#include <iostream>\n#include <map>\n#include <string>\n"),
                starter=STARTER, require=[r"map\s*<"], fallback=[r"map\s*<", r"No exit", r"quit"]),
        ),
        lesson(
            "Capstone: parking lot & library",
            """Two more designs to practise:

PARKING LOT - capacity N; 'park PLATE' fails with FULL when no space; 'leave PLATE' frees a spot; fee = hours × rate. A Map<plate, entryHour> plus a capacity check is enough.

LIBRARY - a book can be borrowed by one user at a time; 'borrow BOOK USER' fails if it is out; 'return BOOK' makes it available. A map<book, user> is enough.

Both are small state machines with clear rules - exactly the shape of real backend services.""",
            mcq("What data tracks who has each book?", ["map<book, user>", "int", "char", "set<int>"], 0),
            mcq("What should 'park' do when the lot is full?", ["Report FULL without changing state", "Crash", "Park anyway", "Delete a car"], 0),
            mcq("What do both projects share?", ["Clear rules over a small state", "Threads", "Templates only", "Networking"], 0),
            run("Library: commands until 'end': 'borrow BOOK USER' prints 'OK' or 'OUT' if already borrowed; 'return BOOK' prints 'RETURNED' or 'NOT OUT'; 'who BOOK' prints the borrower or NONE.", "cpp",
                [t("flow", stdin="borrow dune ann\nborrow dune bob\nwho dune\nreturn dune\nwho dune\nreturn dune\nend"), t("simple", stdin="borrow a x\nwho a\nend")],
                ["OK\nOUT\nann\nRETURNED\nNONE\nNOT OUT", "OK\nx"],
                prog('std::map<std::string, std::string> out;\nstd::string cmd;\nwhile (std::cin >> cmd && cmd != "end") {\n    std::string book;\n    std::cin >> book;\n    if (cmd == "borrow") {\n        std::string user;\n        std::cin >> user;\n        if (out.count(book)) {\n            std::cout << "OUT\\n";\n        } else {\n            out[book] = user;\n            std::cout << "OK\\n";\n        }\n    } else if (cmd == "return") {\n        std::cout << (out.erase(book) ? "RETURNED" : "NOT OUT") << "\\n";\n    } else {\n        auto it = out.find(book);\n        std::cout << (it == out.end() ? "NONE" : it->second) << "\\n";\n    }\n}',
                     includes="#include <iostream>\n#include <map>\n#include <string>\n"),
                starter=STARTER, require=[r"map\s*<"], fallback=[r"map\s*<", r"borrow", r"RETURNED"]),
        ),
    ),
)
