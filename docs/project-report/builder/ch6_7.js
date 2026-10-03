const fs = require("fs");
const L = require("./lib");
const { p, bullets, lb, h2, h3, h4, chapter, table, captionTable, guideReport, figure, ph, run } = L;
const T = "CODEINGO";
const routes = JSON.parse(fs.readFileSync(L.ROOT + "/data_routes.json", "utf8"));

const SHOTS = [
  ["6.1", "User sign-in and entry", [
    ["01-landing-light.png", "Landing page (light theme)", "The first page offers Google sign-in, a passkey button and the consent line with links to the Privacy Policy and Terms. The gradient headline and blue accent follow the light theme."],
    ["02-landing-dark.png", "Landing page (dark theme)", "The same page in the black/green dark theme. The theme can be switched at any time and is remembered."],
    ["03-email-code.png", "2-step verification by e-mailed code", "After Google sign-in the learner enters the 6-digit code sent to the e-mail address. Authenticator app and passkey are alternatives."],
  ]],
  ["6.2", "Learning", [
    ["04-learn-light.png", "Course list (light)", "All ten courses with colour-coded tiles and progress."],
    ["05-learn-path-light.png", "Learning path", "Units and lessons in order; later lessons and chapter tests are locked until the learner reaches them."],
    ["06-learn-dark.png", "Learning path (dark)", "The path in the dark theme with per-section colours."],
    ["07-lesson-intro.png", "Lesson introduction", "Each lesson begins with a short explanation and an example."],
    ["08-lesson-question.png", "Lesson question", "Questions are multiple choice, fill-in-the-blank or code exercises."],
    ["08b-lesson-wrong.png", "Wrong answer feedback", "A wrong answer costs a heart and shows an explanation; an AI hint is available outside tests."],
    ["09-lesson-run-correct.png", "Running code in the browser", "The learner's program runs in a sandbox in the browser and the output is compared with the expected result on the server."],
    ["10-lesson-complete.png", "Lesson complete", "XP, streak and badge rewards are shown at the end of a lesson."],
    ["14-typescript-type-error.png", "TypeScript type error", "The TypeScript course type-checks the program with the real compiler and reports errors with line numbers."],
    ["15-git-terminal.png", "Git terminal", "The Git course offers a terminal that simulates a repository in the browser."],
  ]],
  ["6.3", "Tests, practice and daily challenge", [
    ["11-test-intro.png", "Chapter test introduction", "A chapter test has eight questions; six correct answers unlock the next unit."],
    ["12-test-question.png", "Chapter test question", "During a test hints are disabled and a countdown is shown."],
    ["13-test-result.png", "Chapter test result", "The result page shows the score and XP earned."],
    ["16-practice-hub.png", "Practice hub", "Missed questions are collected and scheduled for review using Leitner boxes."],
    ["17-practice-question.png", "Practice question", "Practice sessions give small rewards."],
    ["18-daily.png", "Daily challenge", "A new challenge each day keeps the streak going."],
  ]],
  ["6.4", "Social features and contests", [
    ["19-leagues-everyone.png", "Weekly league (everyone)", "Learners are ranked by XP earned this week; no e-mail addresses are shown."],
    ["20-leagues-friends.png", "Weekly league (friends)", "Adding a friend by friend code lets learners compete with friends."],
    ["21-contests.png", "Contests list", "A timed contest of ten questions opens every week."],
    ["22-contest-board.png", "Contest leaderboard", "The board ranks by score and then by time."],
    ["23-contest-running.png", "Contest in progress", "Everyone gets the same questions and a time limit."],
  ]],
  ["6.5", "Progress, profile and certificate", [
    ["24-progress-light.png", "Progress (light)", "XP, streak, badges and activity of the learner."],
    ["25-progress-dark.png", "Progress (dark)", "The progress page in the dark theme."],
    ["26-profile.png", "Profile and security", "Passkeys, authenticator app, install-as-app, reminder e-mails and the data and privacy section."],
    ["27-certificate.png", "Certificate", "A certificate is issued when a course is complete and can be verified publicly by its code."],
    ["30-privacy.png", "Your data (export and delete)", "The learner can download all personal data or delete the account after a 2-step code."],
  ]],
  ["6.6", "Administration", [
    ["28-admin-users.png", "Admin: users and roles", "Only an admin sees this area. Granting admin needs a confirmation code and is logged."],
    ["29-admin-audit.png", "Admin: audit log", "Security-relevant events (sign-ins, role changes, deletions) are listed."],
    ["31-admin-hidden-404.png", "Admin area hidden from learners", "A learner who opens an admin address sees an ordinary \"not found\" page."],
    ["35-database.png", "Database tables", "A view of the PostgreSQL tables created by the application."],
  ]],
  ["6.7", "Mobile view", [
    ["32-phone-learn.png", "Phone: learning path", "The layout adapts to a phone screen (390 px)."],
    ["33-phone-leagues.png", "Phone: leagues", "Leagues on a phone."],
    ["34-phone-learn-dark.png", "Phone: dark theme", "The dark theme on a phone."],
  ]],
];

