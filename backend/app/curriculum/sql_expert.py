"""SQL - Expert section, part 1 (units 17-22). SQLite (sql.js in the browser).

Each `q()` exercise's expected rows are produced by running its reference query on SQLite itself (the same engine
the learner uses), formatted exactly like the in-browser runner: columns joined with "|", NULL shown as NULL.
`scripts/validate_curriculum.py` then re-checks every answer through the real browser runner code."""
import sqlite3

from .dsl import fill, lesson, mcq, order, run, section, t, unit
from .sql_adv import SALES, SHOP, STAFF


def _fmt(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def rows_of(setup: str, sql: str) -> str:
    con = sqlite3.connect(":memory:")
    con.executescript(setup)
    statements = [s.strip() for s in sql.strip().rstrip(";").split(";") if s.strip()]
    for s in statements[:-1]:
        con.execute(s)
    out = [" | ".join(_fmt(v) for v in r).replace(" | ", "|") for r in con.execute(statements[-1]).fetchall()]
    con.close()
    return "\n".join(out)


def q(prompt, setup, sql, require=None, forbid=None, hint=""):
    """A `run` exercise whose expected output is what the reference query returns."""
    return run(prompt, "sql", [t("Run")], [rows_of(setup, sql)], sql, setup=setup, require=require, forbid=forbid, hint=hint)


VIEWS = """CREATE TABLE views (id INTEGER PRIMARY KEY, user TEXT, page TEXT, day TEXT, secs INTEGER);
INSERT INTO views VALUES
  (1, 'ada', 'home', '2026-03-01', 30), (2, 'ada', 'docs', '2026-03-01', 120), (3, 'bo', 'home', '2026-03-01', 15),
  (4, 'ada', 'home', '2026-03-02', 45), (5, 'bo', 'docs', '2026-03-03', 200), (6, 'cy', 'home', '2026-03-03', 20),
  (7, 'cy', 'pricing', '2026-03-04', 90), (8, 'ada', 'pricing', '2026-03-05', 60), (9, 'bo', 'home', '2026-03-05', 25),
  (10, 'dee', 'docs', '2026-03-05', 300), (11, 'dee', 'docs', '2026-03-06', 150);"""

SCORES = """CREATE TABLE scores (id INTEGER PRIMARY KEY, player TEXT, game TEXT, points INTEGER, played TEXT);
INSERT INTO scores VALUES
  (1, 'ada', 'chess', 80, '2026-04-01'), (2, 'bo', 'chess', 95, '2026-04-01'), (3, 'cy', 'chess', 95, '2026-04-02'),
  (4, 'ada', 'chess', 70, '2026-04-03'), (5, 'bo', 'go', 60, '2026-04-03'), (6, 'cy', 'go', 88, '2026-04-04'),
  (7, 'dee', 'go', 75, '2026-04-04'), (8, 'ada', 'go', 91, '2026-04-05'), (9, 'dee', 'chess', 50, '2026-04-05'),
  (10, 'bo', 'chess', 85, '2026-04-06');"""

DUPES = """CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT);
INSERT INTO contacts VALUES
  (1, '  Ada Lovelace ', 'ADA@mail.com', '555-0101'), (2, 'ada lovelace', 'ada@mail.com', NULL),
  (3, 'Bo Peep', 'bo@mail.com', ''), (4, 'Cy Young', NULL, '555-0103'), (5, 'bo peep', 'BO@mail.com', '555-0102');"""

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Window functions in depth",
        lesson(
            "Window frames & moving averages",
            """A window can have a FRAME - which neighbouring rows to include:

SELECT day, secs,
  AVG(secs) OVER (ORDER BY day ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS avg2
FROM views;

ROWS BETWEEN 2 PRECEDING AND CURRENT ROW = this row and the two before it. UNBOUNDED PRECEDING means 'from the very first row'. With ORDER BY and no frame, SUM() OVER (ORDER BY ...) is a running total.

Moving averages smooth noisy data.""",
            mcq("What does ROWS BETWEEN 1 PRECEDING AND CURRENT ROW cover?", ["The previous row and this row", "All earlier rows", "The next row", "Only this row"], 0),
            mcq("Which gives a running total?", ["SUM(x) OVER (ORDER BY d)", "SUM(x) GROUP BY d", "COUNT(*) OVER ()", "AVG(x) OVER ()"], 0),
            mcq("What is a frame?", ["The set of rows a window function looks at per row", "A table alias", "A join type", "An index"], 0),
            q("For each sale in order of id, show id and the average of that sale's amount and the two previous sales' amounts (3-sale moving average), rounded to 1 decimal.", SALES,
              "SELECT id, ROUND(AVG(amount) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1)\nFROM sales\nORDER BY id;", require=[r"(?i)\bROWS\b", r"(?i)\bOVER\b"]),
        ),
        lesson(
            "FIRST_VALUE, LAST_VALUE & NTILE",
            """FIRST_VALUE(x) OVER (...) gives the first row's value in the window; NTILE(n) splits rows into n equal buckets (quartiles = NTILE(4)).

SELECT player, points,
  FIRST_VALUE(player) OVER (ORDER BY points DESC) AS leader,
  NTILE(2) OVER (ORDER BY points DESC) AS half
FROM scores;

Careful: with ORDER BY the default frame ends at the current row, so LAST_VALUE needs ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING.""",
            mcq("What does NTILE(4) do?", ["Splits rows into 4 equal-sized groups", "Returns the 4th row", "Limits to 4 rows", "Counts by 4"], 0),
            mcq("Why does LAST_VALUE often surprise people?", ["The default frame stops at the current row", "It is slow", "It ignores ORDER BY", "It returns NULL"], 0),
            mcq("Which function returns the first value in the window?", ["FIRST_VALUE", "TOP", "HEAD", "MIN_ROW"], 0),
            q("Split all scores into 2 halves by points (highest first, ties by id). Show id, points and the half (1 or 2). Order by points descending, then id.", SCORES,
              "SELECT id, points, NTILE(2) OVER (ORDER BY points DESC, id) AS half\nFROM scores\nORDER BY points DESC, id;", require=[r"(?i)NTILE"]),
        ),
        lesson(
            "Top N per group",
            """The classic: 'the best row in each group'. Rank inside each group with PARTITION BY, then filter in an outer query (you can't filter on a window function directly):

SELECT * FROM (
  SELECT game, player, points,
         ROW_NUMBER() OVER (PARTITION BY game ORDER BY points DESC, id) AS rn
  FROM scores
)
WHERE rn <= 2;

Use ROW_NUMBER for exactly N rows, RANK/DENSE_RANK to keep ties.""",
            mcq("Why wrap the window function in an outer query?", ["WHERE cannot reference a window function directly", "It is faster", "SQLite requires it", "To rename columns"], 0),
            mcq("Which keeps tied rows together in the same position?", ["RANK / DENSE_RANK", "ROW_NUMBER", "NTILE", "LAG"], 0),
            mcq("What does PARTITION BY game do?", ["Restarts the numbering for each game", "Joins by game", "Sorts by game", "Deletes games"], 0),
            q("For each game show the single highest-scoring row: game, player, points. If tied, the lowest id wins. Order by game.", SCORES,
              "SELECT game, player, points FROM (\n  SELECT game, player, points, ROW_NUMBER() OVER (PARTITION BY game ORDER BY points DESC, id) AS rn\n  FROM scores\n)\nWHERE rn = 1\nORDER BY game;", require=[r"(?i)PARTITION\s+BY"]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Advanced aggregation",
        lesson(
            "GROUP_CONCAT & DISTINCT counts",
            """GROUP_CONCAT joins the values of a group into one string:

SELECT dept, GROUP_CONCAT(name, ', ') FROM employees GROUP BY dept;

COUNT(DISTINCT col) counts unique values: how many different users visited?

SELECT page, COUNT(DISTINCT user) FROM views GROUP BY page;

The order inside GROUP_CONCAT is not guaranteed unless you sort in a subquery first.""",
            mcq("What does COUNT(DISTINCT user) count?", ["Different users", "All rows", "Non-null rows", "Groups"], 0),
            mcq("What does GROUP_CONCAT(name, ', ') produce for a group?", ["One text with the names joined by commas", "A list", "The first name", "A count"], 0),
            mcq("Is the order inside GROUP_CONCAT guaranteed?", ["No, unless you sort first", "Yes, alphabetical", "Yes, by id", "Yes, insertion"], 0),
            q("For each page show the page name and how many DIFFERENT users viewed it, most users first, then page name.", VIEWS,
              "SELECT page, COUNT(DISTINCT user) AS visitors\nFROM views\nGROUP BY page\nORDER BY visitors DESC, page;", require=[r"(?i)DISTINCT"]),
        ),
        lesson(
            "Conditional aggregates & HAVING",
            """Put a condition inside an aggregate with CASE, or FILTER (SQLite 3.30+):

SELECT user,
  SUM(CASE WHEN page = 'docs' THEN secs ELSE 0 END) AS docs_secs,
  COUNT(*) FILTER (WHERE page = 'home') AS home_views
FROM views GROUP BY user;

HAVING filters AFTER grouping, WHERE filters BEFORE: HAVING SUM(secs) > 100.""",
            mcq("When does HAVING run relative to GROUP BY?", ["After grouping", "Before grouping", "Instead of GROUP BY", "Never"], 0),
            mcq("Which clause filters individual rows before they are grouped?", ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 0),
            mcq("What does SUM(CASE WHEN x THEN 1 ELSE 0 END) compute?", ["How many rows satisfy x", "The total of x", "The first match", "The average"], 0),
            q("Show each user and the total seconds spent on the 'docs' page (0 if none), only for users whose total seconds across ALL pages exceed 100. Order by user.", VIEWS,
              "SELECT user, SUM(CASE WHEN page = 'docs' THEN secs ELSE 0 END) AS docs_secs\nFROM views\nGROUP BY user\nHAVING SUM(secs) > 100\nORDER BY user;", require=[r"(?i)HAVING", r"(?i)CASE"]),
        ),
        lesson(
            "Percent of total",
            """Combine a group total with a window total to show shares:

SELECT region, SUM(amount) AS total,
  ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 1) AS pct
FROM sales GROUP BY region;

SUM(SUM(amount)) OVER () sums the group totals across all groups. Multiply by 100.0 (not 100) so the division isn't an integer division.""",
            mcq("Why multiply by 100.0 instead of 100?", ["To avoid integer division", "It is faster", "100 is invalid", "To round"], 0),
            mcq("What does SUM(SUM(amount)) OVER () give?", ["The grand total across groups", "A running total", "The max group", "A count"], 0),
            mcq("What is 7 / 2 in SQLite with integers?", ["3", "3.5", "4", "2"], 0),
            q("For each month show the month and its share of ALL sales, as a percentage rounded to 1 decimal. Order by month.", SALES,
              "SELECT month, ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 1) AS pct\nFROM sales\nGROUP BY month\nORDER BY month;", require=[r"(?i)OVER"]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Cleaning data",
        lesson(
            "NULLIF, COALESCE & empty strings",
            """Real data mixes NULL and '' for 'missing'. Normalise them:

COALESCE(phone, 'none')                 -- NULL -> 'none'
NULLIF(phone, '')                       -- '' -> NULL (otherwise unchanged)
COALESCE(NULLIF(phone, ''), 'none')     -- both cases

NULLIF(a, b) also prevents division by zero: x / NULLIF(y, 0) gives NULL instead of an error.""",
            mcq("What does NULLIF(phone, '') return when phone is ''?", ["NULL", "''", "0", "An error"], 0),
            mcq("What does COALESCE(NULL, NULL, 'x') return?", ["'x'", "NULL", "''", "0"], 0),
            mcq("How do you avoid division by zero?", ["x / NULLIF(y, 0)", "x / COALESCE(y)", "x / ABS(y)", "IF y THEN"], 0),
            q("List each contact's id and phone, showing 'none' when the phone is NULL OR empty. Order by id.", DUPES,
              "SELECT id, COALESCE(NULLIF(phone, ''), 'none')\nFROM contacts\nORDER BY id;", require=[r"(?i)NULLIF", r"(?i)COALESCE"]),
        ),
        lesson(
            "Normalising text",
            """Before comparing text, clean it: TRIM removes spaces at the ends, LOWER/UPPER fix case, REPLACE swaps pieces.

SELECT LOWER(TRIM(name)) FROM contacts;

Two names that look different ('  Ada Lovelace ' and 'ada lovelace') become equal once normalised - the first step of finding duplicates. For a title-case name use UPPER(SUBSTR(x,1,1)) || LOWER(SUBSTR(x,2)).""",
            mcq("What does TRIM('  hi ') return?", ["'hi'", "'  hi'", "'hi '", "' hi'"], 0),
            mcq("Why normalise before comparing?", ["'Ada' and ' ada ' should match", "It speeds up joins", "NULLs disappear", "It adds an index"], 0),
            mcq("What does || do in SQLite?", ["Concatenates text", "Logical OR", "Divides", "Compares"], 0),
            q("Show each contact's id and a normalised email (trimmed, lower-case) or 'none' when missing. Order by id.", DUPES,
              "SELECT id, COALESCE(LOWER(TRIM(email)), 'none')\nFROM contacts\nORDER BY id;", require=[r"(?i)LOWER", r"(?i)TRIM"]),
        ),
        lesson(
            "Finding and removing duplicates",
            """Rows are duplicates when their normalised key is equal. Number the rows in each key group and keep the first:

SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY LOWER(TRIM(email)) ORDER BY id) AS rn
  FROM contacts WHERE email IS NOT NULL
)
WHERE rn > 1;      -- the duplicates to delete

DELETE FROM contacts WHERE id IN (SELECT id FROM ... WHERE rn > 1) removes them while keeping the earliest row.""",
            mcq("How do you identify duplicates with a window function?", ["ROW_NUMBER() PARTITION BY the key, then rn > 1", "COUNT(*) alone", "ORDER BY the key", "DISTINCT *"], 0),
            mcq("Which row do we keep with ORDER BY id in the window?", ["The lowest id", "The highest id", "A random one", "None"], 0),
            mcq("Why write the SELECT first, then change it to a DELETE?", ["To check what will be removed", "DELETE is slower", "SELECT is required", "To add an index"], 0),
            q("List the ids of the DUPLICATE contacts to remove: among rows with an email, those that repeat an earlier row's normalised email (keep the lowest id). Order by id.", DUPES,
              "SELECT id FROM (\n  SELECT id, ROW_NUMBER() OVER (PARTITION BY LOWER(TRIM(email)) ORDER BY id) AS rn\n  FROM contacts\n  WHERE email IS NOT NULL\n)\nWHERE rn > 1\nORDER BY id;", require=[r"(?i)ROW_NUMBER"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Time-based analysis",
        lesson(
            "Bucketing by day and month",
            """STRFTIME turns dates into buckets: '%Y-%m' for months, '%W' for week number, '%w' for weekday (0 = Sunday).

SELECT STRFTIME('%Y-%m', day) AS month, COUNT(*) FROM views GROUP BY month;

DATE(day, '+7 days'), DATE(day, 'start of month') and julianday(b) - julianday(a) (days between) handle date maths.""",
            mcq("What does STRFTIME('%Y-%m', '2026-03-05') return?", ["'2026-03'", "'03'", "'2026'", "'2026-03-05'"], 0),
            mcq("How do you find the days between two dates in SQLite?", ["julianday(b) - julianday(a)", "b - a", "DATEDIFF(a, b)", "DAYS(a, b)"], 0),
            mcq("What does DATE('2026-03-05', '+7 days') give?", ["'2026-03-12'", "'2026-03-07'", "'2026-04-05'", "'2026-03-05'"], 0),
            q("Show each day and the total seconds viewed that day, ordered by day.", VIEWS, "SELECT day, SUM(secs)\nFROM views\nGROUP BY day\nORDER BY day;", require=[r"(?i)GROUP\s+BY"]),
        ),
        lesson(
            "Daily actives & first-seen",
            """Product questions: how many users were active each day? When did each user first appear?

SELECT day, COUNT(DISTINCT user) AS dau FROM views GROUP BY day;
SELECT user, MIN(day) AS first_day FROM views GROUP BY user;

Joining the two ideas gives 'new vs returning': a user is NEW on the day equal to their first_day.""",
            mcq("What does DAU stand for?", ["Daily active users", "Data and users", "Day after update", "Duplicate all users"], 0),
            mcq("Which aggregate finds a user's first day?", ["MIN(day)", "MAX(day)", "COUNT(day)", "SUM(day)"], 0),
            mcq("A user is 'new' on a day when…", ["That day equals their first_day", "They viewed home", "Their views > 1", "They have an email"], 0),
            q("For each day show the day, how many distinct users were active (dau) and how many of them were seen for the FIRST time that day (new_users). Order by day.", VIEWS,
              "WITH first AS (SELECT user, MIN(day) AS first_day FROM views GROUP BY user)\nSELECT v.day,\n  COUNT(DISTINCT v.user) AS dau,\n  COUNT(DISTINCT CASE WHEN f.first_day = v.day THEN v.user END) AS new_users\nFROM views v JOIN first f ON f.user = v.user\nGROUP BY v.day\nORDER BY v.day;", require=[r"(?i)MIN\s*\(", r"(?i)DISTINCT"]),
        ),
        lesson(
            "Consecutive days (gaps & islands)",
            """To find streaks, use the 'row number trick': for consecutive dates, date minus ROW_NUMBER() stays constant.

WITH d AS (SELECT DISTINCT user, day FROM views),
g AS (
  SELECT user, day,
    julianday(day) - ROW_NUMBER() OVER (PARTITION BY user ORDER BY day) AS grp
  FROM d
)
SELECT user, MIN(day), MAX(day), COUNT(*) FROM g GROUP BY user, grp;

Each unbroken run of days shares the same grp value.""",
            mcq("What stays constant across consecutive days in the row-number trick?", ["date minus ROW_NUMBER()", "the date alone", "the user", "COUNT(*)"], 0),
            mcq("What does a gap in the dates do to grp?", ["Starts a new group value", "Nothing", "Raises an error", "Repeats the old one"], 0),
            mcq("Why take DISTINCT (user, day) first?", ["So several views in a day count as one day", "To sort", "To join", "To add NULLs"], 0),
            q("For each user find their LONGEST streak of consecutive active days. Show user and streak length. Order by streak descending, then user.", VIEWS,
              "WITH d AS (SELECT DISTINCT user, day FROM views),\ng AS (\n  SELECT user, day, julianday(day) - ROW_NUMBER() OVER (PARTITION BY user ORDER BY day) AS grp FROM d\n),\ns AS (SELECT user, COUNT(*) AS len FROM g GROUP BY user, grp)\nSELECT user, MAX(len) FROM s GROUP BY user ORDER BY MAX(len) DESC, user;", require=[r"(?i)ROW_NUMBER", r"(?i)julianday"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Joins in depth",
        lesson(
            "Anti-joins and semi-joins",
            """Anti-join: rows with NO match. Semi-join: rows WITH a match, without duplicating them.

-- customers who never ordered
SELECT c.name FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id IS NULL;
SELECT name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- customers who ordered at least once (no duplicates)
SELECT name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

A plain JOIN would repeat a customer once per order.""",
            mcq("Which finds rows with no match?", ["LEFT JOIN ... WHERE right.id IS NULL", "INNER JOIN", "CROSS JOIN", "UNION"], 0),
            mcq("Why prefer EXISTS for 'has at least one order'?", ["It doesn't repeat the customer per order", "It sorts", "It is required", "It is shorter always"], 0),
            mcq("What does NOT EXISTS (SELECT 1 ...) return rows for?", ["Outer rows with no matching inner row", "All rows", "Only NULLs", "Matched rows"], 0),
            q("List the names of customers who have never placed an order, using NOT EXISTS or a LEFT JOIN anti-join. Order by name.", SHOP,
              "SELECT c.name FROM customers c\nWHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)\nORDER BY c.name;", require=[r"(?i)NOT\s+EXISTS|LEFT\s+JOIN"]),
        ),
        lesson(
            "Range joins & bands",
            """A join condition doesn't have to be equality. Join a value to the BAND that contains it:

CREATE TABLE bands (label TEXT, lo INTEGER, hi INTEGER);
SELECT e.name, b.label
FROM employees e JOIN bands b ON e.salary BETWEEN b.lo AND b.hi;

This pattern assigns grades, price tiers, tax brackets or age groups from a small lookup table instead of a long CASE.""",
            mcq("What is a range join?", ["A join on BETWEEN or inequalities", "A join with UNION", "A join of three tables", "A self join"], 0),
            mcq("Why use a lookup table of bands instead of CASE?", ["Bands can change without editing queries", "It is faster always", "CASE is invalid", "It avoids NULLs"], 0),
            mcq("Which operator suits 'salary within lo and hi'?", ["BETWEEN", "LIKE", "IN", "GLOB"], 0),
            q("Using the pay bands below, show each employee's name and band label. Order by name.", STAFF + "\nCREATE TABLE bands (label TEXT, lo INTEGER, hi INTEGER);\nINSERT INTO bands VALUES ('low', 0, 4999), ('mid', 5000, 6999), ('high', 7000, 99999);",
              "SELECT e.name, b.label\nFROM employees e\nJOIN bands b ON e.salary BETWEEN b.lo AND b.hi\nORDER BY e.name;", require=[r"(?i)BETWEEN"]),
        ),
        lesson(
            "Cross joins & number series",
            """CROSS JOIN pairs every row with every row. A recursive CTE can generate a series, handy for filling gaps in reports (days with zero sales still appear).

WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 5)
SELECT i FROM n;

Then LEFT JOIN real data onto the series so missing numbers show up as 0 via COALESCE.""",
            mcq("How many rows does a CROSS JOIN of 3 and 4 rows give?", ["12", "7", "3", "4"], 0),
            mcq("Why generate a series and LEFT JOIN onto it?", ["So empty periods still appear in the report", "To sort", "To delete rows", "To add columns"], 0),
            mcq("What stops a recursive CTE?", ["Its WHERE condition", "LIMIT only", "A timeout", "Nothing"], 0),
            q("Show every day from 2026-03-01 to 2026-03-07 with the number of page views that day (0 when none). Order by day.", VIEWS,
              "WITH RECURSIVE days(day) AS (\n  SELECT '2026-03-01'\n  UNION ALL\n  SELECT DATE(day, '+1 day') FROM days WHERE day < '2026-03-07'\n)\nSELECT d.day, COUNT(v.id)\nFROM days d LEFT JOIN views v ON v.day = d.day\nGROUP BY d.day\nORDER BY d.day;", require=[r"(?i)RECURSIVE", r"(?i)LEFT\s+JOIN"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Hierarchies & recursion",
        lesson(
            "Org-chart depth",
            """A recursive CTE can compute each employee's level in the hierarchy:

WITH RECURSIVE chain(id, name, level) AS (
  SELECT id, name, 0 FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, c.level + 1 FROM employees e JOIN chain c ON e.manager_id = c.id
)
SELECT name, level FROM chain;

The anchor query starts at the top (no manager); the recursive part adds the next level until no rows remain.""",
            mcq("What is the 'anchor' of a recursive CTE?", ["The starting rows", "The last row", "The index", "The join"], 0),
            mcq("What does the recursive part do?", ["Adds the next level using the previous rows", "Deletes rows", "Sorts", "Counts"], 0),
            mcq("Which employee has level 0 here?", ["The one with no manager", "The newest", "The highest paid", "Everyone"], 0),
            q("Show every employee's name and their level in the reporting chain (the person with no manager is level 0). Order by level, then name.", STAFF,
              "WITH RECURSIVE chain(id, name, level) AS (\n  SELECT id, name, 0 FROM employees WHERE manager_id IS NULL\n  UNION ALL\n  SELECT e.id, e.name, c.level + 1 FROM employees e JOIN chain c ON e.manager_id = c.id\n)\nSELECT name, level FROM chain\nORDER BY level, name;", require=[r"(?i)RECURSIVE"]),
        ),
        lesson(
            "Building paths",
            """Carry text along the recursion to build a path like 'Ada > Di > Eve':

WITH RECURSIVE p(id, path) AS (
  SELECT id, name FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, p.path || ' > ' || e.name FROM employees e JOIN p ON e.manager_id = p.id
)
SELECT path FROM p;

Paths let you filter a whole branch with LIKE 'Ada > Di%'.""",
            mcq("What builds the path string in each step?", ["Concatenating the parent's path with the child's name", "A sub-select", "GROUP_CONCAT only", "ORDER BY"], 0),
            mcq("How can a path filter a whole branch?", ["path LIKE 'Ada > Di%'", "path = 'Ada'", "path IN (...)", "ORDER BY path"], 0),
            mcq("Which operator concatenates text?", ["||", "+", "&", "AND"], 0),
            q("For every employee show the full management path from the top, like 'Ada > Di > Eve'. Order by path.", STAFF,
              "WITH RECURSIVE p(id, path) AS (\n  SELECT id, name FROM employees WHERE manager_id IS NULL\n  UNION ALL\n  SELECT e.id, p.path || ' > ' || e.name FROM employees e JOIN p ON e.manager_id = p.id\n)\nSELECT path FROM p\nORDER BY path;", require=[r"\|\|"]),
        ),
        lesson(
            "Subtree totals",
            """Aggregate over a branch: total salary of a manager and everyone beneath them.

WITH RECURSIVE sub(root, id) AS (
  SELECT id, id FROM employees
  UNION ALL
  SELECT sub.root, e.id FROM employees e JOIN sub ON e.manager_id = sub.id
)
SELECT root, SUM(e.salary) FROM sub JOIN employees e ON e.id = sub.id GROUP BY root;

Each employee is their own root; descendants are added with the same root.""",
            mcq("What is 'root' in the sub CTE?", ["The manager whose subtree we are collecting", "The CEO only", "The table name", "A constant"], 0),
            mcq("Why does every employee start as their own root?", ["A person's total includes themselves", "To avoid NULLs", "To sort", "It is required by SQL"], 0),
            mcq("What does GROUP BY root do?", ["One total per manager", "One total overall", "Removes roots", "Sorts roots"], 0),
            q("For each employee show their name and the total salary of themselves plus everyone who reports to them, directly or indirectly. Order by name.", STAFF,
              "WITH RECURSIVE sub(root, id) AS (\n  SELECT id, id FROM employees\n  UNION ALL\n  SELECT sub.root, e.id FROM employees e JOIN sub ON e.manager_id = sub.id\n)\nSELECT r.name, SUM(e.salary)\nFROM sub JOIN employees r ON r.id = sub.root JOIN employees e ON e.id = sub.id\nGROUP BY r.id\nORDER BY r.name;", require=[r"(?i)RECURSIVE"]),
        ),
    ),
)
