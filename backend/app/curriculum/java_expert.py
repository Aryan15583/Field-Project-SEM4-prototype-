"""Java - Expert section, part 1 (units 17-23): object design, collections in depth, streams, generics & functional
style, exceptions & resources, concurrency, algorithms. Runnable exercises stick to Java 11-15 features; newer
features (records, sealed classes, pattern matching) are taught in the quiz exercises."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .java_adv import MAIN, SCAN, prog, scan

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Designing objects well",
        lesson(
            "Immutable classes",
            """An immutable object never changes after construction - safe to share, cache and use as a map key. Recipe:

- make the class final (no subclass can break the rules)
- make all fields private final
- no setters; methods that 'change' return a NEW object
- copy mutable inputs (defensive copies) and never return internal mutable state

final class Money {
    private final long cents;
    Money(long cents) { this.cents = cents; }
    Money plus(Money other) { return new Money(cents + other.cents); }
}

String and Integer are immutable.""",
            mcq("What does an immutable class's 'plus' method return?", ["A new object", "The same object changed", "void", "null"], 0),
            mcq("Why make the class final?", ["So subclasses can't break immutability", "For speed only", "For serialization", "To hide it"], 0),
            mcq("Which are immutable in Java?", ["String and Integer", "ArrayList", "StringBuilder", "Date"], 0),
            run("Write an immutable class Money(long cents) with plus(Money), times(int) and toString() giving e.g. $12.34. main reads two amounts in cents, prints their sum, then the first times 3.", "java",
                [t("sum", stdin="1050 275"), t("zero", stdin="0 5")], ["$13.25\n$31.50", "$0.05\n$0.00"],
                scan('long a = in.nextLong(), b = in.nextLong();\nMoney x = new Money(a);\nSystem.out.println(x.plus(new Money(b)));\nSystem.out.println(x.times(3));',
                     before='final class Money {\n    private final long cents;\n\n    Money(long cents) {\n        this.cents = cents;\n    }\n\n    Money plus(Money other) {\n        return new Money(cents + other.cents);\n    }\n\n    Money times(int n) {\n        return new Money(cents * n);\n    }\n\n    @Override\n    public String toString() {\n        return String.format("$%d.%02d", cents / 100, cents % 100);\n    }\n}\n\n'),
                starter=SCAN, require=[r"final\s+class\s+Money", r"private\s+final"], fallback=[r"final\s+class\s+Money", r"private\s+final\s+long", r"new\s+Money\("]),
        ),
        lesson(
            "equals, hashCode and toString",
            """Three methods every value class should consider:

- equals(Object) - when are two objects 'the same'? (default: same memory address)
- hashCode() - MUST be consistent with equals: equal objects need equal hash codes, or HashMap/HashSet break
- toString() - a readable description for logs and debugging

@Override public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Point)) return false;
    Point p = (Point) o;
    return x == p.x && y == p.y;
}
@Override public int hashCode() { return Objects.hash(x, y); }

Always override equals and hashCode together.""",
            mcq("Equal objects must have…", ["Equal hash codes", "Different hash codes", "The same memory address", "The same class loader"], 0),
            mcq("What is the default equals?", ["Compares references (identity)", "Compares fields", "Always true", "Compares toString"], 0),
            mcq("What happens to a HashSet if hashCode is inconsistent with equals?", ["It may store duplicates or miss items", "Nothing", "It sorts", "It throws at compile time"], 0),
            run("Write class Point(int x, int y) with equals, hashCode and toString '(x,y)'. main reads n points, adds them to a HashSet and prints how many are distinct, then the set size after adding (0,0).", "java",
                [t("dups", stdin="4\n1 2\n1 2\n3 4\n0 0"), t("one", stdin="1\n5 5")], ["3\n3", "1\n2"],
                scan('int n = in.nextInt();\nSet<Point> set = new HashSet<>();\nfor (int i = 0; i < n; i++) set.add(new Point(in.nextInt(), in.nextInt()));\nSystem.out.println(set.size());\nset.add(new Point(0, 0));\nSystem.out.println(set.size());',
                     before='class Point {\n    private final int x, y;\n\n    Point(int x, int y) {\n        this.x = x;\n        this.y = y;\n    }\n\n    @Override\n    public boolean equals(Object o) {\n        if (this == o) return true;\n        if (!(o instanceof Point)) return false;\n        Point p = (Point) o;\n        return x == p.x && y == p.y;\n    }\n\n    @Override\n    public int hashCode() {\n        return Objects.hash(x, y);\n    }\n\n    @Override\n    public String toString() {\n        return "(" + x + "," + y + ")";\n    }\n}\n\n'),
                starter=SCAN, require=[r"hashCode", r"equals"], fallback=[r"boolean\s+equals\s*\(\s*Object", r"int\s+hashCode\s*\(", r"HashSet"]),
        ),
        lesson(
            "Comparable and Comparator",
            """Comparable gives a class its natural order (compareTo); a Comparator defines other orders without changing the class.

