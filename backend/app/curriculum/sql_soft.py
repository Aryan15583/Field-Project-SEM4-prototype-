"""SQL - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """A database keeps information in TABLES - grids of rows and columns, like a spreadsheet. Each row is one thing (one student); each column is one kind of detail (name, age, city).

To ask the database for information, you write a SELECT query. The shape is always:

SELECT (which columns) FROM (which table);

SELECT name, age FROM students;       -- show the name and age of every student
SELECT * FROM students;               -- the star means "every column"

Read the first one aloud: "Select name and age from students." It really is close to English.

Habits to pick up:
- SQL words (SELECT, FROM) don't care about capital letters, but writing them in CAPITALS makes queries easier to read.
- End a statement with a semicolon ;.

In this lesson you will learn: how to ask a table for the columns you want.""",
    "1/2": """You are not limited to the columns as they are stored. SELECT can CALCULATE new columns, and AS gives the new column a name of your choice (an ALIAS):

SELECT name, score + 5 AS curved FROM students;

This shows each student's name and their score plus 5, with the second column labelled "curved". The stored scores are not changed - you are only changing what is shown.

You can also join pieces of TEXT together with ||:

SELECT name || ' from ' || city AS intro FROM students;

For a student Ada in London this gives: Ada from London.

Text pieces are written in 'single quotes'.

In this lesson you will learn: how to calculate new columns and give them names.""",
    "1/3": """Sometimes a column repeats the same value in many rows. For example, many students live in London. If you just want to know WHICH cities exist, each only once, use DISTINCT:

SELECT DISTINCT city FROM students;

DISTINCT removes duplicate rows from the answer - you get each city once.

When you select more than one column, DISTINCT looks at the whole combination. For example:

SELECT DISTINCT city, age FROM students;

keeps each different (city, age) pair once. Two students from London who are both 16 would appear as a single row.

In this lesson you will learn: how to remove repeated rows from your answer.""",
    "2/1": """Usually you don't want EVERY row. WHERE keeps only the rows that match a condition:

SELECT name FROM students WHERE age >= 17;        -- 17 or older
SELECT * FROM students WHERE city = 'Oslo';       -- only the Oslo students

Read the second one: "Show everything about students where the city is Oslo."

The comparison signs:
=    equal to              (just ONE equals sign in SQL)
<>   not equal to          (or !=)
<  >  <=  >=              smaller, bigger, smaller or equal, bigger or equal

Text values go in 'single quotes'. Numbers don't need quotes.

Think of WHERE as a sieve: only rows that pass the test fall through into your answer.

In this lesson you will learn: how to pick only the rows you want.""",
    "2/2": """You can combine conditions with three small words:

AND   both conditions must be true
OR    at least one must be true
NOT   flips a condition around

WHERE age >= 16 AND city = 'London'            -- 16+ AND from London
WHERE city = 'Oslo' OR city = 'Paris'          -- from either city
WHERE NOT city = 'Oslo'                        -- anywhere except Oslo

A trap: AND is worked out BEFORE OR, like multiplication before addition. If you mix them, use brackets to be clear about what you mean:

WHERE (city = 'Oslo' OR city = 'Paris') AND score > 70

Read it: "from Oslo or Paris, and with a score above 70."

In this lesson you will learn: how to combine several conditions.""",
    "2/3": """Three shortcuts make common filters shorter.

IN - matches any value in a list:
WHERE city IN ('Oslo', 'Paris')            -- same as city = 'Oslo' OR city = 'Paris'

BETWEEN - a range, including both ends:
WHERE age BETWEEN 15 AND 16                -- 15 or 16

LIKE - matches text by pattern, using two wildcards:
%   stands for any number of characters (even none)
_   stands for exactly one character

WHERE name LIKE 'A%'       -- starts with A
WHERE name LIKE '%n'       -- ends with n
WHERE name LIKE '_o'       -- exactly 2 letters, the second is o

Think of % and _ as the joker cards of text search.

In this lesson you will learn: shortcuts for lists, ranges and text patterns.""",
    "3/1": """Rows come back in no particular order unless you ask. ORDER BY sorts the answer:

SELECT name, score FROM students ORDER BY score;         -- smallest score first
SELECT name, score FROM students ORDER BY score DESC;    -- biggest first (DESC = descending)
SELECT * FROM students ORDER BY city, name;              -- by city, and within each city by name

Text is sorted alphabetically (A to Z), numbers from small to big. Add DESC for the opposite direction.

Remember: without ORDER BY, the order of the rows is not guaranteed - it might look sorted today and be different tomorrow. If order matters, always ask for it.

In this lesson you will learn: how to sort your answer.""",
    "3/2": """Sometimes you only want a few rows, like the top 3 scores. LIMIT keeps just the first N rows:

SELECT name FROM students ORDER BY score DESC LIMIT 3;          -- the top 3

OFFSET skips some rows first. Together they let you build pages, like a website's "page 2":

SELECT name FROM students ORDER BY score DESC LIMIT 3 OFFSET 3; -- skip 3, show the next 3

