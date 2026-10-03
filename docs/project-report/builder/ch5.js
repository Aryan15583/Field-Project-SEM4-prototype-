const fs = require("fs");
const L = require("./lib");
const { run, p, bullets, numbered, lb, h2, h3, h4, chapter, table, captionTable, guideReport, figure, code } = L;
const T = "CODEINGO";
const snippets = JSON.parse(fs.readFileSync(L.ROOT + "/data_snippets.json", "utf8"));
const stats = JSON.parse(fs.readFileSync(L.ROOT + "/data_stats.json", "utf8"));
const cap = (src, n = 46) => { const l = src.split("\n"); return l.length > n ? l.slice(0, n).join("\n") + "\n    # ..." : src; };

function ch5Coding() {
  const tree = [
    "codeingo/",
    "|-- backend/                    FastAPI application (Python)",
    "|   |-- app/",
    "|   |   |-- main.py             application factory, middleware, routers",
    "|   |   |-- config.py, db.py    settings (validated in production), database engine",
    "|   |   |-- models.py           23 SQLAlchemy tables",
    "|   |   |-- routers/            auth, learn, checkpoints, practice, contests,",
    "|   |   |                       social, passkeys, account, stats, ai, admin",
    "|   |   |-- services/           grading, progress, review, contests, social,",
    "|   |   |                       certificates, reminders, mailer, gamification",
    "|   |   |-- security/           tokens, mfa, passkeys, ratelimit, middleware",
    "|   |   `-- curriculum/         10 courses + 30 projects (Python data)",
    "|   |-- scripts/validate_curriculum.py   runs every reference solution",
    "|   `-- tests/                  automated tests (pytest)",
    "|-- frontend/                   Next.js application",
    "|   |-- app/                    routes (App Router) + manifest",
    "|   |-- views/                  page components (Learn, Lesson, Practice, ...)",
    "|   |-- components/             shared UI (AppShell, Exercise, QuizRunner, ...)",
    "|   |-- lib/                    api client, auth, theme, PWA, WebAuthn, runners",
    "|   |-- public/runners/         sandboxed workers: Python, JS, TS, SQL, Git",
    "|   |-- proxy.js                per-request Content-Security-Policy",
    "|   `-- e2e/                    browser tests (Playwright)",
    "|-- deploy/                     nginx, Caddy, Vercel/Render guide",
    "|-- docker-compose.yml, render.yaml",
    "`-- README.md, SECURITY.md",
  ].join("\n");
  const lines = stats.code_lines;
  const out = [
    h2("5.1", "Coding"),
    p("This section shows the structure of the code and selected excerpts of the main modules. The complete source code is available in the project repository."),
    h3("5.1.0", "Project structure"),
    code(tree, { size: 16 }),
    p("", { after: 80 }),
    captionTable("Table 5.1.1", "Size of the code base (lines)"),
    table([4200, 2400, 2426], ["Part", "Lines", "Language"], [
      ["Back end application (without curriculum)", String(lines.backend_py), "Python"],
      ["Curriculum (10 courses, 30 projects)", String(lines.curriculum_py), "Python data"],
      ["Back end tests", String(lines.tests_py), "Python (pytest)"],
      ["Front end (pages, components, libraries)", String(lines.frontend_js), "JavaScript / JSX"],
      ["In-browser code runners", String(lines.runners_js), "JavaScript (modules)"],
    ], { size: 21, zebra: true }),
  ];
  for (const s of snippets) out.push(h3(s.id, s.title), code(cap(s.code, s.id === "5.1.8" ? 34 : 48)), p("", { after: 60 }));
  return out;
}