class Person implements Comparable<Person> {
    public int compareTo(Person o) { return Integer.compare(age, o.age); }
}
people.sort(Comparator.comparing(Person::getName));
people.sort(Comparator.comparingInt(Person::getAge).reversed().thenComparing(Person::getName));

compareTo returns negative, zero or positive. Use Integer.compare, never subtraction (it can overflow).""",
            mcq("What should compareTo return when this is smaller?", ["A negative number", "A positive number", "0", "true"], 0),
            mcq("Why avoid 'a - b' in a comparator?", ["It can overflow", "It is slow", "It's invalid", "It sorts descending"], 0),
            mcq("Which sorts by age descending then name?", ["comparingInt(age).reversed().thenComparing(name)", "sort(age, name)", "orderBy(age)", "compareTo(age)"], 0),
            run("Read n then n lines 'name score'. Print the names ordered by score descending, ties alphabetically (use a Comparator).", "java",
                [t("ties", stdin="4\nbo 80\nada 90\ncy 80\ndee 70"), t("one", stdin="1\nsolo 5")], ["ada\nbo\ncy\ndee", "solo"],
                scan('int n = in.nextInt();\nList<String[]> rows = new ArrayList<>();\nfor (int i = 0; i < n; i++) rows.add(new String[] {in.next(), in.next()});\nrows.sort(Comparator.comparingInt((String[] r) -> -Integer.parseInt(r[1])).thenComparing(r -> r[0]));\nfor (String[] r : rows) System.out.println(r[0]);'),
                starter=SCAN, require=[r"Comparator|compareTo"], fallback=[r"Comparator|compareTo", r"sort\("]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Collections in depth",
        lesson(
            "TreeMap and TreeSet navigation",
            """TreeMap/TreeSet keep keys SORTED and offer range queries in O(log n):

TreeMap<Integer, String> m = new TreeMap<>();
m.firstKey(); m.lastKey();
m.floorKey(5);     // greatest key <= 5
m.ceilingKey(5);   // smallest key >= 5
m.headMap(5);      // keys < 5
m.tailMap(5, true);// keys >= 5

HashMap is faster for plain lookups; use a Tree structure when you need order or 'nearest key' queries.""",
            mcq("What does floorKey(5) return?", ["The greatest key <= 5", "The smallest key >= 5", "5 always", "The first key"], 0),
            mcq("Which map keeps keys sorted?", ["TreeMap", "HashMap", "LinkedHashMap", "ConcurrentHashMap"], 0),
            mcq("What is TreeMap's lookup cost?", ["O(log n)", "O(1)", "O(n)", "O(n log n)"], 0),
            run("Read n numbers (sorted or not), then q queries. For each query x print the largest number <= x, or NONE. Use a TreeSet.", "java",
                [t("classic", stdin="4\n10 3 7 20\n3\n8 2 20"), t("one", stdin="1\n5\n2\n4 5")], ["7\nNONE\n20", "NONE\n5"],
                scan('int n = in.nextInt();\nTreeSet<Integer> set = new TreeSet<>();\nfor (int i = 0; i < n; i++) set.add(in.nextInt());\nint q = in.nextInt();\nfor (int i = 0; i < q; i++) {\n    Integer f = set.floor(in.nextInt());\n    System.out.println(f == null ? "NONE" : String.valueOf(f));\n}'),
                starter=SCAN, require=[r"TreeSet|TreeMap"], fallback=[r"TreeSet|TreeMap", r"floor"]),
        ),
        lesson(
            "Deque, stack and queue",
            """ArrayDeque is the go-to stack AND queue (faster than Stack and LinkedList):

Deque<Integer> stack = new ArrayDeque<>();
stack.push(1); stack.push(2); stack.pop();     // 2  (LIFO at the front)

Queue<Integer> queue = new ArrayDeque<>();
queue.offer(1); queue.offer(2); queue.poll();  // 1  (FIFO)

offer/poll/peek return null when empty; add/remove/element throw. The old Stack and Vector classes are legacy - avoid them.""",
            mcq("Which class should you prefer for a stack?", ["ArrayDeque", "Stack", "Vector", "Hashtable"], 0),
            mcq("What does queue.poll() return when empty?", ["null", "An exception", "0", "false"], 0),
            mcq("Which end does push() use?", ["The front", "The back", "Random", "Sorted"], 0),
            run("Read a string of brackets ()[]{} and print VALID if every bracket is closed in the right order, otherwise INVALID. Use a Deque.", "java",
                [t("ok", stdin="([]{})"), t("bad", stdin="(]"), t("open", stdin="((")], ["VALID", "INVALID", "INVALID"],
                scan('String s = in.nextLine();\nDeque<Character> stack = new ArrayDeque<>();\nboolean ok = true;\nfor (char c : s.toCharArray()) {\n    if (c == \'(\' || c == \'[\' || c == \'{\') stack.push(c);\n    else {\n        if (stack.isEmpty()) { ok = false; break; }\n        char open = stack.pop();\n        if ((c == \')\' && open != \'(\') || (c == \']\' && open != \'[\') || (c == \'}\' && open != \'{\')) { ok = false; break; }\n    }\n}\nSystem.out.println(ok && stack.isEmpty() ? "VALID" : "INVALID");'),
                starter=SCAN, require=[r"Deque|Stack|ArrayDeque"], fallback=[r"Deque|Stack", r"push\(", r"pop\("]),
        ),
        lesson(
            "PriorityQueue and LinkedHashMap",
            """PriorityQueue is a heap: poll() always returns the smallest element (or the one your Comparator ranks first), in O(log n).

PriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.reverseOrder());   // max-heap

LinkedHashMap remembers insertion order - and with accessOrder=true plus removeEldestEntry you get an LRU cache:

new LinkedHashMap<K, V>(16, 0.75f, true) {
    protected boolean removeEldestEntry(Map.Entry<K, V> e) { return size() > CAPACITY; }
};""",
            mcq("What does PriorityQueue.poll() return?", ["The highest-priority (smallest by default) element", "The newest element", "A random one", "The largest always"], 0),
            mcq("How do you get a max-heap?", ["Pass Comparator.reverseOrder()", "Use a TreeSet", "Call reverse()", "It's the default"], 0),
            mcq("What does LinkedHashMap(…, true) enable?", ["Access-order, for LRU caches", "Sorting", "Thread safety", "Null keys"], 0),
            run("Read n numbers and k. Print the k largest numbers in descending order using a PriorityQueue.", "java",
                [t("classic", stdin="6\n3 2 1 5 6 4\n2"), t("all", stdin="3\n9 8 7\n3")], ["6 5", "9 8 7"],
                scan('int n = in.nextInt();\nPriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.reverseOrder());\nfor (int i = 0; i < n; i++) pq.add(in.nextInt());\nint k = in.nextInt();\nStringBuilder sb = new StringBuilder();\nfor (int i = 0; i < k; i++) {\n    if (i > 0) sb.append(\' \');\n    sb.append(pq.poll());\n}\nSystem.out.println(sb);'),
                starter=SCAN, require=[r"PriorityQueue"], fallback=[r"PriorityQueue", r"poll\("]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Streams in depth",
        lesson(
            "groupingBy and counting",
            """Collectors turn a stream into a data structure. groupingBy builds a Map of lists, or counts, sums or any other downstream collector:

Map<Integer, List<String>> byLength = words.stream().collect(Collectors.groupingBy(String::length));
Map<Character, Long> counts = text.chars().mapToObj(c -> (char) c).collect(Collectors.groupingBy(c -> c, TreeMap::new, Collectors.counting()));

Passing TreeMap::new as the map factory gives sorted keys. Collectors.partitioningBy splits into exactly two groups (true / false).""",
            mcq("What does groupingBy return?", ["A Map from keys to grouped results", "A List", "A Set", "A String"], 0),
            mcq("What does partitioningBy produce?", ["A Map with true and false groups", "Two lists", "A sorted list", "A stream"], 0),
            mcq("How do you get sorted keys from groupingBy?", ["Pass TreeMap::new", "Call sort", "Use HashMap", "It's automatic"], 0),
            run("Read words on one line. Print each word length with how many words have that length, as 'length:count' lines in ascending length order (use streams and groupingBy with a TreeMap).", "java",
                [t("mixed", stdin="a bb cc d eee"), t("one", stdin="hello")], ["1:2\n2:2\n3:1", "5:1"],
                scan('String[] words = in.nextLine().split(" ");\nMap<Integer, Long> m = Arrays.stream(words).collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));\nm.forEach((k, v) -> System.out.println(k + ":" + v));').replace("import java.util.*;", "import java.util.*;\nimport java.util.stream.*;"),
                starter=SCAN, require=[r"groupingBy"], fallback=[r"groupingBy", r"Collectors"]),
        ),
        lesson(
            "map, filter, flatMap and reduce",
            """The core stream operations:

filter(x -> x > 0)           keep matching items
map(String::toUpperCase)     transform each item
flatMap(list -> list.stream()) flatten nested collections into one stream
sorted() / distinct() / limit(n) / skip(n)
reduce(0, Integer::sum)      combine all items into one value
mapToInt(...).sum() / average() / max()

Streams are lazy: nothing runs until a terminal operation (collect, forEach, sum, count) is called.""",
            mcq("What does flatMap do?", ["Turns nested collections into one stream", "Filters nulls", "Sorts", "Counts"], 0),
            mcq("When does a stream pipeline actually run?", ["At the terminal operation", "At creation", "At each map", "Never"], 0),
            mcq("What does reduce(0, Integer::sum) do?", ["Adds all items together", "Returns the first item", "Filters zeros", "Counts items"], 0),
            run("Read n then n numbers. Print the sum of the squares of the even numbers using a stream (filter, mapToInt, sum).", "java",
                [t("mix", stdin="5\n1 2 3 4 5"), t("none", stdin="2\n1 3")], ["20", "0"],
                scan('int n = in.nextInt();\nList<Integer> nums = new ArrayList<>();\nfor (int i = 0; i < n; i++) nums.add(in.nextInt());\nSystem.out.println(nums.stream().filter(x -> x % 2 == 0).mapToInt(x -> x * x).sum());'),
                starter=SCAN, require=[r"\.stream\(\)", r"filter"], fallback=[r"\.stream\(\)", r"filter\(", r"sum\("]),
        ),
        lesson(
            "Optional done right",
            """Optional<T> says 'a value might be missing' in the type, instead of returning null:

