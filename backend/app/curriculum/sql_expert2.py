"""SQL - Expert section, part 2 (units 23-29): text & JSON, modelling, integrity, performance, reporting, warehouse
patterns and capstone queries. Expected rows come from running the reference query on SQLite (see sql_expert.py)."""
from .dsl import lesson, mcq, section, unit
from .sql_adv import EVENTS, SALES, SHOP, STAFF
from .sql_expert import SCORES, VIEWS, q

LIBRARY = """CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, year INTEGER);
CREATE TABLE book_authors (book_id INTEGER REFERENCES books(id), author_id INTEGER REFERENCES authors(id), PRIMARY KEY (book_id, author_id));
INSERT INTO authors VALUES (1, 'Ada'), (2, 'Bo'), (3, 'Cy'), (4, 'Dee');
INSERT INTO books VALUES (1, 'Sql Basics', 2020), (2, 'Data Tales', 2021), (3, 'Graphs', 2021), (4, 'Solo Work', 2022);
INSERT INTO book_authors VALUES (1, 1), (1, 2), (2, 2), (2, 3), (2, 4), (3, 1), (4, 4);"""

STOCK = """CREATE TABLE moves (id INTEGER PRIMARY KEY, sku TEXT, qty INTEGER, kind TEXT, day TEXT);
INSERT INTO moves VALUES
  (1, 'pen', 100, 'in', '2026-05-01'), (2, 'pen', 30, 'out', '2026-05-02'), (3, 'ink', 50, 'in', '2026-05-02'),
  (4, 'pen', 20, 'out', '2026-05-03'), (5, 'ink', 10, 'out', '2026-05-03'), (6, 'pen', 40, 'in', '2026-05-04'),
  (7, 'ink', 35, 'out', '2026-05-05'), (8, 'cap', 60, 'in', '2026-05-05'), (9, 'cap', 5, 'out', '2026-05-06');"""

FUNNEL = """CREATE TABLE steps (user TEXT, step TEXT, at TEXT);
INSERT INTO steps VALUES
  ('a', 'visit', '2026-06-01'), ('a', 'signup', '2026-06-01'), ('a', 'buy', '2026-06-02'),
  ('b', 'visit', '2026-06-01'), ('b', 'signup', '2026-06-03'),
  ('c', 'visit', '2026-06-02'),
  ('d', 'visit', '2026-06-02'), ('d', 'signup', '2026-06-02'), ('d', 'buy', '2026-06-04'),
  ('e', 'visit', '2026-06-05'), ('f', 'visit', '2026-06-05'), ('f', 'signup', '2026-06-06');"""

PLANS = """CREATE TABLE plan_history (customer TEXT, plan TEXT, valid_from TEXT, valid_to TEXT);
INSERT INTO plan_history VALUES
  ('ada', 'free', '2026-01-01', '2026-02-28'), ('ada', 'pro', '2026-03-01', NULL),
  ('bo', 'free', '2026-01-01', NULL),
  ('cy', 'pro', '2026-01-01', '2026-03-31'), ('cy', 'free', '2026-04-01', NULL);
CREATE TABLE invoices (id INTEGER PRIMARY KEY, customer TEXT, day TEXT, amount INTEGER);
INSERT INTO invoices VALUES (1, 'ada', '2026-02-10', 0), (2, 'ada', '2026-03-10', 20), (3, 'cy', '2026-02-15', 20), (4, 'cy', '2026-04-15', 0), (5, 'bo', '2026-03-01', 0);"""

BILLING = """CREATE TABLE lines (id INTEGER PRIMARY KEY, invoice INTEGER, item TEXT, qty INTEGER, unit_cents INTEGER, taxable INTEGER);
INSERT INTO lines VALUES
  (1, 100, 'Widget', 3, 500, 1), (2, 100, 'Manual', 1, 1200, 0), (3, 101, 'Widget', 10, 500, 1),
  (4, 101, 'Shipping', 1, 800, 0), (5, 102, 'Gadget', 2, 2500, 1);"""

