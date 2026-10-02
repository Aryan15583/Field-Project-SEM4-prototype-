"""Java projects - one at the end of each section (added to units 8, 12 and 16)."""
from .dsl import project, run, t
from .java_adv import prog, scan

# ------------------------------------------------------------------ Beginner: bank account
BANK_IN = "100\ndeposit 50\nwithdraw 30\nwithdraw 500\ndeposit 5"
BANK_IN2 = "0\nwithdraw 1\ndeposit 10"

BANK1 = scan('''int balance = in.nextInt();
while (in.hasNext()) {
    String op = in.next();
    int amount = in.nextInt();
    if (op.equals("deposit")) balance += amount;
    else if (op.equals("withdraw")) balance -= amount;
}
System.out.println("Balance: " + balance);''')

BANK2 = scan('''int balance = in.nextInt();
int count = 0;
while (in.hasNext()) {
    String op = in.next();
    int amount = in.nextInt();
    if (op.equals("deposit")) {
        balance += amount;
        count++;
    } else if (op.equals("withdraw")) {
        if (amount > balance) {
            System.out.println("Insufficient funds: withdraw " + amount);
        } else {
            balance -= amount;
            count++;
        }
    }
}
System.out.println("Transactions: " + count);
System.out.println("Balance: " + balance);''')

ACCOUNT = '''class Account {
    private int balance;
    private final List<String> history = new ArrayList<>();

    Account(int opening) {
        balance = opening;
        history.add("open " + opening);
    }

    void deposit(int amount) {
        balance += amount;
        history.add("deposit " + amount);
    }

    boolean withdraw(int amount) {
        if (amount > balance) return false;
        balance -= amount;
        history.add("withdraw " + amount);
        return true;
    }

    int getBalance() {
        return balance;
    }

    List<String> getHistory() {
        return history;
    }
}

'''

BANK3 = scan('''Account acc = new Account(in.nextInt());
while (in.hasNext()) {
    String op = in.next();
    int amount = in.nextInt();
    if (op.equals("deposit")) acc.deposit(amount);
    else if (op.equals("withdraw") && !acc.withdraw(amount)) System.out.println("Insufficient funds: withdraw " + amount);
}
for (String line : acc.getHistory()) System.out.println("- " + line);
System.out.println("Balance: " + acc.getBalance());''', before=ACCOUNT)

BEGINNER = project(
    "Project: Bank account",
    "Build a small banking program, step by step:\n\n1. Process deposits and withdrawals.\n2. Refuse overdrafts and "
    "count transactions.\n3. Move the logic into an Account class that keeps a statement.\n\nInput: the opening balance, "
    "then lines like 'deposit 50' or 'withdraw 30' until the input ends.",
    run("Step 1 - Read the opening balance, then process every 'deposit N' / 'withdraw N'. Print 'Balance: X'.", "java",
        [t("mixed", stdin=BANK_IN), t("small", stdin=BANK_IN2)], ["Balance: -375", "Balance: 9"], BANK1,
        starter=scan(""), fallback=[r"hasNext", r"deposit", r"withdraw", r"Balance: "]),
    run("Step 2 - Refuse a withdrawal bigger than the balance (print 'Insufficient funds: withdraw N'). At the end print "
        "'Transactions: K' (successful ones), then the balance.", "java",
        [t("mixed", stdin=BANK_IN), t("small", stdin=BANK_IN2)],
        ["Insufficient funds: withdraw 500\nTransactions: 3\nBalance: 125", "Insufficient funds: withdraw 1\nTransactions: 1\nBalance: 10"],
        BANK2, starter=BANK1, carry=True, fallback=[r"Insufficient funds", r"Transactions: "]),
    run("Step 3 - Create class Account (opening balance, deposit, withdraw returning false when refused, getBalance, and "
        "a history list). Print the statement as '- open 100', '- deposit 50'… then the balance.", "java",
        [t("mixed", stdin=BANK_IN), t("small", stdin=BANK_IN2)],
        ["Insufficient funds: withdraw 500\n- open 100\n- deposit 50\n- withdraw 30\n- deposit 5\nBalance: 125",
         "Insufficient funds: withdraw 1\n- open 0\n- deposit 10\nBalance: 10"],
        BANK3, starter=BANK2, carry=True, require=[r"class\s+Account"], fallback=[r"class\s+Account", r"history|List<String>"]),
)

# ------------------------------------------------------------------ Intermediate: inventory
INV_IN = "add apple 10\nadd pear 4\nremove apple 3\nadd apple 1\nremove pear 9\nreport"