Optional<String> name = findName(id);
String shown = name.map(String::toUpperCase).orElse("unknown");
name.ifPresent(System.out::println);
int len = name.map(String::length).orElseGet(() -> 0);

Avoid Optional.get() without checking (it throws), don't use Optional for fields or parameters, and never return null from a method that returns Optional. Stream's findFirst, min and max return Optionals.""",
            mcq("What does orElse(\"x\") do?", ["Returns the value or \"x\" if empty", "Throws if empty", "Returns null", "Sets the value"], 0),
            mcq("Which is a bad use of Optional?", ["As a field type or method parameter", "As a return type", "With map()", "With ifPresent()"], 0),
            mcq("What does Optional.get() do on an empty Optional?", ["Throws NoSuchElementException", "Returns null", "Returns 0", "Returns empty"], 0),
            run("Read words on one line. Print the longest word, upper-cased, or NONE if the line is empty (use stream().max with a Comparator and an Optional).", "java",
                [t("words", stdin="cat elephant dog"), t("one", stdin="hi")], ["ELEPHANT", "HI"],
                scan('String line = in.nextLine().trim();\nOptional<String> longest = line.isEmpty() ? Optional.empty() : Arrays.stream(line.split(" ")).max(Comparator.comparingInt(String::length));\nSystem.out.println(longest.map(String::toUpperCase).orElse("NONE"));'),
                starter=SCAN, require=[r"Optional"], fallback=[r"Optional", r"orElse"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Generics & functional style",
        lesson(
            "Bounded types and wildcards",
            """A bounded type parameter limits what T can be:

static <T extends Comparable<T>> T max(List<T> list) { ... }       // T must be comparable

Wildcards express flexibility in method parameters - 'PECS': Producer Extends, Consumer Super.

double sum(List<? extends Number> nums)      // reads Numbers (producer)
void fill(List<? super Integer> out)         // writes Integers (consumer)

List<Integer> is NOT a List<Number> (generics are invariant) - wildcards are how you accept both.""",
            mcq("What does <T extends Comparable<T>> require of T?", ["That T can be compared with itself", "That T is a number", "That T is a String", "Nothing"], 0),
            mcq("When do you use ? extends T?", ["When you only read from the collection", "When you only write", "When you do both", "Never"], 0),
            mcq("Is List<Integer> a subtype of List<Number>?", ["No", "Yes", "Only for final classes", "Only in methods"], 0),
            run("Write a generic method <T extends Comparable<T>> T maxOf(List<T> list) and use it: main reads n words, prints the alphabetically greatest, then reads n integers and prints the greatest of them.", "java",
                [t("both", stdin="3\nfig apple pear\n10 3 7"), t("one", stdin="1\nsolo\n42")], ["pear\n10", "solo\n42"],
                scan('int n = in.nextInt();\nList<String> words = new ArrayList<>();\nfor (int i = 0; i < n; i++) words.add(in.next());\nList<Integer> nums = new ArrayList<>();\nfor (int i = 0; i < n; i++) nums.add(in.nextInt());\nSystem.out.println(maxOf(words));\nSystem.out.println(maxOf(nums));',
                     extra="    static <T extends Comparable<T>> T maxOf(List<T> list) {\n        T best = list.get(0);\n        for (T x : list) {\n            if (x.compareTo(best) > 0) best = x;\n        }\n        return best;\n    }\n\n"),
                starter=SCAN, require=[r"<T extends Comparable<T>>"], fallback=[r"<T extends Comparable<T>>", r"compareTo"]),
        ),
        lesson(
            "Functional interfaces and method references",
            """A functional interface has exactly one abstract method, so a lambda can implement it. The standard ones:

Function<T,R>   R apply(T)          Predicate<T>   boolean test(T)
Supplier<T>     T get()             Consumer<T>    void accept(T)
BiFunction<A,B,R>   UnaryOperator<T>   BinaryOperator<T>

Method references are shorthand: String::length, System.out::println, Person::new. Compose functions with andThen / compose and predicates with and / or / negate.""",
            mcq("Which functional interface returns a boolean?", ["Predicate", "Function", "Supplier", "Consumer"], 0),
            mcq("What does String::length equal as a lambda?", ["s -> s.length()", "() -> length", "s -> length", "length(s)"], 0),
            mcq("Which has no input but returns a value?", ["Supplier", "Consumer", "Predicate", "Function"], 0),
            run("Using Function composition: read a word, then print its length doubled and then squared by composing two Function<Integer,Integer> with andThen.", "java",
                [t("word", stdin="abc"), t("longer", stdin="hello")], ["36", "100"],
                scan('String w = in.next();\nFunction<Integer, Integer> doubleIt = x -> x * 2;\nFunction<Integer, Integer> square = x -> x * x;\nSystem.out.println(doubleIt.andThen(square).apply(w.length()));').replace("import java.util.*;", "import java.util.*;\nimport java.util.function.*;"),
                starter=SCAN, require=[r"andThen|compose"], fallback=[r"Function<", r"andThen|compose"]),
        ),
        lesson(
            "Writing your own functional interface",
            """You can declare a functional interface for a domain idea, optionally annotated @FunctionalInterface so the compiler checks it has one abstract method:

@FunctionalInterface
interface Rule {
    boolean check(String input);
    default Rule and(Rule other) { return s -> check(s) && other.check(s); }
}

default methods let you add helpers without breaking implementers. Rules then compose: Rule r = notEmpty.and(shortEnough);""",
            mcq("What does @FunctionalInterface check?", ["Exactly one abstract method", "That it has lambdas", "That it's public", "That it's generic"], 0),
            mcq("What can a default method do in an interface?", ["Provide behaviour implementers inherit", "Declare fields", "Be private only", "Replace lambdas"], 0),
            mcq("Can a lambda implement a functional interface with a default method?", ["Yes", "No", "Only static ones", "Only generic ones"], 0),
            run("Define @FunctionalInterface Rule { boolean check(String s); default Rule and(Rule o) } then read a word and print OK if it is non-empty, has length <= 6 and contains no digit; otherwise REJECT. Build the rule by combining three lambdas with and().", "java",
                [t("ok", stdin="java"), t("long", stdin="javascript"), t("digit", stdin="a1b")], ["OK", "REJECT", "REJECT"],
                scan('String w = in.hasNext() ? in.next() : "";\nRule notEmpty = s -> !s.isEmpty();\nRule shortEnough = s -> s.length() <= 6;\nRule noDigit = s -> s.chars().noneMatch(Character::isDigit);\nRule all = notEmpty.and(shortEnough).and(noDigit);\nSystem.out.println(all.check(w) ? "OK" : "REJECT");',
                     before='@FunctionalInterface\ninterface Rule {\n    boolean check(String s);\n\n    default Rule and(Rule other) {\n        return s -> check(s) && other.check(s);\n    }\n}\n\n'),
                starter=SCAN, require=[r"@FunctionalInterface", r"default\s+Rule"], fallback=[r"interface\s+Rule", r"default\s+Rule\s+and"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Exceptions & resources",
        lesson(
            "try-with-resources",
            """Anything that implements AutoCloseable can be closed automatically - even when an exception is thrown:

try (Scanner in = new Scanner(System.in); PrintWriter out = new PrintWriter(System.out)) {
    ...
}   // in and out are closed here, in reverse order

Resources are closed BEFORE the catch block runs. Exceptions from close() are attached as 'suppressed' exceptions to the main one, so none is lost. It replaces error-prone try/finally blocks.""",
            mcq("When are try-with-resources resources closed?", ["Automatically at the end of the try block", "Never", "Only on errors", "When garbage collected"], 0),
            mcq("In which order are multiple resources closed?", ["Reverse of creation", "Creation order", "Random", "Alphabetical"], 0),
            mcq("What interface must a resource implement?", ["AutoCloseable", "Runnable", "Serializable", "Comparable"], 0),
            run("Write class Resource implements AutoCloseable (constructor prints 'open NAME', close() prints 'close NAME'). main reads two names and opens both in one try-with-resources, printing 'work' inside.", "java",
                [t("two", stdin="a b"), t("same", stdin="x x")], ["open a\nopen b\nwork\nclose b\nclose a", "open x\nopen x\nwork\nclose x\nclose x"],
                scan('String a = in.next(), b = in.next();\ntry (Resource r1 = new Resource(a); Resource r2 = new Resource(b)) {\n    System.out.println("work");\n}',
                     before='class Resource implements AutoCloseable {\n    private final String name;\n\n    Resource(String name) {\n        this.name = name;\n        System.out.println("open " + name);\n    }\n\n    @Override\n    public void close() {\n        System.out.println("close " + name);\n    }\n}\n\n'),
                starter=SCAN, require=[r"try\s*\(", r"AutoCloseable"], fallback=[r"AutoCloseable", r"try\s*\("]),
        ),
        lesson(
            "Custom exceptions",
            """Create your own exception to give a failure a precise name:

class InsufficientFundsException extends Exception {          // checked: callers MUST handle or declare it
    InsufficientFundsException(String message) { super(message); }
}
class ValidationException extends RuntimeException { ... }     // unchecked: programming/validation errors