SESSIONS = """CREATE TABLE clicks (id INTEGER PRIMARY KEY, user TEXT, minute INTEGER);
INSERT INTO clicks VALUES
  (1, 'ada', 0), (2, 'ada', 5), (3, 'ada', 12), (4, 'ada', 60), (5, 'ada', 65),
  (6, 'bo', 10), (7, 'bo', 80), (8, 'bo', 83), (9, 'bo', 84);"""

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Text & JSON",
        lesson(
            "LIKE, GLOB & pattern search",
            """LIKE uses % (any text) and _ (one character) and ignores letter case for ASCII; GLOB uses * and ? and IS case-sensitive.

SELECT * FROM books WHERE title LIKE 'S%';       -- starts with S or s
SELECT * FROM books WHERE title LIKE '%Data%';   -- contains
SELECT * FROM books WHERE title GLOB '[A-Z]*s';  -- starts with a capital, ends with s

A pattern starting with % can't use an index, so searching big tables with LIKE '%word%' is slow.""",
            mcq("What does _ match in LIKE?", ["Exactly one character", "Any text", "A space only", "Nothing"], 0),
            mcq("Is LIKE 'a%' case-sensitive in SQLite for ASCII?", ["No", "Yes", "Only for numbers", "Only with GLOB"], 0),
            mcq("Why is LIKE '%word%' slow on a huge table?", ["It can't use an ordinary index", "It sorts first", "It locks the table", "It always errors"], 0),
            q("List the titles of books containing the letters 'ta' anywhere (case-insensitive), ordered by title.", LIBRARY, "SELECT title FROM books\nWHERE title LIKE '%ta%'\nORDER BY title;", require=[r"(?i)LIKE|GLOB"]),
        ),
        lesson(
            "Splitting text with SUBSTR & INSTR",
            """INSTR(text, find) returns the 1-based position (0 if missing); SUBSTR(text, start, length) slices.

SELECT SUBSTR(email, INSTR(email, '@') + 1) AS domain FROM employees;   -- everything after the @
SELECT SUBSTR(name, 1, INSTR(name, ' ') - 1) AS first_word FROM ...

Handy for pulling pieces out of structured text: domains, file extensions, 'key=value' pairs.""",
            mcq("What does INSTR('hello', 'l') return?", ["3", "2", "4", "0"], 0),
            mcq("What does SUBSTR('database', 5) return?", ["'base'", "'data'", "'databas'", "'ase'"], 0),
            mcq("What does INSTR return when the text isn't found?", ["0", "NULL", "-1", "An error"], 0),
            q("Show each distinct email domain (the part after @, lower-case) and how many employees use it, ignoring employees without an email. Order by domain.", STAFF,
              "SELECT LOWER(SUBSTR(email, INSTR(email, '@') + 1)) AS domain, COUNT(*)\nFROM employees\nWHERE email IS NOT NULL\nGROUP BY domain\nORDER BY domain;", require=[r"(?i)SUBSTR", r"(?i)INSTR"]),
        ),
        lesson(
            "JSON functions: json_extract & json_each",
            """SQLite can read JSON stored in a text column:

SELECT json_extract(payload, '$.user') FROM events;          -- one value
SELECT e.id, j.value FROM events e, json_each(e.payload, '$.items') j;   -- one row per array item
json_group_array(x) builds a JSON array from rows; json_object('k', v) builds an object.

Paths start with $ : $.a.b for nested keys, $.list[0] for array items.""",
            mcq("What does json_each do?", ["Turns a JSON array/object into rows", "Counts keys", "Sorts JSON", "Validates JSON"], 0),
            mcq("What does the path $.items[0] refer to?", ["The first element of the items array", "The key named 0", "The last item", "The whole object"], 0),
            mcq("Which function builds a JSON array from grouped rows?", ["json_group_array", "json_array_agg_all", "array()", "json_list"], 0),
            q("For each event show its id and the 'user' value from the JSON payload, only for events whose type is 'login'. Order by id.", EVENTS,
              "SELECT id, json_extract(payload, '$.user')\nFROM events\nWHERE json_extract(payload, '$.type') = 'login'\nORDER BY id;", require=[r"(?i)json_extract"]),
        ),
    ),
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Modelling relationships",
        lesson(
            "Many-to-many with junction tables",
            """A book can have several authors and an author several books. A many-to-many relationship needs a JUNCTION table holding pairs of keys:

book_authors(book_id, author_id)   -- PRIMARY KEY (book_id, author_id)

To list books with authors, join through it:

SELECT b.title, a.name FROM books b
JOIN book_authors ba ON ba.book_id = b.id
JOIN authors a ON a.id = ba.author_id;""",
            mcq("Why does a many-to-many relationship need a junction table?", ["A single column can't hold many keys cleanly", "It is faster only", "SQL requires it for all joins", "To store dates"], 0),
            mcq("What is a good primary key for the junction table?", ["(book_id, author_id) together", "Just book_id", "Just author_id", "A random text"], 0),
            mcq("How many joins list books with their authors?", ["Two (through the junction table)", "One", "Three", "Zero"], 0),
            q("Show each book title with how many authors it has, most authors first, then title.", LIBRARY,
              "SELECT b.title, COUNT(ba.author_id) AS authors\nFROM books b\nJOIN book_authors ba ON ba.book_id = b.id\nGROUP BY b.id\nORDER BY authors DESC, b.title;", require=[r"(?i)JOIN\s+book_authors"]),
        ),
        lesson(
            "Finding co-occurrences",
            """Self-join a junction table to find pairs that share something - authors who wrote a book together:

SELECT x.author_id, y.author_id
FROM book_authors x JOIN book_authors y
  ON x.book_id = y.book_id AND x.author_id < y.author_id;

The condition x.author_id < y.author_id keeps each pair once and removes pairs of an author with themselves.""",
            mcq("Why use x.author_id < y.author_id?", ["Each pair appears once, not twice", "Authors must be sorted", "It is a join type", "To avoid NULLs"], 0),
            mcq("What does self-joining the junction table by book_id give?", ["Pairs of authors on the same book", "All books", "Duplicates of books", "Orphan rows"], 0),
            mcq("Which is a real-world use?", ["'People who bought this also bought…'", "Sorting names", "Counting rows", "Renaming columns"], 0),
            q("List every pair of authors who co-wrote at least one book, as 'first|second' author names with the first alphabetically before the second, and how many books they share. Order by names.", LIBRARY,
              "SELECT a1.name, a2.name, COUNT(*) AS shared\nFROM book_authors x\nJOIN book_authors y ON x.book_id = y.book_id AND x.author_id < y.author_id\nJOIN authors a1 ON a1.id = x.author_id\nJOIN authors a2 ON a2.id = y.author_id\nGROUP BY x.author_id, y.author_id\nORDER BY a1.name, a2.name;", require=[r"(?i)JOIN\s+book_authors"]),
        ),
        lesson(
            "Keys, surrogate vs natural",
            """A NATURAL key is real-world data that identifies a row (an email, an ISBN). A SURROGATE key is an invented id (INTEGER PRIMARY KEY) with no meaning.

Surrogate keys never change and are small; natural keys can change (people change emails) and may be reused. Best practice: a surrogate primary key plus a UNIQUE constraint on the natural key.

CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);""",
            mcq("Which can change over time?", ["A natural key like an email", "A surrogate id", "Neither", "Both never"], 0),
            mcq("What is a good combination?", ["Surrogate primary key + UNIQUE natural key", "No key", "Two primary keys", "Only natural keys"], 0),
            mcq("What does INTEGER PRIMARY KEY do in SQLite?", ["Auto-assigns unique row ids", "Stores text", "Makes it NULL", "Disables indexes"], 0),
            q("Find email-like duplicates in the contacts: show each normalised (trimmed, lower-case) email that appears more than once and how many times. Order by email.",
              "CREATE TABLE contacts (id INTEGER PRIMARY KEY, email TEXT);\nINSERT INTO contacts VALUES (1, 'a@x.com'), (2, 'A@x.com '), (3, 'b@x.com'), (4, 'c@x.com'), (5, 'b@X.com');",
              "SELECT LOWER(TRIM(email)) AS e, COUNT(*)\nFROM contacts\nGROUP BY e\nHAVING COUNT(*) > 1\nORDER BY e;", require=[r"(?i)HAVING"]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · Integrity & change",
        lesson(
            "Foreign keys & ON DELETE",
            """Foreign keys keep references valid. ON DELETE decides what happens to children when a parent row is deleted:

PRAGMA foreign_keys = ON;       -- SQLite needs this per connection
CREATE TABLE posts (id INTEGER PRIMARY KEY, author INTEGER REFERENCES users(id) ON DELETE CASCADE);

CASCADE deletes the children too; SET NULL clears the reference; RESTRICT (default) blocks the delete. Choose deliberately - CASCADE is convenient and dangerous.""",
            mcq("What does ON DELETE CASCADE do?", ["Deletes the child rows as well", "Blocks the delete", "Sets NULL", "Copies rows"], 0),
            mcq("Which option keeps child rows but removes the link?", ["ON DELETE SET NULL", "CASCADE", "RESTRICT", "UNIQUE"], 0),
            mcq("What must SQLite run for foreign keys to be enforced?", ["PRAGMA foreign_keys = ON", "CREATE INDEX", "VACUUM", "ANALYZE"], 0),
            q("With foreign keys ON and cascading deletes, deleting the user 'ada' should remove her posts. After the delete, show how many posts remain.",
              "PRAGMA foreign_keys = ON;\nCREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);\nCREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT);\nINSERT INTO users VALUES (1, 'ada'), (2, 'bo');\nINSERT INTO posts VALUES (1, 1, 'a1'), (2, 1, 'a2'), (3, 2, 'b1');",
              "DELETE FROM users WHERE name = 'ada';\nSELECT COUNT(*) FROM posts;", require=[r"(?i)DELETE\s+FROM\s+users"]),
        ),
        lesson(
            "Audit triggers",
            """A trigger can write an audit trail automatically:

CREATE TRIGGER log_price AFTER UPDATE OF price ON products
BEGIN
  INSERT INTO price_log (product_id, old_price, new_price) VALUES (OLD.id, OLD.price, NEW.price);
END;

OLD is the row before the change, NEW is after. Triggers fire for every change, even from other applications - good for auditing, but hidden logic can surprise people.""",
            mcq("What do OLD and NEW refer to?", ["The row before and after the change", "Two tables", "Two users", "Two triggers"], 0),
            mcq("When does AFTER UPDATE fire?", ["After a row has been updated", "Before it", "At server start", "At login"], 0),
            mcq("A downside of triggers is…", ["Logic hidden from application code", "They cannot insert", "They are slow always", "They only run once"], 0),
            q("A trigger copies every salary change into salary_log. After raising Bo's salary to 7500 and Di's to 6500, show the log as name_id|old|new ordered by employee id.",
              "CREATE TABLE emp (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER);\nCREATE TABLE salary_log (emp_id INTEGER, old_salary INTEGER, new_salary INTEGER);\nINSERT INTO emp VALUES (1, 'Bo', 7000), (2, 'Di', 6000);\nCREATE TRIGGER log_salary AFTER UPDATE OF salary ON emp\nBEGIN\n  INSERT INTO salary_log VALUES (OLD.id, OLD.salary, NEW.salary);\nEND;",
              "UPDATE emp SET salary = 7500 WHERE name = 'Bo';\nUPDATE emp SET salary = 6500 WHERE name = 'Di';\nSELECT emp_id, old_salary, new_salary FROM salary_log ORDER BY emp_id;", require=[r"(?i)UPDATE\s+emp"]),
        ),
        lesson(
            "Upserts for idempotent loads",
            """An idempotent load can be run twice without creating duplicates. UPSERT does it:

INSERT INTO stock (sku, qty) VALUES ('pen', 5)
ON CONFLICT(sku) DO UPDATE SET qty = qty + excluded.qty;

excluded is the row you tried to insert. Combine a UNIQUE key with ON CONFLICT DO NOTHING to skip rows that exist, or DO UPDATE to merge them.""",
            mcq("What does 'excluded' refer to in an upsert?", ["The row that failed to insert", "A deleted row", "A hidden column", "The table"], 0),
            mcq("What does ON CONFLICT DO NOTHING do?", ["Skips rows that already exist", "Raises an error", "Updates the row", "Deletes the row"], 0),
            mcq("An idempotent operation…", ["Gives the same result if run twice", "Runs only once ever", "Is always fast", "Needs a trigger"], 0),
            q("Load these counts into stock: (pen, 5), (ink, 2), (pen, 3) using an upsert that ADDS to existing quantities. Then show sku|qty ordered by sku.",
              "CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER);\nINSERT INTO stock VALUES ('pen', 10);",
              "INSERT INTO stock (sku, qty) VALUES ('pen', 5) ON CONFLICT(sku) DO UPDATE SET qty = qty + excluded.qty;\nINSERT INTO stock (sku, qty) VALUES ('ink', 2) ON CONFLICT(sku) DO UPDATE SET qty = qty + excluded.qty;\nINSERT INTO stock (sku, qty) VALUES ('pen', 3) ON CONFLICT(sku) DO UPDATE SET qty = qty + excluded.qty;\nSELECT sku, qty FROM stock ORDER BY sku;", require=[r"(?i)ON\s+CONFLICT"]),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · Fast queries",
        lesson(
            "Keyset pagination",
            """OFFSET pagination gets slower on deep pages: OFFSET 100000 still reads and throws away 100000 rows. KEYSET pagination continues from the last seen key and uses the index:

SELECT * FROM views WHERE id > :last_id ORDER BY id LIMIT 3;

Always ORDER BY a unique, indexed column. Trade-off: you can go 'next' easily but can't jump to page 50.""",
            mcq("Why is OFFSET slow for deep pages?", ["It must read and skip all earlier rows", "It locks the table", "It copies the table", "It ignores indexes always"], 0),
            mcq("What does keyset pagination remember?", ["The last key seen", "The page number", "The row count", "The table size"], 0),
            mcq("The ORDER BY column for keyset pagination should be…", ["Unique and indexed", "Any text", "Random", "NULL"], 0),
            q("Page through views by id: show ids and users for the 3 rows AFTER id 4 (id > 4), in order.", VIEWS, "SELECT id, user FROM views\nWHERE id > 4\nORDER BY id\nLIMIT 3;", require=[r"(?i)LIMIT", r"(?i)id\s*>"]),
        ),
        lesson(
            "Sargable conditions",
            """A condition is 'sargable' when the database can use an index for it. Wrapping the indexed column in a function usually breaks that:

WHERE STRFTIME('%Y', day) = '2026'     -- scans every row
WHERE day >= '2026-01-01' AND day < '2027-01-01'   -- can use the index on day
WHERE LOWER(email) = 'a@x.com'         -- scans (unless you index the expression)

Rule: keep the column bare on one side and move the maths to the other side.""",
            mcq("Which condition can use an index on day?", ["day >= '2026-03-01' AND day < '2026-04-01'", "STRFTIME('%m', day) = '03'", "SUBSTR(day, 1, 7) = '2026-03'", "day || '' = '2026-03-05'"], 0),
            mcq("What does 'sargable' mean?", ["The index can be used for the condition", "The query is sorted", "The column is unique", "The table is small"], 0),
            mcq("What is the fix for WHERE LOWER(email) = 'a@x.com'?", ["Store normalised emails or index the expression", "Use LIKE %", "Use ORDER BY", "Use UNION"], 0),
            q("Count the views in March 2026 using a range on day (>= first day, < first day of April) rather than a function on day.", VIEWS,
              "SELECT COUNT(*) FROM views\nWHERE day >= '2026-03-01' AND day < '2026-04-01';", require=[r"day\s*>=", r"day\s*<"], forbid=[r"(?i)STRFTIME|SUBSTR"]),
        ),
        lesson(
            "IN vs EXISTS vs JOIN, and N+1",
            """Three ways to ask 'rows in A that match B': IN (subquery), EXISTS (correlated), JOIN. Modern engines optimise them alike for simple cases; EXISTS is clearest for 'has any'.

The N+1 problem: an app loads 1 list, then runs 1 query per row (N more). Fix it with ONE query using a JOIN or IN, or two queries total.

-- N+1: one query per customer
-- Better: SELECT c.name, COUNT(o.id) FROM customers c LEFT JOIN orders o ON ... GROUP BY c.id""",
            mcq("What is the N+1 problem?", ["One query per row of an earlier query", "N tables with 1 index", "N rows with 1 NULL", "N+1 duplicated rows"], 0),
            mcq("How do you fix N+1?", ["Fetch the related data in one JOIN or IN query", "Add more loops", "Use LIMIT 1", "Add OFFSET"], 0),
            mcq("Which expresses 'has at least one' most clearly?", ["EXISTS", "COUNT(*) > 0 in WHERE", "ORDER BY", "DISTINCT *"], 0),
            q("In ONE query, list every customer with their number of orders (0 for customers with none), ordered by name.", SHOP,
              "SELECT c.name, COUNT(o.id)\nFROM customers c LEFT JOIN orders o ON o.customer_id = c.id\nGROUP BY c.id\nORDER BY c.name;", require=[r"(?i)LEFT\s+JOIN"]),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · Reporting patterns",
        lesson(
            "Funnel analysis",
            """A funnel counts how many users reach each step: visit -> signup -> buy. Count DISTINCT users per step, then compute conversion from the first step.

SELECT step, COUNT(DISTINCT user) FROM steps GROUP BY step;

Conversion = users at this step / users at the first step. Funnels show where people drop off.""",
            mcq("What does a funnel show?", ["How many users reach each step", "Total money", "Sorted users", "Index usage"], 0),
            mcq("What is conversion rate?", ["Users at a step / users at the first step", "Users / days", "Steps / users", "Total rows"], 0),
            mcq("Why COUNT(DISTINCT user)?", ["A user may repeat a step", "To sort", "To join", "To avoid NULLs"], 0),
            q("Show each step with the number of distinct users and the percentage of 'visit' users that reached it (rounded to 1 decimal). Order by users descending.", FUNNEL,
              "WITH c AS (SELECT step, COUNT(DISTINCT user) AS n FROM steps GROUP BY step)\nSELECT step, n, ROUND(100.0 * n / (SELECT n FROM c WHERE step = 'visit'), 1)\nFROM c\nORDER BY n DESC, step;", require=[r"(?i)DISTINCT"]),
        ),
        lesson(
            "Cumulative share (Pareto)",
            """A Pareto view asks 'which few items make most of the total?' Sort descending and compute a running share:

SELECT page, total,
  ROUND(100.0 * SUM(total) OVER (ORDER BY total DESC, page) / SUM(total) OVER (), 1) AS cum_pct
FROM (SELECT page, SUM(secs) AS total FROM views GROUP BY page);

The first rows covering ~80% of the total are your 'vital few'.""",
            mcq("What does a Pareto analysis find?", ["The few items that make most of the total", "The smallest item", "Duplicates", "Gaps"], 0),
            mcq("Which window gives the running total in descending order?", ["SUM(x) OVER (ORDER BY x DESC)", "SUM(x) OVER ()", "COUNT(*) OVER ()", "AVG(x) OVER ()"], 0),
            mcq("Why add a tie-breaker like page to the ORDER BY?", ["So the running order is deterministic", "To speed up", "To join", "To rename"], 0),
            q("For each page show total seconds and the cumulative percentage of all seconds when pages are sorted by total descending (ties by page), rounded to 1 decimal.", VIEWS,
              "SELECT page, total,\n  ROUND(100.0 * SUM(total) OVER (ORDER BY total DESC, page) / SUM(total) OVER (), 1)\nFROM (SELECT page, SUM(secs) AS total FROM views GROUP BY page)\nORDER BY total DESC, page;", require=[r"(?i)OVER"]),
        ),
        lesson(
            "Retention-style cohorts",
            """A cohort groups users by when they first appeared. Retention asks how many of each cohort come back later.

WITH first AS (SELECT user, MIN(day) AS d0 FROM views GROUP BY user)
SELECT d0, COUNT(*) AS users,
  COUNT(DISTINCT CASE WHEN EXISTS (SELECT 1 FROM views v WHERE v.user = first.user AND v.day > first.d0) THEN user END) AS returned
FROM first GROUP BY d0;

Cohort tables are everywhere in product analytics.""",
            mcq("What is a cohort?", ["Users grouped by when they started", "A kind of join", "An index", "A trigger"], 0),
            mcq("What does 'returned' count here?", ["Users with a later visit than their first day", "Users with an email", "All users", "Visits"], 0),
            mcq("Which column defines the cohort in the example?", ["d0 (first day)", "user", "secs", "page"], 0),
            q("Group users by the day of their first view. Show that day, how many users started that day, and how many of them were seen on any LATER day. Order by day.", VIEWS,
              "WITH first AS (SELECT user, MIN(day) AS d0 FROM views GROUP BY user)\nSELECT d0, COUNT(*) AS users,\n  SUM(EXISTS (SELECT 1 FROM views v WHERE v.user = first.user AND v.day > first.d0)) AS returned\nFROM first\nGROUP BY d0\nORDER BY d0;", require=[r"(?i)MIN\s*\(", r"(?i)EXISTS|JOIN"]),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Warehouse modelling",
        lesson(
            "Star schemas",
            """Analytics databases often use a STAR SCHEMA: a central FACT table of events (sales, with amounts and keys) surrounded by DIMENSION tables describing them (products, customers, dates).

SELECT p.category, SUM(f.amount) FROM sales_fact f JOIN product_dim p ON p.id = f.product_id GROUP BY p.category;

Facts are narrow and numerous; dimensions are wide and few. The shape makes reports simple: join facts to the dimensions you slice by.""",
            mcq("What does a fact table hold?", ["Measurable events with keys", "Descriptions only", "Indexes", "Users' passwords"], 0),
            mcq("What do dimension tables describe?", ["Who, what, where, when of the facts", "Row counts", "Triggers", "Transactions"], 0),
            mcq("Why is the star schema popular?", ["Reports are simple joins from one fact table", "It avoids all joins", "It needs no keys", "It is only for JSON"], 0),
            q("Report revenue (qty * price) per product category from the shop, highest first, as category|revenue.", SHOP,
              "SELECT p.category, SUM(oi.qty * p.price) AS revenue\nFROM order_items oi JOIN products p ON p.id = oi.product_id\nGROUP BY p.category\nORDER BY revenue DESC;", require=[r"(?i)GROUP\s+BY"]),
        ),
        lesson(
            "History tables (slowly changing dimensions)",
            """To remember what a customer's plan WAS, keep history rows with valid_from / valid_to instead of overwriting (a 'type 2' slowly changing dimension). The current row has valid_to NULL.

SELECT i.id, h.plan FROM invoices i JOIN plan_history h
  ON h.customer = i.customer AND i.day >= h.valid_from AND (h.valid_to IS NULL OR i.day <= h.valid_to);

This joins each event to the dimension row that was valid AT THAT TIME.""",
            mcq("What does valid_to NULL mean?", ["This is the current version", "The row is deleted", "The row is invalid", "No end was recorded by mistake"], 0),
            mcq("Why keep history instead of overwriting?", ["Old facts need the old description", "It saves space", "It is faster", "It avoids keys"], 0),
            mcq("How do you find the plan valid on an invoice's date?", ["Join on customer and a date range", "Join on id only", "ORDER BY plan", "UNION"], 0),
            q("For every invoice show its id and the plan the customer had ON THE INVOICE DATE. Order by invoice id.", PLANS,
              "SELECT i.id, h.plan\nFROM invoices i\nJOIN plan_history h ON h.customer = i.customer AND i.day >= h.valid_from AND (h.valid_to IS NULL OR i.day <= h.valid_to)\nORDER BY i.id;", require=[r"(?i)valid_to"]),
        ),
        lesson(
            "Events vs snapshots",
            """Store EVENTS (what happened) and derive the current STATE: a stock level is the sum of movements.

SELECT sku, SUM(CASE WHEN kind = 'in' THEN qty ELSE -qty END) AS on_hand FROM moves GROUP BY sku;

Events keep full history and are easy to append; snapshots (a table of current values) are fast to read. Many systems keep both: events as the truth, a snapshot as a cache.""",
            mcq("How do you compute current stock from movements?", ["Sum in minus out", "Take the last row", "Count rows", "Average"], 0),
            mcq("Which keeps a complete history?", ["An events table", "A snapshot table", "A view only", "An index"], 0),
            mcq("Why keep a snapshot too?", ["Reading current values is fast", "It stores history", "It avoids keys", "It needs no updates"], 0),
            q("Compute the quantity on hand for each sku (in minus out), keeping only skus with more than 10 on hand. Order by sku.", STOCK,
              "SELECT sku, SUM(CASE WHEN kind = 'in' THEN qty ELSE -qty END) AS on_hand\nFROM moves\nGROUP BY sku\nHAVING on_hand > 10\nORDER BY sku;", require=[r"(?i)CASE", r"(?i)HAVING"]),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Capstone queries",
        lesson(
            "Leaderboards with ties",
            """A fair leaderboard gives tied players the same rank and skips the following ranks (1, 2, 2, 4) with RANK, or doesn't skip (1, 2, 2, 3) with DENSE_RANK. Decide which your product needs and say so.

SELECT player, best, RANK() OVER (ORDER BY best DESC) FROM (SELECT player, MAX(points) AS best FROM scores GROUP BY player);""",
            mcq("What does RANK give two tied players, then the next?", ["2, 2, then 4", "1, 2, 3", "2, 2, then 3", "1, 1, then 1"], 0),
            mcq("Which does not skip numbers after a tie?", ["DENSE_RANK", "RANK", "ROW_NUMBER", "NTILE"], 0),
            mcq("Which gives every row a different number?", ["ROW_NUMBER", "RANK", "DENSE_RANK", "NTILE(1)"], 0),
            q("Show each player's best score and a dense rank by best score (highest first). Order by rank, then player.", SCORES,
              "SELECT player, best, DENSE_RANK() OVER (ORDER BY best DESC) AS rnk\nFROM (SELECT player, MAX(points) AS best FROM scores GROUP BY player)\nORDER BY rnk, player;", require=[r"(?i)DENSE_RANK"]),
        ),
        lesson(
            "Invoices with tax",
            """Money rules: compute in whole CENTS, apply tax only to taxable lines, round once at the end.

SELECT invoice,
  SUM(qty * unit_cents) AS subtotal,
  SUM(CASE WHEN taxable = 1 THEN qty * unit_cents ELSE 0 END) * 18 / 100 AS tax
FROM lines GROUP BY invoice;

Integer maths avoids floating-point surprises; multiply before dividing so you don't lose cents.""",
            mcq("Why compute money in cents?", ["Integers avoid floating-point rounding errors", "It's shorter", "SQL requires it", "It is encrypted"], 0),
            mcq("Why multiply by 18 before dividing by 100?", ["Integer division would lose precision otherwise", "It is faster", "SQL requires it", "To round up"], 0),
            mcq("When should you round?", ["Once, at the end", "At every step", "Never", "Before summing"], 0),
            q("For each invoice show its number, subtotal in cents, tax in cents (18% of taxable lines, integer division), and total in cents. Order by invoice.", BILLING,
              "SELECT invoice,\n  SUM(qty * unit_cents) AS subtotal,\n  SUM(CASE WHEN taxable = 1 THEN qty * unit_cents ELSE 0 END) * 18 / 100 AS tax,\n  SUM(qty * unit_cents) + SUM(CASE WHEN taxable = 1 THEN qty * unit_cents ELSE 0 END) * 18 / 100 AS total\nFROM lines\nGROUP BY invoice\nORDER BY invoice;", require=[r"(?i)CASE"]),
        ),
        lesson(
            "Sessionization",
            """A session is a burst of activity separated by a gap of inactivity (say 30 minutes). Mark a new session when the gap from the previous event exceeds the limit, then number sessions with a running SUM of those flags.

WITH f AS (
  SELECT *, CASE WHEN minute - LAG(minute) OVER (PARTITION BY user ORDER BY minute) > 30 THEN 1 ELSE 0 END AS new_session
  FROM clicks
)
SELECT user, SUM(new_session) OVER (PARTITION BY user ORDER BY minute) AS session_no, ... FROM f;""",
            mcq("What starts a new session?", ["A gap longer than the limit", "A new day only", "Every click", "A NULL"], 0),
            mcq("How are sessions numbered?", ["A running SUM of 'new session' flags", "COUNT(*)", "RANK()", "MAX(minute)"], 0),
            mcq("Which function reads the previous click's time?", ["LAG", "LEAD", "FIRST_VALUE", "NTILE"], 0),
            q("A new session starts after a gap of more than 30 minutes between a user's clicks. For each user show how many sessions they had. Order by user.", SESSIONS,
              "WITH f AS (\n  SELECT user, minute,\n    CASE WHEN LAG(minute) OVER (PARTITION BY user ORDER BY minute) IS NULL OR minute - LAG(minute) OVER (PARTITION BY user ORDER BY minute) > 30 THEN 1 ELSE 0 END AS starts\n  FROM clicks\n)\nSELECT user, SUM(starts) FROM f GROUP BY user ORDER BY user;", require=[r"(?i)LAG"]),
        ),
        lesson(
            "Reconciliation checks",
            """Reconciliation compares two sources that should agree and lists the differences - the daily job of every finance and data team.

SELECT a.sku, a.expected, COALESCE(b.counted, 0) AS counted, COALESCE(b.counted, 0) - a.expected AS diff
FROM expected a LEFT JOIN counted b ON b.sku = a.sku
WHERE COALESCE(b.counted, 0) <> a.expected;

Remember skus that exist on only ONE side: use LEFT JOIN both ways, or a UNION of both lists, so nothing is missed.""",
            mcq("What does reconciliation find?", ["Differences between two sources that should match", "Duplicates only", "Slow queries", "Unused indexes"], 0),
            mcq("Why check both directions?", ["Items can be missing from either side", "To sort", "To save time", "To add keys"], 0),
            mcq("What does COALESCE(b.counted, 0) handle?", ["Items missing from the counted side", "Duplicates", "Sorting", "Dates"], 0),
            q("Expected stock is pen 70, ink 8, cap 55. Compare with the calculated on-hand quantities from the moves (in minus out) and list sku|expected|actual for every sku where they differ, ordered by sku.",
              STOCK + "\nCREATE TABLE expected (sku TEXT PRIMARY KEY, qty INTEGER);\nINSERT INTO expected VALUES ('pen', 70), ('ink', 8), ('cap', 55);",
              "WITH actual AS (SELECT sku, SUM(CASE WHEN kind = 'in' THEN qty ELSE -qty END) AS qty FROM moves GROUP BY sku)\nSELECT e.sku, e.qty, COALESCE(a.qty, 0)\nFROM expected e LEFT JOIN actual a ON a.sku = e.sku\nWHERE e.qty <> COALESCE(a.qty, 0)\nORDER BY e.sku;", require=[r"(?i)JOIN"]),
        ),
    ),
)