function ch6() {
  const out = [chapter(6, "Results and Discussion"), h2("6.1", "Screenshots of the system"), p("This chapter shows the finished system. The screenshots were captured from the running application with demonstration data. Each screen is followed by a short discussion."),];
  let n = 0;
  SHOTS.forEach(([id, title, items], gi) => {
    out.push(h3(`6.1.${gi + 1}`, title));
    for (const [file, cap, text] of items) {
      n++;
      const phone = file.startsWith("3") && /phone/.test(file);
      out.push(...figure(`shots/${file}`, `Figure 6.${n}`, cap, { maxW: phone ? 220 : 560, maxH: phone ? 400 : 330 }), p(text));
    }
  });
  out.push(
    h2("6.2", "Discussion of results"),
    p("The objectives set in Chapter 1 were met. The platform provides ten courses with real code execution in the browser, game elements that the survey found appealing, projects at the end of every section, and social features. The security design (mandatory 2-step verification, hidden admin area, rate limiting, signed tokens) was checked by automated tests."),
    captionTable("Table 6.2.1", "Survey finding and how the finished system answers it"),
    table([3300, 5726], ["Survey finding", "Result in Codeingo"], [
      ["Confusing syntax is the main difficulty (13 of 40)", "Short lessons, hints, instant feedback with explanations and in-browser practice."],
      ["Lack of guidance and no real-world use (8 + 8)", "A fixed learning path, readiness tests and three-step projects in every section."],
      ["Real projects are the best motivator (17 of 43)", "30 projects, each building on the learner's own code."],
      ["Friends and community (32 of 43 want some)", "Friend codes, leagues and weekly contests."],
      ["Videos preferred by many (13)", "Not provided; listed as future scope."],
    ], { size: 21, zebra: true }),
  );
  return out;
}
function ch6Report() {
  return guideReport("CHAPTER 6: RESULTS AND DISCUSSION", T, {
    overview: "In this period the finished system was run end to end and screenshots of all main screens were prepared in both themes and on a phone. The results were compared with the survey findings and the objectives of Chapter 1.",
    outcomes: "We learned to present results clearly with captions and short discussions, to check the work against the original requirements, and to see the system through the eyes of a first-time user.",
    challenges: "Taking clean screenshots needed demonstration data and a repeatable script. Some screens looked different in the dark theme and needed adjustment.",
  });
}

function ch7() {
  return [
    chapter(7, "Conclusion and Future Work"),
    h2("7.1", "Conclusion"),
    p("Codeingo shows that a game-like, project-oriented coding course can be delivered entirely as a web application that is secure and does not need the learner to install anything. The learner's code runs in the browser, so the server stays small and safe; grading on the server prevents answer copying; and a layered security design protects accounts and data."),
    p("Starting from a survey of 43 learners, the project delivered ten courses with 438 lessons, 2,130 exercises and 30 projects, seven kinds of gamification, friends and contests, certificates, a progressive web app, and an administration area. It is verified by 95 automated tests (on SQLite and PostgreSQL) and by running all 492 reference solutions."),
    h2("7.2", "Limitations"),
    ...bullets([
      "Java, C and C++ programs cannot run in the browser; they are checked on the server and need a sandboxed runtime to be installed for the full experience.",
      "The AI hint feature depends on an external AI service and an API key.",
      "Contests are not live in the sense of instant push updates; the board refreshes at short intervals.",
      "Learning content was written by the project team only and has not yet been reviewed by external teachers.",
      "The survey had 43 respondents from one region and age group, so its results are indicative rather than statistical.",
      "The platform has been tested with demonstration users and not yet with a large public audience.",
    ]),
    h2("7.3", "Future Scope"),
    ...bullets([
      "Video explanations and audio for lessons, as many survey respondents prefer videos.",
      "Live contests with push updates, team contests and a public contest archive.",
      "Native mobile apps and offline lesson downloads.",
      "More courses (Rust, Go, Kotlin, data science) and longer advanced tracks.",
      "Teacher dashboards and classrooms for colleges and schools.",
      "Content review by educators and adaptive difficulty based on learner performance.",
      "Accessibility audit and translations into Indian languages.",
    ]),
    h2("7.4", "Bibliography"),
    ...L.numbered([
      "FastAPI documentation, https://fastapi.tiangolo.com",
      "Next.js documentation, https://nextjs.org/docs",
      "SQLAlchemy 2.0 documentation, https://docs.sqlalchemy.org",
      "PostgreSQL 16 documentation, https://www.postgresql.org/docs/16/",
      "W3C Web Authentication (WebAuthn) Level 2 specification, https://www.w3.org/TR/webauthn-2/",
      "OWASP Cheat Sheet Series (Authentication, CSRF Prevention, Content Security Policy), https://cheatsheetseries.owasp.org",
      "Pyodide documentation, https://pyodide.org",
      "TypeScript compiler API, https://www.typescriptlang.org/docs",
      "S. Leitner, So lernt man lernen, Herder, 1972 (Leitner system for spaced repetition).",
      "Playwright documentation, https://playwright.dev",
      "Mozilla Developer Network, Progressive Web Apps, https://developer.mozilla.org/docs/Web/Progressive_web_apps",
      "Pressman R. S., Software Engineering: A Practitioner's Approach, McGraw-Hill.",
    ], "numbers10"),
  ];
}
function ch7Report() {
  return guideReport("CHAPTER 7: CONCLUSION AND FUTURE WORK", T, {
    overview: "The project was summarised, its limits were listed honestly and ideas for future work were written. The bibliography and annexures were prepared and the report was finalised.",
    outcomes: "We learned to judge our own work fairly, to separate what is finished from what is planned, and to cite sources.",
    challenges: "Deciding which limitations to state, and keeping the report consistent with the final code, took several revisions.",
  });
}

