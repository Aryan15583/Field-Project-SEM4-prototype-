"""SQL - Intermediate and Advanced sections (units 9-16). Runs on SQLite (sql.js)."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit

STAFF = """CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  dept TEXT,
  salary INTEGER,
  manager_id INTEGER REFERENCES employees(id),
  hired TEXT,
  email TEXT
);
INSERT INTO employees VALUES
  (1, 'Ada', 'Engineering', 9000, NULL, '2019-03-01', 'ada@corp.io'),
  (2, 'Bo', 'Engineering', 7000, 1, '2021-06-15', 'bo@corp.io'),
  (3, 'Cy', 'Engineering', 7000, 1, '2022-01-10', 'CY@Corp.io'),
  (4, 'Di', 'Sales', 6000, 1, '2020-11-20', 'di@corp.io'),
  (5, 'Eve', 'Sales', 5500, 4, '2023-02-01', NULL),
  (6, 'Finn', 'Sales', 4800, 4, '2024-07-07', 'finn@corp.io'),
  (7, 'Gia', 'Support', 4200, 1, '2022-09-30', 'gia@corp.io');"""

SALES = """CREATE TABLE sales (id INTEGER PRIMARY KEY, rep TEXT, region TEXT, month TEXT, amount INTEGER);
INSERT INTO sales VALUES
  (1, 'Ada', 'North', '2026-01', 120), (2, 'Bo', 'North', '2026-01', 90), (3, 'Cy', 'South', '2026-01', 150),
  (4, 'Ada', 'North', '2026-02', 80), (5, 'Bo', 'North', '2026-02', 130), (6, 'Cy', 'South', '2026-02', 110),
  (7, 'Ada', 'North', '2026-03', 160), (8, 'Bo', 'North', '2026-03', 100), (9, 'Cy', 'South', '2026-03', 150),
  (10, 'Di', 'South', '2026-03', 70);"""

SHOP = """CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, country TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), order_date TEXT);
CREATE TABLE order_items (order_id INTEGER REFERENCES orders(id), product_id INTEGER REFERENCES products(id), qty INTEGER);
INSERT INTO customers VALUES (1, 'Ada', 'UK'), (2, 'Linus', 'Finland'), (3, 'Grace', 'USA'), (4, 'Tim', 'UK');
INSERT INTO products VALUES
  (1, 'Keyboard', 'Hardware', 49.5), (2, 'Mouse', 'Hardware', 19.0), (3, 'Monitor', 'Hardware', 199.0),
  (4, 'Editor Pro', 'Software', 30.0), (5, 'Game', 'Software', 60.0);