An important habit: always use LIMIT together with ORDER BY. Otherwise "the first 3 rows" means nothing, because without sorting there is no first.

In this lesson you will learn: how to take just the top rows, or a "page" of results.""",
    "3/3": """Sometimes a value is MISSING - for example, a student whose city nobody recorded. The database stores this as NULL, meaning "unknown".

NULL is not zero and not empty text - it means "we don't know". And it has an odd rule: NULL is not equal to ANYTHING, not even to another NULL. So the normal = test fails. Use IS instead:

WHERE city IS NULL            -- rows where the city is missing
WHERE city IS NOT NULL        -- rows where the city is known

A common beginner mistake: WHERE city = NULL finds nothing, ever.

To show a friendly value instead of NULL, use COALESCE. It picks the first value that is not NULL:

SELECT COALESCE(city, 'unknown') FROM students;

In this lesson you will learn: how to find and handle missing values.""",
    "4/1": """So far each result row came from one stored row. AGGREGATE functions summarise MANY rows into a single value - a count, a total, an average.

SELECT COUNT(*) FROM students;           -- how many rows
SELECT COUNT(city) FROM students;        -- how many rows have a city (skips NULLs)
SELECT SUM(score), AVG(score) FROM students;    -- total and average
SELECT ROUND(AVG(score), 1) FROM students;      -- average, rounded to 1 decimal

Think of them as a calculator at the bottom of a column: you feed in a whole column, and get one number out.

COUNT(*) counts all rows; COUNT(column) counts only rows where that column is not NULL.

In this lesson you will learn: how to count, add up and average rows.""",
    "4/2": """MIN and MAX find the smallest and the biggest value. They work on numbers, text (alphabetical order) and dates:

SELECT MIN(age), MAX(age) FROM students;       -- youngest and oldest
SELECT MAX(name) FROM students;                -- the alphabetically LAST name

A catch: MAX(score) tells you the highest SCORE, but not WHO got it. To get the whole row of the top student, sort and take one:

SELECT name FROM students ORDER BY score DESC LIMIT 1;

Read it: "sort by score, highest first, and keep only the first row."

