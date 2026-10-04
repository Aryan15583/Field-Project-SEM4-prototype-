from .dsl import code, course, fill, lesson, mcq, order, run, t, unit
from .sql_adv import ADVANCED, INTERMEDIATE
from .sql_expert import EXPERT
from .sql_expert2 import EXPERT2

# Output of a query = its rows, one per line, columns joined by "|" (NULL shown as NULL).

STUDENTS = """CREATE TABLE students (
  id INTEGER PRIMARY KEY,
  name TEXT,
  age INTEGER,
  city TEXT,
  score INTEGER
);
INSERT INTO students VALUES
  (1, 'Ada', 17, 'London', 91),
  (2, 'Bo', 15, 'Oslo', 78),
  (3, 'Cy', 16, 'London', 85),
  (4, 'Di', 18, 'Paris', 62),
  (5, 'Eve', 15, NULL, 95),
  (6, 'Finn', 17, 'Oslo', 70),
  (7, 'Gia', 16, 'Paris', 88),
  (8, 'Hal', 18, 'London', 55);"""

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

BOOKS = """CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author TEXT, year INTEGER, copies INTEGER);
INSERT INTO books VALUES
  (1, 'Dune', 'Herbert', 1965, 3),
  (2, 'Neuromancer', 'Gibson', 1984, 1),
  (3, 'Hyperion', 'Simmons', 1989, 0),
  (4, 'Foundation', 'Asimov', 1951, 2);"""


