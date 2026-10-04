"""SQL - gentle 'Start here' units for people who have never seen code or a database."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

PETS = """CREATE TABLE pets (id INTEGER PRIMARY KEY, name TEXT, kind TEXT, age INTEGER);
INSERT INTO pets VALUES (1, 'Milo', 'cat', 3), (2, 'Rex', 'dog', 5), (3, 'Luna', 'cat', 2), (4, 'Coco', 'bird', 1), (5, 'Buddy', 'dog', 7);"""

START = [
    start_unit(
        1,
        "Start here · What is a database?",
        lesson(
            "A database is a smart spreadsheet",
            """You already know spreadsheets: a grid of rows and columns, like a class list with a row for each pupil and columns for name and age.

A DATABASE is the same idea for much bigger information - every user of an app, every product in a shop, every message you ever sent. Apps keep their information in databases because a computer can search millions of rows in a blink.

The language we use to talk to a database is called SQL (people say "S-Q-L" or "sequel"). SQL isn't a programming language for building apps - it is a language for ASKING QUESTIONS, almost like English:

"Show me the names of all the dogs, oldest first."

You write your questions as short commands called QUERIES, and the database sends back the answer.

In this lesson you will learn: what a database is and what SQL is for.""",
            mcq("What is a database most like?", ["A big organised spreadsheet", "A paint program", "A video player", "A calculator"], 0, "A database stores information in tables of rows and columns."),
            mcq("What is SQL used for?", ["Asking a database questions", "Editing photos", "Playing music", "Sending emails"], 0, "SQL is the language for talking to databases."),
            mcq("What do we call a command we send to a database?", ["A query", "A cable", "A picture", "A page"], 0, "A question to the database is a query."),
        ),
        lesson(
            "Tables, rows and columns",
            """A database keeps its information in TABLES. A table is a grid:

 id | name  | kind | age
----+-------+------+----
 1  | Milo  | cat  | 3
 2  | Rex   | dog  | 5
 3  | Luna  | cat  | 2

- Each COLUMN is one kind of information (id, name, kind, age). It has a name at the top.
- Each ROW is one thing (one pet). Row 2 is Rex, a 5-year-old dog.
- Each little box is a VALUE.

This table is called pets. A database can hold many tables - maybe one for pets, one for owners.

Every value in a column has the same type: names are TEXT, ages are INTEGER (whole numbers).

In this lesson you will learn: the words table, row and column.""",
            mcq("In the pets table, what is one ROW?", ["One pet, with all its details", "The name of every pet", "The word 'pets'", "The age column"], 0, "A row is one thing: here, one pet."),
            mcq("What is the 'age' column?", ["All the ages, one per pet", "One pet", "A table", "A query"], 0, "A column holds one kind of information for all rows."),
            mcq("How many rows does the little table above show?", ["3", "4", "1", "12"], 0, "Milo, Rex and Luna - three rows."),
            mcq("Which is the best name for a table that stores students?", ["students", "table1", "x", "stuff"], 0, "Clear names help everyone."),
        ),
        lesson(
            "Asking questions: SELECT",
            """The main SQL command is SELECT: "show me this". After SELECT you list the columns you want, then FROM and the table name:

SELECT name FROM pets;

This means: "show the name column from the pets table". You get:

Milo
Rex
Luna
Coco
Buddy

For two columns, separate them with a comma:

SELECT name, age FROM pets;

To get EVERY column, use a star:

SELECT * FROM pets;

Notes: SQL words (SELECT, FROM) are usually written in capitals so they stand out, and a query ends with a semicolon ;.

In this lesson you will learn: how to ask a database for information.""",
            mcq("What does SELECT name FROM pets; show?", ["The name of every pet", "One pet", "How many pets", "The table's name"], 0, "It lists the name column of every row."),
            mcq("What does the star in SELECT * mean?", ["All columns", "Nothing", "Multiply", "The first row"], 0, "* means every column."),
            fill("Show the age column from pets.", "SELECT ___ FROM pets;", "age", "Write the column name you want."),
            order("Order the query.", ["SELECT name, age", "FROM pets;"], "SELECT (what) comes first, then FROM (where)."),
            run("Show the name of every pet.", "sql", [t("Run")], ["Milo\nRex\nLuna\nCoco\nBuddy"], "SELECT name FROM pets;", setup=PETS, hint="SELECT name FROM pets;"),
        ),
    ),
    start_unit(
        2,
        "Start here · Filtering, sorting and counting",
        lesson(
            "Choosing rows: WHERE",
            """Usually you don't want EVERY row. WHERE keeps only the rows that match a condition:

SELECT name FROM pets WHERE kind = 'dog';

Read it as: "show the name of pets where the kind is dog". You get:

Rex
Buddy

Notes:
- Text goes in SINGLE quotes: 'dog'.
- In SQL a single = means "is equal to" (unlike many programming languages).
- Numbers need no quotes, and you can compare them:

SELECT name FROM pets WHERE age > 2;      older than 2
SELECT name FROM pets WHERE age <= 3;     3 or younger

Other comparison signs: >  <  >=  <=  =  and <> (not equal).

In this lesson you will learn: how to pick only the rows you want.""",
            mcq("What does WHERE do?", ["Keeps only rows that match a condition", "Sorts rows", "Counts rows", "Deletes rows"], 0, "WHERE filters the rows."),
            mcq("Which line shows only the cats?", ["SELECT name FROM pets WHERE kind = 'cat';", "SELECT cat FROM pets;", "SELECT name FROM cat;", "WHERE name = pets;"], 0, "Filter the kind column for 'cat'."),
            mcq("Which sign means 'bigger than'?", [">", "<", "=", "<>"], 0, "> is bigger than."),
            fill("Show pets older than 4.", "SELECT name FROM pets WHERE age ___ 4;", ">", "Use the 'bigger than' sign."),
            run("Show the names of the pets that are older than 2.", "sql", [t("Run")], ["Milo\nRex\nBuddy"], "SELECT name FROM pets WHERE age > 2;", setup=PETS, hint="WHERE age > 2"),
        ),
        lesson(
            "Putting rows in order: ORDER BY",
            """Rows come back in no special order. ORDER BY sorts them:

SELECT name, age FROM pets ORDER BY age;

This sorts from the smallest age to the biggest. For the biggest first, add DESC (short for "descending"):

SELECT name, age FROM pets ORDER BY age DESC;

Text sorts alphabetically (A to Z):

SELECT name FROM pets ORDER BY name;

You can combine WHERE and ORDER BY - WHERE always comes first:

SELECT name FROM pets WHERE kind = 'dog' ORDER BY age DESC;

In this lesson you will learn: how to sort your answer.""",
            mcq("What does ORDER BY age do?", ["Sorts rows from smallest to biggest age", "Removes ages", "Counts ages", "Adds ages"], 0, "ORDER BY sorts."),
            mcq("What does DESC add?", ["Biggest first", "Smallest first", "Delete", "Describe"], 0, "DESC means descending: biggest first."),
            mcq("In a query with both, which comes first?", ["WHERE", "ORDER BY", "Either", "Neither"], 0, "Filter first, then sort."),
            run("Show the names of all pets, youngest first (smallest age first).", "sql", [t("Run")], ["Coco\nLuna\nMilo\nRex\nBuddy"], "SELECT name FROM pets ORDER BY age;", setup=PETS, hint="ORDER BY age"),
        ),
        lesson(
            "Counting: how many?",
            """Often you just want a number: "how many pets are there?" SQL has COUNT for that:

SELECT COUNT(*) FROM pets;

The answer is a single number: 5.

Add WHERE to count only some rows:

SELECT COUNT(*) FROM pets WHERE kind = 'cat';

Answer: 2.

Other helpers work the same way. They are called FUNCTIONS (small tools that take many values and give one answer):

SELECT MAX(age) FROM pets;      the biggest age (7)
SELECT MIN(age) FROM pets;      the smallest age (1)
SELECT AVG(age) FROM pets;      the average age

You have now learned the heart of SQL: SELECT, FROM, WHERE, ORDER BY and COUNT. Well done!

In this lesson you will learn: how to count rows and find the biggest or smallest value.""",
            mcq("What does COUNT(*) give?", ["How many rows", "The first row", "The biggest value", "All the names"], 0, "COUNT(*) counts rows."),
            mcq("What does MAX(age) give?", ["The biggest age", "The smallest age", "The average age", "How many ages"], 0, "MAX = maximum = biggest."),
            fill("Count the pets.", "SELECT ___(*) FROM pets;", "COUNT", "COUNT counts rows."),
            run("Count how many pets are dogs (the answer is 2).", "sql", [t("Run")], ["2"], "SELECT COUNT(*) FROM pets WHERE kind = 'dog';", setup=PETS, hint="COUNT(*) with WHERE kind = 'dog'"),
        ),
    ),
]