Choose CHECKED exceptions for recoverable conditions the caller can do something about; UNCHECKED (RuntimeException) for bugs and invalid arguments. Include helpful messages and keep the original as the cause: new X("msg", cause).""",
            mcq("What must callers do with a checked exception?", ["Catch it or declare it with throws", "Nothing", "Ignore it", "Log it only"], 0),
            mcq("Which should an invalid argument usually be?", ["Unchecked (RuntimeException)", "Checked", "An Error", "A return code"], 0),
            mcq("What does passing a cause to an exception do?", ["Keeps the original error in the chain", "Hides the error", "Retries", "Changes the type"], 0),
            run("Write a checked InsufficientFundsException and method withdraw(balance, amount) that throws it when amount > balance. main reads balance and amount, prints the new balance or 'Insufficient: need X more'.", "java",
                [t("ok", stdin="100 30"), t("short", stdin="50 80")], ["70", "Insufficient: need 30 more"],
                scan('int balance = in.nextInt(), amount = in.nextInt();\ntry {\n    System.out.println(withdraw(balance, amount));\n} catch (InsufficientFundsException e) {\n    System.out.println(e.getMessage());\n}',
                     extra='    static int withdraw(int balance, int amount) throws InsufficientFundsException {\n        if (amount > balance) throw new InsufficientFundsException("Insufficient: need " + (amount - balance) + " more");\n        return balance - amount;\n    }\n\n',
                     before='class InsufficientFundsException extends Exception {\n    InsufficientFundsException(String message) {\n        super(message);\n    }\n}\n\n'),
                starter=SCAN, require=[r"extends\s+Exception", r"throws\s+InsufficientFundsException"], fallback=[r"extends\s+Exception", r"throw\s+new", r"catch\s*\("]),
        ),
        lesson(
            "finally, rethrowing and exception chains",
            """finally ALWAYS runs - after a normal finish, an exception, or even a return in the try block. Don't put return in finally (it swallows exceptions).

try { ... } catch (IOException e) { throw new UncheckedIOException(e); } finally { cleanup(); }

Multi-catch handles several types the same way: catch (IllegalArgumentException | IllegalStateException e). Catch the most specific type first. Never leave a catch block empty - at least log, or rethrow with context.""",
            mcq("When does finally run?", ["Always", "Only after errors", "Only on success", "Never with return"], 0),
            mcq("Which catch order is correct?", ["Specific types before general ones", "General first", "Alphabetical", "Any order"], 0),
            mcq("What's wrong with an empty catch block?", ["Failures are silently hidden", "It won't compile", "It runs twice", "It's slow"], 0),
            run("Read a number n. Print 'start', then the result of 100 / n, or 'cannot divide' on error, and always print 'done' (use try / catch / finally).", "java",
                [t("ok", stdin="4"), t("zero", stdin="0")], ["start\n25\ndone", "start\ncannot divide\ndone"],
                scan('int n = in.nextInt();\nSystem.out.println("start");\ntry {\n    System.out.println(100 / n);\n} catch (ArithmeticException e) {\n    System.out.println("cannot divide");\n} finally {\n    System.out.println("done");\n}'),
                starter=SCAN, require=[r"finally", r"catch"], fallback=[r"try\s*\{", r"catch\s*\(\s*ArithmeticException", r"finally"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Concurrency",
        lesson(
            "Threads and joining",
            """A thread runs code concurrently. Start it with start() (not run()!) and wait for it with join():

Thread t = new Thread(() -> System.out.println("hello from thread"));
t.start();
t.join();            // wait until it has finished

Without join the main thread may finish first and the output order is unpredictable. Threads share memory, which is powerful - and the source of race conditions.""",
            mcq("Which method starts a new thread?", ["start()", "run()", "begin()", "go()"], 0),
            mcq("What does join() do?", ["Waits for the thread to finish", "Starts the thread", "Kills the thread", "Merges threads"], 0),
            mcq("What happens if you call run() directly?", ["It runs on the CURRENT thread", "A new thread starts", "An error", "Nothing"], 0),
            run("Start two threads that each add 1000 to a shared counter's total (with synchronization) and join both. Print the final total.", "java",
                [t("run", stdin="")], ["2000"],
                prog('Counter c = new Counter();\nThread a = new Thread(() -> { for (int i = 0; i < 1000; i++) c.inc(); });\nThread b = new Thread(() -> { for (int i = 0; i < 1000; i++) c.inc(); });\na.start();\nb.start();\ntry {\n    a.join();\n    b.join();\n} catch (InterruptedException e) {\n    throw new RuntimeException(e);\n}\nSystem.out.println(c.get());',
                     before='class Counter {\n    private int total = 0;\n\n    synchronized void inc() {\n        total++;\n    }\n\n    synchronized int get() {\n        return total;\n    }\n}\n\n'),
                starter=MAIN, require=[r"Thread", r"\.join\(\)", r"synchronized"], fallback=[r"new\s+Thread", r"\.start\(\)", r"\.join\(\)", r"synchronized"]),
        ),
        lesson(
            "Race conditions and synchronized",
            """When two threads update shared data, increments can be LOST: count++ is three steps (read, add, write), and threads can interleave them.

int count = 0;     // two threads doing count++ 1000 times each may end below 2000

Fixes: synchronized methods/blocks (one thread at a time), AtomicInteger (lock-free atomic operations), or avoiding shared mutable state by using immutable data and thread-local results.