// ---------------------------------------------------------------- test cases (each one is an automated test that passes)
const TC = [
  // [group, case, description, input, expected, actual-note]
  ["Email Code Testing #1", "A correct emailed 6-digit code signs the user in.", "Code from the e-mail", "Sign-in completes; session cookies are set."],
  ["Email Code Testing #2", "A wrong code is refused.", "Code: 000000", "Error \"Invalid verification code\"; no session."],
  ["Email Code Testing #3", "An expired code is refused.", "Code used after 10 minutes", "Rejected; the user is asked to request a new code."],
  ["Email Code Testing #4", "A code can be used only once.", "The same correct code twice", "Second use is rejected."],
  ["Email Code Testing #5", "Lock-out after repeated wrong guesses.", "Five wrong codes in a row", "Further attempts are refused (HTTP 429) for a period."],
  ["Email Code Testing #6", "Resend cool-down and hourly cap.", "Request codes quickly and more than 6 per hour", "Cool-down message; hourly limit stops further sends."],
  ["Email Code Testing #7", "Reloading the page keeps the code the user is typing valid.", "Open the code page, reload, enter the first code", "The first code still works; only \"send new code\" replaces it."],
  ["Email Code Testing #8", "E-mail header injection is impossible.", "Address containing a line break", "Message is rejected; no extra headers are sent."],
  ["Email Code Testing #9", "Production refuses to start without SMTP.", "ENV=production without SMTP settings", "Start-up error naming the missing setting."],
  ["Session Security #1", "Protected data needs a session.", "GET /api/courses without sign-in", "HTTP 401 Unauthorized."],
  ["Session Security #2", "CSRF token is required for changes.", "POST without the X-CSRF-Token header", "HTTP 403; nothing is changed."],
  ["Session Security #3", "Forged and wrong-type tokens are rejected.", "Token signed with another key / refresh token used as access token", "HTTP 401."],
  ["Session Security #4", "Sign-in endpoints are rate-limited.", "25 sign-in requests in a minute", "HTTP 429 appears."],
  ["Passkey Testing #1", "A passkey can be added and used to sign in without a code.", "Software authenticator (real P-256 signatures)", "Registered; sign-in returns the same account."],
  ["Passkey Testing #2", "A captured sign-in response cannot be replayed.", "Send the same signed response twice", "Second attempt fails (challenge already used)."],
  ["Passkey Testing #3", "A phishing site's origin is rejected.", "Assertion with origin https://evil.example", "HTTP 400; not signed in."],
  ["Passkey Testing #4", "User verification is mandatory.", "Assertion without the user-verified flag", "Rejected."],
  ["Passkey Testing #5", "A wrong private key is rejected.", "Signature made by another key", "Rejected."],
  ["Passkey Testing #6", "Unknown credentials and disabled accounts are refused.", "Unregistered authenticator / disabled user", "HTTP 400 / HTTP 403."],
  ["Learning Testing #1", "Lessons unlock in order and the path shows sections and tests.", "GET course path as a new learner", "Only the first lesson is unlocked; chapter tests are locked."],
  ["Learning Testing #2", "Answers are graded on the server and not revealed in advance.", "Request lesson questions", "No solution fields in the response."],
  ["Learning Testing #3", "Finishing a lesson too fast is refused.", "Complete a lesson instantly", "HTTP 400 \"suspiciously fast\"."],
  ["Learning Testing #4", "A lesson attempt belongs to its owner.", "Another user completes the attempt", "HTTP 404."],
  ["Test Testing #1", "A chapter test needs 6 of 8 to pass and unlocks the next unit.", "Answer 8 correctly / all wrong", "Passed, +20 XP, next unit open / failed, retry with new questions."],
  ["Test Testing #2", "A readiness test lets the learner jump ahead.", "Pass the 15-question test (12 to pass)", "Earlier lessons marked tested out; next section unlocked."],
  ["Test Testing #3", "AI hints are blocked during an open test or contest.", "Ask for a hint for a test question", "HTTP 403; after the test, hints work again."],
  ["Practice Testing #1", "Missed questions enter the practice list; practice moves boxes.", "Miss a question, then answer it correctly in practice", "Item moves up a Leitner box; due date grows."],
  ["Practice Testing #2", "Practice reward limits.", "Finish 6 practice sessions in a day", "+10 XP and a heart for the first five only."],
  ["Project Testing #1", "Every section ends with a three-step project.", "Inspect all lessons flagged as projects", "30 projects, 3 run steps each, steps continue the learner's code."],
  ["Certificate Testing #1", "A certificate is issued only when everything is complete.", "Complete all lessons but not the last chapter test; then pass it", "No certificate first; then one certificate (issued once)."],
  ["Certificate Testing #2", "Public verification.", "Open /api/public/certificates/<code> signed out; try a fake code", "Certificate data returned; fake code gives 404."],
  ["Social Testing #1", "Follow a friend by friend code (case and dashes ignored).", "Code \"abcd-2345\"", "Friend added; Friendly badge awarded once."],
  ["Social Testing #2", "Invalid follow requests.", "Own code / unknown code / disabled account / bad characters", "HTTP 400 / 404 / 404 / 422."],
  ["Social Testing #3", "Leagues never expose e-mail addresses.", "Read global and friends leagues", "Only name, picture, code, streak and XP."],
  ["Reminder Testing #1", "One streak reminder per evening.", "Run the job twice on the evening the streak would end", "One e-mail; second run sends nothing."],
  ["Reminder Testing #2", "No reminder when it is not needed.", "Already active today / streak lost / opted out / disabled", "No e-mail is sent."],
  ["Reminder Testing #3", "A failed send is retried; unsubscribe is signed.", "Mail server down, then up; tampered link", "Retried later the same day; tampered link HTTP 400."],
  ["Contest Testing #1", "Everyone gets the same ten questions.", "Two users enter the same contest", "Identical question list; resume keeps the same run."],
  ["Contest Testing #2", "Score and ranking; no answers revealed live.", "Finish with 10/10 and with 1/10", "Ranked by score then time; no correct answer in responses."],
  ["Contest Testing #3", "Time limit and anti-automation.", "Answer instantly / after 11 minutes", "HTTP 429 / HTTP 410 and the run is closed."],
  ["Admin Testing #1", "Admin area is hidden from learners.", "Learner calls /api/admin/tree", "HTTP 404."],
  ["Admin Testing #2", "Granting admin needs a valid 2-step code.", "Wrong code, then the right code", "HTTP 400, then role changed; both audit-logged."],
  ["Admin Testing #3", "Owners and self are protected.", "Demote an owner; change own role; disable an owner", "HTTP 403 / 400 / 403."],
  ["Admin Testing #4", "Only finished accounts can become admins.", "Promote an account without 2-step set up", "HTTP 400."],
  ["Privacy Testing #1", "Data export has no secrets.", "GET /api/account/export", "JSON of own data; no tokens, hashes or other users' e-mails."],
  ["Privacy Testing #2", "Account deletion is complete.", "Delete with a valid 2-step code", "User and all linked rows removed; anonymous audit entry kept; session ended."],
  ["Privacy Testing #3", "Deletion needs the right code; owners cannot self-delete.", "Wrong code / owner account", "HTTP 400 / HTTP 403; account stays."],
  ["Database Testing #1", "The whole suite passes on PostgreSQL as well as SQLite.", "Run all tests with TEST_DATABASE_URL on PostgreSQL 16", "All tests pass on both databases."],
  ["Curriculum Testing #1", `Every reference solution is executed (${stats.runnable} runnable exercises).`, "scripts/validate_curriculum.py", `All ${stats.lessons} lessons / ${stats.exercises} exercises valid; starters do not pass.`],
];