function annexes() {
  const out = [];
  L.toc.push({ level: 1, label: "", title: "Annexures", search: "ANNEXURES" });
  out.push(new (L.D.Paragraph)({ heading: L.D.HeadingLevel.HEADING_1, alignment: L.D.AlignmentType.CENTER, pageBreakBefore: true, spacing: { after: 360 }, children: [run("ANNEXURES", { bold: true, size: 40 })] }));
  out.push(h2("A", "Survey questionnaire"), p("A Google Form titled \"Coding Platform Interest Survey\" was answered by 43 people. The questions were:"),
    ...L.numbered(["Age group (under 15, 15-18, 19-22, 23+).", "Have you tried to learn coding before? (currently learning / tried and gave up / never tried).", "What was the hardest part of learning to code?", "Which learning style do you prefer? (videos, hands-on, games, interactive, reading).", "How appealing is a game-like coding app? (1 to 5).", "Which programming language would you like to learn first?", "What would motivate you most? (real projects, friends, points, certificates, curiosity).", "Would you prefer to learn alone, with a community, or a mix?", "If you quit a course before, why?", "Which learning platforms have you used before?"], "numbers6"));
  out.push(h2("B", "REST API endpoints"), p(`The back end exposes ${routes.length} endpoints. Interactive documentation is generated automatically by FastAPI in development.`));
  out.push(captionTable("Table B.1", "REST API endpoints"), table([900, 5326, 2800], ["Method", "Path", "Group"], routes.map((r) => [r.m, r.p, r.tag]), { size: 17, zebra: true }));
  out.push(h2("C", "Security controls"), table([3000, 6026], ["Control", "How it is done"], [
    ["Sign-in", "Google account + mandatory 2-step verification (e-mail code, authenticator app or passkey)."],
    ["Sessions", "Short-lived signed access token and rotating refresh token in HttpOnly, Secure, SameSite cookies."],
    ["CSRF", "Double-submit token header on every state-changing request."],
    ["Content-Security-Policy", "Per-request nonce; no inline script without nonce."],
    ["Rate limiting", "Per-IP and per-account limits, backed by Redis in production."],
    ["Secrets at rest", "Authenticator secrets encrypted with Fernet; e-mail codes stored hashed."],
    ["Admin area", "Hidden (404) for non-admins; role changes need a 2-step code; owners protected; all actions in an audit log."],
    ["Privacy", "Data export, account deletion with cascading removal, signed unsubscribe links."],
    ["Answer protection", "Expected answers never leave the server; very fast completions are refused."],
  ], { size: 21, zebra: true }));
  out.push(h2("D", "Installation and user guide"),
    h4("Running locally"),
    ...L.numbered(["Install Python 3.11+, Node.js 20+ and (optionally) Docker.", "Back end: create a virtual environment, run pip install -r requirements.txt, copy .env.example to .env and start uvicorn app.main:app.", "Front end: run npm install and npm run dev inside the frontend folder.", "Open http://localhost:3000, sign in and verify with the code (in development it is written to the server console)."], "numbers7"),
    h4("Deployment"),
    p("The repository contains render.yaml (API and Redis), a Vercel guide (front end) and docker-compose.yml. Production needs a PostgreSQL database, SMTP credentials, Google OAuth keys and an encryption key; the application refuses to start if a required secret is missing."),
    h4("Using the platform"),
    ...L.numbered(["Sign in with Google and complete 2-step verification.", "Pick a course and follow the path; finish lessons to earn XP and keep your streak.", "Pass chapter tests to unlock new units; take the readiness test to jump ahead.", "Use Practice for mistakes, the Daily challenge and the weekly Contest.", "Add friends with your friend code and watch the leagues.", "Complete a course to receive a certificate with a public verification link."], "numbers8"),
  );
  return out;
}
module.exports = { ch6, ch6Report, ch7, ch7Report, annexes };