COURSE = course(
    "sql", "SQL", "🗄️", "Ask databases questions and get answers - the language of data.",
    # ------------------------------------------------------------------ 1
    unit(
        "Unit 1 · Querying data",
        lesson(
            "SELECT",
            "A database stores data in tables (rows and columns). SELECT asks for columns FROM a table:\n\nSELECT name, age FROM students;\nSELECT * FROM students;     -- * means every column\n\nSQL keywords aren't case-sensitive, but writing them in CAPITALS is the convention. End statements with ;",
            fill("Get every column from users.", "SELECT ___ FROM users;", "*"),
            mcq("Which keyword names the table?", ["FROM", "WHERE", "INTO", "TABLE"], 0),
            mcq("What does SELECT name FROM students; return?", ["The name column of every row", "One name", "The number of students", "The whole table"], 0),
            order("Order the query.", ["SELECT name, city", "FROM students;"]),
            run("Select the name and age of every student.", "sql", [t("Run")],
                ["Ada|17\nBo|15\nCy|16\nDi|18\nEve|15\nFinn|17\nGia|16\nHal|18"], "SELECT name, age FROM students;", setup=STUDENTS,
                hint="SELECT column1, column2 FROM table;"),
        ),
        lesson(
            "Aliases & expressions",
            "You can compute new columns and rename them with AS:\n\nSELECT name, score + 5 AS curved FROM students;\nSELECT name || ' from ' || city AS intro FROM students;\n\n|| joins text in SQLite (and standard SQL).",
            mcq("What does AS do?", ["Gives a column a new name in the result", "Filters rows", "Sorts rows", "Creates a table"], 0),
            fill("Rename the computed column to total.", "SELECT price * qty ___ total FROM items;", "AS"),
            mcq("What does SELECT 2 + 3; return?", ["5", "2 + 3", "An error", "23"], 0, "SELECT can compute values without a table."),
            mcq("Which operator joins two strings in SQLite?", ["||", "+", "&", "CONCAT only"], 0),
            run("For every student, select the name and their score out of 10 (score / 10.0) as a column named out_of_10.", "sql", [t("Run")],
                ["Ada|9.1\nBo|7.8\nCy|8.5\nDi|6.2\nEve|9.5\nFinn|7\nGia|8.8\nHal|5.5"], "SELECT name, score / 10.0 AS out_of_10 FROM students;",
                setup=STUDENTS, require=[r"(?i)\bAS\s+out_of_10"], hint="Divide by 10.0 (not 10) to keep the decimals."),
        ),
        lesson(
            "DISTINCT",
            "DISTINCT removes duplicate rows from the result:\n\nSELECT DISTINCT city FROM students;\n\nIt applies to the whole selected row: SELECT DISTINCT city, age … keeps each unique (city, age) pair.",
            mcq("What does DISTINCT do?", ["Removes duplicate result rows", "Sorts the rows", "Counts rows", "Removes NULLs"], 0),
            fill("List each age only once.", "SELECT ___ age FROM students;", "DISTINCT"),
            mcq("Where does DISTINCT go?", ["Right after SELECT", "After FROM", "At the end", "Before SELECT"], 0),
            mcq("If ages are 15, 15, 16, how many rows does SELECT DISTINCT age return?", ["2", "3", "1", "0"], 0),
            run("List every different city students come from, sorted alphabetically (NULLs sort first in SQLite).", "sql", [t("Run")],
                ["NULL\nLondon\nOslo\nParis"], "SELECT DISTINCT city FROM students ORDER BY city;", setup=STUDENTS, require=[r"(?i)DISTINCT"],
                hint="Add ORDER BY city at the end."),
        ),
    ),
    # ------------------------------------------------------------------ 2
    unit(
        "Unit 2 · Filtering rows",
        lesson(
            "WHERE",
            "WHERE keeps only rows that match a condition:\n\nSELECT name FROM students WHERE age >= 17;\nSELECT * FROM students WHERE city = 'Oslo';\n\nComparisons: =  <>  (or !=)  <  >  <=  >=\nText values go in 'single quotes'.",
            fill("Only rows where city is Paris.", "SELECT * FROM students ___ city = 'Paris';", ["WHERE", "where"]),
            mcq("Text values in SQL are written in…", ["single quotes", "double quotes", "no quotes", "brackets"], 0, "Standard SQL uses 'text'. Double quotes are for column names."),
            mcq("Which means 'not equal' in standard SQL?", ["<>", "=!", "!==", "~="], 0, "SQLite also accepts !=."),
            mcq("Which clause comes first?", ["FROM", "WHERE", "They can be in any order", "Neither"], 0),
            run("Select the names of students who scored 85 or more.", "sql", [t("Run")], ["Ada\nCy\nEve\nGia"],
                "SELECT name FROM students WHERE score >= 85;", setup=STUDENTS, require=[r"(?i)\bWHERE\b"]),
        ),
        lesson(
            "AND, OR, NOT",
            "Combine conditions:\n\nWHERE age >= 16 AND city = 'London'\nWHERE city = 'Oslo' OR city = 'Paris'\nWHERE NOT city = 'Oslo'\n\nAND is evaluated before OR - use parentheses to be clear:\nWHERE (city = 'Oslo' OR city = 'Paris') AND score > 70",
            mcq("Which combines two conditions that must BOTH be true?", ["AND", "OR", "NOT", "BOTH"], 0),
            fill("Rows from Oslo or Paris.", "WHERE city = 'Oslo' ___ city = 'Paris'", ["OR", "or"]),
            mcq("Which is evaluated first without parentheses?", ["AND", "OR", "Left to right", "NOT only"], 0),
            mcq("How many rows match age = 15 AND age = 16?", ["0", "All 15- and 16-year-olds", "1", "It's an error"], 0, "No single row can have two ages."),
            run("Select the name and score of students from London who scored above 60.", "sql", [t("Run")], ["Ada|91\nCy|85"],
                "SELECT name, score FROM students WHERE city = 'London' AND score > 60;", setup=STUDENTS, require=[r"(?i)\bAND\b"]),
        ),
        lesson(
            "IN, BETWEEN & LIKE",
            "Shortcuts for common filters:\n\nWHERE city IN ('Oslo', 'Paris')      -- any of a list\nWHERE age BETWEEN 15 AND 16          -- inclusive range\nWHERE name LIKE 'A%'                 -- starts with A\nWHERE name LIKE '%n'                 -- ends with n\nWHERE name LIKE '_o'                 -- 2 letters, second is o\n\n% matches any number of characters, _ exactly one.",
            mcq("Is BETWEEN 15 AND 16 inclusive?", ["Yes - it includes 15 and 16", "No", "Only 15", "Only 16"], 0),
            fill("Names that start with G.", "WHERE name LIKE '___'", "G%"),
            mcq("What does _ match in LIKE?", ["Exactly one character", "Any number of characters", "A space", "Nothing"], 0),
            mcq("Which is the same as city = 'Oslo' OR city = 'Paris'?", ["city IN ('Oslo', 'Paris')", "city BETWEEN 'Oslo' AND 'Paris'", "city LIKE 'Oslo%Paris'", "city = ('Oslo', 'Paris')"], 0),
            run("Select the names of students aged 16 to 17 (inclusive) whose name contains the letter i (any case is fine in SQLite LIKE).", "sql", [t("Run")],
                ["Finn\nGia"], "SELECT name FROM students WHERE age BETWEEN 16 AND 17 AND name LIKE '%i%';", setup=STUDENTS,
                require=[r"(?i)\bLIKE\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 3
    unit(
        "Unit 3 · Sorting & NULL",
        lesson(
            "ORDER BY",
            "ORDER BY sorts the result:\n\nSELECT name, score FROM students ORDER BY score;        -- ascending\nSELECT name, score FROM students ORDER BY score DESC;   -- descending\nSELECT * FROM students ORDER BY city, name;             -- by city, then name\n\nWithout ORDER BY, the row order isn't guaranteed.",
            fill("Sort from highest to lowest score.", "ORDER BY score ___", ["DESC", "desc"]),
            mcq("What's the default sort direction?", ["Ascending (ASC)", "Descending", "Random", "Insertion order"], 0),
            mcq("Where does ORDER BY go?", ["After WHERE, near the end", "Before FROM", "Before WHERE", "After SELECT"], 0),
            order("Order the clauses.", ["SELECT name", "FROM students", "WHERE age > 15", "ORDER BY name;"]),
            run("Select every student's name and score, highest score first.", "sql", [t("Run")],
                ["Eve|95\nAda|91\nGia|88\nCy|85\nBo|78\nFinn|70\nDi|62\nHal|55"], "SELECT name, score FROM students ORDER BY score DESC;",
                setup=STUDENTS, require=[r"(?i)ORDER\s+BY"]),
        ),
        lesson(
            "LIMIT & OFFSET",
            "LIMIT keeps only the first N rows; OFFSET skips some first:\n\nSELECT name FROM students ORDER BY score DESC LIMIT 3;          -- top 3\nSELECT name FROM students ORDER BY score DESC LIMIT 3 OFFSET 3; -- next 3 (page 2)\n\nAlways combine LIMIT with ORDER BY so 'first' means something.",
            mcq("What does LIMIT 1 do?", ["Keeps only the first row", "Removes one row", "Keeps the last row", "Limits columns to 1"], 0),
            fill("Skip the first 10 rows.", "LIMIT 10 ___ 10", ["OFFSET", "offset"]),
            mcq("Why pair LIMIT with ORDER BY?", ["Otherwise which rows you get isn't defined", "It's a syntax requirement", "For speed", "It isn't needed"], 0),
            mcq("With 8 rows, LIMIT 5 OFFSET 5 returns how many rows?", ["3", "5", "0", "8"], 0),
            run("Select the names of the 2nd and 3rd youngest students (sort by age, then name to break ties).", "sql", [t("Run")], ["Eve\nCy"],
                "SELECT name FROM students ORDER BY age, name LIMIT 2 OFFSET 1;", setup=STUDENTS, require=[r"(?i)\bLIMIT\b"]),
        ),
        lesson(
            "NULL",
            "NULL means 'unknown / missing'. It isn't equal to anything - not even NULL - so use IS:\n\nWHERE city IS NULL\nWHERE city IS NOT NULL\n\nWHERE city = NULL never matches! COALESCE picks the first non-NULL value:\nSELECT COALESCE(city, 'unknown') FROM students;",
            mcq("How do you find rows where city is missing?", ["WHERE city IS NULL", "WHERE city = NULL", "WHERE city == NULL", "WHERE NULL(city)"], 0),
            mcq("How many rows does WHERE city = NULL return?", ["Always 0", "The rows with NULL city", "All rows", "An error"], 0),
            fill("Show 'none' instead of NULL.", "SELECT ___(city, 'none') FROM students;", ["COALESCE", "coalesce", "IFNULL", "ifnull"]),
            mcq("What is NULL + 5?", ["NULL", "5", "0", "An error"], 0, "Arithmetic with NULL gives NULL."),
            run("Select every student's name and their city, showing 'Unknown' where the city is NULL, sorted by name.", "sql", [t("Run")],
                ["Ada|London\nBo|Oslo\nCy|London\nDi|Paris\nEve|Unknown\nFinn|Oslo\nGia|Paris\nHal|London"],
                "SELECT name, COALESCE(city, 'Unknown') FROM students ORDER BY name;", setup=STUDENTS, require=[r"(?i)COALESCE|IFNULL|CASE"]),
        ),
    ),
    # ------------------------------------------------------------------ 4
    unit(
        "Unit 4 · Aggregates",
        lesson(
            "COUNT, SUM & AVG",
            "Aggregate functions summarise many rows into one value:\n\nSELECT COUNT(*) FROM students;       -- number of rows\nSELECT COUNT(city) FROM students;    -- rows where city isn't NULL\nSELECT SUM(score), AVG(score) FROM students;\nSELECT ROUND(AVG(score), 1) FROM students;",
            mcq("What does COUNT(*) count?", ["All rows", "Non-NULL values in a column", "Distinct values", "Columns"], 0),
            mcq("Does COUNT(city) include rows where city is NULL?", ["No", "Yes", "Only if all are NULL", "It errors"], 0),
            fill("Average score.", "SELECT ___(score) FROM students;", ["AVG", "avg"]),
            mcq("What does ROUND(3.14159, 2) give?", ["3.14", "3.1", "3", "3.15"], 0),
            run("Select three values: the number of students, the total of all scores, and the average score rounded to 1 decimal.", "sql", [t("Run")],
                ["8|624|78"], "SELECT COUNT(*), SUM(score), ROUND(AVG(score), 1) FROM students;", setup=STUDENTS,
                require=[r"(?i)COUNT\(", r"(?i)SUM\(", r"(?i)AVG\("]),
        ),
        lesson(
            "MIN & MAX",
            "MIN and MAX find the smallest and largest values - they work on numbers, text and dates:\n\nSELECT MIN(age), MAX(age) FROM students;\nSELECT MAX(name) FROM students;   -- alphabetically last\n\nTo get the WHOLE row with the maximum, sort and limit:\nSELECT name FROM students ORDER BY score DESC LIMIT 1;",
            mcq("What does MAX(name) return for text?", ["The alphabetically last name", "The longest name", "An error", "The last row"], 0),
            fill("Smallest price.", "SELECT ___(price) FROM products;", ["MIN", "min"]),
            mcq("Can you combine aggregates with WHERE?", ["Yes - WHERE filters rows before aggregating", "No", "Only with GROUP BY", "Only COUNT"], 0),
            mcq("What does SELECT MIN(score) FROM students WHERE city = 'Oslo'; return for this data (Bo 78, Finn 70)?", ["70", "78", "148", "2"], 0),
            run("Select the lowest and highest score among students from London.", "sql", [t("Run")], ["55|91"],
                "SELECT MIN(score), MAX(score) FROM students WHERE city = 'London';", setup=STUDENTS, require=[r"(?i)MIN\(", r"(?i)MAX\("]),
        ),
        lesson(
            "GROUP BY",
            "GROUP BY makes one result row per group, and aggregates run per group:\n\nSELECT city, COUNT(*) FROM students GROUP BY city;\nSELECT age, AVG(score) FROM students GROUP BY age ORDER BY age;\n\nEvery selected column must either be in GROUP BY or inside an aggregate.",
            mcq("What does GROUP BY city do?", ["Makes one result row per city", "Sorts by city", "Removes cities", "Counts cities"], 0),
            fill("Count students per age.", "SELECT age, COUNT(*) FROM students ___ age;", ["GROUP BY", "group by"]),
            mcq("With GROUP BY city, which of these can you SELECT?", ["city and aggregates like COUNT(*)", "Any column", "Only COUNT(*)", "Only city"], 0),
            order("Order the clauses.", ["SELECT city, COUNT(*)", "FROM students", "WHERE age > 15", "GROUP BY city", "ORDER BY city;"]),
            run("For each city (ignore NULL), select the city and its number of students, sorted by city.", "sql", [t("Run")],
                ["London|3\nOslo|2\nParis|2"], "SELECT city, COUNT(*) FROM students WHERE city IS NOT NULL GROUP BY city ORDER BY city;",
                setup=STUDENTS, require=[r"(?i)GROUP\s+BY"]),
        ),
    ),
    # ------------------------------------------------------------------ 5
    unit(
        "Unit 5 · More grouping",
        lesson(
            "HAVING",
            "WHERE filters rows BEFORE grouping; HAVING filters groups AFTER:\n\nSELECT city, AVG(score)\nFROM students\nGROUP BY city\nHAVING AVG(score) > 75;\n\nUse HAVING whenever the condition uses an aggregate.",
            mcq("Which filters groups after aggregation?", ["HAVING", "WHERE", "GROUP BY", "FILTER"], 0),
            mcq("Can WHERE use COUNT(*)?", ["No - use HAVING", "Yes", "Only with GROUP BY", "Only in SQLite"], 0),
            fill("Keep only cities with more than 2 students.", "GROUP BY city ___ COUNT(*) > 2", ["HAVING", "having"]),
            order("Order the clauses.", ["SELECT age, COUNT(*)", "FROM students", "GROUP BY age", "HAVING COUNT(*) >= 2", "ORDER BY age;"]),
            run("Ignoring students without a city, select each city whose AVERAGE score is at least 75, with that average rounded to 1 decimal, sorted by city.",
                "sql", [t("Run")], ["London|77\nParis|75"],
                "SELECT city, ROUND(AVG(score), 1) FROM students WHERE city IS NOT NULL GROUP BY city HAVING AVG(score) >= 75 ORDER BY city;",
                setup=STUDENTS, require=[r"(?i)\bHAVING\b"]),
        ),
        lesson(
            "CASE expressions",
            "CASE is SQL's if/else, usable inside SELECT:\n\nSELECT name,\n  CASE\n    WHEN score >= 90 THEN 'A'\n    WHEN score >= 75 THEN 'B'\n    ELSE 'C'\n  END AS grade\nFROM students;\n\nCombine with aggregates: SUM(CASE WHEN score >= 80 THEN 1 ELSE 0 END) counts high scorers.",
            mcq("How does a CASE expression end?", ["END", "ENDCASE", "ELSE", ";"], 0),
            fill("The fallback branch.", "CASE WHEN x > 0 THEN 'pos' ___ 'other' END", ["ELSE", "else"]),
            mcq("Which WHEN wins if several are true?", ["The first one", "The last one", "All of them", "It's an error"], 0),
            mcq("What does SUM(CASE WHEN age > 16 THEN 1 ELSE 0 END) compute?", ["How many rows have age > 16", "The sum of ages", "The average age", "1"], 0),
            run("Select every student's name and a column band: 'high' for scores ≥ 85, 'mid' for ≥ 70, otherwise 'low'. Sort by name.", "sql", [t("Run")],
                ["Ada|high\nBo|mid\nCy|high\nDi|low\nEve|high\nFinn|mid\nGia|high\nHal|low"],
                "SELECT name, CASE WHEN score >= 85 THEN 'high' WHEN score >= 70 THEN 'mid' ELSE 'low' END AS band FROM students ORDER BY name;",
                setup=STUDENTS, require=[r"(?i)\bCASE\b"]),
        ),
        lesson(
            "Dates & text functions",
            "SQLite stores dates as text like '2026-01-05'. Handy functions:\n\nstrftime('%m', order_date)   -- month '01'\ndate('2026-01-05', '+7 days') -- '2026-01-12'\nUPPER(name), LOWER(name), LENGTH(name)\nSUBSTR(name, 1, 3)           -- first 3 characters\n\nISO dates (YYYY-MM-DD) sort correctly as text.",
            mcq("What does LENGTH('SQL') return?", ["3", "4", "2", "An error"], 0),
            mcq("What does SUBSTR('Keyboard', 1, 3) return?", ["'Key'", "'eyb'", "'Keyb'", "'ey'"], 0, "SQL string positions start at 1."),
            fill("Upper-case every name.", "SELECT ___(name) FROM customers;", ["UPPER", "upper"]),
            mcq("Why do ISO dates like 2026-02-11 sort correctly as text?", ["Year, month and day go from biggest to smallest unit", "SQLite converts them", "They don't", "Because of the dashes"], 0),
            run("Using the shop tables, count the orders per month, selecting the month number ('01', '02', …) and the count, sorted by month.", "sql", [t("Run")],
                ["01|2\n02|2"], "SELECT strftime('%m', order_date) AS month, COUNT(*) FROM orders GROUP BY month ORDER BY month;", setup=SHOP,
                require=[r"(?i)strftime|substr"]),
        ),
    ),
    # ------------------------------------------------------------------ 6
    unit(
        "Unit 6 · Joins",
        lesson(
            "INNER JOIN",
            "Real data is split across tables linked by keys. JOIN combines them:\n\nSELECT orders.id, customers.name\nFROM orders\nJOIN customers ON orders.customer_id = customers.id;\n\nINNER JOIN (plain JOIN) keeps only rows that match on both sides. Table aliases keep it short: FROM orders o JOIN customers c ON o.customer_id = c.id",
            mcq("What does ON specify?", ["How rows from the two tables match", "Which columns to show", "The sort order", "A filter on one table only"], 0),
            fill("Join the tables.", "FROM orders ___ customers ON orders.customer_id = customers.id", ["JOIN", "join", "INNER JOIN", "inner join"]),
            mcq("Which rows does an INNER JOIN keep?", ["Only rows that match in both tables", "All rows from the left table", "All rows from both", "None"], 0),
            mcq("What is a foreign key?", ["A column that refers to another table's key", "A key from another country", "An encrypted key", "The first column"], 0),
            run("Select each order's id and the customer's name, sorted by order id.", "sql", [t("Run")], ["1|Ada\n2|Linus\n3|Ada\n4|Grace"],
                "SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.id;", setup=SHOP, require=[r"(?i)\bJOIN\b"]),
        ),
        lesson(
            "LEFT JOIN",
            "LEFT JOIN keeps EVERY row from the left table, filling NULLs where there's no match:\n\nSELECT c.name, o.id\nFROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id;\n\nFind rows with no match: add WHERE o.id IS NULL (e.g. customers who never ordered).",
            mcq("What does LEFT JOIN keep?", ["All rows from the left table", "Only matches", "All rows from the right table", "Only non-matches"], 0),
            mcq("For a customer with no orders, what is o.id in a LEFT JOIN?", ["NULL", "0", "The row is missing", "An error"], 0),
            fill("Keep only customers without orders.", "LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id ___", ["IS NULL", "is null"]),
            mcq("Which join lists customers who never ordered (with WHERE … IS NULL)?", ["LEFT JOIN from customers", "INNER JOIN", "CROSS JOIN", "None"], 0),
            run("Select every customer's name and how many orders they placed (0 if none), sorted by name.", "sql", [t("Run")],
                ["Ada|2\nGrace|1\nLinus|1\nTim|0"],
                "SELECT c.name, COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id ORDER BY c.name;",
                setup=SHOP, require=[r"(?i)LEFT\s+(OUTER\s+)?JOIN"], hint="COUNT(o.id) ignores the NULLs from customers without orders."),
        ),
        lesson(
            "Joining several tables",
            "Chain joins to follow the links:\n\nSELECT c.name, p.name, oi.qty\nFROM orders o\nJOIN customers c    ON c.id = o.customer_id\nJOIN order_items oi ON oi.order_id = o.id\nJOIN products p     ON p.id = oi.product_id;\n\nThen aggregate across them: SUM(p.price * oi.qty) is money spent.",
            mcq("How many JOINs connect 4 tables in a chain?", ["3", "4", "2", "1"], 0),
            fill("Money for each order line.", "SELECT p.price ___ oi.qty FROM ...", "*"),
            mcq("Why use table aliases like c and p?", ["Shorter, clearer queries", "They're required", "They're faster", "To rename tables permanently"], 0),
            mcq("If two tables both have a name column, how do you pick one?", ["Prefix it: c.name or p.name", "You can't", "Use DISTINCT", "Rename the table"], 0),
            run("Select each customer's name and total money spent (price × qty over all their orders), only for customers who ordered, highest total first.", "sql", [t("Run")],
                ["Ada|406.5\nLinus|30\nGrace|19"],
                "SELECT c.name, SUM(p.price * oi.qty) AS total\nFROM customers c\nJOIN orders o ON o.customer_id = c.id\nJOIN order_items oi ON oi.order_id = o.id\nJOIN products p ON p.id = oi.product_id\nGROUP BY c.id\nORDER BY total DESC;",
                setup=SHOP, require=[r"(?i)JOIN[\s\S]*JOIN[\s\S]*JOIN"]),
        ),
    ),
    # ------------------------------------------------------------------ 7
    unit(
        "Unit 7 · Changing data",
        lesson(
            "INSERT",
            "INSERT adds rows:\n\nINSERT INTO books (title, author, year, copies)\nVALUES ('Snow Crash', 'Stephenson', 1992, 2);\n\nList the columns you're filling; an INTEGER PRIMARY KEY (id) is filled automatically. Insert several rows with VALUES (...), (...);",
            fill("Add a row to books.", "___ INTO books (title) VALUES ('Emma');", ["INSERT", "insert"]),
            mcq("What happens to id if you leave it out for an INTEGER PRIMARY KEY?", ["SQLite assigns the next number", "It's NULL", "An error", "It's 0"], 0),
            mcq("Which inserts two rows at once?", ["VALUES ('a'), ('b')", "VALUES ('a', 'b')", "VALUES ['a', 'b']", "Two INTO clauses"], 0),
            order("Order the statement.", ["INSERT INTO books (title, year)", "VALUES ('Dracula', 1897);"]),
            run("Insert the book 'Snow Crash' by 'Stephenson' from 1992 with 2 copies.", "sql",
                [t("new row", append="SELECT id, title, author, year, copies FROM books WHERE title = 'Snow Crash';"),
                 t("row count", append="SELECT COUNT(*) FROM books;")],
                ["5|Snow Crash|Stephenson|1992|2", "5"],
                "INSERT INTO books (title, author, year, copies) VALUES ('Snow Crash', 'Stephenson', 1992, 2);", setup=BOOKS, require=[r"(?i)INSERT\s+INTO"]),
        ),
        lesson(
            "UPDATE",
            "UPDATE changes existing rows:\n\nUPDATE books SET copies = copies + 1 WHERE title = 'Dune';\n\n⚠️ Without WHERE, EVERY row is updated! Test your WHERE with a SELECT first. Set several columns: SET a = 1, b = 2",
            mcq("What happens with UPDATE books SET copies = 0; (no WHERE)?", ["Every book gets 0 copies", "Nothing", "An error", "Only the first book changes"], 0),
            fill("Change the value.", "UPDATE books ___ copies = 5 WHERE id = 1;", ["SET", "set"]),
            mcq("How do you add 1 to the current value?", ["SET copies = copies + 1", "SET copies++", "SET copies += 1", "INCREMENT copies"], 0),
            mcq("Good habit before running an UPDATE?", ["Run a SELECT with the same WHERE to see which rows change", "Delete the table", "Add LIMIT 1", "Nothing"], 0),
            run("A library donation arrived: add 2 copies to every book published before 1970.", "sql",
                [t("after update", append="SELECT title, copies FROM books ORDER BY id;")], ["Dune|5\nNeuromancer|1\nHyperion|0\nFoundation|4"],
                "UPDATE books SET copies = copies + 2 WHERE year < 1970;", setup=BOOKS, require=[r"(?i)\bUPDATE\b", r"(?i)\bWHERE\b"]),
        ),
        lesson(
            "DELETE",
            "DELETE removes rows:\n\nDELETE FROM books WHERE copies = 0;\n\n⚠️ DELETE FROM books; with no WHERE empties the whole table. Deleting rows that other tables reference can break links - that's what foreign key constraints protect against.",
            mcq("What does DELETE FROM books; do?", ["Removes every row", "Deletes the table itself", "Nothing", "An error"], 0),
            fill("Remove only the matching rows.", "DELETE FROM books ___ year < 1900;", ["WHERE", "where"]),
            mcq("Which removes the table structure completely?", ["DROP TABLE books;", "DELETE FROM books;", "REMOVE books;", "TRUNCATE books;"], 0),
            mcq("How many rows does DELETE FROM books WHERE 1 = 0; remove?", ["0", "All", "1", "An error"], 0),
            run("Remove every book that has no copies left.", "sql",
                [t("remaining", append="SELECT title FROM books ORDER BY id;")], ["Dune\nNeuromancer\nFoundation"],
                "DELETE FROM books WHERE copies = 0;", setup=BOOKS, require=[r"(?i)DELETE\s+FROM", r"(?i)\bWHERE\b"]),
        ),
    ),
    # ------------------------------------------------------------------ 8
    unit(
        "Unit 8 · Designing databases",
        lesson(
            "CREATE TABLE",
            "CREATE TABLE defines a table's columns and types:\n\nCREATE TABLE pets (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  species TEXT,\n  born INTEGER\n);\n\nCommon SQLite types: INTEGER, REAL, TEXT, BLOB. PRIMARY KEY uniquely identifies each row.",
            fill("Create a new table.", "___ TABLE pets (id INTEGER PRIMARY KEY);", ["CREATE", "create"]),
            mcq("What does PRIMARY KEY guarantee?", ["Each row has a unique, non-duplicate key", "The column is first", "It's encrypted", "It's a number"], 0),
            mcq("Which type stores decimals in SQLite?", ["REAL", "DECIMALS", "FLOATY", "NUMBER only"], 0),
            mcq("What does DROP TABLE pets; do?", ["Deletes the table and all its data", "Empties it", "Renames it", "Nothing"], 0),
            run("Create a table pets with columns id (INTEGER PRIMARY KEY), name (TEXT), species (TEXT) and age (INTEGER), then insert a cat named Tom aged 3.", "sql",
                [t("columns", append="SELECT name, type FROM pragma_table_info('pets') ORDER BY cid;"), t("data", append="SELECT id, name, species, age FROM pets;")],
                ["id|INTEGER\nname|TEXT\nspecies|TEXT\nage|INTEGER", "1|Tom|cat|3"],
                "CREATE TABLE pets (\n  id INTEGER PRIMARY KEY,\n  name TEXT,\n  species TEXT,\n  age INTEGER\n);\nINSERT INTO pets (name, species, age) VALUES ('Tom', 'cat', 3);",
                require=[r"(?i)CREATE\s+TABLE\s+pets"]),
        ),
        lesson(
            "Constraints",
            "Constraints make the database reject bad data:\n\nCREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  email TEXT NOT NULL UNIQUE,\n  age INTEGER CHECK (age >= 13),\n  plan TEXT DEFAULT 'free'\n);\n\nNOT NULL - must have a value · UNIQUE - no duplicates · CHECK - must satisfy a rule · DEFAULT - value when omitted",
            mcq("Which constraint prevents two users having the same email?", ["UNIQUE", "NOT NULL", "CHECK", "DEFAULT"], 0),
            fill("Reject ages under 13.", "age INTEGER ___ (age >= 13)", ["CHECK", "check"]),
            mcq("What does DEFAULT 'free' do?", ["Uses 'free' when no value is given", "Makes the column free-form", "Allows NULL", "Nothing"], 0),
            mcq("Why put rules in the database instead of only in the app?", ["Every app and script writing to it is protected", "It's faster to type", "Apps can't validate", "It's required"], 0),
            run("Create table users with: id INTEGER PRIMARY KEY, email TEXT that is NOT NULL and UNIQUE, and plan TEXT defaulting to 'free'.", "sql",
                [t("duplicate email rejected", append="INSERT OR IGNORE INTO users (email) VALUES ('a@x.io');\nINSERT OR IGNORE INTO users (email) VALUES ('a@x.io');\nSELECT COUNT(*) FROM users;"),
                 t("missing email rejected", append="INSERT OR IGNORE INTO users (email) VALUES (NULL);\nSELECT COUNT(*) FROM users;"),
                 t("default plan", append="INSERT INTO users (email) VALUES ('b@x.io');\nSELECT plan FROM users;")],
                ["1", "0", "free"],
                "CREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  email TEXT NOT NULL UNIQUE,\n  plan TEXT DEFAULT 'free'\n);",
                require=[r"(?i)UNIQUE", r"(?i)NOT\s+NULL", r"(?i)DEFAULT"]),
        ),
        lesson(
            "Subqueries",
            "A subquery is a query inside another query:\n\n-- students scoring above the average\nSELECT name FROM students\nWHERE score > (SELECT AVG(score) FROM students);\n\n-- products that were never ordered\nSELECT name FROM products\nWHERE id NOT IN (SELECT product_id FROM order_items);",
            mcq("What does (SELECT AVG(score) FROM students) produce?", ["A single value", "A table of names", "An error", "One row per student"], 0),
            fill("Rows whose id is in the subquery's results.", "WHERE id ___ (SELECT product_id FROM order_items)", ["IN", "in"]),
            mcq("Where can a subquery appear?", ["In WHERE, FROM and SELECT", "Only in WHERE", "Only in FROM", "Nowhere in SQLite"], 0),
            mcq("What does NOT IN return here if order_items is empty?", ["Every product", "No products", "An error", "NULL"], 0),
            run("Select the names of students who scored ABOVE the class average (use a subquery for the average), sorted by name.", "sql", [t("Run")],
                ["Ada\nCy\nEve\nGia"], "SELECT name FROM students WHERE score > (SELECT AVG(score) FROM students) ORDER BY name;", setup=STUDENTS,
                require=[r"(?i)SELECT[\s\S]*\(\s*SELECT"], forbid=[r"\b78\b"]),
        ),
    ),
    INTERMEDIATE,
    ADVANCED,
    EXPERT,
    EXPERT2,
)
