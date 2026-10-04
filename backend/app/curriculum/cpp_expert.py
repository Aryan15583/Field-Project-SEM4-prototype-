"""C++ - Expert section, part 1 (units 17-23): classes & RAII, STL algorithms, containers, templates, memory & move,
strings & streams, algorithms. Runnable code targets C++17."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .cpp_adv import STARTER, prog

IO = "#include <iostream>\n"

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Classes & RAII",
        lesson(
            "Constructors, destructors and RAII",
            """RAII (Resource Acquisition Is Initialization): a resource is acquired in a constructor and released in the destructor, so cleanup happens automatically when the object goes out of scope - even if an exception is thrown.

class Guard {
public:
    explicit Guard(std::string n) : name(std::move(n)) { std::cout << "open " << name << "\\n"; }
    ~Guard() { std::cout << "close " << name << "\\n"; }
private:
    std::string name;
};

Objects are destroyed in REVERSE order of construction. This is C++'s answer to try/finally.""",
            mcq("When does a destructor run?", ["When the object goes out of scope", "Only on delete", "At program start", "Never automatically"], 0),
            mcq("In which order are local objects destroyed?", ["Reverse of construction", "Construction order", "Random", "Alphabetical"], 0),
            mcq("What does RAII tie a resource to?", ["An object's lifetime", "A global variable", "A thread", "A file name"], 0),
            run("Write class Guard whose constructor prints 'open NAME' and destructor prints 'close NAME'. In main read two names, create a Guard for each in order, and print 'work' between creation and the end of main.", "cpp",
                [t("two", stdin="a b"), t("same", stdin="x x")], ["open a\nopen b\nwork\nclose b\nclose a", "open x\nopen x\nwork\nclose x\nclose x"],
                prog('std::string a, b;\nstd::cin >> a >> b;\nGuard g1(a);\nGuard g2(b);\nstd::cout << "work\\n";',
                     includes="#include <iostream>\n#include <string>\n",
                     before='class Guard {\npublic:\n    explicit Guard(std::string n) : name(n) { std::cout << "open " << name << "\\n"; }\n    ~Guard() { std::cout << "close " << name << "\\n"; }\n\nprivate:\n    std::string name;\n};\n\n'),
                starter=STARTER, require=[r"~Guard"], fallback=[r"class\s+Guard", r"~Guard\s*\(", r"open"]),
        ),
        lesson(
            "const correctness",
            """const documents and enforces what must not change:

int size() const { return n; }                 // const member function: promises not to modify the object
void print(const Point& p);                    // const reference: no copy, no modification
const std::vector<int>& get() const;           // callers can read but not edit

A const object can only call const member functions. Pass big objects by const reference, small ones (int, double) by value. Mark everything const you can - the compiler then finds accidental changes for you.""",
            mcq("What does a const member function promise?", ["Not to modify the object", "To be inline", "To be static", "To return const always"], 0),
            mcq("How should you pass a large string you only read?", ["const std::string&", "std::string", "std::string&", "std::string*"], 0),
            mcq("Can a const object call a non-const member?", ["No", "Yes", "Only in main", "Only if public"], 0),
            run("Write class Rectangle(int w, int h) with const methods area() and perimeter(). Read w and h and print both, one per line, calling them through a const reference.", "cpp",
                [t("sq", stdin="4 4"), t("rect", stdin="3 7")], ["16\n16", "21\n20"],
                prog('int w, h;\nstd::cin >> w >> h;\nconst Rectangle r(w, h);\nconst Rectangle& ref = r;\nstd::cout << ref.area() << "\\n" << ref.perimeter() << "\\n";',
                     before='class Rectangle {\npublic:\n    Rectangle(int w, int h) : w(w), h(h) {}\n    int area() const { return w * h; }\n    int perimeter() const { return 2 * (w + h); }\n\nprivate:\n    int w, h;\n};\n\n'),
                starter=STARTER, require=[r"\)\s*const"], fallback=[r"area\s*\(\s*\)\s*const", r"perimeter\s*\(\s*\)\s*const"]),
        ),
        lesson(
            "Operator overloading",
            """Operators are just functions with special names, so your own types can use + - == << like built-ins:

struct Vec { int x, y; };
Vec operator+(const Vec& a, const Vec& b) { return {a.x + b.x, a.y + b.y}; }
bool operator==(const Vec& a, const Vec& b) { return a.x == b.x && a.y == b.y; }
std::ostream& operator<<(std::ostream& os, const Vec& v) { return os << "(" << v.x << "," << v.y << ")"; }

Return the stream from operator<< so calls can be chained. Overload only when the meaning is obvious (adding vectors yes, adding two users no).""",
            mcq("Why return the ostream& from operator<<?", ["So << calls can be chained", "To end the program", "To flush", "It's required for ints"], 0),
            mcq("When should you overload an operator?", ["When its meaning is obvious for the type", "Always", "Never", "To hide logic"], 0),
            mcq("Which is the function name for +?", ["operator+", "plus", "add", "operator_add"], 0),
            run("Define struct Vec {int x, y;} with operator+ and operator<< (prints (x,y)). Read two vectors and print their sum.", "cpp",
                [t("sum", stdin="1 2 3 4"), t("neg", stdin="-1 5 1 -5")], ["(4,6)", "(0,0)"],
                prog('Vec a, b;\nstd::cin >> a.x >> a.y >> b.x >> b.y;\nstd::cout << a + b << "\\n";',
                     before='struct Vec {\n    int x, y;\n};\n\nVec operator+(const Vec& a, const Vec& b) {\n    return {a.x + b.x, a.y + b.y};\n}\n\nstd::ostream& operator<<(std::ostream& os, const Vec& v) {\n    return os << "(" << v.x << "," << v.y << ")";\n}\n\n'),
                starter=STARTER, require=[r"operator\s*\+", r"operator\s*<<"], fallback=[r"operator\s*\+", r"operator\s*<<", r"struct\s+Vec"]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · STL algorithms",
        lesson(
            "sort with lambdas",
            """<algorithm> works on iterator ranges. sort takes an optional comparison - perfect for a lambda:

std::sort(v.begin(), v.end());                                   // ascending
std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });   // descending
std::sort(people.begin(), people.end(), [](const P& a, const P& b) { return a.age < b.age; });

The comparison must be a strict ordering ('less than', never '<='). std::stable_sort keeps equal elements in their original order.""",
            mcq("What does the comparator return?", ["true when a should come before b", "The difference", "An index", "void"], 0),
            mcq("Which keeps equal elements in order?", ["stable_sort", "sort", "reverse", "partial_sort"], 0),
            mcq("Why must a comparator use < not <=?", ["It must be a strict ordering", "Speed", "Style", "Compilers ban <="], 0),
            run("Read n then n lines 'name score'. Print the names ordered by score descending, ties alphabetically.", "cpp",
                [t("ties", stdin="4\nbo 80\nada 90\ncy 80\ndee 70"), t("one", stdin="1\nsolo 5")], ["ada\nbo\ncy\ndee", "solo"],
                prog('int n;\nstd::cin >> n;\nstd::vector<std::pair<std::string, int>> v(n);\nfor (auto& p : v) std::cin >> p.first >> p.second;\nstd::sort(v.begin(), v.end(), [](const auto& a, const auto& b) {\n    if (a.second != b.second) return a.second > b.second;\n    return a.first < b.first;\n});\nfor (const auto& p : v) std::cout << p.first << "\\n";',
                     includes="#include <algorithm>\n#include <iostream>\n#include <string>\n#include <vector>\n"),
                starter=STARTER, require=[r"sort", r"\[\s*\]"], fallback=[r"std::sort|\bsort\s*\(", r"\[\s*\]\s*\("]),
        ),
        lesson(
            "accumulate, count_if and transform",
            """Many loops are one algorithm call:

std::accumulate(v.begin(), v.end(), 0)                       // sum (needs <numeric>)
std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; })
std::transform(v.begin(), v.end(), v.begin(), [](int x) { return x * x; })
std::any_of / all_of / none_of / find / find_if / min_element / max_element

Pass 0LL (or 0.0) as the initial value to accumulate in long long (or double) - the initial value's type decides the result type.""",
            mcq("Which header declares accumulate?", ["<numeric>", "<algorithm>", "<vector>", "<cmath>"], 0),
            mcq("What decides accumulate's result type?", ["The initial value", "The container", "The lambda", "The compiler flag"], 0),
            mcq("What does count_if return?", ["How many elements satisfy the predicate", "The first match", "A bool", "A sorted range"], 0),
            run("Read n numbers. Print the sum of the squares of the even numbers, using transform/accumulate or count_if style algorithms (no hand-written index loop for the sum).", "cpp",
                [t("mix", stdin="5\n1 2 3 4 5"), t("none", stdin="2\n1 3")], ["20", "0"],
                prog('int n;\nstd::cin >> n;\nstd::vector<long long> v(n);\nfor (auto& x : v) std::cin >> x;\nlong long sum = std::accumulate(v.begin(), v.end(), 0LL, [](long long acc, long long x) {\n    return x % 2 == 0 ? acc + x * x : acc;\n});\nstd::cout << sum << "\\n";',
                     includes="#include <iostream>\n#include <numeric>\n#include <vector>\n"),
                starter=STARTER, require=[r"accumulate|transform|count_if|for_each"], fallback=[r"accumulate|transform|count_if|for_each"]),
        ),
        lesson(
            "unique, erase and lower_bound",
            """Removing duplicates from a vector: sort, then unique + erase (the erase-remove idiom):

std::sort(v.begin(), v.end());
v.erase(std::unique(v.begin(), v.end()), v.end());

unique only shifts the kept elements forward and returns the new end - erase actually shrinks the vector.

On SORTED data: binary_search(first, last, x) tells if x exists; lower_bound returns an iterator to the first element >= x; upper_bound to the first > x. The distance from begin gives the index - O(log n).""",
            mcq("Why call erase after unique?", ["unique only moves elements; erase shrinks the vector", "unique is broken", "erase sorts", "To free memory"], 0),
            mcq("What does lower_bound return?", ["The first element >= x", "The last element <= x", "A bool", "The index of x always"], 0),
            mcq("What must be true before unique or lower_bound?", ["The range is sorted", "The range is non-empty", "Elements are ints", "Nothing"], 0),
            run("Read n numbers then q queries. Print the sorted distinct numbers on one line, then for each query print how many distinct numbers are strictly less than it (use unique/erase and lower_bound).", "cpp",
                [t("dups", stdin="6\n5 1 5 3 1 9\n3\n5 0 10"), t("one", stdin="1\n4\n2\n4 5")], ["1 3 5 9\n2\n0\n4", "4\n0\n1"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> v(n);\nfor (auto& x : v) std::cin >> x;\nstd::sort(v.begin(), v.end());\nv.erase(std::unique(v.begin(), v.end()), v.end());\nfor (size_t i = 0; i < v.size(); i++) std::cout << v[i] << (i + 1 < v.size() ? " " : "\\n");\nint q;\nstd::cin >> q;\nwhile (q--) {\n    int x;\n    std::cin >> x;\n    std::cout << (std::lower_bound(v.begin(), v.end(), x) - v.begin()) << "\\n";\n}',
                     includes="#include <algorithm>\n#include <iostream>\n#include <vector>\n"),
                starter=STARTER, require=[r"unique", r"lower_bound"], fallback=[r"unique", r"erase", r"lower_bound"]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Containers in depth",
        lesson(
            "priority_queue",
            """std::priority_queue is a heap: top() is the LARGEST element by default (a max-heap).

std::priority_queue<int> pq;                       // max-heap
std::priority_queue<int, std::vector<int>, std::greater<int>> mn;   // min-heap
pq.push(5); pq.top(); pq.pop(); pq.empty();

Elements can be pairs - compared by first, then second - so {distance, node} gives Dijkstra's algorithm for free. push and pop cost O(log n), top O(1).""",
            mcq("What does a default priority_queue give from top()?", ["The largest element", "The smallest", "The oldest", "A random one"], 0),
            mcq("How do you get a min-heap?", ["Add std::greater<int> as the third template argument", "Call reverse()", "Use a set", "Negate nothing"], 0),
            mcq("What is the cost of pop()?", ["O(log n)", "O(1)", "O(n)", "O(n log n)"], 0),
            run("Read n numbers and k. Print the k largest numbers in descending order using a priority_queue.", "cpp",
                [t("classic", stdin="6\n3 2 1 5 6 4\n2"), t("all", stdin="3\n9 8 7\n3")], ["6 5", "9 8 7"],
                prog('int n;\nstd::cin >> n;\nstd::priority_queue<int> pq;\nfor (int i = 0; i < n; i++) {\n    int x;\n    std::cin >> x;\n    pq.push(x);\n}\nint k;\nstd::cin >> k;\nfor (int i = 0; i < k; i++) {\n    std::cout << pq.top() << (i + 1 < k ? " " : "\\n");\n    pq.pop();\n}',
                     includes="#include <iostream>\n#include <queue>\n"),
                starter=STARTER, require=[r"priority_queue"], fallback=[r"priority_queue", r"\.top\(\)", r"\.pop\(\)"]),
        ),
        lesson(
            "deque, stack and queue",
            """Adaptors give restricted interfaces over containers:

std::stack<int> s;  s.push(1); s.top(); s.pop();      // LIFO
std::queue<int> q;  q.push(1); q.front(); q.pop();    // FIFO
std::deque<int> d;  d.push_front(1); d.push_back(2);  // O(1) at both ends, indexable

top/front on an EMPTY container is undefined behaviour - always check empty() first. pop() returns void; read the value before you pop it.""",
            mcq("What does stack::pop() return?", ["Nothing (void)", "The element", "A bool", "The size"], 0),
            mcq("What is top() on an empty stack?", ["Undefined behaviour", "0", "An exception always", "-1"], 0),
            mcq("Which supports O(1) insertion at both ends?", ["std::deque", "std::vector", "std::stack", "std::set"], 0),
            run("Read a string of brackets ()[]{} and print VALID if every bracket is closed in the right order, otherwise INVALID (use std::stack).", "cpp",
                [t("ok", stdin="([]{})"), t("bad", stdin="(]"), t("open", stdin="((")], ["VALID", "INVALID", "INVALID"],
                prog('std::string s;\nstd::cin >> s;\nstd::stack<char> st;\nbool ok = true;\nfor (char c : s) {\n    if (c == \'(\' || c == \'[\' || c == \'{\') {\n        st.push(c);\n    } else {\n        if (st.empty()) { ok = false; break; }\n        char o = st.top();\n        st.pop();\n        if ((c == \')\' && o != \'(\') || (c == \']\' && o != \'[\') || (c == \'}\' && o != \'{\')) { ok = false; break; }\n    }\n}\nstd::cout << (ok && st.empty() ? "VALID" : "INVALID") << "\\n";',
                     includes="#include <iostream>\n#include <stack>\n#include <string>\n"),
                starter=STARTER, require=[r"stack"], fallback=[r"stack\s*<", r"\.push\(", r"\.pop\(\)"]),
        ),
        lesson(
            "unordered_map and pairs",
            """std::unordered_map is a hash table: average O(1) insert and lookup (std::map is O(log n) but sorted).

std::unordered_map<std::string, int> m;
m["a"]++;                       // creates 0 then increments
auto it = m.find("b");          // m.end() when missing
if (it != m.end()) it->second;
m.count("a");                   // 0 or 1

Iteration order is unspecified. std::pair<A,B> (.first/.second) and std::tuple group values; structured bindings unpack them: auto [k, v] = *it;""",
            mcq("What does m.find(key) return when missing?", ["m.end()", "nullptr", "0", "An exception"], 0),
            mcq("What is unordered_map's iteration order?", ["Unspecified", "Sorted", "Insertion", "Reverse"], 0),
            mcq("What does m[key]++ do for a new key?", ["Creates it at 0 then increments", "Throws", "Does nothing", "Returns -1"], 0),
            run("Two sum: read n numbers then a target. Print the 0-based indices i<j of the first pair (smallest j, then smallest i) that sums to the target, or NONE. Use an unordered_map.", "cpp",
                [t("found", stdin="4\n2 7 11 15\n9"), t("none", stdin="3\n1 2 3\n10"), t("late", stdin="4\n3 2 4 1\n6")], ["0 1", "NONE", "1 2"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> a(n);\nfor (auto& x : a) std::cin >> x;\nint target;\nstd::cin >> target;\nstd::unordered_map<int, int> seen;\nfor (int j = 0; j < n; j++) {\n    auto it = seen.find(target - a[j]);\n    if (it != seen.end()) {\n        std::cout << it->second << " " << j << "\\n";\n        return 0;\n    }\n    if (!seen.count(a[j])) seen[a[j]] = j;\n}\nstd::cout << "NONE\\n";',
                     includes="#include <iostream>\n#include <unordered_map>\n#include <vector>\n"),
                starter=STARTER, require=[r"unordered_map"], fallback=[r"unordered_map", r"\.find\(|\.count\("]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Templates",
        lesson(
            "Function templates",
            """A template writes ONE function that works for many types; the compiler generates a version per type used:

template <typename T>
T maxOf(const T& a, const T& b) { return a > b ? a : b; }

maxOf(3, 7);          // T = int
maxOf(2.5, 1.5);      // T = double
maxOf<std::string>("a", "b");   // explicit type

The type must support the operations the body uses (here, >). Templates are resolved at COMPILE time - no runtime cost.""",
            mcq("When is a template instantiated?", ["At compile time for each type used", "At runtime", "At link time only", "Never"], 0),
            mcq("What must type T support in maxOf?", ["The > operator", "Nothing", "Virtual functions", "Inheritance"], 0),
            mcq("Is there a runtime cost for templates?", ["No - resolved at compile time", "Yes, a big one", "Only for ints", "Only for classes"], 0),
            run("Write template<typename T> T maxOf(const T&, const T&) and use it: read two ints and print the larger, then read two words and print the alphabetically greater.", "cpp",
                [t("both", stdin="3 9 apple pear"), t("neg", stdin="-5 -2 b a")], ["9\npear", "-2\nb"],
                prog('int a, b;\nstd::string s, u;\nstd::cin >> a >> b >> s >> u;\nstd::cout << maxOf(a, b) << "\\n" << maxOf(s, u) << "\\n";',
                     includes="#include <iostream>\n#include <string>\n",
                     before='template <typename T>\nT maxOf(const T& a, const T& b) {\n    return a > b ? a : b;\n}\n\n'),
                starter=STARTER, require=[r"template\s*<\s*(typename|class)\s+T\s*>"], fallback=[r"template\s*<\s*(typename|class)\s+T\s*>", r"maxOf"]),
        ),
        lesson(
            "Class templates",
            """A class template defines a type parameterised by another type - this is how std::vector<T> and std::stack<T> are written.

template <typename T>
class Stack {
public:
    void push(const T& v) { data.push_back(v); }
    T pop() { T v = data.back(); data.pop_back(); return v; }
    bool empty() const { return data.empty(); }
private:
    std::vector<T> data;
};

Stack<int> a; Stack<std::string> b;   // two different types made from one definition""",
            mcq("What does Stack<int> mean?", ["Stack instantiated with T = int", "A stack of 1 int", "An int named Stack", "An array"], 0),
            mcq("Which std types are class templates?", ["vector, map and stack", "int and double", "main", "cout only"], 0),
            mcq("Where must template code usually live?", ["In headers (visible at use)", "Only in .cpp files", "In the linker", "Nowhere"], 0),
            run("Write class template Stack<T> (push, pop, empty). Read n commands ('push x' or 'pop') on a Stack<int> and print popped values, or EMPTY when popping an empty stack.", "cpp",
                [t("mix", stdin="5\npush 1\npush 2\npop\npop\npop"), t("empty", stdin="1\npop")], ["2\n1\nEMPTY", "EMPTY"],
                prog('int n;\nstd::cin >> n;\nStack<int> s;\nwhile (n--) {\n    std::string cmd;\n    std::cin >> cmd;\n    if (cmd == "push") {\n        int x;\n        std::cin >> x;\n        s.push(x);\n    } else if (s.empty()) {\n        std::cout << "EMPTY\\n";\n    } else {\n        std::cout << s.pop() << "\\n";\n    }\n}',
                     includes="#include <iostream>\n#include <string>\n#include <vector>\n",
                     before='template <typename T>\nclass Stack {\npublic:\n    void push(const T& v) { data.push_back(v); }\n    T pop() {\n        T v = data.back();\n        data.pop_back();\n        return v;\n    }\n    bool empty() const { return data.empty(); }\n\nprivate:\n    std::vector<T> data;\n};\n\n'),
                starter=STARTER, require=[r"template\s*<", r"class\s+Stack"], fallback=[r"template\s*<", r"class\s+Stack", r"Stack\s*<\s*int\s*>"]),
        ),
        lesson(
            "auto, constexpr and structured bindings",
            """Modern C++ trims boilerplate:

auto x = 5;  auto it = v.begin();           // type deduced from the value
constexpr int N = 10;                         // computed at compile time
constexpr int sq(int x) { return x * x; }     // can run at compile time
static_assert(sq(4) == 16, "math broke");

for (const auto& [name, score] : scores)     // structured bindings (C++17)
auto [lo, hi] = std::minmax(a, b);

Prefer auto when the type is obvious or very long; spell the type out when it documents intent.""",
            mcq("What does constexpr allow?", ["Computation at compile time", "Faster loops always", "Hidden variables", "Dynamic typing"], 0),
            mcq("What does auto do?", ["Deduces the type from the initialiser", "Makes the variable automatic memory", "Disables types", "Allocates on the heap"], 0),
            mcq("What does static_assert check?", ["A condition at compile time", "A condition at runtime", "A pointer", "Memory leaks"], 0),
            run("Write constexpr int cube(int x) and use static_assert(cube(3) == 27). Then read n and print the sum of cube(i) for i = 1..n using auto in the loop.", "cpp",
                [t("n=3", stdin="3"), t("n=0", stdin="0"), t("n=5", stdin="5")], ["36", "0", "225"],
                prog('int n;\nstd::cin >> n;\nauto total = 0;\nfor (auto i = 1; i <= n; i++) total += cube(i);\nstd::cout << total << "\\n";',
                     before='constexpr int cube(int x) {\n    return x * x * x;\n}\n\nstatic_assert(cube(3) == 27, "cube is wrong");\n\n'),
                starter=STARTER, require=[r"constexpr", r"static_assert"], fallback=[r"constexpr", r"static_assert", r"\bauto\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Memory & move semantics",
        lesson(
            "unique_ptr ownership",
            """std::unique_ptr owns a heap object exclusively and deletes it automatically - no manual delete, no leaks.

auto p = std::make_unique<Widget>(5);
p->use();                       // use like a pointer
auto q = std::move(p);          // ownership TRANSFERS; p is now null
// auto r = q;                  // error: unique_ptr cannot be copied

Pass a raw pointer or reference to functions that just USE the object; pass unique_ptr by value to hand ownership over. Prefer make_unique over new.""",
            mcq("Can a unique_ptr be copied?", ["No, only moved", "Yes", "Only in functions", "Only if const"], 0),
            mcq("What happens to the object when the unique_ptr is destroyed?", ["It is deleted", "It leaks", "It is copied", "Nothing"], 0),
            mcq("What is the state of p after auto q = std::move(p)?", ["Null", "Still owns it", "Dangling", "Invalid compile"], 0),
            run("Create a unique_ptr<int> holding the number read from input (make_unique), move it into a second unique_ptr, and print the value through the new one and whether the old one is null (1 or 0).", "cpp",
                [t("five", stdin="5"), t("neg", stdin="-3")], ["5\n1", "-3\n1"],
                prog('int v;\nstd::cin >> v;\nauto p = std::make_unique<int>(v);\nauto q = std::move(p);\nstd::cout << *q << "\\n" << (p == nullptr ? 1 : 0) << "\\n";',
                     includes="#include <iostream>\n#include <memory>\n"),
                starter=STARTER, require=[r"make_unique", r"move"], forbid=[r"\bnew\b", r"\bdelete\b"], fallback=[r"make_unique", r"std::move", r"unique_ptr|auto"]),
        ),
        lesson(
            "shared_ptr and reference counts",
            """std::shared_ptr allows SEVERAL owners; the object is deleted when the last owner goes away (reference counting).

auto a = std::make_shared<int>(7);
auto b = a;                     // copying shares ownership
a.use_count();                  // 2
b.reset();                      // b gives up; use_count() is 1

Use unique_ptr by default (cheaper, clear ownership) and shared_ptr only when ownership is genuinely shared. Two shared_ptrs pointing at each other leak (a cycle) - break it with std::weak_ptr.""",
            mcq("When is the shared object deleted?", ["When the last shared_ptr goes away", "When the first goes away", "Never", "At program start"], 0),
            mcq("What does use_count() report?", ["How many shared_ptrs share the object", "The object's size", "Bytes used", "Threads"], 0),
            mcq("What breaks a shared_ptr cycle?", ["weak_ptr", "unique_ptr", "delete", "volatile"], 0),
            run("Read n. Create a shared_ptr<int> with value n, make two more copies of it, print use_count(), reset one copy and print use_count() again, then print the value.", "cpp",
                [t("seven", stdin="7"), t("zero", stdin="0")], ["3\n2\n7", "3\n2\n0"],
                prog('int n;\nstd::cin >> n;\nauto a = std::make_shared<int>(n);\nauto b = a;\nauto c = a;\nstd::cout << a.use_count() << "\\n";\nc.reset();\nstd::cout << a.use_count() << "\\n";\nstd::cout << *a << "\\n";',
                     includes="#include <iostream>\n#include <memory>\n"),
                starter=STARTER, require=[r"make_shared", r"use_count"], fallback=[r"make_shared", r"use_count\(\)", r"reset\(\)"]),
        ),
        lesson(
            "Move semantics",
            """Copying a big vector duplicates every element. MOVING steals its internal buffer in O(1), leaving the source valid but empty.

std::vector<int> a(1000000);
std::vector<int> b = std::move(a);    // b takes the buffer; a is now empty (don't rely on its contents)

std::move doesn't move anything itself - it just marks a value as 'safe to steal from'. Returning a local by value is already optimised (move or elision), so write 'return v;' not 'return std::move(v);'. Types that own resources define a move constructor and move assignment (rule of five).""",
            mcq("What does std::move actually do?", ["Casts to an rvalue so a move may happen", "Copies memory", "Deletes the object", "Moves threads"], 0),
            mcq("What is the state of a moved-from vector?", ["Valid but unspecified (usually empty)", "Destroyed", "Unchanged always", "Locked"], 0),
            mcq("How should you return a local vector?", ["return v;", "return std::move(v);", "return &v;", "return *v;"], 0),
            run("Read n then n numbers into a vector, move it into a second vector, and print the second vector's size and sum, then the first vector's size.", "cpp",
                [t("three", stdin="3\n1 2 3"), t("zero", stdin="0")], ["3\n6\n0", "0\n0\n0"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> a(n);\nfor (auto& x : a) std::cin >> x;\nstd::vector<int> b = std::move(a);\nlong long sum = 0;\nfor (int x : b) sum += x;\nstd::cout << b.size() << "\\n" << sum << "\\n" << a.size() << "\\n";',
                     includes="#include <iostream>\n#include <utility>\n#include <vector>\n"),
                starter=STARTER, require=[r"std::move"], fallback=[r"std::move", r"vector"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Strings & streams",
        lesson(
            "stringstream parsing",
            """std::stringstream turns a string into a stream you can read with >> - handy for splitting and converting:

std::stringstream ss("10 20 30");
int x; while (ss >> x) sum += x;

std::getline(ss, field, ',');        // split on a custom delimiter (comma)
ss << 42 << "-" << 7;  ss.str();     // build a string from pieces

Use std::stoi / std::stod to convert (they throw std::invalid_argument on bad text). getline(cin, line) reads a whole line; after cin >> n, call cin.ignore() first or the newline is read as an empty line.""",
            mcq("What does getline(ss, f, ',') do?", ["Reads up to the next comma", "Reads a number", "Skips spaces", "Writes a comma"], 0),
            mcq("What does stoi throw on bad input?", ["std::invalid_argument", "nothing", "std::bad_alloc", "a string"], 0),
            mcq("Why call cin.ignore() after cin >> n?", ["To skip the leftover newline", "To flush output", "To reset n", "To close input"], 0),
            run("Read a line of comma-separated integers (e.g. 4,8,15). Print their sum and count, split with stringstream and getline.", "cpp",
                [t("three", stdin="4,8,15"), t("one", stdin="42")], ["27 3", "42 1"],
                prog('std::string line;\nstd::getline(std::cin, line);\nstd::stringstream ss(line);\nstd::string field;\nlong long sum = 0;\nint count = 0;\nwhile (std::getline(ss, field, \',\')) {\n    sum += std::stoll(field);\n    count++;\n}\nstd::cout << sum << " " << count << "\\n";',
                     includes="#include <iostream>\n#include <sstream>\n#include <string>\n"),
                starter=STARTER, require=[r"stringstream|istringstream"], fallback=[r"stringstream|istringstream", r"getline"]),
        ),
        lesson(
            "Formatting with iomanip",
            """<iomanip> controls how numbers and text are laid out:

std::cout << std::fixed << std::setprecision(2) << 3.14159;   // 3.14
std::cout << std::setw(8) << 42;                              // width 8, right-aligned
std::cout << std::left << std::setw(8) << "ab";               // left-aligned
std::cout << std::setfill('0') << std::setw(5) << 42;         // 00042

setw affects only the NEXT output; fixed/setprecision/left/setfill stay until changed. In C++20 std::format is simpler, but iomanip works everywhere.""",
            mcq("How long does setw last?", ["Only the next output", "Forever", "One line", "Until main ends"], 0),
            mcq("What does fixed + setprecision(2) print for 3.14159?", ["3.14", "3.1", "3.141", "3"], 0),
            mcq("Which pads numbers with zeros?", ["setfill('0') and setw", "setzero", "fixed", "left"], 0),
            run("Read n then n lines 'name qty'. Print each as a row with the name left-aligned in width 8 and qty right-aligned in width 4, then 12 dashes and the total right-aligned in width 12.", "cpp",
                [t("two", stdin="2\napple 5\nfig 12"), t("one", stdin="1\nplum 7")], ["apple      5\nfig       12\n------------\n          17", "plum       7\n------------\n           7"],
                prog('int n;\nstd::cin >> n;\nint total = 0;\nwhile (n--) {\n    std::string name;\n    int q;\n    std::cin >> name >> q;\n    total += q;\n    std::cout << std::left << std::setw(8) << name << std::right << std::setw(4) << q << "\\n";\n}\nstd::cout << std::string(12, \'-\') << "\\n" << std::right << std::setw(12) << total << "\\n";',
                     includes="#include <iomanip>\n#include <iostream>\n#include <string>\n"),
                starter=STARTER, require=[r"setw"], fallback=[r"setw", r"std::left|left", r"std::right|right"]),
        ),
        lesson(
            "std::string_view and algorithms on text",
            """std::string_view (C++17) is a lightweight, non-owning window onto characters - no copy, ideal for read-only function parameters:

size_t countVowels(std::string_view s) { ... }
countVowels("hello");               // works with literals and std::string alike

Never keep a string_view longer than the string it points at (dangling). Text algorithms from <algorithm>: std::reverse, std::count, std::all_of(..., ::isdigit), std::transform(..., ::toupper). find returns std::string::npos when nothing matches.""",
            mcq("What does string_view do?", ["Views characters without copying", "Owns the text", "Sorts text", "Converts to number"], 0),
            mcq("What does string::find return on no match?", ["std::string::npos", "-1 as int always", "0", "end()"], 0),
            mcq("What is the danger of string_view?", ["It can dangle if the owner dies", "It is slow", "It copies", "It is read/write"], 0),
            run("Read a word and print YES if it is a palindrome (ignoring case), else NO. Use std::string_view for the checking function.", "cpp",
                [t("yes", stdin="Racecar"), t("no", stdin="hello"), t("single", stdin="a")], ["YES", "NO", "YES"],
                prog('std::string w;\nstd::cin >> w;\nstd::cout << (isPal(w) ? "YES" : "NO") << "\\n";',
                     includes="#include <cctype>\n#include <iostream>\n#include <string>\n#include <string_view>\n",
                     before='bool isPal(std::string_view s) {\n    size_t i = 0, j = s.size();\n    while (i + 1 < j) {\n        if (std::tolower(static_cast<unsigned char>(s[i])) != std::tolower(static_cast<unsigned char>(s[j - 1]))) return false;\n        i++;\n        j--;\n    }\n    return true;\n}\n\n'),
                starter=STARTER, require=[r"string_view"], fallback=[r"string_view", r"tolower"]),
        ),
    ),
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Algorithms in C++",
        lesson(
            "Merge sort",
            """Merge sort splits a vector, sorts both halves and merges them - O(n log n), stable.

void mergeSort(std::vector<int>& a, int lo, int hi) {         // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) / 2;
    mergeSort(a, lo, mid); mergeSort(a, mid, hi);
    std::inplace_merge(a.begin() + lo, a.begin() + mid, a.begin() + hi);
}

std::inplace_merge merges two adjacent sorted ranges - the 'merge' step. Writing it by hand is a classic exercise too: copy into a temp vector, then pick the smaller front each time.""",
            mcq("What is merge sort's time complexity?", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 0),
            mcq("What does inplace_merge need?", ["Two adjacent sorted ranges", "An unsorted range", "A map", "A lambda"], 0),
            mcq("Is merge sort stable?", ["Yes", "No", "Only for ints", "Only in place"], 0),
            run("Read n then n integers and sort them with your own recursive merge sort (no std::sort); print them space-separated.", "cpp",
                [t("mix", stdin="6\n5 2 9 1 5 6"), t("one", stdin="1\n7")], ["1 2 5 5 6 9", "7"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> a(n);\nfor (auto& x : a) std::cin >> x;\nmergeSort(a, 0, n);\nfor (int i = 0; i < n; i++) std::cout << a[i] << (i + 1 < n ? " " : "\\n");',
                     includes="#include <algorithm>\n#include <iostream>\n#include <vector>\n",
                     before='void mergeSort(std::vector<int>& a, int lo, int hi) {\n    if (hi - lo < 2) return;\n    int mid = (lo + hi) / 2;\n    mergeSort(a, lo, mid);\n    mergeSort(a, mid, hi);\n    std::inplace_merge(a.begin() + lo, a.begin() + mid, a.begin() + hi);\n}\n\n'),
                starter=STARTER, require=[r"mergeSort"], forbid=[r"std::sort", r"\bsort\s*\("], fallback=[r"mergeSort", r"void\s+mergeSort"]),
        ),
        lesson(
            "Binary search by hand",
            """Binary search halves a sorted range each step - O(log n):

int lo = 0, hi = (int)a.size() - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;      // avoids overflow of (lo + hi)
    if (a[mid] == x) return mid;
    if (a[mid] < x) lo = mid + 1; else hi = mid - 1;
}
return -1;

The same idea finds the answer to 'what is the smallest X that works?' problems (binary search on the answer) whenever 'works' flips once from false to true.""",
            mcq("Why write mid = lo + (hi - lo) / 2?", ["Avoids integer overflow", "It's faster", "It's required", "It rounds up"], 0),
            mcq("Binary search needs the data to be…", ["Sorted", "Unique", "Small", "Positive"], 0),
            mcq("What is its time complexity?", ["O(log n)", "O(n)", "O(1)", "O(n²)"], 0),
            run("Read n sorted integers then q queries. For each query print its index (0-based) or -1. Write the loop yourself (no std::binary_search/lower_bound).", "cpp",
                [t("some", stdin="5\n1 3 5 7 9\n3\n7 4 1"), t("one", stdin="1\n4\n2\n4 5")], ["3\n-1\n0", "0\n-1"],
                prog('int n;\nstd::cin >> n;\nstd::vector<int> a(n);\nfor (auto& x : a) std::cin >> x;\nint q;\nstd::cin >> q;\nwhile (q--) {\n    int x;\n    std::cin >> x;\n    int lo = 0, hi = n - 1, ans = -1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (a[mid] == x) { ans = mid; break; }\n        if (a[mid] < x) lo = mid + 1; else hi = mid - 1;\n    }\n    std::cout << ans << "\\n";\n}',
                     includes="#include <iostream>\n#include <vector>\n"),
                starter=STARTER, require=[r"while", r"mid"], forbid=[r"binary_search", r"lower_bound"], fallback=[r"while\s*\(\s*lo\s*<=\s*hi", r"mid"]),
        ),
        lesson(
            "BFS on a grid",
            """Breadth-first search with a queue finds the fewest steps in an unweighted grid or graph.

std::queue<std::pair<int,int>> q;  dist[sr][sc] = 0;  q.push({sr, sc});
while (!q.empty()) {
    auto [r, c] = q.front(); q.pop();
    for (auto [dr, dc] : dirs) {                       // up, down, left, right
        int nr = r + dr, nc = c + dc;
        if (inside && grid[nr][nc] != '#' && dist[nr][nc] == -1) { dist[nr][nc] = dist[r][c] + 1; q.push({nr, nc}); }
    }
}

Initialise every distance to -1 (unvisited): that doubles as the visited set.""",
            mcq("What does BFS guarantee in an unweighted grid?", ["Fewest steps", "Most steps", "A random path", "Cycles only"], 0),
            mcq("What does dist == -1 mean here?", ["Not yet visited", "A wall", "Goal", "Start"], 0),
            mcq("Which data structure drives BFS?", ["Queue", "Stack", "Heap", "Set"], 0),
            run("Read R and C, then R rows of the grid ('.' open, '#' wall, 'S' start, 'E' end). Print the fewest steps (up/down/left/right) from S to E, or -1 if unreachable.", "cpp",
                [t("open", stdin="3 4\nS...\n.##.\n...E"), t("blocked", stdin="2 3\nS#E\n.#."), t("adjacent", stdin="1 2\nSE")], ["5", "-1", "1"],
                prog('int R, C;\nstd::cin >> R >> C;\nstd::vector<std::string> g(R);\nint sr = 0, sc = 0, er = 0, ec = 0;\nfor (int r = 0; r < R; r++) {\n    std::cin >> g[r];\n    for (int c = 0; c < C; c++) {\n        if (g[r][c] == \'S\') { sr = r; sc = c; }\n        if (g[r][c] == \'E\') { er = r; ec = c; }\n    }\n}\nstd::vector<std::vector<int>> dist(R, std::vector<int>(C, -1));\nstd::queue<std::pair<int, int>> q;\ndist[sr][sc] = 0;\nq.push({sr, sc});\nint dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};\nwhile (!q.empty()) {\n    auto [r, c] = q.front();\n    q.pop();\n    for (int d = 0; d < 4; d++) {\n        int nr = r + dr[d], nc = c + dc[d];\n        if (nr >= 0 && nr < R && nc >= 0 && nc < C && g[nr][nc] != \'#\' && dist[nr][nc] == -1) {\n            dist[nr][nc] = dist[r][c] + 1;\n            q.push({nr, nc});\n        }\n    }\n}\nstd::cout << dist[er][ec] << "\\n";',
                     includes="#include <iostream>\n#include <queue>\n#include <string>\n#include <vector>\n"),
                starter=STARTER, require=[r"queue"], fallback=[r"queue\s*<", r"\.push\(", r"\.front\(\)"]),
        ),
    ),
)
