"""Java - Expert section, part 2 (units 24-29): text & regex, dynamic programming, design patterns, enums & nested
types, big numbers & bits, capstones. Runnable exercises stick to Java 11-15 features."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .java_adv import MAIN, SCAN, prog, scan

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Text, regex & parsing",
        lesson(
            "Regular expressions",
            """java.util.regex finds patterns in text:

Pattern p = Pattern.compile("(\\\\d+)-(\\\\d+)");
Matcher m = p.matcher("call 555-1234 now");
if (m.find()) System.out.println(m.group(1));   // 555

Common pieces: \\\\d digit, \\\\w word char, \\\\s space, + one or more, * zero or more, ? optional, [abc] set, ( ) capture group. Remember to double the backslash inside a Java string. String has matches(regex), replaceAll(regex, text) and split(regex) too.""",
            mcq("What does group(1) return?", ["The text of the first capture group", "The whole match", "The match count", "The pattern"], 0),
            mcq("Why write \"\\\\d\" in Java source?", ["The backslash must be escaped in a string", "It's a typo", "To make it greedy", "It means two digits"], 0),
            mcq("Which method finds the next match?", ["find()", "next()", "scan()", "search()"], 0),
            run("Read a line of text. Print the sum of all the integers found in it (use Pattern and Matcher with \\d+). Print 0 if none.", "java",
                [t("mixed", stdin="a1 b22 c333"), t("none", stdin="no digits")], ["356", "0"],
                scan('String line = in.hasNextLine() ? in.nextLine() : "";\nMatcher m = Pattern.compile("\\\\d+").matcher(line);\nlong sum = 0;\nwhile (m.find()) sum += Long.parseLong(m.group());\nSystem.out.println(sum);').replace("import java.util.*;", "import java.util.*;\nimport java.util.regex.*;"),
                starter=SCAN, require=[r"Pattern", r"Matcher"], fallback=[r"Pattern", r"Matcher", r"find\(\)"]),
        ),
        lesson(
            "Parsing structured text",
            """Real input is rarely clean. A reliable approach: split into records, split each record into fields, trim whitespace, convert types and handle bad rows explicitly.

String[] parts = line.split(",", -1);   // -1 keeps trailing empty fields
int qty = Integer.parseInt(parts[1].trim());

Wrap risky conversions in try/catch NumberFormatException, and count or report bad rows instead of crashing. split takes a regex, so split on a literal pipe with "\\\\|".""",
            mcq("What does split(\",\", -1) keep?", ["Trailing empty fields", "Nothing", "Only the first field", "Whitespace"], 0),
            mcq("Which exception does Integer.parseInt throw on bad text?", ["NumberFormatException", "IOException", "ArithmeticException", "ParseError"], 0),
            mcq("How do you split on a literal pipe?", ["split(\"\\\\|\")", "split(\"|\")", "split('|')", "split(\"||\")"], 0),
            run("Read n lines 'item,qty,price' (qty int, price decimal). Skip any line whose qty or price is not a number. Print the total of qty*price with 2 decimals, then the number of skipped lines.", "java",
                [t("one bad", stdin="3\napple,2,1.50\nbad,x,2\npear,1,0.75"), t("all good", stdin="1\nfig,4,2.5")], ["3.75\n1", "10.00\n0"],
                scan('int n = in.nextInt();\nin.nextLine();\ndouble total = 0;\nint bad = 0;\nfor (int i = 0; i < n; i++) {\n    String[] p = in.nextLine().split(",");\n    try {\n        total += Integer.parseInt(p[1].trim()) * Double.parseDouble(p[2].trim());\n    } catch (NumberFormatException e) {\n        bad++;\n    }\n}\nSystem.out.printf("%.2f%n", total);\nSystem.out.println(bad);'),
                starter=SCAN, require=[r"NumberFormatException"], fallback=[r"split\(", r"parseInt", r"NumberFormatException"]),
        ),
        lesson(
            "String.format and text blocks",
            """String.format / printf build aligned output:

%d integer   %5d width 5   %-8s left-aligned string   %05d zero padded   %.2f two decimals   %,d thousands separators   %n newline