INSERT INTO orders VALUES (1, 1, '2026-01-05'), (2, 2, '2026-01-07'), (3, 1, '2026-02-11'), (4, 3, '2026-02-20');
INSERT INTO order_items VALUES (1, 1, 1), (1, 2, 2), (2, 4, 1), (3, 3, 1), (3, 5, 2), (4, 2, 1);"""

ACCOUNTS = """CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT UNIQUE, balance INTEGER CHECK (balance >= 0));
INSERT INTO accounts VALUES (1, 'ada', 100), (2, 'bo', 50);"""

CATEGORIES = """CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT, parent_id INTEGER REFERENCES categories(id));
INSERT INTO categories VALUES
  (1, 'All', NULL), (2, 'Tech', 1), (3, 'Books', 1), (4, 'Laptops', 2), (5, 'Phones', 2), (6, 'Gaming laptops', 4), (7, 'Novels', 3);"""

EVENTS = """CREATE TABLE events (id INTEGER PRIMARY KEY, payload TEXT);
INSERT INTO events VALUES
  (1, '{"type": "login", "user": "ada", "ms": 120}'),
  (2, '{"type": "purchase", "user": "bo", "ms": 340, "items": ["pen", "ink"]}'),
  (3, '{"type": "login", "user": "bo", "ms": 95}'),
  (4, '{"type": "purchase", "user": "ada", "ms": 410, "items": ["book"]}');"""


INTERMEDIATE = section(
    "Intermediate",
    # ------------------------------------------------------------------ 9
    unit(
        "Unit 9 · Functions",
        lesson(
            "String functions",
            "SQL can transform text:\n\nUPPER(name)  LOWER(email)  LENGTH(name)  TRIM('  x ')\nSUBSTR(text, start, length)        -- 1-based\nREPLACE(email, '@corp.io', '')\nINSTR(email, '@')                  -- position, 0 if missing\nname || ' (' || dept || ')'          -- concatenation\n\nFunction names vary a little between databases (e.g. SUBSTRING, CONCAT), but the ideas are the same.",
            mcq("What is SUBSTR('database', 1, 4)?", ["'data'", "'atab'", "'base'", "'datab'"], 0, "SQL strings are 1-based."),
            fill("Lower-case every email.", "SELECT ___(email) FROM employees;", "LOWER"),
            mcq("What does INSTR('a@b', '@') return?", ["2", "1", "0", "'@'"], 0),
            mcq("What is LENGTH(NULL)?", ["NULL", "0", "An error", "4"], 0),
            run("For every employee with an email, select the name and the part of the email before the @, lower-cased, as username. Order by name.", "sql", [t("Run")],
                ["Ada|ada\nBo|bo\nCy|cy\nDi|di\nFinn|finn\nGia|gia"],
                "SELECT name, LOWER(SUBSTR(email, 1, INSTR(email, '@') - 1)) AS username\nFROM employees\nWHERE email IS NOT NULL\nORDER BY name;",
                setup=STAFF, require=[r"(?i)SUBSTR|INSTR|REPLACE"], hint="SUBSTR(email, 1, INSTR(email, '@') - 1), then LOWER it."),
        ),
        lesson(
            "Numbers & CASE",
            "Numeric helpers: ROUND(x, 2), ABS(x), x % 3, MAX(a, b) / MIN(a, b) as scalar functions in SQLite.\n\nCASE builds values from conditions:\n\nSELECT name,\n  CASE\n    WHEN salary >= 8000 THEN 'senior'\n    WHEN salary >= 5000 THEN 'mid'\n    ELSE 'junior'\n  END AS band\nFROM employees;\n\nCOALESCE(a, b, ...) returns the first non-NULL value.",
            mcq("What does COALESCE(NULL, NULL, 'x') return?", ["'x'", "NULL", "An error", "''"], 0),
            fill("End a CASE expression.", "CASE WHEN x > 0 THEN 'pos' ELSE 'neg' ___", "END"),
            mcq("What is ROUND(2.567, 1)?", ["2.6", "2.5", "3", "2.56"], 0),
            mcq("Which CASE branch runs when several WHEN conditions are true?", ["The first true one", "The last", "All of them", "None"], 0),
            run("Select each employee's name and email, using COALESCE to show 'no email' when it's NULL, plus a pay band: 'high' for salary ≥ 7000, 'mid' for ≥ 5000, else 'low'. Order by id.", "sql", [t("Run")],
                ["Ada|ada@corp.io|high\nBo|bo@corp.io|high\nCy|CY@Corp.io|high\nDi|di@corp.io|mid\nEve|no email|mid\nFinn|finn@corp.io|low\nGia|gia@corp.io|low"],
                "SELECT name,\n  COALESCE(email, 'no email'),\n  CASE WHEN salary >= 7000 THEN 'high' WHEN salary >= 5000 THEN 'mid' ELSE 'low' END\nFROM employees\nORDER BY id;",
                setup=STAFF, require=[r"(?i)COALESCE|IFNULL", r"(?i)\bCASE\b"]),
        ),
        lesson(
            "Dates",
            "SQLite stores dates as ISO text ('2026-10-02') and has date functions:\n\nDATE('now')   DATE('2026-01-31', '+1 month')\nSTRFTIME('%Y', hired)          -- year as text\nJULIANDAY(b) - JULIANDAY(a)    -- days between\n\nISO dates sort correctly as text. Other databases use EXTRACT(YEAR FROM d), DATE_TRUNC, INTERVAL…",
            mcq("Why do ISO dates ('YYYY-MM-DD') sort correctly as text?", ["Biggest unit first, fixed width", "SQLite converts them", "They're numbers", "They don't"], 0),
            fill("Extract the year in SQLite.", "SELECT ___('%Y', hired) FROM employees;", "STRFTIME"),
            mcq("What is DATE('2026-01-15', '+10 days')?", ["'2026-01-25'", "'2026-01-15'", "'2026-11-15'", "An error"], 0),
            mcq("How do you get the number of days between two dates in SQLite?", ["JULIANDAY(b) - JULIANDAY(a)", "b - a", "DAYS(a, b)", "DATEDIFF only"], 0),
            run("Count how many employees were hired in each year, as year|count, ordered by year.", "sql", [t("Run")],
                ["2019|1\n2020|1\n2021|1\n2022|2\n2023|1\n2024|1"],
                "SELECT STRFTIME('%Y', hired) AS year, COUNT(*)\nFROM employees\nGROUP BY year\nORDER BY year;",
                setup=STAFF, require=[r"(?i)GROUP\s+BY"], hint="STRFTIME('%Y', hired) or SUBSTR(hired, 1, 4)."),
        ),
    ),
    # ------------------------------------------------------------------ 10
    unit(
        "Unit 10 · Combining queries",
        lesson(
            "Self joins",
            "A table can be joined to ITSELF - e.g. employees and their managers:\n\nSELECT e.name, m.name AS manager\nFROM employees e\nLEFT JOIN employees m ON e.manager_id = m.id;\n\nAliases (e, m) are required so SQL knows which copy you mean.",
            mcq("Why are aliases needed in a self join?", ["To tell the two copies of the table apart", "For speed", "They aren't", "To rename columns"], 0),
            mcq("Why LEFT JOIN for managers?", ["So employees without a manager still appear", "It's faster", "To remove duplicates", "It's required"], 0),
            fill("Join employees to their managers.", "FROM employees e LEFT JOIN employees m ON e.manager_id = ___.id", "m"),
            mcq("Which employees match m.name IS NULL after that LEFT JOIN?", ["Those with no manager", "Managers", "Nobody", "Everyone"], 0),
            run("List each employee and their manager's name ('none' if no manager), ordered by employee id.", "sql", [t("Run")],
                ["Ada|none\nBo|Ada\nCy|Ada\nDi|Ada\nEve|Di\nFinn|Di\nGia|Ada"],
                "SELECT e.name, COALESCE(m.name, 'none')\nFROM employees e\nLEFT JOIN employees m ON e.manager_id = m.id\nORDER BY e.id;",
                setup=STAFF, require=[r"(?i)JOIN\s+employees"]),
        ),
        lesson(
            "UNION, INTERSECT, EXCEPT",
            "Set operators combine the results of two queries with the same columns:\n\nA UNION B       -- rows in either (duplicates removed)\nA UNION ALL B   -- keep duplicates (faster)\nA INTERSECT B   -- rows in both\nA EXCEPT B      -- rows in A but not B\n\nSELECT name FROM customers\nEXCEPT\nSELECT c.name FROM customers c JOIN orders o ON o.customer_id = c.id;   -- never ordered",
            mcq("What's the difference between UNION and UNION ALL?", ["UNION removes duplicates", "UNION ALL removes duplicates", "None", "UNION ALL sorts"], 0),
            mcq("What must both sides of a UNION have?", ["The same number of compatible columns", "The same table", "A WHERE clause", "An ORDER BY"], 0),
            fill("Rows in the first query but not the second.", "SELECT id FROM a ___ SELECT id FROM b;", "EXCEPT"),
            mcq("Where does ORDER BY go in a UNION?", ["Once, at the very end", "On each side", "Not allowed", "At the start"], 0),
            run("List the names of customers who have never placed an order, using EXCEPT. Order by name.", "sql", [t("Run")], ["Tim"],
                "SELECT name FROM customers\nEXCEPT\nSELECT c.name FROM customers c JOIN orders o ON o.customer_id = c.id\nORDER BY name;",
                setup=SHOP, require=[r"(?i)\bEXCEPT\b"]),
        ),
        lesson(
            "Joining many tables",
            "Real questions often need three or four tables:\n\nSELECT c.name, p.name, oi.qty\nFROM customers c\nJOIN orders o       ON o.customer_id = c.id\nJOIN order_items oi ON oi.order_id = o.id\nJOIN products p     ON p.id = oi.product_id;\n\nFollow the foreign keys step by step, then aggregate.",
            mcq("How many JOINs connect customers to products here?", ["3", "1", "2", "4"], 0),
            order("Order the joins from customers to products.", ["FROM customers c", "JOIN orders o ON o.customer_id = c.id", "JOIN order_items oi ON oi.order_id = o.id", "JOIN products p ON p.id = oi.product_id"]),
            mcq("What happens to customers without orders in an INNER JOIN chain?", ["They disappear from the result", "They show NULLs", "An error", "They appear once"], 0),
            fill("Total spend per customer.", "SUM(oi.qty * p.___)", "price"),
            run("For each category, show the total revenue (qty × price) across all orders, highest first, as category|revenue.", "sql", [t("Run")],
                ["Hardware|305.5\nSoftware|150"],
                "SELECT p.category, SUM(oi.qty * p.price) AS revenue\nFROM order_items oi\nJOIN products p ON p.id = oi.product_id\nGROUP BY p.category\nORDER BY revenue DESC;",
                setup=SHOP, require=[r"(?i)JOIN", r"(?i)GROUP\s+BY"]),
        ),
    ),
    # ------------------------------------------------------------------ 11
    unit(
        "Unit 11 · Subqueries & CTEs",
        lesson(
            "Correlated subqueries",
            "A correlated subquery refers to the outer row, so it runs per row:\n\nSELECT name, dept, salary\nFROM employees e\nWHERE salary > (SELECT AVG(salary) FROM employees WHERE dept = e.dept);\n\n'Who earns more than their department's average?'",
            mcq("What makes a subquery 'correlated'?", ["It references a column from the outer query", "It uses JOIN", "It returns many rows", "It's in SELECT"], 0),
            mcq("How often does a correlated subquery conceptually run?", ["Once per outer row", "Once", "Never", "Twice"], 0),
            fill("Compare with the same department.", "WHERE dept = ___.dept", "e"),
            mcq("Which can often replace a correlated subquery?", ["A JOIN with a grouped subquery, or a window function", "UNION", "DISTINCT", "LIMIT"], 0),
            run("List the name and dept of employees who earn more than their department's average salary, ordered by name.", "sql", [t("Run")],
                ["Ada|Engineering\nDi|Sales\nEve|Sales"],
                "SELECT name, dept\nFROM employees e\nWHERE salary > (SELECT AVG(salary) FROM employees WHERE dept = e.dept)\nORDER BY name;",
                setup=STAFF, require=[r"(?i)\(\s*SELECT"]),
        ),
        lesson(
            "EXISTS & NOT EXISTS",
            "EXISTS checks whether a subquery returns ANY row:\n\nSELECT name FROM customers c\nWHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);\n\nNOT EXISTS is the safe way to find 'missing' rows - NOT IN behaves surprisingly if the subquery contains a NULL.",
            mcq("What does EXISTS care about?", ["Whether any row is returned", "The values returned", "The row count", "Column names"], 0),
            mcq("Why can NOT IN (subquery) return no rows unexpectedly?", ["If the subquery yields a NULL, every comparison is unknown", "It's slow", "It's not SQL", "It sorts"], 0),
            fill("Customers without orders.", "WHERE ___ EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)", "NOT"),
            mcq("What's conventional to SELECT inside EXISTS?", ["1 (any value works)", "*only", "COUNT(*)", "NULL is required"], 0),
            run("List the names of products that have never been ordered, using NOT EXISTS. Order by name.", "sql", [t("Run")], ["Antivirus\nWebcam"],
                "SELECT name FROM products p\nWHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.id)\nORDER BY name;",
                setup=SHOP + "\nINSERT INTO products VALUES (6, 'Webcam', 'Hardware', 35.0), (7, 'Antivirus', 'Software', 25.0);",
                require=[r"(?i)NOT\s+EXISTS"]),
        ),
        lesson(
            "Common table expressions",
            "WITH names a subquery so the main query reads top to bottom:\n\nWITH dept_avg AS (\n  SELECT dept, AVG(salary) AS avg_salary\n  FROM employees\n  GROUP BY dept\n)\nSELECT e.name, e.salary, d.avg_salary\nFROM employees e JOIN dept_avg d ON d.dept = e.dept;\n\nYou can chain several: WITH a AS (...), b AS (SELECT ... FROM a) SELECT ...",
            mcq("What does WITH ... AS (...) define?", ["A named temporary result for this query", "A permanent table", "A view", "An index"], 0),
            fill("Separate two CTEs.", "WITH a AS (...)___ b AS (...) SELECT ...", ","),
            mcq("Can a later CTE use an earlier one?", ["Yes", "No", "Only with UNION", "Only in views"], 0),
            mcq("Main benefit of CTEs?", ["Readability - name each step", "They're always faster", "They create indexes", "They store data"], 0),
            run("Using a CTE that computes each customer's total spend, list customers whose total is above 100, as name|total ordered by total descending.", "sql", [t("Run")],
                ["Ada|406.5"],
                "WITH spend AS (\n  SELECT o.customer_id, SUM(oi.qty * p.price) AS total\n  FROM orders o\n  JOIN order_items oi ON oi.order_id = o.id\n  JOIN products p ON p.id = oi.product_id\n  GROUP BY o.customer_id\n)\nSELECT c.name, s.total\nFROM spend s JOIN customers c ON c.id = s.customer_id\nWHERE s.total > 100\nORDER BY s.total DESC;",
                setup=SHOP, require=[r"(?i)\bWITH\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 12
    unit(
        "Unit 12 · Window functions",
        lesson(
            "ROW_NUMBER, RANK, DENSE_RANK",
            "Window functions compute over a set of rows WITHOUT collapsing them like GROUP BY:\n\nSELECT name, dept, salary,\n  RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk\nFROM employees;\n\nROW_NUMBER: 1,2,3,4   RANK: 1,2,2,4   DENSE_RANK: 1,2,2,3\nPARTITION BY restarts the numbering per group.",
            mcq("Ties at 2nd place - what does RANK give the next row?", ["4", "3", "2", "1"], 0),
            mcq("What does PARTITION BY dept do?", ["Restarts the window for each department", "Filters departments", "Sorts output", "Groups and collapses rows"], 0),
            fill("Window clause.", "ROW_NUMBER() ___ (ORDER BY salary DESC)", "OVER"),
            mcq("Can you filter on a window function in WHERE directly?", ["No - wrap it in a subquery/CTE", "Yes", "Only RANK", "Only with HAVING"], 0),
            run("Show the top earner in each department (ties included), as dept|name|salary ordered by dept then name. Use RANK() in a CTE.", "sql", [t("Run")],
                ["Engineering|Ada|9000\nSales|Di|6000\nSupport|Gia|4200"],
                "WITH ranked AS (\n  SELECT dept, name, salary,\n    RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk\n  FROM employees\n)\nSELECT dept, name, salary FROM ranked WHERE rnk = 1 ORDER BY dept, name;",
                setup=STAFF, require=[r"(?i)\bOVER\s*\("]),
        ),
        lesson(
            "Running totals",
            "Aggregates become window functions with OVER:\n\nSELECT month, amount,\n  SUM(amount) OVER (ORDER BY month) AS running_total,\n  AVG(amount) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg\nFROM monthly;\n\nThe frame clause (ROWS BETWEEN …) chooses which rows feed each calculation.",
            mcq("What does SUM(x) OVER (ORDER BY d) compute?", ["A running total", "The grand total on every row", "One row", "A count"], 0),
            mcq("What does SUM(x) OVER () (empty window) give?", ["The grand total on every row", "A running total", "Zero", "An error"], 0),
            fill("A 3-row moving window.", "ROWS BETWEEN 2 ___ AND CURRENT ROW", "PRECEDING"),
            mcq("Do window functions reduce the number of rows?", ["No", "Yes", "Only with PARTITION", "Only SUM"], 0),
            run("For rep 'Ada', show month, amount and the running total of her sales ordered by month.", "sql", [t("Run")],
                ["2026-01|120|120\n2026-02|80|200\n2026-03|160|360"],
                "SELECT month, amount, SUM(amount) OVER (ORDER BY month) AS running\nFROM sales\nWHERE rep = 'Ada'\nORDER BY month;",
                setup=SALES, require=[r"(?i)SUM\s*\([^)]*\)\s*OVER"]),
        ),
        lesson(
            "LAG & LEAD",
            "LAG reads a value from a previous row in the window; LEAD from a following one:\n\nSELECT month, amount,\n  amount - LAG(amount) OVER (ORDER BY month) AS change\nFROM monthly;\n\nLAG(x, 1, 0) supplies a default instead of NULL for the first row. Great for month-over-month change.",
            mcq("What does LAG(amount) return on the first row?", ["NULL (unless a default is given)", "0", "The same row", "An error"], 0),
            fill("The next row's value.", "___(amount) OVER (ORDER BY month)", "LEAD"),
            mcq("What's LAG(x, 2) ?", ["The value two rows back", "x squared", "Two rows ahead", "The 2nd row"], 0),
            mcq("How do you compute changes per rep separately?", ["PARTITION BY rep inside OVER", "GROUP BY rep", "WHERE rep", "ORDER BY rep only"], 0),
            run("For each rep with sales in every month, show rep, month and the change from their previous month (NULL for their first month), ordered by rep then month. Exclude Di.", "sql", [t("Run")],
                ["Ada|2026-01|NULL\nAda|2026-02|-40\nAda|2026-03|80\nBo|2026-01|NULL\nBo|2026-02|40\nBo|2026-03|-30\nCy|2026-01|NULL\nCy|2026-02|-40\nCy|2026-03|40"],
                "SELECT rep, month,\n  amount - LAG(amount) OVER (PARTITION BY rep ORDER BY month) AS change\nFROM sales\nWHERE rep <> 'Di'\nORDER BY rep, month;",
                setup=SALES, require=[r"(?i)\bLAG\s*\(", r"(?i)PARTITION\s+BY"]),
        ),
    ),
)

ADVANCED = section(
    "Advanced",
    # ------------------------------------------------------------------ 13
    unit(
        "Unit 13 · Schema design",
        lesson(
            "Normalization",
            "Normalization removes duplicated data so it can't get out of sync:\n\n1NF - one value per cell (no 'tags: a,b,c' lists)\n2NF - every column depends on the whole key\n3NF - no column depends on another non-key column (store city once in a cities table, not on every row)\n\nOne-to-many: a foreign key on the 'many' side. Many-to-many: a junction table (student_courses).",
            mcq("How do you model students ↔ courses (many-to-many)?", ["A junction table with both foreign keys", "A course list column", "Two foreign keys on students", "One big table"], 0),
            mcq("A 'tags' column holding 'sql,db,web' violates…", ["1NF", "3NF only", "Nothing", "Foreign keys"], 0),
            fill("The 'many' side holds the…", "___ key", "foreign"),
            mcq("Why might you denormalize on purpose?", ["For read performance in reporting", "To fix bugs", "It's always better", "To save keys"], 0),
            run("Create tables students(id, name), courses(id, title) and a junction table enrollments(student_id, course_id) with a composite PRIMARY KEY. The check inserts data and lists who takes 'SQL'.", "sql",
                [t("schema", append="INSERT INTO students VALUES (1, 'Ada'), (2, 'Bo'), (3, 'Cy'); INSERT INTO courses VALUES (1, 'SQL'), (2, 'Art'); INSERT INTO enrollments VALUES (1, 1), (2, 2), (3, 1); SELECT s.name FROM students s JOIN enrollments e ON e.student_id = s.id JOIN courses c ON c.id = e.course_id WHERE c.title = 'SQL' ORDER BY s.name;"),
                 t("no duplicates", append="INSERT INTO enrollments VALUES (1, 1); INSERT OR IGNORE INTO enrollments VALUES (1, 1); SELECT COUNT(*) FROM enrollments;")],
                ["Ada\nCy", "1"],
                "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL);\nCREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL);\nCREATE TABLE enrollments (\n  student_id INTEGER REFERENCES students(id),\n  course_id INTEGER REFERENCES courses(id),\n  PRIMARY KEY (student_id, course_id)\n);",
                require=[r"(?i)PRIMARY\s+KEY\s*\(\s*\w+\s*,\s*\w+\s*\)"], hint="PRIMARY KEY (student_id, course_id) at the end of the column list."),
        ),
        lesson(
            "Constraints",
            "Constraints make the database reject bad data:\n\nNOT NULL       - value required\nUNIQUE         - no duplicates (e.g. email)\nCHECK (expr)   - custom rule: CHECK (price >= 0)\nDEFAULT value  - used when omitted\nREFERENCES t(id) ON DELETE CASCADE - linked rows\n\nIn SQLite, foreign keys are enforced after PRAGMA foreign_keys = ON;",
            mcq("Which constraint stops two users sharing an email?", ["UNIQUE", "CHECK", "DEFAULT", "NOT NULL"], 0),
            fill("Reject negative prices.", "price REAL ___ (price >= 0)", "CHECK"),
            mcq("What does ON DELETE CASCADE do?", ["Deletes referencing rows when the parent is deleted", "Blocks deletes", "Sets NULL", "Copies rows"], 0),
            mcq("Why put rules in constraints rather than only app code?", ["Every client and bug is stopped at the database", "Speed", "Style", "Required by SQL"], 0),
            run("Create table users(id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, age INTEGER CHECK (age >= 13), role TEXT DEFAULT 'member'). The checks try invalid inserts and count rows.", "sql",
                [t("valid row", append="INSERT INTO users (email, age) VALUES ('a@x.io', 20); SELECT email, age, role FROM users;"),
                 t("rejects bad data", append="INSERT OR IGNORE INTO users (email, age) VALUES ('a@x.io', 20); INSERT OR IGNORE INTO users (email, age) VALUES ('a@x.io', 30); INSERT OR IGNORE INTO users (email, age) VALUES ('k@x.io', 9); INSERT OR IGNORE INTO users (email, age) VALUES (NULL, 40); SELECT COUNT(*) FROM users;")],
                ["a@x.io|20|member", "1"],
                "CREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  email TEXT NOT NULL UNIQUE,\n  age INTEGER CHECK (age >= 13),\n  role TEXT DEFAULT 'member'\n);",
                require=[r"(?i)\bUNIQUE\b", r"(?i)\bCHECK\s*\("]),
        ),
        lesson(
            "ALTER & migrations",
            "Schemas evolve. ALTER TABLE changes an existing table:\n\nALTER TABLE users ADD COLUMN last_login TEXT;\nALTER TABLE users RENAME COLUMN name TO full_name;\nALTER TABLE users RENAME TO accounts;\n\nIn real projects every change is a numbered migration file checked into version control (Alembic, Flyway, Rails migrations…) so every environment ends up with the same schema.",
            mcq("What's a migration?", ["A versioned, repeatable schema change", "Copying a database", "A backup", "A query plan"], 0),
            fill("Add a column.", "ALTER TABLE users ___ COLUMN bio TEXT;", "ADD"),
            mcq("Why keep migrations in version control?", ["Every environment can apply the same changes in order", "To slow deploys", "It's required by SQL", "To store data"], 0),
            mcq("What value do existing rows get for a newly added column with no default?", ["NULL", "0", "''", "An error"], 0),
            run("The books table exists. Add a column rating INTEGER with default 0, then set rating = 5 for 'Dune', then select title and rating ordered by id.", "sql", [t("Run")],
                ["Dune|5\nNeuromancer|0\nHyperion|0\nFoundation|0"],
                "ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT 0;\nUPDATE books SET rating = 5 WHERE title = 'Dune';\nSELECT title, rating FROM books ORDER BY id;",
                setup="CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author TEXT, year INTEGER, copies INTEGER);\nINSERT INTO books VALUES (1, 'Dune', 'Herbert', 1965, 3), (2, 'Neuromancer', 'Gibson', 1984, 1), (3, 'Hyperion', 'Simmons', 1989, 0), (4, 'Foundation', 'Asimov', 1951, 2);",
                require=[r"(?i)ALTER\s+TABLE"]),
        ),
    ),
    # ------------------------------------------------------------------ 14
    unit(
        "Unit 14 · Indexes, views & performance",
        lesson(
            "Indexes",
            "An index is a sorted lookup structure (usually a B-tree) that makes WHERE, JOIN and ORDER BY on its columns fast:\n\nCREATE INDEX idx_employees_dept ON employees(dept);\nCREATE UNIQUE INDEX idx_users_email ON users(email);\nCREATE INDEX idx_sales_rep_month ON sales(rep, month);   -- composite\n\nTrade-off: faster reads, slower writes and more storage. EXPLAIN QUERY PLAN shows whether an index is used.",
            mcq("What's the cost of an index?", ["Slower writes and extra storage", "Slower reads", "Nothing", "Data loss"], 0),
            mcq("A composite index on (rep, month) helps WHERE…", ["rep = ? (and rep = ? AND month = ?)", "month = ? alone, best", "Only ORDER BY", "Nothing"], 0),
            fill("Create an index.", "CREATE ___ idx_name ON users(name);", "INDEX"),
            mcq("Which columns are good index candidates?", ["Frequently filtered or joined columns", "Every column", "Rarely used columns", "Boolean columns only"], 0),
            run("Create an index named idx_sales_rep_month on sales(rep, month). The check lists the indexed columns from SQLite's catalog.", "sql",
                [t("index", append="SELECT name FROM pragma_index_info('idx_sales_rep_month') ORDER BY seqno;")], ["rep\nmonth"],
                "CREATE INDEX idx_sales_rep_month ON sales(rep, month);", setup=SALES, require=[r"(?i)CREATE\s+INDEX"]),
        ),
        lesson(
            "Views",
            "A view is a saved query you can SELECT from like a table:\n\nCREATE VIEW dept_stats AS\nSELECT dept, COUNT(*) AS staff, AVG(salary) AS avg_salary\nFROM employees GROUP BY dept;\n\nSELECT * FROM dept_stats WHERE staff > 1;\n\nViews simplify complex queries and can hide sensitive columns from some users. Ordinary views store no data; they run the query each time.",
            mcq("Does an ordinary view store its rows?", ["No - it runs its query when used", "Yes", "Only the first time", "Only indexes"], 0),
            fill("Create a view.", "CREATE ___ active_users AS SELECT * FROM users WHERE active = 1;", "VIEW"),
            mcq("How can a view help security?", ["Expose only some columns or rows", "Encrypts data", "Blocks SQL injection", "It can't"], 0),
            mcq("What is a materialized view?", ["A view whose results are stored and refreshed", "A view with JOINs", "A temp table", "An index"], 0),
            run("Create a view rep_totals(rep, total) summing sales per rep. The check queries the view.", "sql",
                [t("view", append="SELECT rep, total FROM rep_totals ORDER BY total DESC, rep;")], ["Cy|410\nAda|360\nBo|320\nDi|70"],
                "CREATE VIEW rep_totals AS\nSELECT rep, SUM(amount) AS total FROM sales GROUP BY rep;", setup=SALES, require=[r"(?i)CREATE\s+VIEW"]),
        ),
        lesson(
            "SQL injection & parameters",
            "Never build SQL by gluing user input into a string:\n\n# DANGEROUS\nquery = \"SELECT * FROM users WHERE name = '\" + name + \"'\"\n# name = \"x' OR '1'='1\" → returns every user!\n\nUse parameters (placeholders) - the driver sends data separately from code:\ncursor.execute(\"SELECT * FROM users WHERE name = ?\", (name,))\n\nAlso: least-privilege database accounts, and ORMs that parameterize for you.",
            mcq("What prevents SQL injection?", ["Parameterized queries", "Escaping quotes by hand only", "Using SELECT *", "Upper-case keywords"], 0),
            mcq("What does name = x' OR '1'='1 do to a string-built query?", ["Makes the WHERE always true", "Nothing", "Causes a syntax error always", "Deletes the table"], 0),
            fill("Placeholder in many drivers.", "SELECT * FROM users WHERE id = ___", "?"),
            mcq("Why give the app's DB user minimal privileges?", ["Limits damage if something goes wrong", "Speed", "It's required", "To allow injection"], 0),
            code("Write the parameterized Python call that selects users by email (use cursor.execute with a ? placeholder and a one-item tuple called (email,)).",
                 [r"cursor\.execute\(\s*[\"']SELECT\s+\*\s+FROM\s+users\s+WHERE\s+email\s*=\s*\?[\"']\s*,\s*\(\s*email\s*,\s*\)\s*\)"],
                 'cursor.execute("SELECT * FROM users WHERE email = ?", (email,))', hint='cursor.execute("... = ?", (email,))'),
        ),
    ),
    # ------------------------------------------------------------------ 15
    unit(
        "Unit 15 · Transactions & triggers",
        lesson(
            "Transactions",
            "A transaction groups statements so they ALL happen or NONE do:\n\nBEGIN;\nUPDATE accounts SET balance = balance - 30 WHERE owner = 'ada';\nUPDATE accounts SET balance = balance + 30 WHERE owner = 'bo';\nCOMMIT;      -- or ROLLBACK; to undo everything since BEGIN\n\nACID: Atomic, Consistent, Isolated, Durable.",
            mcq("What does ROLLBACK do?", ["Undoes everything since BEGIN", "Saves changes", "Deletes the table", "Restarts the DB"], 0),
            mcq("What does the A in ACID stand for?", ["Atomic", "Available", "Accurate", "Async"], 0),
            fill("Make the changes permanent.", "___;", "COMMIT"),
            mcq("Why use a transaction for a money transfer?", ["So money is never removed without being added", "Speed", "To lock the DB forever", "To log queries"], 0),
            run("Transfer 30 from ada to bo inside a transaction, then (in a second transaction) try to move 500 from bo to ada but ROLLBACK it. Finally select owner and balance ordered by id.", "sql", [t("Run")],
                ["ada|70\nbo|80"],
                "BEGIN;\nUPDATE accounts SET balance = balance - 30 WHERE owner = 'ada';\nUPDATE accounts SET balance = balance + 30 WHERE owner = 'bo';\nCOMMIT;\n\nBEGIN;\nUPDATE accounts SET balance = balance + 500 WHERE owner = 'ada';\nROLLBACK;\n\nSELECT owner, balance FROM accounts ORDER BY id;",
                setup=ACCOUNTS, require=[r"(?i)\bBEGIN\b", r"(?i)\bCOMMIT\b", r"(?i)\bROLLBACK\b"]),
        ),
        lesson(
            "UPSERT & RETURNING",
            "Insert, or update if the row already exists:\n\nINSERT INTO stock (sku, qty) VALUES ('pen', 5)\nON CONFLICT (sku) DO UPDATE SET qty = qty + excluded.qty;\n\nexcluded refers to the row you tried to insert. Needs a UNIQUE or PRIMARY KEY on the conflict column.\n\nRETURNING gives back the affected rows: INSERT ... RETURNING id;",
            mcq("What does excluded.qty refer to?", ["The value from the attempted insert", "The old value", "A deleted row", "NULL"], 0),
            mcq("What must exist for ON CONFLICT (sku)?", ["A UNIQUE/PRIMARY KEY constraint on sku", "An index named sku", "A trigger", "Nothing"], 0),
            fill("Skip duplicates silently.", "INSERT INTO t VALUES (1) ON CONFLICT DO ___;", "NOTHING"),
            mcq("What does RETURNING do?", ["Returns the inserted/updated rows", "Rolls back", "Returns the row count", "Returns the schema"], 0),
            run("Table stock(sku PRIMARY KEY, qty) exists. Write ONE upsert statement that adds ('pen', 5), ('ink', 2), ('pen', 3) - adding qty to existing rows. Then select sku and qty ordered by sku.", "sql", [t("Run")],
                ["ink|2\npaper|10\npen|9"],
                "INSERT INTO stock (sku, qty) VALUES ('pen', 5), ('ink', 2), ('pen', 3)\nON CONFLICT (sku) DO UPDATE SET qty = qty + excluded.qty;\nSELECT sku, qty FROM stock ORDER BY sku;",
                setup="CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER);\nINSERT INTO stock VALUES ('pen', 1), ('paper', 10);",
                require=[r"(?i)ON\s+CONFLICT", r"(?i)excluded\."]),
        ),
        lesson(
            "Triggers",
            "A trigger runs SQL automatically when rows change:\n\nCREATE TRIGGER log_salary AFTER UPDATE OF salary ON employees\nBEGIN\n  INSERT INTO audit (emp_id, old_salary, new_salary)\n  VALUES (OLD.id, OLD.salary, NEW.salary);\nEND;\n\nOLD = the row before, NEW = after. Use triggers sparingly - hidden logic is hard to debug.",
            mcq("In an UPDATE trigger, what is NEW?", ["The row after the change", "The row before", "A new table", "The next row"], 0),
            fill("Value before the update.", "___.salary", "OLD"),
            mcq("A good use of triggers?", ["Audit logs", "All business logic", "Sending emails", "Replacing transactions"], 0),
            mcq("When does an AFTER INSERT trigger run?", ["After each inserted row", "Before the insert", "Once a day", "On SELECT"], 0),
            run("Create a table audit(emp_id, old_salary, new_salary) and an AFTER UPDATE OF salary trigger on employees that logs changes. The check gives raises and reads the audit table.", "sql",
                [t("audit", append="UPDATE employees SET salary = salary + 500 WHERE dept = 'Support'; UPDATE employees SET name = 'Bobby' WHERE id = 2; UPDATE employees SET salary = 7500 WHERE id = 2; SELECT emp_id, old_salary, new_salary FROM audit ORDER BY emp_id;")],
                ["2|7000|7500\n7|4200|4700"],
                "CREATE TABLE audit (emp_id INTEGER, old_salary INTEGER, new_salary INTEGER);\nCREATE TRIGGER log_salary AFTER UPDATE OF salary ON employees\nBEGIN\n  INSERT INTO audit (emp_id, old_salary, new_salary) VALUES (OLD.id, OLD.salary, NEW.salary);\nEND;",
                setup=STAFF, require=[r"(?i)CREATE\s+TRIGGER"]),
        ),
    ),
    # ------------------------------------------------------------------ 16
    unit(
        "Unit 16 · Advanced querying",
        lesson(
            "Recursive CTEs",
            "WITH RECURSIVE walks hierarchies and generates sequences:\n\nWITH RECURSIVE tree(id, name, depth) AS (\n  SELECT id, name, 0 FROM categories WHERE parent_id IS NULL     -- anchor\n  UNION ALL\n  SELECT c.id, c.name, t.depth + 1\n  FROM categories c JOIN tree t ON c.parent_id = t.id            -- recursive step\n)\nSELECT * FROM tree;\n\nIt stops when the recursive step returns no new rows.",
            mcq("What are the two parts of a recursive CTE?", ["An anchor query and a recursive query joined by UNION ALL", "Two JOINs", "A SELECT and a WHERE", "A view and a table"], 0),
            fill("Generate numbers 1..5.", "WITH ___ n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 5) SELECT x FROM n;", "RECURSIVE"),
            mcq("When does recursion stop?", ["When the recursive part adds no rows", "After 10 levels", "Never", "At the first NULL"], 0),
            mcq("Typical use of recursive CTEs?", ["Org charts and category trees", "Indexes", "Transactions", "Triggers"], 0),
            run("List every category under 'Tech' (not Tech itself) with its depth below Tech (children = 1), ordered by depth then name.", "sql", [t("Run")],
                ["Laptops|1\nPhones|1\nGaming laptops|2"],
                "WITH RECURSIVE sub(id, name, depth) AS (\n  SELECT id, name, 0 FROM categories WHERE name = 'Tech'\n  UNION ALL\n  SELECT c.id, c.name, s.depth + 1 FROM categories c JOIN sub s ON c.parent_id = s.id\n)\nSELECT name, depth FROM sub WHERE depth > 0 ORDER BY depth, name;",
                setup=CATEGORIES, require=[r"(?i)WITH\s+RECURSIVE"]),
        ),
        lesson(
            "Pivoting",
            "Turn rows into columns with conditional aggregation:\n\nSELECT rep,\n  SUM(CASE WHEN month = '2026-01' THEN amount ELSE 0 END) AS jan,\n  SUM(CASE WHEN month = '2026-02' THEN amount ELSE 0 END) AS feb\nFROM sales\nGROUP BY rep;\n\nSome databases have a PIVOT keyword; this pattern works everywhere. FILTER (WHERE ...) is a shorter form: SUM(amount) FILTER (WHERE month = '2026-01').",
            mcq("What is pivoting?", ["Turning row values into columns", "Sorting", "Joining", "Deleting duplicates"], 0),
            fill("Conditional sum.", "SUM(___ WHEN region = 'North' THEN amount ELSE 0 END)", "CASE"),
            mcq("Why ELSE 0 rather than leaving it out?", ["So missing months show 0 instead of NULL", "Required syntax", "Speed", "No reason"], 0),
            mcq("What groups the pivot rows?", ["GROUP BY the row label", "ORDER BY", "PARTITION BY", "HAVING"], 0),
            run("Pivot sales into rep|jan|feb|mar totals (0 when none), ordered by rep.", "sql", [t("Run")],
                ["Ada|120|80|160\nBo|90|130|100\nCy|150|110|150\nDi|0|0|70"],
                "SELECT rep,\n  SUM(CASE WHEN month = '2026-01' THEN amount ELSE 0 END),\n  SUM(CASE WHEN month = '2026-02' THEN amount ELSE 0 END),\n  SUM(CASE WHEN month = '2026-03' THEN amount ELSE 0 END)\nFROM sales\nGROUP BY rep\nORDER BY rep;",
                setup=SALES, require=[r"(?i)CASE|FILTER"]),
        ),
        lesson(
            "JSON in SQL",
            "Modern databases can query JSON stored in columns:\n\nSELECT json_extract(payload, '$.user') FROM events;          -- SQLite\nSELECT payload->>'user' FROM events;                          -- PostgreSQL / SQLite 3.38+\nSELECT value FROM events, json_each(payload, '$.items');     -- expand arrays\n\nGreat for flexible data, but keep core fields in real columns so they can be indexed and constrained.",
            mcq("What does json_extract(payload, '$.ms') return?", ["The ms field's value", "The whole JSON", "A boolean", "A table"], 0),
            fill("Expand a JSON array into rows (SQLite).", "FROM events, json____(payload, '$.items')", "each"),
            mcq("Why keep key fields as real columns too?", ["Indexing and constraints work best on columns", "JSON can't be read", "It's required", "To save space"], 0),
            mcq("In JSON paths, what does $ mean?", ["The root of the document", "A variable", "Money", "The last element"], 0),
            run("For each user, show the number of purchase items they bought (expand $.items with json_each over purchase events), as user|items ordered by user.", "sql", [t("Run")],
                ["ada|1\nbo|2"],
                "SELECT json_extract(e.payload, '$.user') AS user, COUNT(*)\nFROM events e, json_each(e.payload, '$.items')\nWHERE json_extract(e.payload, '$.type') = 'purchase'\nGROUP BY user\nORDER BY user;",
                setup=EVENTS, require=[r"(?i)json_each|json_array_length"]),
        ),
    ),
)