INV1 = scan('''Map<String, Integer> stock = new TreeMap<>();
while (in.hasNext()) {
    String cmd = in.next();
    if (cmd.equals("report")) {
        for (Map.Entry<String, Integer> e : stock.entrySet()) System.out.println(e.getKey() + ": " + e.getValue());
    } else {
        String item = in.next();
        int qty = in.nextInt();
        if (cmd.equals("add")) stock.merge(item, qty, Integer::sum);
        else if (cmd.equals("remove")) stock.merge(item, -qty, Integer::sum);
    }
}''')

OUT_OF_STOCK = '''class OutOfStockException extends Exception {
    OutOfStockException(String item, int have, int want) {
        super("Cannot remove " + want + " " + item + " (only " + have + ")");
    }
}

'''

INV_REMOVE = '''    static void remove(Map<String, Integer> stock, String item, int qty) throws OutOfStockException {
        int have = stock.getOrDefault(item, 0);
        if (qty > have) throw new OutOfStockException(item, have, qty);
        if (qty == have) stock.remove(item);
        else stock.put(item, have - qty);
    }

'''

INV_LOOP = '''Map<String, Integer> stock = new TreeMap<>();
while (in.hasNext()) {
    String cmd = in.next();
    if (cmd.equals("report")) {
        for (Map.Entry<String, Integer> e : stock.entrySet()) System.out.println(e.getKey() + ": " + e.getValue());
REPORT_EXTRA    } LOW_CMD else {
        String item = in.next();
        int qty = in.nextInt();
        try {
            if (cmd.equals("add")) stock.merge(item, qty, Integer::sum);
            else if (cmd.equals("remove")) remove(stock, item, qty);
        } catch (OutOfStockException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}'''

INV2 = scan(INV_LOOP.replace("REPORT_EXTRA", "").replace("LOW_CMD ", ""), before=OUT_OF_STOCK, extra=INV_REMOVE)

INV3 = scan(
    INV_LOOP.replace(
        "REPORT_EXTRA",
        '''        int total = 0;
        for (int q : stock.values()) total += q;
        System.out.println("Items: " + stock.size() + ", units: " + total);
''',
    ).replace(
        "LOW_CMD ",
        '''else if (cmd.equals("low")) {
        int limit = in.nextInt();
        List<String> low = new ArrayList<>();
        for (Map.Entry<String, Integer> e : stock.entrySet()) if (e.getValue() < limit) low.add(e.getKey());
        System.out.println("Low stock: " + (low.isEmpty() ? "none" : String.join(", ", low)));
    } ''',
    ),
    before=OUT_OF_STOCK,
    extra=INV_REMOVE,
)

INTERMEDIATE = project(
    "Project: Inventory manager",
    "Build a warehouse inventory tool with collections and exceptions:\n\n1. Track stock in a sorted map.\n2. Refuse to "
    "remove more than you have, using a custom checked exception.\n3. Add totals and a low-stock alert.\n\nCommands: "
    "'add item qty', 'remove item qty', 'report' (and in step 3 'low N').",
    run("Step 1 - Keep stock in a TreeMap. 'add' and 'remove' change quantities; 'report' prints 'item: qty' lines in "
        "alphabetical order.", "java",
        [t("commands", stdin="add pear 2\nadd apple 5\nremove apple 1\nreport")], ["apple: 4\npear: 2"], INV1,
        starter=scan(""), fallback=[r"TreeMap", r"report"]),
    run("Step 2 - Removing more than you have throws your own OutOfStockException (checked); catch it and print "
        "'Error: Cannot remove 9 pear (only 4)'. Items that reach 0 disappear from the report.", "java",
        [t("errors", stdin=INV_IN), t("to zero", stdin="add kiwi 2\nremove kiwi 2\nreport\nadd fig 1\nreport")],
        ["Error: Cannot remove 9 pear (only 4)\napple: 8\npear: 4", "fig: 1"],
        INV2, starter=INV1, carry=True, require=[r"extends\s+Exception"], fallback=[r"class\s+OutOfStockException\s+extends\s+Exception", r"catch"]),
    run("Step 3 - 'report' also prints 'Items: N, units: U'. New command 'low N' prints 'Low stock: a, b' (items below "
        "N, alphabetical) or 'Low stock: none'.", "java",
        [t("report", stdin=INV_IN + "\nlow 5\nlow 1")],
        ["Error: Cannot remove 9 pear (only 4)\napple: 8\npear: 4\nItems: 2, units: 12\nLow stock: pear\nLow stock: none"],
        INV3, starter=INV2, carry=True, fallback=[r"Items: ", r"Low stock"]),
)