In this lesson you will learn: how to find smallest and biggest values, and the winner's whole row.""",
    "4/3": """What if you want a count PER city, not one count for the whole table? GROUP BY splits the rows into groups, and then each aggregate is worked out for each group separately.

SELECT city, COUNT(*) FROM students GROUP BY city;

This gives one result row per city, with the number of students in it, like:
London | 3
Oslo   | 2

Another example - the average score for each age:

SELECT age, AVG(score) FROM students GROUP BY age ORDER BY age;

One rule: every column you SELECT must either be in the GROUP BY or be inside an aggregate function. (Otherwise the database wouldn't know which value to show for the group.)

In this lesson you will learn: how to summarise per group.""",
    "5/1": """You know WHERE filters rows. But what if you want to filter on a summary, like "cities whose average score is above 75"? You can't use WHERE for that, because the average doesn't exist until the rows are grouped.

The answer is HAVING - it filters GROUPS after they are made:

SELECT city, AVG(score)
FROM students
GROUP BY city
HAVING AVG(score) > 75;

The order of events:
1. WHERE - throws away individual rows.
2. GROUP BY - makes the groups.
3. HAVING - throws away whole groups.

The simple rule: if the condition uses an aggregate (COUNT, AVG, SUM...), use HAVING. Otherwise use WHERE.

In this lesson you will learn: how to filter groups by their summary values.""",
    "5/2": """CASE is SQL's version of if / else. It lets a query make a decision for each row:

SELECT name,
  CASE
    WHEN score >= 90 THEN 'A'
    WHEN score >= 75 THEN 'B'
    ELSE 'C'
  END AS grade
FROM students;

Read it from the top: "if the score is 90 or more, the grade is A; otherwise if 75 or more, B; otherwise C." SQL uses the FIRST WHEN that is true.

CASE works inside aggregates too, which makes a handy counting trick:

SUM(CASE WHEN score >= 80 THEN 1 ELSE 0 END)

That adds 1 for every student who scored 80 or more - in other words, it counts the high scorers.

In this lesson you will learn: how to make a query choose a value by a rule.""",
    "5/3": """Dates and text have their own helper functions. This database (SQLite) stores dates as TEXT in the form YEAR-MONTH-DAY, like '2026-01-05'.

strftime('%m', order_date)       -- the month: '01'
date('2026-01-05', '+7 days')    -- a week later: '2026-01-12'

For text:

UPPER(name)       LOWER(name)       LENGTH(name)
SUBSTR(name, 1, 3)       -- a piece of text: start at 1, take 3 characters

A nice fact: dates written year-first like 2026-01-05 SORT correctly as plain text, because the biggest unit (the year) comes first. That's why this format is recommended.

In this lesson you will learn: handy functions for dates and text.""",
    "6/1": """Real databases split information over several tables to avoid repeating things. For example, orders hold a customer_id (a number) instead of the customer's full name, and a separate customers table holds the names.

The number that links the two is a KEY. A JOIN combines the tables back together by matching the keys:

SELECT orders.id, customers.name
FROM orders
JOIN customers ON orders.customer_id = customers.id;

Read it: "take each order, and attach the customer whose id matches the order's customer_id."

A plain JOIN (INNER JOIN) keeps only rows that have a match on BOTH sides.

Short names (ALIASES) make joins easier to read:

FROM orders o JOIN customers c ON o.customer_id = c.id

In this lesson you will learn: how to combine two linked tables.""",
    "6/2": """A plain JOIN drops rows that have no match. What if you want a list of ALL customers, even those who never ordered? Use LEFT JOIN. It keeps EVERY row of the left table (the one after FROM), and fills the missing right side with NULL:

SELECT c.name, o.id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id;

A customer with no orders still appears, with NULL in the order column.

This gives a neat trick for finding "who has NOTHING": keep only the rows where the right side is NULL.

... LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;

That lists the customers who never ordered.

In this lesson you will learn: how to keep all rows from one table and find missing matches.""",
    "6/3": """You can chain several JOINs to follow links across many tables - like following a trail of clues.

SELECT c.name, p.name, oi.qty
FROM orders o
JOIN customers c    ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id;

Read it as a story: "For each order, find its customer; find the items in that order; for each item, find the product."

Each JOIN adds one more table and one more matching rule (the ON part).

Once the tables are joined, you can summarise across them. For example, the money spent is the price times the quantity, added up:

SUM(p.price * oi.qty)

In this lesson you will learn: how to follow links across several tables.""",
    "7/1": """Until now you have only READ data. INSERT adds NEW rows:

INSERT INTO books (title, author, year, copies)
VALUES ('Snow Crash', 'Stephenson', 1992, 2);

Read it: "Insert into the books table, filling the columns title, author, year and copies, with these values."

The values must be in the same order as the columns you listed.

A column marked as an INTEGER PRIMARY KEY (usually the id) is filled in automatically - you don't have to give it a value.

You can add several rows at once by listing more brackets, separated by commas:

VALUES ('A', 'x', 2000, 1), ('B', 'y', 2001, 3);

In this lesson you will learn: how to add new rows to a table.""",
    "7/2": """UPDATE changes rows that already exist:

UPDATE books SET copies = copies + 1 WHERE title = 'Dune';

Read it: "In the books table, set copies to copies plus one, but only for the row where the title is Dune."

WARNING: if you forget the WHERE part, EVERY row in the table is changed! A good habit is to write the same WHERE in a SELECT first, to see exactly which rows will be touched.

You can change several columns at once:

UPDATE books SET copies = 5, year = 1966 WHERE title = 'Dune';

In this lesson you will learn: how to change existing rows safely.""",
    "7/3": """DELETE removes rows:

DELETE FROM books WHERE copies = 0;

Read it: "Remove from the books table every row where copies is 0."

WARNING: DELETE FROM books; with no WHERE removes EVERY row and empties the table! There is no undo button, so, as with UPDATE, test your WHERE with a SELECT first.

Another thing to be careful about: if other tables point to the rows you delete (through their keys), those links break. Databases can protect you from this with "foreign key constraints", which refuse to delete a row that something else still depends on.

In this lesson you will learn: how to remove rows - and how to avoid deleting too much.""",
    "8/1": """So far the tables already existed. CREATE TABLE makes a new one. You list each column and what kind of data it holds:

CREATE TABLE pets (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  species TEXT,
  born INTEGER
);

The common kinds in SQLite:
INTEGER  whole numbers
REAL     decimals
TEXT     words
BLOB     raw data like a picture

PRIMARY KEY marks the column that identifies each row uniquely, like a student number - no two rows share it. NOT NULL means "this must always have a value".

Designing a table is like designing a form: decide what questions it asks, and what kind of answer each accepts.

In this lesson you will learn: how to create a table with the right columns.""",
    "8/2": """You can make the database refuse bad data automatically. These rules are called CONSTRAINTS:

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  age INTEGER CHECK (age >= 13),
  plan TEXT DEFAULT 'free'
);

What each means:
NOT NULL   a value is required - it can't be left empty.
UNIQUE     no two rows can have the same value (no two users with one email).
CHECK      the value must pass a test (age must be 13 or more).
DEFAULT    the value used when you don't give one (plan becomes 'free').

It is like a bouncer at the door: bad data is turned away instantly, instead of causing problems later.

In this lesson you will learn: how to build rules into a table.""",
    "8/3": """A SUBQUERY is a query placed INSIDE another query, in brackets. The inner one runs first, and its answer is used by the outer one.

-- students scoring above the average
SELECT name FROM students
WHERE score > (SELECT AVG(score) FROM students);

Read it: "First work out the average score (the inner query). Then show the students whose score is higher than that number."

Another use - "things that never appeared somewhere else":

-- products that were never ordered
SELECT name FROM products
WHERE id NOT IN (SELECT product_id FROM order_items);

Read it: "Show products whose id is NOT in the list of product ids that appear in order_items."

Subqueries let you ask a question that depends on the answer to another question.

In this lesson you will learn: how to use one query's answer inside another.""",
}