String.join(", ", list) glues strings; String.repeat(n) (Java 11) repeats one; strip() trims Unicode whitespace. Text blocks (Java 15+) use triple quotes for multi-line text without escaping.""",
            mcq("What does \"%-8s\" do?", ["Left-aligns in a width of 8", "Right-aligns in 8", "Truncates to 8", "Pads with zeros"], 0),
            mcq("Which prints 1,234,567?", ["%,d", "%d", "%e", "%s,"], 0),
            mcq("What does \"ab\".repeat(3) give?", ["ababab", "ab3", "aaabbb", "An error"], 0),
            run("Read n then n lines 'name qty'. Print each as a row with the name left-aligned in width 8 and qty right-aligned in width 4, then a line of 12 dashes (use String.repeat) and the total qty right-aligned in width 12.", "java",
                [t("two", stdin="2\napple 5\nfig 12"), t("one", stdin="1\nplum 7")], ["apple      5\nfig       12\n------------\n          17", "plum       7\n------------\n           7"],
                scan('int n = in.nextInt();\nint total = 0;\nfor (int i = 0; i < n; i++) {\n    String name = in.next();\n    int qty = in.nextInt();\n    total += qty;\n    System.out.println(String.format("%-8s%4d", name, qty));\n}\nSystem.out.println("-".repeat(12));\nSystem.out.println(String.format("%12d", total));'),
                starter=SCAN, require=[r"format|printf"], fallback=[r"format|printf", r"repeat\("]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · Dynamic programming",
        lesson(
            "Memoization",
            """Memoization stores results of expensive calls so each is computed once - turning exponential recursion into linear time.

static Map<Integer, Long> memo = new HashMap<>();
static long fib(int n) {
    if (n < 2) return n;
    if (memo.containsKey(n)) return memo.get(n);
    long r = fib(n - 1) + fib(n - 2);
    memo.put(n, r);
    return r;
}

Plain fib(50) would make ~40 billion calls; memoized it makes 50.""",
            mcq("What does memoization save?", ["Results of earlier calls", "Memory", "Source code", "Threads"], 0),
            mcq("Plain recursive fib(n) is roughly…", ["Exponential", "Linear", "Constant", "Logarithmic"], 0),
            mcq("Memoized fib(n) is roughly…", ["Linear", "Exponential", "Quadratic", "Constant"], 0),
            run("Read n and print the nth Fibonacci number (fib(0)=0, fib(1)=1) using memoization with a HashMap. n goes up to 80.", "java",
                [t("small", stdin="10"), t("big", stdin="80"), t("zero", stdin="0")], ["55", "23416728348467685", "0"],
                scan('System.out.println(fib(in.nextInt()));',
                     extra="    static Map<Integer, Long> memo = new HashMap<>();\n\n    static long fib(int n) {\n        if (n < 2) return n;\n        if (memo.containsKey(n)) return memo.get(n);\n        long r = fib(n - 1) + fib(n - 2);\n        memo.put(n, r);\n        return r;\n    }\n\n"),
                starter=SCAN, require=[r"Map<", r"memo|cache"], fallback=[r"Map<", r"containsKey|get\(", r"put\("]),
        ),
        lesson(
            "Bottom-up tables: coin change",
            """Bottom-up DP fills a table from the smallest subproblem up. Fewest coins to make an amount:

int[] best = new int[amount + 1];
Arrays.fill(best, Integer.MAX_VALUE);
best[0] = 0;
for (int a = 1; a <= amount; a++)
    for (int c : coins)
        if (c <= a && best[a - c] != Integer.MAX_VALUE)
            best[a] = Math.min(best[a], best[a - c] + 1);

Greedy 'biggest coin first' can fail (coins 1,3,4 for 6: greedy 4+1+1, best 3+3). DP is always right.""",
            mcq("Why can greedy fail for coin change?", ["Biggest-first isn't always optimal", "It's slow", "It overflows", "It needs recursion"], 0),
            mcq("What is best[0] in the table?", ["0 coins for amount 0", "1", "Infinity", "-1"], 0),
            mcq("What is the table's time cost?", ["O(amount × coins)", "O(2^amount)", "O(coins)", "O(amount!)"], 0),
            run("Read k coin values, then an amount. Print the fewest coins needed, or -1 if impossible.", "java",
                [t("greedy trap", stdin="3\n1 3 4\n6"), t("impossible", stdin="1\n5\n3"), t("zero", stdin="2\n2 5\n0")], ["2", "-1", "0"],
                scan('int k = in.nextInt();\nint[] coins = new int[k];\nfor (int i = 0; i < k; i++) coins[i] = in.nextInt();\nint amount = in.nextInt();\nint INF = Integer.MAX_VALUE;\nint[] best = new int[amount + 1];\nArrays.fill(best, INF);\nbest[0] = 0;\nfor (int a = 1; a <= amount; a++) {\n    for (int c : coins) {\n        if (c <= a && best[a - c] != INF) best[a] = Math.min(best[a], best[a - c] + 1);\n    }\n}\nSystem.out.println(best[amount] == INF ? -1 : best[amount]);'),
                starter=SCAN, require=[r"Math\.min", r"new int\[\s*amount"], fallback=[r"Math\.min", r"new\s+int\[", r"for"]),
        ),
        lesson(
            "Longest common subsequence",
            """LCS compares two strings with a 2-D table: cell [i][j] = best answer for the first i letters of A and the first j letters of B.

if (a.charAt(i-1) == b.charAt(j-1)) dp[i][j] = dp[i-1][j-1] + 1;
else dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);