AtomicInteger counter = new AtomicInteger(); counter.incrementAndGet();""",
            mcq("Why can count++ lose updates?", ["It is read, add, write - threads can interleave", "It is slow", "Ints are small", "The JVM forbids it"], 0),
            mcq("Which makes increments thread-safe without locking?", ["AtomicInteger", "int", "static int", "volatile int"], 0),
            mcq("What does synchronized guarantee?", ["One thread at a time in the block", "Faster code", "Ordering of prints", "Immutability"], 0),
            run("Read n. Start 4 threads that each call incrementAndGet on one shared AtomicInteger n times, join them all, and print the total.", "java",
                [t("n=1000", stdin="1000"), t("n=0", stdin="0"), t("n=7", stdin="7")], ["4000", "0", "28"],
                scan('int n = in.nextInt();\nAtomicInteger counter = new AtomicInteger();\nThread[] ts = new Thread[4];\nfor (int i = 0; i < 4; i++) {\n    ts[i] = new Thread(() -> { for (int j = 0; j < n; j++) counter.incrementAndGet(); });\n    ts[i].start();\n}\nfor (Thread t : ts) {\n    try {\n        t.join();\n    } catch (InterruptedException e) {\n        throw new RuntimeException(e);\n    }\n}\nSystem.out.println(counter.get());').replace("import java.util.*;", "import java.util.*;\nimport java.util.concurrent.atomic.*;"),
                starter=SCAN, require=[r"AtomicInteger"], fallback=[r"AtomicInteger", r"Thread", r"join\(\)"]),
        ),
        lesson(
            "ExecutorService and futures",
            """Don't manage threads by hand - use a thread pool:

ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> f = pool.submit(() -> expensive());
int result = f.get();                  // waits for the result
pool.shutdown();                        // always shut the pool down

CompletableFuture chains async steps: CompletableFuture.supplyAsync(() -> 21).thenApply(x -> x * 2).join(). Pools reuse threads, limit how many run at once and return results through Futures.""",
            mcq("Why use a thread pool?", ["Threads are reused and limited in number", "It is required", "It avoids Java", "It sorts tasks"], 0),
            mcq("What does Future.get() do?", ["Waits for and returns the result", "Starts the task", "Cancels the task", "Creates a thread"], 0),
            mcq("What must you do when finished with an ExecutorService?", ["Call shutdown()", "Nothing", "Call stop()", "Call close() on threads"], 0),
            run("Read n numbers. Submit one task per number to an ExecutorService that squares it, collect the Futures in order and print the sum of the results.", "java",
                [t("three", stdin="3\n1 2 3"), t("one", stdin="1\n9")], ["14", "81"],
                scan('int n = in.nextInt();\nExecutorService pool = Executors.newFixedThreadPool(2);\nList<Future<Integer>> futures = new ArrayList<>();\nfor (int i = 0; i < n; i++) {\n    int x = in.nextInt();\n    futures.add(pool.submit(() -> x * x));\n}\nint sum = 0;\ntry {\n    for (Future<Integer> f : futures) sum += f.get();\n} catch (Exception e) {\n    throw new RuntimeException(e);\n}\npool.shutdown();\nSystem.out.println(sum);').replace("import java.util.*;", "import java.util.*;\nimport java.util.concurrent.*;"),
                starter=SCAN, require=[r"ExecutorService", r"Future"], fallback=[r"ExecutorService", r"submit\(", r"shutdown\(\)"]),
        ),
    ),
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Algorithms in Java",
        lesson(
            "Sorting by hand: merge sort",
            """Merge sort splits an array, sorts both halves and merges them - O(n log n).

static void mergeSort(int[] a, int lo, int hi) {            // sorts a[lo..hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) / 2;
    mergeSort(a, lo, mid); mergeSort(a, mid, hi);
    int[] tmp = new int[hi - lo]; int i = lo, j = mid, k = 0;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, 0, a, lo, tmp.length);
}""",
            mcq("What is merge sort's time complexity?", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 0),
            mcq("What does System.arraycopy do?", ["Copies a block of an array", "Sorts an array", "Clones the object", "Prints an array"], 0),
            mcq("Why is merge sort stable when written with <=?", ["Equal items keep their order", "It is fast", "It uses recursion", "It uses tmp"], 0),
            run("Read n then n integers. Sort them with your own merge sort (no Arrays.sort) and print them space-separated.", "java",
                [t("mix", stdin="6\n5 2 9 1 5 6"), t("one", stdin="1\n7")], ["1 2 5 5 6 9", "7"],
                scan('int n = in.nextInt();\nint[] a = new int[n];\nfor (int i = 0; i < n; i++) a[i] = in.nextInt();\nmergeSort(a, 0, n);\nStringBuilder sb = new StringBuilder();\nfor (int i = 0; i < n; i++) {\n    if (i > 0) sb.append(\' \');\n    sb.append(a[i]);\n}\nSystem.out.println(sb);',
                     extra="    static void mergeSort(int[] a, int lo, int hi) {\n        if (hi - lo < 2) return;\n        int mid = (lo + hi) / 2;\n        mergeSort(a, lo, mid);\n        mergeSort(a, mid, hi);\n        int[] tmp = new int[hi - lo];\n        int i = lo, j = mid, k = 0;\n        while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];\n        while (i < mid) tmp[k++] = a[i++];\n        while (j < hi) tmp[k++] = a[j++];\n        System.arraycopy(tmp, 0, a, lo, tmp.length);\n    }\n\n"),
                starter=SCAN, require=[r"mergeSort"], forbid=[r"Arrays\.sort", r"Collections\.sort", r"\.sort\("], fallback=[r"mergeSort", r"static\s+void\s+mergeSort"]),
        ),
        lesson(
            "Binary search & Arrays utilities",
            """Binary search halves a sorted range each step - O(log n):