function ch5Testing(totalTests) {
  const rows = TC.map((r, i) => [`T${String(i + 1).padStart(2, "0")}`, r[0], r[1], r[2], r[3], r[3], "Pass"]);
  const w = [650, 1650, 2750, 2500, 2850, 2850, 1428];
  const byFile = [["test_security.py", 16, "Session, CSRF, tokens, headers, admin, rate limits"], ["test_learning.py", 15, "Courses, lessons, answers, hearts, daily challenge"], ["test_email_codes.py", 14, "E-mail 2-step codes and mailer"], ["test_social.py", 11, "Friends, leagues, reminders, unsubscribe"], ["test_practice.py", 9, "Spaced repetition and practice sessions"], ["test_passkeys.py", 8, "WebAuthn passkeys"], ["test_checkpoints.py", 6, "Chapter and readiness tests"], ["test_contests.py", 6, "Weekly contests"], ["test_projects_certificates.py", 4, "Projects and certificates"], ["test_account.py", 3, "Data export and deletion"], ["test_admin_roles.py", 3, "Admin role management"]];
  return {
    intro: [
      h2("5.2", "Testing"),
      p("Testing combines four layers: automated back-end tests (pytest) that call the real API with an in-process client, a validation script that executes the reference solution of every exercise, manual and automated browser checks of the main flows, and security-oriented tests (CSRF, token forgery, rate limits, replay, hidden admin area). The whole back-end suite is run on SQLite and on PostgreSQL 16."),
      captionTable("Table 5.2.1", "Automated back-end tests by file"),
      table([3400, 1000, 4626], ["Test file", "Tests", "What it covers"], [...byFile.map(([f, n, d]) => [f, String(n), d]), ["Total", String(totalTests), "All pass on SQLite and on PostgreSQL 16"]], { size: 21, zebra: true }),
      p("", { after: 80 }),
      h3("5.2.1", "Test Cases"),
      p("The table on the following pages lists the main test cases. Every row corresponds to one or more automated tests in the repository that were executed, and all of them passed."),
    ],
    cases: [
      captionTable("Table 5.2.2", "Test cases"),
      table(w, ["Test ID", "Test Cases", "Test Description", "Input", "Expected Output", "Actual Output", "Result"], rows, { size: 16, zebra: true }),
    ],
    after: [
      h3("5.2.2", "Curriculum validation"),
      p(`Content quality is tested by scripts/validate_curriculum.py. For every exercise it checks the structure (options, a single blank, valid patterns, tests matching expected outputs) and that the exercise's own reference answer is accepted by the real grader. For each of the ${stats.runnable} program exercises it executes the reference solution with the real toolchain (python3, Node with the browser runners' own code, the TypeScript compiler, the Git simulator, sql.js, Chromium for HTML/CSS, javac, gcc and g++) and compares the output with the expected output, and it also checks that the empty starter code does not pass. The result for the final curriculum is: ${stats.courses} courses, ${stats.lessons} lessons, ${stats.exercises} exercises, ${stats.projects} projects - all valid. The same script runs in the continuous-integration pipeline on every push.`),
      captionTable("Table 5.2.3", "Curriculum size verified by execution"),
      table([3500, 1500, 1500, 2526], ["Course", "Units", "Lessons", "Projects"], [...stats.by_course.map((c) => [c.title, String(c.units), String(c.lessons), "3"]), ["Total", String(stats.by_course.reduce((a, c) => a + c.units, 0)), String(stats.lessons), String(stats.projects)]], { size: 21, zebra: true }),
      h3("5.2.3", "Observations from browser testing"),
      ...bullets([
        "The complete flow was driven in a real Chromium browser: sign-up with an e-mailed code, a lesson with a deliberate wrong answer, a chapter test, practice, daily challenge, leagues, a two-learner friend flow, a contest with a live board on a second device, certificate issue and public verification, hidden admin 404, role promotion with a confirmation code, account deletion.",
        "The first TypeScript run (which loads the compiler into the worker) took about 0.65 s; later runs took about 0.07 s.",
        "Type errors in TypeScript exercises are shown with line numbers and stop the run, as intended.",
        "The in-browser Git terminal showed the full session (commands and output) while only the check commands were graded.",
        "No horizontal scrolling appeared at a 390 px phone width on the pages tested, in both themes.",
      ]),
      h3("5.2.4", "Defects found and fixed during testing"),
      captionTable("Table 5.2.4", "Notable defects found by testing and how they were fixed"),
      table([700, 3200, 5126], ["No.", "Defect", "Fix"], [
        ["1", "A hydration warning appeared in the browser console (the mascot's blink delay used a random number on the server and another in the browser).", "The delay is now derived from a stable id, so server and browser render the same value; verified by temporarily reverting the fix."],
        ["2", "Reloading the e-mail code page replaced the code the learner was typing, so the correct-looking code was refused.", "A page load now reuses a still-valid code; only an explicit \"send a new code\" replaces it."],
        ["3", "The resend cool-down stayed active after a code had been used, blocking the next sign-in.", "The cool-down now applies only while a live code exists."],
        ["4", "Certificates were issued but not listed because SQLite returned time stamps without a zone.", "Dates are normalised to UTC before comparison."],
        ["5", "Automated sign-ins were blocked by the reverse proxy's rate limit during tests.", "Test scripts pace their requests; the number of start-up requests was reduced."],
        ["6", "The first TypeScript run timed out because the compiler was loaded before the message handler existed.", "The worker now attaches its handler first and waits for the compiler inside it."],
        ["7", "SQLite ignored cascading deletes, so account deletion left rows behind in development.", "Foreign-key enforcement is switched on for SQLite connections; the account tests pass on both databases."],
      ], { size: 20, zebra: true }),
    ],
  };
}