Row 0 and column 0 are 0 (empty prefix). The answer is dp[a.length()][b.length()]. A subsequence keeps order but may skip letters (ACE is a subsequence of ABCDE). Used in diff tools and DNA alignment.""",
            mcq("What is the LCS of ABCDE and ACE?", ["ACE (length 3)", "ABC", "AE", "BD"], 0),
            mcq("What does dp[i][j] mean?", ["Best for first i letters of A and j of B", "Last letter match", "Count of letters", "Edit distance"], 0),
            mcq("When the letters match, we take…", ["Diagonal + 1", "Max of neighbours", "0", "Left + above"], 0),
            run("Read two words and print the length of their longest common subsequence.", "java",
                [t("classic", stdin="abcde ace"), t("none", stdin="abc xyz"), t("same", stdin="java java")], ["3", "0", "4"],
                scan('String a = in.next(), b = in.next();\nint[][] dp = new int[a.length() + 1][b.length() + 1];\nfor (int i = 1; i <= a.length(); i++) {\n    for (int j = 1; j <= b.length(); j++) {\n        if (a.charAt(i - 1) == b.charAt(j - 1)) dp[i][j] = dp[i - 1][j - 1] + 1;\n        else dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);\n    }\n}\nSystem.out.println(dp[a.length()][b.length()]);'),
                starter=SCAN, require=[r"int\[\]\[\]", r"Math\.max"], fallback=[r"int\[\]\[\]", r"Math\.max", r"charAt"]),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · Design patterns",
        lesson(
            "Strategy",
            """Strategy puts interchangeable algorithms behind one interface, so behaviour can be chosen at runtime instead of with if/else chains.

interface Discount { double apply(double price); }
class Percent implements Discount { ... }
class Flat implements Discount { ... }
double total = discount.apply(price);

Because a functional interface is just a lambda, Strategy in modern Java is often a Map<String, Function<...>> of named behaviours.""",
            mcq("What problem does Strategy solve?", ["Choosing an algorithm at runtime without if/else chains", "Creating objects", "Speed", "Threading"], 0),
            mcq("In modern Java a simple Strategy can be…", ["A lambda", "A thread", "A static field", "A package"], 0),
            mcq("Which principle does Strategy support?", ["Open/closed - add behaviour without editing callers", "DRY only", "KISS only", "None"], 0),
            run("Define interface Discount with double apply(double price) and two strategies: percent off and flat off. Read a kind (percent or flat), an amount and a price, then print the discounted price with 2 decimals (never below 0).", "java",
                [t("percent", stdin="percent 10 200"), t("flat", stdin="flat 30 100"), t("floor", stdin="flat 500 50")], ["180.00", "70.00", "0.00"],
                scan('String kind = in.next();\ndouble amount = in.nextDouble(), price = in.nextDouble();\nDiscount d = kind.equals("percent") ? new Percent(amount) : new Flat(amount);\nSystem.out.printf("%.2f%n", d.apply(price));',
                     before='interface Discount {\n    double apply(double price);\n}\n\nclass Percent implements Discount {\n    private final double pct;\n\n    Percent(double pct) {\n        this.pct = pct;\n    }\n\n    public double apply(double price) {\n        return price - price * pct / 100;\n    }\n}\n\nclass Flat implements Discount {\n    private final double off;\n\n    Flat(double off) {\n        this.off = off;\n    }\n\n    public double apply(double price) {\n        return Math.max(0, price - off);\n    }\n}\n\n'),
                starter=SCAN, require=[r"interface\s+Discount", r"implements\s+Discount"], fallback=[r"interface\s+Discount", r"implements\s+Discount", r"apply\("]),
        ),
        lesson(
            "Builder",
            """Builder constructs complex objects step by step, avoiding constructors with a dozen parameters. Methods return 'this' so calls chain:

Pizza p = new Pizza.Builder("large").cheese(true).topping("olives").build();

static class Builder {
    private final String size; private boolean cheese;
    Builder(String size) { this.size = size; }
    Builder cheese(boolean c) { this.cheese = c; return this; }
    Pizza build() { return new Pizza(this); }
}

