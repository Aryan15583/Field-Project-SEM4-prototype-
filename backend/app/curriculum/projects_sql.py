"""SQL projects - one at the end of each section (added to units 8, 12 and 16)."""
from .dsl import project, run, t
from .sql import STUDENTS
from .sql_adv import SALES, SHOP

# ------------------------------------------------------------------ Beginner: school report
BEGINNER = project(
    "Project: School report card",
    "The head teacher wants a report from the students table (id, name, age, city, score). Build it query by query:\n\n"
    "1. The honour roll.\n2. City averages.\n3. A grade-band summary.",
    run("Step 1 - Honour roll: name and score of students scoring 85 or more, best first (ties by name).", "sql",
        [t("Run")], ["Eve|95\nAda|91\nGia|88\nCy|85"],
        "SELECT name, score FROM students\nWHERE score >= 85\nORDER BY score DESC, name;", setup=STUDENTS,
        require=[r"(?i)WHERE", r"(?i)ORDER\s+BY"]),
    run("Step 2 - City averages: city, number of students and average score (1 decimal) for students with a known city, "
        "highest average first.", "sql",
        [t("Run")], ["London|3|77\nParis|2|75\nOslo|2|74"],
        "SELECT city, COUNT(*), ROUND(AVG(score), 1) AS avg_score\nFROM students\nWHERE city IS NOT NULL\nGROUP BY city\nORDER BY avg_score DESC;",
        setup=STUDENTS, require=[r"(?i)GROUP\s+BY", r"(?i)IS\s+NOT\s+NULL"]),
    run("Step 3 - Grade bands: label each student A (90+), B (80-89), C (70-79) or D (below 70) with CASE, and show each "
        "band with how many students it has, in band order.", "sql",
        [t("Run")], ["A|2\nB|2\nC|2\nD|2"],
        "SELECT CASE\n         WHEN score >= 90 THEN 'A'\n         WHEN score >= 80 THEN 'B'\n         WHEN score >= 70 THEN 'C'\n         ELSE 'D'\n"
        "       END AS band,\n       COUNT(*)\nFROM students\nGROUP BY band\nORDER BY band;",
        setup=STUDENTS, require=[r"(?i)\bCASE\b", r"(?i)GROUP\s+BY"]),
)

# ------------------------------------------------------------------ Intermediate: sales dashboard
INTERMEDIATE = project(
    "Project: Sales dashboard",
    "Build the queries behind a sales dashboard for the shop database (customers, products, orders, order_items) and "
    "the monthly sales table (rep, region, month, amount):\n\n1. Revenue per customer.\n2. Best rep in each region.\n3. "
    "Month-by-month growth.",
    run("Step 1 - Revenue per customer: name and total spent (qty × price), including customers with no orders (0), "
        "highest first, ties by name.", "sql",
        [t("Run")], ["Ada|406.5\nLinus|30\nGrace|19\nTim|0"],
        "SELECT c.name, COALESCE(SUM(oi.qty * p.price), 0) AS spent\nFROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id\n"
        "LEFT JOIN order_items oi ON oi.order_id = o.id\nLEFT JOIN products p ON p.id = oi.product_id\nGROUP BY c.id, c.name\nORDER BY spent DESC, c.name;",
        setup=SHOP, require=[r"(?i)LEFT\s+JOIN", r"(?i)GROUP\s+BY"]),
    run("Step 2 - Best rep per region: using a CTE of total sales per rep and region and RANK(), show region, rep and "
        "total for the top rep in each region.", "sql",
        [t("Run")], ["North|Ada|360\nSouth|Cy|410"],
        "WITH totals AS (\n  SELECT region, rep, SUM(amount) AS total,\n         RANK() OVER (PARTITION BY region ORDER BY SUM(amount) DESC) AS rnk\n"
        "  FROM sales\n  GROUP BY region, rep\n)\nSELECT region, rep, total FROM totals WHERE rnk = 1 ORDER BY region;",
        setup=SALES, require=[r"(?i)\bWITH\b", r"(?i)\bRANK\s*\("]),
    run("Step 3 - Growth: for each month show total sales, the previous month's total and the change (LAG), in month "
        "order (NULLs for the first month).", "sql",
        [t("Run")], ["2026-01|360|NULL|NULL\n2026-02|320|360|-40\n2026-03|480|320|160"],
        "WITH monthly AS (\n  SELECT month, SUM(amount) AS total FROM sales GROUP BY month\n)\n"
        "SELECT month, total, LAG(total) OVER (ORDER BY month) AS previous,\n       total - LAG(total) OVER (ORDER BY month) AS change\n"
        "FROM monthly\nORDER BY month;",
        setup=SALES, require=[r"(?i)\bLAG\s*\("]),
)