function ch5Report() {
  return guideReport("CHAPTER 5: IMPLEMENTATION AND TESTING", T, {
    overview: "This chapter shows the implementation: the project structure and selected code excerpts (application factory, e-mail code issue and verification, server-side grading, spaced repetition, passkey verification, contest ranking, in-browser TypeScript type checking, per-request content-security policy), and the testing: automated back-end tests on two databases, about fifty documented test cases with input, expected and actual output, execution of every reference solution, browser observations and a table of defects that were found and fixed.",
    outcomes: "We learned how a real project is organised in routers, services, models and views, and how to write code so that it can be tested. We learned test-case writing with ID, description, input, expected and actual output, and the value of security tests such as replay, wrong origin and token forgery. We learned that automated tests catch regressions when features are added, and that running the same tests on PostgreSQL finds differences that SQLite hides.",
    challenges: "Coding was the longest part. A hydration error caused by random values in the interface, the e-mail code that changed when the page reloaded, and the first TypeScript run that never started were difficult to find. Running the compiler and a Git simulator inside a locked-down worker was new for us. Writing tests for time (expiry, cool-downs, contest limits) needed fake clocks. Keeping all tests green after each change took discipline.",
  });
}

module.exports = { ch5Coding, ch5Testing, ch5Report, TC };