Required values go in the Builder's constructor; optional ones are chained methods. The built object can stay immutable.""",
            mcq("What does a chaining builder method return?", ["this (the builder)", "void", "The product", "null"], 0),
            mcq("Why use a Builder?", ["Many optional parameters stay readable", "It's faster", "It avoids classes", "It enables threads"], 0),
            mcq("Where do required values usually go?", ["The Builder constructor", "Setters", "Static fields", "toString"], 0),
            run("Write a Pizza with a nested static Builder: size (required), cheese(boolean), topping(String) (repeatable) and build(). main reads a size, a cheese flag (yes/no) and n toppings, then prints 'SIZE pizza, cheese: yes|no, toppings: a,b' (toppings: none if empty).", "java",
                [t("full", stdin="large yes 2 olives ham"), t("plain", stdin="small no 0")], ["large pizza, cheese: yes, toppings: olives,ham", "small pizza, cheese: no, toppings: none"],
                scan('String size = in.next();\nboolean cheese = in.next().equals("yes");\nint n = in.nextInt();\nPizza.Builder b = new Pizza.Builder(size).cheese(cheese);\nfor (int i = 0; i < n; i++) b.topping(in.next());\nSystem.out.println(b.build());',
                     before='class Pizza {\n    private final String size;\n    private final boolean cheese;\n    private final List<String> toppings;\n\n    private Pizza(Builder b) {\n        this.size = b.size;\n        this.cheese = b.cheese;\n        this.toppings = b.toppings;\n    }\n\n    @Override\n    public String toString() {\n        String t = toppings.isEmpty() ? "none" : String.join(",", toppings);\n        return size + " pizza, cheese: " + (cheese ? "yes" : "no") + ", toppings: " + t;\n    }\n\n    static class Builder {\n        private final String size;\n        private boolean cheese;\n        private final List<String> toppings = new ArrayList<>();\n\n        Builder(String size) {\n            this.size = size;\n        }\n\n        Builder cheese(boolean c) {\n            this.cheese = c;\n            return this;\n        }\n\n        Builder topping(String t) {\n            toppings.add(t);\n            return this;\n        }\n\n        Pizza build() {\n            return new Pizza(this);\n        }\n    }\n}\n\n'),
                starter=SCAN, require=[r"class\s+Builder", r"return\s+this", r"build\(\)"], fallback=[r"static\s+class\s+Builder", r"return\s+this", r"build\(\)"]),
        ),
        lesson(
            "Observer",
            """Observer lets one object (the subject) notify many listeners without knowing who they are - the basis of events and GUIs.

interface Listener { void onChange(String value); }
class Subject {
    private final List<Listener> listeners = new ArrayList<>();
    void subscribe(Listener l) { listeners.add(l); }
    void set(String v) { for (Listener l : listeners) l.onChange(v); }
}

Subscribers can be lambdas: subject.subscribe(v -> System.out.println("got " + v));""",
            mcq("What does the subject know about its listeners?", ["Only the Listener interface", "Their concrete classes", "Their fields", "Nothing at all, not even that they exist"], 0),
            mcq("Which feature gives you events in GUIs?", ["Observer / listeners", "Singletons", "Recursion", "Generics"], 0),
            mcq("Can a lambda be a Listener?", ["Yes, if it's a functional interface", "No", "Only static ones", "Only with abstract classes"], 0),
            run("Implement a Subject with subscribe(Listener) and set(String). Read n words; subscribe two listeners (one prints 'A:word', one prints 'B:LENGTH') then call set for each word.", "java",
                [t("two", stdin="2\nhi java"), t("one", stdin="1\nok")], ["A:hi\nB:2\nA:java\nB:4", "A:ok\nB:2"],
                scan('int n = in.nextInt();\nSubject s = new Subject();\ns.subscribe(v -> System.out.println("A:" + v));\ns.subscribe(v -> System.out.println("B:" + v.length()));\nfor (int i = 0; i < n; i++) s.set(in.next());',
                     before='interface Listener {\n    void onChange(String value);\n}\n\nclass Subject {\n    private final List<Listener> listeners = new ArrayList<>();\n\n    void subscribe(Listener l) {\n        listeners.add(l);\n    }\n\n    void set(String value) {\n        for (Listener l : listeners) l.onChange(value);\n    }\n}\n\n'),
                starter=SCAN, require=[r"interface\s+Listener", r"subscribe"], fallback=[r"interface\s+Listener", r"subscribe\(", r"onChange"]),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · Enums & nested types",
        lesson(
            "Enums with fields and methods",
            """A Java enum is a full class with a fixed set of instances. It can have fields, constructors and methods:

enum Planet {
    MERCURY(3.30e23), EARTH(5.97e24);
    private final double mass;
    Planet(double mass) { this.mass = mass; }
    double mass() { return mass; }
}

values() lists the constants, valueOf("EARTH") parses one, ordinal() gives its position, and enums work in switch and as map keys.""",
            mcq("What does Enum.values() return?", ["An array of all constants", "A list of strings", "The first constant", "The count"], 0),
            mcq("Can enums have constructors?", ["Yes, and they are private", "No", "Only public", "Only static"], 0),
            mcq("What does valueOf(\"EARTH\") do for a missing name?", ["Throws IllegalArgumentException", "Returns null", "Returns first", "Returns -1"], 0),
            run("Define enum Size with fields extra (price addition): SMALL(0), MEDIUM(2), LARGE(4). Read a size name and a base price and print the total price. Print INVALID if the size name does not exist.", "java",
                [t("medium", stdin="MEDIUM 10"), t("large", stdin="LARGE 5"), t("bad", stdin="HUGE 1")], ["12", "9", "INVALID"],
                scan('String name = in.next();\nint base = in.nextInt();\ntry {\n    System.out.println(base + Size.valueOf(name).extra());\n} catch (IllegalArgumentException e) {\n    System.out.println("INVALID");\n}',
                     before='enum Size {\n    SMALL(0), MEDIUM(2), LARGE(4);\n\n    private final int extra;\n\n    Size(int extra) {\n        this.extra = extra;\n    }\n\n    int extra() {\n        return extra;\n    }\n}\n\n'),
                starter=SCAN, require=[r"enum\s+Size", r"valueOf"], fallback=[r"enum\s+Size", r"valueOf\(", r"IllegalArgumentException"]),
        ),
        lesson(
            "Enum state machines & EnumMap",
            """Enums model states perfectly, and each constant can override behaviour:

enum Light {
    RED { Light next() { return GREEN; } },
    GREEN { Light next() { return YELLOW; } },
    YELLOW { Light next() { return RED; } };
    abstract Light next();
}

EnumMap<K,V> and EnumSet are compact, fast collections keyed by enum constants, iterated in declaration order.""",
            mcq("What can each enum constant do?", ["Override an abstract method with its own body", "Nothing", "Extend another enum", "Be created with new"], 0),
            mcq("EnumMap iterates in…", ["Declaration order of the constants", "Random order", "Alphabetical order", "Insertion order"], 0),
            mcq("Why prefer enums over int constants?", ["Type safety and readability", "Speed only", "Less code always", "Reflection"], 0),
            run("Define enum Light with RED->GREEN->YELLOW->RED via an abstract next(). Read n and print the light after n steps starting from RED.", "java",
                [t("three", stdin="3"), t("four", stdin="4"), t("zero", stdin="0")], ["RED", "GREEN", "RED"],
                scan('int n = in.nextInt();\nLight l = Light.RED;\nfor (int i = 0; i < n; i++) l = l.next();\nSystem.out.println(l);',
                     before='enum Light {\n    RED {\n        Light next() {\n            return GREEN;\n        }\n    },\n    GREEN {\n        Light next() {\n            return YELLOW;\n        }\n    },\n    YELLOW {\n        Light next() {\n            return RED;\n        }\n    };\n\n    abstract Light next();\n}\n\n'),
                starter=SCAN, require=[r"enum\s+Light", r"abstract\s+Light\s+next"], fallback=[r"enum\s+Light", r"abstract\s+Light\s+next", r"RED"]),
        ),
        lesson(
            "Nested, inner and anonymous classes",
            """Classes can live inside classes:

- static nested class: independent of the outer instance (Builder, Node)
- inner class: each instance belongs to an outer object and can use its fields
- local / anonymous class: defined inside a method; anonymous ones implement an interface on the spot: new Runnable() { public void run() { ... } }

Lambdas replace most anonymous classes when the interface has one method. Inside a lambda, 'this' is the enclosing object - inside an anonymous class it is the anonymous object itself.""",
            mcq("What is a static nested class independent of?", ["An outer instance", "The compiler", "Packages", "Imports"], 0),
            mcq("What can an inner (non-static) class access?", ["The outer instance's fields", "Nothing", "Only static fields", "Only constants"], 0),
            mcq("What does an anonymous class do?", ["Implements or extends a type on the spot", "Hides a name", "Is always static", "Runs on a thread"], 0),
            run("Write a LinkedStack<T> using a private static nested class Node<T>. Read n commands ('push x' or 'pop') and print the popped values; print EMPTY when popping an empty stack.", "java",
                [t("mix", stdin="5\npush 1\npush 2\npop\npop\npop"), t("empty", stdin="1\npop")], ["2\n1\nEMPTY", "EMPTY"],
                scan('int n = in.nextInt();\nLinkedStack<Integer> s = new LinkedStack<>();\nfor (int i = 0; i < n; i++) {\n    String cmd = in.next();\n    if (cmd.equals("push")) s.push(in.nextInt());\n    else System.out.println(s.isEmpty() ? "EMPTY" : String.valueOf(s.pop()));\n}',
                     before='class LinkedStack<T> {\n    private static class Node<T> {\n        final T value;\n        final Node<T> next;\n\n        Node(T value, Node<T> next) {\n            this.value = value;\n            this.next = next;\n        }\n    }\n\n    private Node<T> top;\n\n    void push(T v) {\n        top = new Node<>(v, top);\n    }\n\n    T pop() {\n        T v = top.value;\n        top = top.next;\n        return v;\n    }\n\n    boolean isEmpty() {\n        return top == null;\n    }\n}\n\n'),
                starter=SCAN, require=[r"static\s+class\s+Node", r"LinkedStack"], fallback=[r"static\s+class\s+Node", r"class\s+LinkedStack", r"push\("]),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Big numbers, bits & time",
        lesson(
            "BigInteger and BigDecimal",
            """long overflows at about 9.2 × 10^18. BigInteger has unlimited size; BigDecimal does exact decimal arithmetic (never use double for money).

BigInteger f = BigInteger.ONE;
for (int i = 2; i <= 30; i++) f = f.multiply(BigInteger.valueOf(i));

BigDecimal a = new BigDecimal("0.1"), b = new BigDecimal("0.2");
a.add(b);                         // exactly 0.3 (the double 0.1 + 0.2 is 0.30000000000000004)

Both are immutable: add, multiply, divide return NEW objects. Construct BigDecimal from a String, not a double.""",
            mcq("Why use BigDecimal for money?", ["Exact decimal arithmetic", "It's faster", "It's shorter", "It avoids classes"], 0),
            mcq("Are BigInteger methods in-place?", ["No, they return new objects", "Yes", "Only add", "Only multiply"], 0),
            mcq("How should you create a BigDecimal of 0.1?", ["new BigDecimal(\"0.1\")", "new BigDecimal(0.1)", "0.1.big()", "BigDecimal.of(0.1f)"], 0),
            run("Read n (up to 50) and print n! exactly using BigInteger.", "java",
                [t("20", stdin="20"), t("30", stdin="30"), t("zero", stdin="0")], ["2432902008176640000", "265252859812191058636308480000000", "1"],
                scan('int n = in.nextInt();\nBigInteger f = BigInteger.ONE;\nfor (int i = 2; i <= n; i++) f = f.multiply(BigInteger.valueOf(i));\nSystem.out.println(f);').replace("import java.util.*;", "import java.math.BigInteger;\nimport java.util.*;"),
                starter=SCAN, require=[r"BigInteger", r"multiply"], fallback=[r"BigInteger", r"multiply\("]),
        ),
        lesson(
            "Bit manipulation",
            """Integers are bit patterns, and bit operators are fast and powerful:

a & b   AND     a | b   OR     a ^ b   XOR     ~a   NOT
a << k  shift left (multiply by 2^k)    a >> k  shift right    a >>> k  unsigned shift

Test bit i: (x >> i) & 1.   Set it: x | (1 << i).   Clear it: x & ~(1 << i).   Toggle it: x ^ (1 << i).
Integer.bitCount(x) counts the 1 bits; x & (x - 1) clears the lowest set bit; a power of two has exactly one bit.""",
            mcq("What does x << 3 do?", ["Multiplies by 8", "Divides by 8", "Adds 3", "Rotates"], 0),
            mcq("How do you test bit i of x?", ["(x >> i) & 1", "x | i", "x ^ i", "x << i"], 0),
            mcq("What does a ^ a equal?", ["0", "a", "1", "-a"], 0),
            run("Read n numbers. Print how many are powers of two (positive and with exactly one set bit).", "java",
                [t("some", stdin="6\n1 2 3 4 6 8"), t("none", stdin="2\n0 -4")], ["4", "0"],
                scan('int n = in.nextInt();\nint count = 0;\nfor (int i = 0; i < n; i++) {\n    int x = in.nextInt();\n    if (x > 0 && (x & (x - 1)) == 0) count++;\n}\nSystem.out.println(count);'),
                starter=SCAN, require=[r"&"], fallback=[r"&\s*\(", r"bitCount|x\s*-\s*1"]),
        ),
        lesson(
            "Dates with java.time",
            """java.time replaces the old Date and Calendar. The classes are immutable:

LocalDate d = LocalDate.of(2024, 2, 28);
d.plusDays(2);                              // 2024-03-01 (2024 is a leap year)
d.getDayOfWeek();                           // WEDNESDAY
ChronoUnit.DAYS.between(d1, d2);            // whole days between two dates
Duration.ofMinutes(90).toHours();           // 1

LocalDate parses ISO 'yyyy-MM-dd' strings with LocalDate.parse(...). Use DateTimeFormatter for other formats.""",
            mcq("Are java.time objects mutable?", ["No, they are immutable", "Yes", "Only LocalDate", "Only Duration"], 0),
            mcq("Which gives days between two dates?", ["ChronoUnit.DAYS.between", "d1 - d2", "d1.minus(d2)", "Duration.days"], 0),
            mcq("Does plusDays change the original date?", ["No, it returns a new one", "Yes", "Only in leap years", "Only for negative"], 0),
            run("Read two ISO dates (yyyy-MM-dd). Print the number of days between them (second minus first, may be negative) and the weekday name of the first in capitals.", "java",
                [t("span", stdin="2024-02-28 2024-03-01"), t("negative", stdin="2024-01-10 2024-01-01")], ["2\nWEDNESDAY", "-9\nWEDNESDAY"],
                scan('LocalDate a = LocalDate.parse(in.next()), b = LocalDate.parse(in.next());\nSystem.out.println(ChronoUnit.DAYS.between(a, b));\nSystem.out.println(a.getDayOfWeek());').replace("import java.util.*;", "import java.time.*;\nimport java.time.temporal.ChronoUnit;\nimport java.util.*;"),
                starter=SCAN, require=[r"LocalDate", r"ChronoUnit|between"], fallback=[r"LocalDate", r"ChronoUnit", r"between"]),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Capstone projects",
        lesson(
            "Capstone: bank accounts",
            """Combine objects, collections and exceptions in one small system.

Design: an Account holds a balance; a Bank keeps accounts in a Map by id; operations validate input and throw descriptive exceptions; main parses commands. Keep each rule in ONE place (Account.withdraw checks funds; Bank looks accounts up) so changes stay local.""",
            mcq("Where should the 'enough funds' rule live?", ["In Account.withdraw", "In every caller", "In main", "In toString"], 0),
            mcq("Which collection finds an account by id fastest?", ["HashMap", "ArrayList scan", "Stack", "Queue"], 0),
            mcq("Why throw exceptions instead of printing inside Account?", ["The caller decides how to report errors", "Printing is forbidden", "It's faster", "Exceptions are shorter"], 0),
            run("Commands, one per line, ending with 'end': 'open ID' (balance 0), 'deposit ID AMT', 'withdraw ID AMT', 'show ID'. Print 'ID: BALANCE' for show. Print 'ERROR' for an unknown id or when a withdrawal exceeds the balance (and leave the balance unchanged).", "java",
                [t("flow", stdin="open a\ndeposit a 100\nwithdraw a 30\nshow a\nwithdraw a 500\nshow a\nshow z\nend"), t("empty", stdin="open x\nshow x\nend")],
                ["a: 70\nERROR\na: 70\nERROR", "x: 0"],
                scan('Map<String, Integer> accounts = new HashMap<>();\nwhile (true) {\n    String cmd = in.next();\n    if (cmd.equals("end")) break;\n    String id = in.next();\n    if (cmd.equals("open")) {\n        accounts.put(id, 0);\n    } else if (!accounts.containsKey(id)) {\n        if (cmd.equals("deposit") || cmd.equals("withdraw")) in.nextInt();\n        System.out.println("ERROR");\n    } else if (cmd.equals("deposit")) {\n        accounts.merge(id, in.nextInt(), Integer::sum);\n    } else if (cmd.equals("withdraw")) {\n        int amt = in.nextInt();\n        if (amt > accounts.get(id)) System.out.println("ERROR");\n        else accounts.put(id, accounts.get(id) - amt);\n    } else {\n        System.out.println(id + ": " + accounts.get(id));\n    }\n}'),
                starter=SCAN, require=[r"Map<"], fallback=[r"Map<", r"deposit", r"withdraw", r"ERROR"]),
        ),
        lesson(
            "Capstone: inventory",
            """An inventory tracks stock levels and enforces simple business rules. The same structure - a Map keyed by item plus small operations - powers carts, wallets and game state.

Plan before coding: list the commands, decide the data (item -> quantity), list the error cases (unknown item, not enough stock), and decide the output format. Then implement one command at a time and test each.""",
            mcq("What is a good first step for a project like this?", ["List commands, data and error cases", "Write all the code at once", "Pick colours", "Add threads"], 0),
            mcq("Which structure maps item -> quantity?", ["Map<String, Integer>", "List<String>", "Set<Integer>", "int[]"], 0),
            mcq("How should unknown items be handled?", ["Explicit, consistent error output", "Ignore silently", "Crash", "Create them silently"], 0),
            run("Commands until 'end': 'add ITEM QTY', 'remove ITEM QTY' and 'report'. remove prints 'SHORT' when stock is insufficient or the item is unknown (no change). report prints items alphabetically as 'item=qty', space-separated (or EMPTY), dropping items at 0.", "java",
                [t("flow", stdin="add pen 10\nadd ink 4\nremove pen 3\nremove ink 9\nremove cap 1\nreport\nend"), t("empty", stdin="add a 2\nremove a 2\nreport\nend")],
                ["SHORT\nSHORT\nink=4 pen=7", "EMPTY"],
                scan('TreeMap<String, Integer> stock = new TreeMap<>();\nwhile (true) {\n    String cmd = in.next();\n    if (cmd.equals("end")) break;\n    if (cmd.equals("add")) {\n        stock.merge(in.next(), in.nextInt(), Integer::sum);\n    } else if (cmd.equals("remove")) {\n        String item = in.next();\n        int q = in.nextInt();\n        int have = stock.getOrDefault(item, 0);\n        if (q > have) {\n            System.out.println("SHORT");\n        } else if (q == have) {\n            stock.remove(item);\n        } else {\n            stock.put(item, have - q);\n        }\n    } else {\n        StringBuilder sb = new StringBuilder();\n        for (Map.Entry<String, Integer> e : stock.entrySet()) {\n            if (sb.length() > 0) sb.append(\' \');\n            sb.append(e.getKey()).append(\'=\').append(e.getValue());\n        }\n        System.out.println(sb.length() == 0 ? "EMPTY" : sb.toString());\n    }\n}'),
                starter=SCAN, require=[r"Map<"], fallback=[r"Map<", r"SHORT", r"EMPTY"]),
        ),
        lesson(
            "Capstone: state machine game",
            """A text adventure is a state machine: a current ROOM plus commands that move between rooms. Model the rooms as an enum or map, store exits as room -> (direction -> room), and loop reading commands until 'quit'.

Separating the DATA (the map of rooms) from the ENGINE (the loop) means you can add rooms without touching the loop - the hallmark of a clean design.""",
            mcq("What is the 'state' in a text adventure?", ["The current room", "The score only", "The command list", "The code"], 0),
            mcq("Why separate the room data from the loop?", ["Add rooms without editing the engine", "It runs faster", "It is shorter", "Java requires it"], 0),
            mcq("Which structure stores exits?", ["Map<String, Map<String, String>>", "int[]", "StringBuilder", "Optional"], 0),
            run("Rooms: hall (north->study, east->kitchen), study (south->hall), kitchen (west->hall). Start in hall. Read commands until 'quit'. 'go DIR' moves if an exit exists and prints 'You are in ROOM'; otherwise prints 'No exit'. 'where' prints the room name.", "java",
                [t("walk", stdin="go north\ngo north\nwhere\ngo south\ngo east\nwhere\nquit"), t("lost", stdin="go west\nwhere\nquit")],
                ["You are in study\nNo exit\nstudy\nYou are in hall\nYou are in kitchen\nkitchen", "No exit\nhall"],
                scan('Map<String, Map<String, String>> rooms = new HashMap<>();\nrooms.put("hall", Map.of("north", "study", "east", "kitchen"));\nrooms.put("study", Map.of("south", "hall"));\nrooms.put("kitchen", Map.of("west", "hall"));\nString room = "hall";\nwhile (true) {\n    String cmd = in.next();\n    if (cmd.equals("quit")) break;\n    if (cmd.equals("where")) {\n        System.out.println(room);\n    } else {\n        String dir = in.next();\n        String next = rooms.get(room).get(dir);\n        if (next == null) {\n            System.out.println("No exit");\n        } else {\n            room = next;\n            System.out.println("You are in " + room);\n        }\n    }\n}'),
                starter=SCAN, require=[r"Map<"], fallback=[r"Map<", r"No exit", r"quit"]),
        ),
        lesson(
            "Capstone: parking lot & library",
            """Two more designs to practise:

PARKING LOT - capacity N; 'park PLATE' fails with FULL when no space; 'leave PLATE' frees a spot; fee = hours × rate. The lot is a Map<plate, entryHour> plus a capacity check.

LIBRARY - books can be borrowed once at a time; 'borrow BOOK USER' fails if already out; 'return BOOK' makes it available. A Map<book, user> is enough.

Both are small state machines with clear rules - exactly the shape of real backend services.""",
            mcq("What data tracks who has each book?", ["Map<book, user>", "int", "String[]", "Set<int>"], 0),
            mcq("What should 'park' do when the lot is full?", ["Report FULL without changing state", "Crash", "Park anyway", "Delete a car"], 0),
            mcq("What do both projects share?", ["Clear rules over a small state", "Threads", "Generics only", "Networking"], 0),
            run("Library: commands until 'end': 'borrow BOOK USER' prints 'OK' or 'OUT' if the book is already borrowed; 'return BOOK' prints 'RETURNED' or 'NOT OUT'; 'who BOOK' prints the borrower or NONE.", "java",
                [t("flow", stdin="borrow dune ann\nborrow dune bob\nwho dune\nreturn dune\nwho dune\nreturn dune\nend"), t("simple", stdin="borrow a x\nwho a\nend")],
                ["OK\nOUT\nann\nRETURNED\nNONE\nNOT OUT", "OK\nx"],
                scan('Map<String, String> out = new HashMap<>();\nwhile (true) {\n    String cmd = in.next();\n    if (cmd.equals("end")) break;\n    String book = in.next();\n    if (cmd.equals("borrow")) {\n        String user = in.next();\n        if (out.containsKey(book)) {\n            System.out.println("OUT");\n        } else {\n            out.put(book, user);\n            System.out.println("OK");\n        }\n    } else if (cmd.equals("return")) {\n        System.out.println(out.remove(book) != null ? "RETURNED" : "NOT OUT");\n    } else {\n        System.out.println(out.getOrDefault(book, "NONE"));\n    }\n}'),
                starter=SCAN, require=[r"Map<"], fallback=[r"Map<", r"borrow", r"RETURNED"]),
        ),
    ),
)