# ------------------------------------------------------------------ Advanced: event booking system
SCHEMA = """CREATE TABLE venues (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  capacity INTEGER NOT NULL CHECK (capacity > 0)
);
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  venue_id INTEGER NOT NULL REFERENCES venues(id),
  title TEXT NOT NULL,
  day TEXT NOT NULL
);
CREATE TABLE bookings (
  event_id INTEGER NOT NULL REFERENCES events(id),
  email TEXT NOT NULL,
  seats INTEGER NOT NULL CHECK (seats BETWEEN 1 AND 4),
  PRIMARY KEY (event_id, email)
);"""

TRIGGER = """
CREATE TRIGGER no_overbooking BEFORE INSERT ON bookings
BEGIN
  SELECT RAISE(ABORT, 'event is full')
  WHERE (SELECT COALESCE(SUM(seats), 0) FROM bookings WHERE event_id = NEW.event_id) + NEW.seats
        > (SELECT v.capacity FROM events e JOIN venues v ON v.id = e.venue_id WHERE e.id = NEW.event_id);
END;"""

VIEW = """
CREATE VIEW event_report AS
SELECT e.title, v.name AS venue, v.capacity,
       COALESCE(SUM(b.seats), 0) AS booked,
       v.capacity - COALESCE(SUM(b.seats), 0) AS free
FROM events e
JOIN venues v ON v.id = e.venue_id
LEFT JOIN bookings b ON b.event_id = e.id
GROUP BY e.id;"""

DATA = ("INSERT INTO venues VALUES (1, 'Hall', 5), (2, 'Lab', 2); "
        "INSERT INTO events VALUES (1, 1, 'SQL Night', '2026-11-01'), (2, 2, 'Rust Lab', '2026-11-02'); ")

ADVANCED = project(
    "Project: Event booking system",
    "Design the database behind an event-booking site. You'll build it up in three steps, each continuing from your "
    "previous script:\n\n1. Tables with keys and constraints.\n2. A trigger that refuses overbooking.\n3. A reporting view.",
    run("Step 1 - Create venues(id, name UNIQUE, capacity > 0), events(id, venue_id → venues, title, day) and "
        "bookings(event_id → events, email, seats 1-4) with PRIMARY KEY (event_id, email). The checks insert good and bad "
        "rows.", "sql",
        [t("valid data", append=DATA + "INSERT INTO bookings VALUES (1, 'a@x.io', 2); SELECT COUNT(*) FROM bookings;"),
         t("constraints", append=DATA + "INSERT OR IGNORE INTO bookings VALUES (1, 'a@x.io', 2); INSERT OR IGNORE INTO bookings VALUES (1, 'a@x.io', 1); "
                                        "INSERT OR IGNORE INTO bookings VALUES (1, 'b@x.io', 9); INSERT OR IGNORE INTO venues VALUES (3, 'Hall', 10); "
                                        "INSERT OR IGNORE INTO venues VALUES (4, 'Tiny', 0); SELECT (SELECT COUNT(*) FROM bookings), (SELECT COUNT(*) FROM venues);")],
        ["1", "1|2"], SCHEMA, require=[r"(?i)PRIMARY\s+KEY\s*\(\s*event_id\s*,\s*email\s*\)", r"(?i)\bCHECK\b"]),
    run("Step 2 - Add a BEFORE INSERT trigger no_overbooking on bookings that aborts with 'event is full' when the new "
        "seats would exceed the venue's capacity.", "sql",
        [t("fits", append=DATA + "INSERT INTO bookings VALUES (1, 'a@x.io', 3); INSERT INTO bookings VALUES (1, 'b@x.io', 2); "
                                 "SELECT SUM(seats) FROM bookings;"),
         # the refused booking aborts the script, so nothing is printed; without the trigger the count prints
         t("full", append=DATA + "INSERT INTO bookings VALUES (2, 'a@x.io', 2); INSERT INTO bookings VALUES (2, 'b@x.io', 1); "
                                 "SELECT COUNT(*) FROM bookings;")],
        ["5", ""], SCHEMA + TRIGGER, starter=SCHEMA, carry=True, require=[r"(?i)CREATE\s+TRIGGER", r"(?i)RAISE\s*\("]),
    run("Step 3 - Add a view event_report(title, venue, capacity, booked, free) with one row per event (events with no "
        "bookings show 0 booked).", "sql",
        [t("report", append=DATA + "INSERT INTO bookings VALUES (1, 'a@x.io', 3); SELECT * FROM event_report ORDER BY title;")],
        ["Rust Lab|Lab|2|0|2\nSQL Night|Hall|5|3|2"], SCHEMA + TRIGGER + VIEW, starter=SCHEMA + TRIGGER, carry=True,
        require=[r"(?i)CREATE\s+VIEW"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