int lo = 0, hi = a.length - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;          // avoids int overflow of (lo + hi)
    if (a[mid] == target) return mid;
    if (a[mid] < target) lo = mid + 1; else hi = mid - 1;
}
return -1;

java.util.Arrays has Arrays.sort, Arrays.binarySearch, Arrays.fill, Arrays.copyOf, Arrays.toString and Arrays.equals.""",
            mcq("Why write mid = lo + (hi - lo) / 2?", ["Avoids integer overflow", "It's faster", "It's required", "It rounds up"], 0),
            mcq("What does Arrays.copyOf(a, 5) do?", ["Copies a into a new array of length 5", "Sorts a", "Fills a with 5", "Prints a"], 0),
            mcq("Binary search needs the array to be…", ["Sorted", "Unique", "Short", "Positive"], 0),
            run("Read n sorted integers, then q queries. For each query print its index (0-based) or -1. Write the binary search yourself.", "java",
                [t("some", stdin="5\n1 3 5 7 9\n3\n7 4 1"), t("one", stdin="1\n4\n2\n4 5")], ["3\n-1\n0", "0\n-1"],
                scan('int n = in.nextInt();\nint[] a = new int[n];\nfor (int i = 0; i < n; i++) a[i] = in.nextInt();\nint q = in.nextInt();\nfor (int t = 0; t < q; t++) {\n    int target = in.nextInt();\n    int lo = 0, hi = n - 1, ans = -1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (a[mid] == target) { ans = mid; break; }\n        if (a[mid] < target) lo = mid + 1; else hi = mid - 1;\n    }\n    System.out.println(ans);\n}'),
                starter=SCAN, require=[r"while", r"mid"], forbid=[r"binarySearch", r"indexOf"], fallback=[r"while\s*\(\s*lo\s*<=\s*hi", r"mid"]),
        ),
        lesson(
            "Graph search with maps and queues",
            """Represent a graph as Map<Integer, List<Integer>> (adjacency list). Breadth-first search uses a queue and a visited set, and finds the FEWEST edges between two nodes:

Queue<Integer> q = new ArrayDeque<>(); Map<Integer,Integer> dist = new HashMap<>();
dist.put(start, 0); q.add(start);
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj.getOrDefault(u, List.of())) if (!dist.containsKey(v)) { dist.put(v, dist.get(u) + 1); q.add(v); }
}

getOrDefault avoids null checks. O(V + E).""",
            mcq("What does BFS find in an unweighted graph?", ["The fewest edges to each node", "The longest path", "A random path", "Cycles only"], 0),
            mcq("Why keep a visited/dist map?", ["To avoid revisiting nodes", "To sort nodes", "To count edges only", "To print"], 0),
            mcq("What does getOrDefault(u, List.of()) give for a missing key?", ["An empty list", "null", "An exception", "0"], 0),
            run("Read n m, then m undirected edges 'a b', then start and goal. Print the fewest edges from start to goal using BFS, or -1 if unreachable.", "java",
                [t("path", stdin="5 4\n0 1\n1 2\n2 3\n0 4\n0 3"), t("none", stdin="3 1\n0 1\n0 2"), t("same", stdin="2 1\n0 1\n1 1")], ["3", "-1", "0"],
                scan('int n = in.nextInt(), m = in.nextInt();\nMap<Integer, List<Integer>> adj = new HashMap<>();\nfor (int i = 0; i < m; i++) {\n    int a = in.nextInt(), b = in.nextInt();\n    adj.computeIfAbsent(a, k -> new ArrayList<>()).add(b);\n    adj.computeIfAbsent(b, k -> new ArrayList<>()).add(a);\n}\nint start = in.nextInt(), goal = in.nextInt();\nMap<Integer, Integer> dist = new HashMap<>();\nQueue<Integer> q = new ArrayDeque<>();\ndist.put(start, 0);\nq.add(start);\nwhile (!q.isEmpty()) {\n    int u = q.poll();\n    for (int v : adj.getOrDefault(u, new ArrayList<>())) {\n        if (!dist.containsKey(v)) {\n            dist.put(v, dist.get(u) + 1);\n            q.add(v);\n        }\n    }\n}\nSystem.out.println(dist.getOrDefault(goal, -1));'),
                starter=SCAN, require=[r"Queue|Deque"], fallback=[r"Queue|Deque", r"poll\(", r"Map<"]),
        ),
    ),
)