# ------------------------------------------------------------------ Advanced: leaderboard analytics
SCORES_IN = "ada red 90\nbo blue 75\ncy red 60\ndi green 88\neve blue 95\nfin red 75"

PLAYER = '''class Player {
    final String name, team;
    final int score;

    Player(String name, String team, int score) {
        this.name = name;
        this.team = team;
        this.score = score;
    }

    String getName() {
        return name;
    }

    String getTeam() {
        return team;
    }

    int getScore() {
        return score;
    }
}

'''

STREAMS = "import java.util.*;\nimport java.util.stream.*;\n\n"


def _lb(body):
    return prog("Scanner in = new Scanner(System.in);\nList<Player> players = new ArrayList<>();\n"
                "while (in.hasNext()) players.add(new Player(in.next(), in.next(), in.nextInt()));\n" + body,
                imports=STREAMS, before=PLAYER)


LB1 = _lb('''players.stream()
        .sorted(Comparator.comparingInt(Player::getScore).reversed().thenComparing(Player::getName))
        .limit(3)
        .forEach(p -> System.out.println(p.getName() + " " + p.getScore()));''')

LB2 = _lb('''players.stream()
        .sorted(Comparator.comparingInt(Player::getScore).reversed().thenComparing(Player::getName))
        .limit(3)
        .forEach(p -> System.out.println(p.getName() + " " + p.getScore()));
Map<String, Integer> totals = players.stream()
        .collect(Collectors.groupingBy(Player::getTeam, TreeMap::new, Collectors.summingInt(Player::getScore)));
totals.entrySet().stream()
        .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
        .forEach(e -> System.out.println(e.getKey() + ": " + e.getValue()));''')

LB3 = _lb('''players.stream()
        .sorted(Comparator.comparingInt(Player::getScore).reversed().thenComparing(Player::getName))
        .limit(3)
        .forEach(p -> System.out.println(p.getName() + " " + p.getScore()));
Map<String, Integer> totals = players.stream()
        .collect(Collectors.groupingBy(Player::getTeam, TreeMap::new, Collectors.summingInt(Player::getScore)));
totals.entrySet().stream()
        .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
        .forEach(e -> System.out.println(e.getKey() + ": " + e.getValue()));
Optional<Map.Entry<String, Double>> best = players.stream()
        .collect(Collectors.groupingBy(Player::getTeam, Collectors.averagingInt(Player::getScore)))
        .entrySet().stream()
        .filter(e -> players.stream().filter(p -> p.getTeam().equals(e.getKey())).count() >= 2)
        .max(Map.Entry.comparingByValue());
System.out.println(best.map(e -> String.format("Best team: %s (%.1f)", e.getKey(), e.getValue())).orElse("Best team: none"));''')

ADVANCED = project(
    "Project: Leaderboard analytics",
    "Turn raw game results into analytics using streams, collectors and Optional:\n\n1. The top 3 players.\n2. Team "
    "totals.\n3. The best team by average (teams with at least 2 players).\n\nInput lines: 'name team score'.",
    run("Step 1 - Read all players (a Player class with getters is a good idea) and print the top 3 as 'name score' - "
        "highest score first, ties by name. Use a stream.", "java",
        [t("results", stdin=SCORES_IN)], ["eve 95\nada 90\ndi 88"], LB1, starter=prog("", imports=STREAMS),
        require=[r"\.stream\(\)"], fallback=[r"\.stream\(\)", r"\.limit\(\s*3\s*\)"]),
    run("Step 2 - After the top 3, print each team's total score as 'team: total', highest first (use "
        "Collectors.groupingBy).", "java",
        [t("results", stdin=SCORES_IN)], ["eve 95\nada 90\ndi 88\nred: 225\nblue: 170\ngreen: 88"], LB2,
        starter=LB1, carry=True, fallback=[r"groupingBy"]),
    run("Step 3 - Finally print 'Best team: name (average)' - the highest average among teams with at least 2 players, "
        "1 decimal - using Optional ('Best team: none' if no team qualifies).", "java",
        [t("results", stdin=SCORES_IN), t("solo players", stdin="a x 1\nb y 2")],
        ["eve 95\nada 90\ndi 88\nred: 225\nblue: 170\ngreen: 88\nBest team: blue (85.0)",
         "b 2\na 1\ny: 2\nx: 1\nBest team: none"],
        LB3, starter=LB2, carry=True, require=[r"Optional"], fallback=[r"Optional", r"averaging"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
