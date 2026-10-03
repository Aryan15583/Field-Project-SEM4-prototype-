const fs = require("fs");
const L = require("./lib");
const { run, p, bullets, numbered, lb, h2, h3, h4, chapter, table, captionTable, guideReport, figure, center } = L;
const T = "CODEINGO";
const schema = JSON.parse(fs.readFileSync(L.ROOT + "/data_schema.json", "utf8"));

// short, human descriptions of every column (shared names get the same text everywhere)
const D = {
  id: "Primary identifier", user_id: "Owner of the record (users.id); deleted with the user", course_id: "Course (courses.id)", unit_id: "Unit (units.id)", lesson_id: "Lesson (lessons.id)", exercise_id: "Exercise (exercises.id)", contest_id: "Contest (contests.id)",
  created_at: "Creation timestamp", started_at: "When it started", completed_at: "When it was finished", expires_at: "Expiry timestamp", issued_at: "Issue timestamp", earned_at: "When it was earned", updated_at: "Last update timestamp", passed_at: "When it was first passed", finished_at: "When the run finished", revoked_at: "When it was revoked", used_at: "When it was used", due_at: "When the item is due again",
  slug: "Short unique name used in URLs", title: "Display title", description: "Short description", icon: "Emoji icon", position: "Order position", key: "Stable curriculum key, e.g. python/3/1", section: "Section name (Beginner / Intermediate / Advanced)", intro: "Concept explanation shown before the exercises", xp_reward: "XP awarded for completing the lesson", is_project: "True for end-of-section project lessons", content_hash: "Hash of the lesson content (detects changes at start-up sync)",
  kind: "Exercise kind (mcq, fill, order, code, run) or test kind (unit / section)", prompt: "Question text", code: "Code shown with the question", data: "Public part (options, starter code, tests) as JSON", solution: "Private answer data as JSON, never sent to the browser", explanation: "Explanation shown after answering", hint: "Author hint",
  google_sub: "Google account identifier", email: "E-mail address (never shown to other users)", name: "Display name", avatar_url: "Profile picture URL", role: "learner or admin", is_active: "False when the account is disabled", last_login_at: "Last successful sign-in", token_version: "Increase to invalidate all access tokens",
  mfa_enabled: "True when 2-step verification is set up", mfa_method: "email or totp", totp_secret_enc: "Authenticator secret, encrypted (Fernet)", totp_pending_enc: "Secret during set-up, encrypted", totp_last_step: "Last accepted TOTP time-step (replay protection)", mfa_failed_count: "Consecutive wrong codes", mfa_locked_until: "Lock-out end time", email_code_hash: "Keyed hash of the emailed code (never the code)", email_code_expires_at: "Code expiry (10 minutes)", email_code_sent_at: "When the code was sent (resend cool-down)", email_code_attempts: "Wrong guesses for this code", email_code_window_start: "Start of the hourly send window", email_code_window_count: "Codes sent in the window",
  xp_total: "Total XP earned", streak_current: "Current streak in days", streak_best: "Best streak", last_active_date: "Last day with activity", hearts: "Hearts left", hearts_updated_at: "Heart refill reference time", daily_goal: "Daily XP goal", friend_code: "Shareable 8-character code", reminder_emails: "Whether streak reminder e-mails are on", last_reminder_on: "Day of the last reminder (max one a day)",
  completed_count: "Times completed", perfect: "True if finished without mistakes", first_completed_at: "First completion time", tested_out: "True if skipped via a readiness test", target: "unit:<id> or section:<course>:<name>", best_score: "Best score", attempts: "Number of attempts", exercise_ids: "Questions in this attempt (JSON list)", results: "Answers so far: {exercise id: correct}", pass_mark: "Score needed to pass", score: "Final score", passed: "True if passed", xp_awarded: "XP given for this attempt", mistakes: "Number of wrong answers", correct_ids: "Exercises answered correctly",
  box: "Leitner box 0-5", lapses: "Times forgotten", reviews: "Times reviewed", heart_awarded: "True if a heart was given back",
  holder_name: "Name printed on the certificate (snapshot)", course_title: "Course name printed on the certificate", lessons: "Number of lessons completed",
  follower_id: "User who follows", followee_id: "User being followed", week: "ISO week, e.g. 2026-W40", starts_at: "Contest start (Monday 00:00 UTC)", ends_at: "Contest end", time_ms: "Time taken in milliseconds",
  credential_id: "WebAuthn credential id (base64url)", public_key: "Public key only (private key stays on the device)", sign_count: "Signature counter (clone detection)", transports: "Authenticator transports", backed_up: "True for synced passkeys", last_used_at: "Last sign-in with this passkey",
  event: "Event name, e.g. login, mfa_failed", ip: "Client IP address", detail: "Short extra detail", token_hash: "Hash of the refresh token", family_id: "Token family (reuse detection)", user_agent: "Browser identification", code_hash: "Hash of the recovery code", badge: "Badge key", amount: "XP amount", reason: "Why the XP was awarded", day: "Calendar day", correct: "True if answered correctly", challenge: "Random one-time challenge (base64url)", purpose: "register or login", mix: "",
};
const TYPE = (t) => t.replace(/\(.*\)/, "").replace("DATETIME", "DateTime").replace("INTEGER", "Integer").replace("BOOLEAN", "Boolean").replace("VARCHAR", "String").replace("TEXT", "Text").replace("JSON", "JSON").replace("DATE", "Date");
const TITLE = {
  users: "Account, security settings, gamification state", courses: "The ten courses", units: "Units (chapters) of a course", lessons: "Lessons and projects", exercises: "Questions and programs", user_lessons: "A learner's lesson progress", user_tests: "Best result per test", test_attempts: "One sitting of a chapter or readiness test", lesson_attempts: "One play-through of a lesson", review_items: "Spaced-repetition list", practice_attempts: "Practice sessions", certificates: "Issued certificates", follows: "Friend relations", contests: "Weekly contests", contest_entries: "A learner's single timed run", passkeys: "WebAuthn credentials", audit_log: "Security audit log", refresh_tokens: "Rotating refresh tokens", xp_events: "XP history", user_badges: "Earned badges", recovery_codes: "Authenticator recovery codes", webauthn_challenges: "One-time passkey challenges", daily_claims: "Daily challenge answers",
};
const ORDER = ["users", "courses", "units", "lessons", "exercises", "user_lessons", "lesson_attempts", "user_tests", "test_attempts", "review_items", "practice_attempts", "daily_claims", "certificates", "xp_events", "user_badges", "follows", "contests", "contest_entries", "passkeys", "webauthn_challenges", "recovery_codes", "refresh_tokens", "audit_log"];

function dataTables() {
  const out = [];
  ORDER.forEach((name, i) => {
    const cols = schema[name];
    out.push(p(`${i + 1}. ${name}`, { bold: true, after: 40, before: 160, keepNext: true }));
    out.push(captionTable(`Table 4.2.${i + 1}`, `${name} - ${TITLE[name]}`));
    out.push(table([2300, 1700, 5026], ["Field", "Type / Key", "Description"], cols.map(([c, t, k]) => [c, `${TYPE(t)}${k ? " / " + k : ""}`, D[c] || ""]), { size: 18, zebra: true, cantSplit: true }));
  });
  return out;
}

function ch4() {
  const mod = (n, title, items) => [h4(`${n}. ${title}`), ...bullets(items)];
  return [
    chapter(4, "System Design"),
    h2("4.1", "Basic Modules"),
    ...mod(1, "Authentication & Security Module", ["Signs users in with Google (OpenID Connect with PKCE) or a passkey.", "Requires 2-step verification: emailed code, authenticator app (TOTP) or passkey; issues HttpOnly session cookies and rotating refresh tokens.", "Provides recovery codes, lock-out after five wrong codes, rate limiting and CSRF protection.", "Writes security events to the audit log."]),
    ...mod(2, "Learning Path Module", ["Stores courses, units, lessons and exercises and synchronises the built-in curriculum at start-up.", "Decides which lessons are locked or unlocked, based on earlier lessons and passed chapter tests (old progress is grandfathered).", "Serves the lesson player with exercises, without the private solutions."]),
    ...mod(3, "Code Execution & Grading Module", ["Runs Python, JavaScript, TypeScript, SQL, HTML/CSS and Git programs in sandboxed Web Workers in the browser; optionally runs Java, C and C++ in a server sandbox.", "Grades every answer on the server by comparing the reported output with expected output that is never sent to the browser; checks required patterns so a program cannot simply print the answer.", "Blocks paste/drop in answer boxes and marks revealed answers as non-copyable."]),
    ...mod(4, "Tests & Practice Module", ["Chapter tests (8 questions, 6 to pass), readiness tests (15 questions, 12 to pass) with jump-ahead, no hearts lost and no hints during a test.", "Spaced-repetition practice: Leitner boxes with intervals of 0, 1, 3, 7, 16 and 35 days; sessions of ten questions.", "Daily challenge from a rotating course."]),
    ...mod(5, "Projects & Certificates Module", ["Thirty three-step projects (the last lesson of each section). Each step starts from the learner's own code of the previous step.", "A certificate with a random public code is issued once when all lessons and chapter tests of a course are complete; a public page verifies and prints it."]),
    ...mod(6, "Gamification Module", ["XP, daily goal, streaks, hearts that refill over time, fourteen badges.", "Progress page with charts of XP per day and lessons per language."]),
    ...mod(7, "Social & Contest Module", ["Friend codes, invite links, follow and unfollow, friends league beside the global weekly league.", "Weekly contest for every course: same ten questions for all, one ten-minute attempt, ranked by score then time, with a live (polled) leaderboard."]),
    ...mod(8, "Notification Module", ["Sends e-mail through SMTP over TLS: sign-in codes and optional streak reminders (once per day, atomic claim, signed one-click unsubscribe)."]),
    ...mod(9, "Administration & Content Module", ["Hidden from non-admins (the page and API answer 404). Edits lessons and exercises with server-side validation, disables users, searches users and audit log.", "Grants or removes admin access only after the acting admin re-enters a 2-step code; owner accounts (ADMIN_EMAILS) cannot be demoted."]),
    ...mod(10, "Account & Privacy Module", ["Download of all personal data as a JSON file; permanent account deletion (cascading) after a 2-step code.", "Privacy Policy and Terms of Service pages."]),
    ...mod(11, "Progressive Web App Module", ["Web-app manifest and icons, a service worker that caches static files and shows an offline page, an install button."]),

    h2("4.2", "Data Design"),
    p("Codeingo stores its data in a relational database (PostgreSQL in production, SQLite in development and tests) managed through SQLAlchemy models. There are 23 tables. Relations use foreign keys with ON DELETE CASCADE, so deleting a user removes everything that belongs to that user. The curriculum tables (courses, units, lessons, exercises) are synchronised from code at start-up and keyed by a stable key such as python/3/1, so learners' progress survives content updates. The Entity-Relationship diagram below shows the main tables; the field lists follow."),
    ...figure("figures/er.png", "Figure 4.2", "Entity-Relationship diagram (generated from the SQLAlchemy models)", { maxW: 600, maxH: 520 }),
    ...dataTables(),

    h2("4.3", "Logic Design"),
    p("The logic design shows how the layers of Codeingo are connected. The learner's browser runs the Next.js application and the sandboxed code runners. Requests reach the hosting edge (Vercel or nginx), which adds security headers and forwards /api requests to the FastAPI back end. The back end contains the authentication, learning, grading and administration services, and talks to PostgreSQL and Redis. External services are only Google sign-in and SMTP e-mail (and, optionally, an AI hint provider and a code sandbox)."),
    ...figure("figures/architecture.png", "Figure 4.3", "System architecture (logic diagram)", { maxW: 560, maxH: 520 }),
    h3("4.3.1", "Sign-in and 2-step verification flow"),
    ...numbered([
      "The learner chooses \"Continue with Google\" (or \"Sign in with a passkey\"). For Google, the server redirects with a random state, a nonce and a PKCE challenge; the callback verifies the ID token against Google's keys.",
      "The server creates or finds the user and sets a short-lived MFA cookie that proves only that the first step is done; no session exists yet.",
      "For e-mail codes the server generates a 6-digit code, stores only a keyed hash with a 10-minute expiry, and sends the code over SMTP. A wrong code counts toward a limit of five; a correct code is accepted once.",
      "On success the server starts a session: a short-lived access token and a rotating refresh token in HttpOnly cookies, plus a CSRF token. A passkey sign-in (user verification required) skips the e-mailed code because it already combines device and biometric/PIN.",
    ], "numbers4"),
    h3("4.3.2", "Answer grading flow"),
    ...numbered([
      "The browser asks for a lesson. The server returns the questions without solutions (for run exercises the expected outputs are also withheld).",
      "For a program the browser runs the learner's code in a worker, once for every test case, and sends the code and the printed outputs.",
      "The server compares the outputs with the stored expected outputs, checks the required and forbidden patterns, and replies correct/incorrect with the explanation. The correct answer is revealed only after the answer.",
      "The server records the result, updates the review list, awards XP, streak and badges, and, at the end of a course, issues the certificate. A minimum time per question and per lesson stops automation.",
    ], "numbers5"),
    h3("4.3.3", "Security design"),
    ...bullets([
      "Cookies: HttpOnly, Secure, SameSite=Strict; CSRF double-submit token and Origin check on every state-changing request.",
      "Content-Security-Policy with a fresh nonce per request; code workers get an even stricter policy (no network).",
      "Rate limiting per IP and per user (Redis); lock-out after five wrong 2-step codes; reuse detection for refresh tokens.",
      "Secrets: authenticator secrets encrypted with Fernet, e-mail codes and recovery codes stored only as hashes, passkeys store only public keys.",
      "Admin API answers 404 to non-admins; role changes need a fresh 2-step code and are audit-logged.",
    ]),

    h2("4.4", "User Interface Design"),
    p("The interface follows a Duolingo-style layout: a left sidebar on large screens and a bottom navigation bar on phones, a learning path in the centre and cards on the right. The diagram shows how the screens are connected."),
    ...figure("figures/screens.png", "Figure 4.4", "Screen map of Codeingo (user interface diagram)", { maxW: 600, maxH: 330 }),
    h4("Design system"),
    p("All colours are defined as CSS variables, so the two required themes swap by one class. Section accent colours (orange for Daily, violet for Practice, gold for Leagues, pink for Contests, teal for Progress, sky for Profile, red for Admin) re-colour the page using a tint class."),
    captionTable("Table 4.4.1", "Main colour tokens of the two themes"),
    table([2200, 2300, 2300, 2226], ["Token", "Light theme", "Dark theme", "Use"], [
      ["Background", "White #FFFFFF", "Black #000000", "Page background"],
      ["Primary", "Blue #1D6FF2", "Green #22C55E", "Buttons, active items, banners"],
      ["Text", "Near-black #0A0A0A", "Soft white #E8F5EC", "Body text"],
      ["Surface / raised", "#F4F7FF / white", "#0A0F0C / #101712", "Cards and panels"],
      ["Accents", "Violet, pink, orange, teal, sky, amber (deeper tones)", "Same hues, brighter tones", "Section colours, charts, badges"],
      ["Danger / success", "Red #EA2B2B", "Red #FF5454", "Mistakes, delete actions"],
    ], { size: 20, zebra: true }),
    p("", { after: 100 }),
    h4("Responsive and accessible behaviour"),
    ...bullets(["Layouts adapt from 320 px phones to 4K monitors; the root font size steps up on very large screens.", "All controls are reachable by keyboard with visible focus; charts have a table alternative; motion respects the reduced-motion setting.", "Text colours were chosen for contrast; light-theme accents are deeper so that white text on them stays readable."]),

    h2("4.5", "Work Break-Down Structure"),
    p("The project was divided into seven work packages: planning and survey, design, back end, front end, content, testing and quality, and deployment and documentation. The work break-down structure shows the main tasks of each package."),
    ...figure("figures/wbs.png", "Figure 4.5", "Work break-down structure of Codeingo", { maxW: 400, maxH: 600 }),
  ];
}

function ch4Report() {
  return guideReport("CHAPTER 4: SYSTEM DESIGN", T, {
    overview: "This chapter shows the design of Codeingo: eleven modules (authentication, learning path, code execution and grading, tests and practice, projects and certificates, gamification, social and contests, notifications, administration, privacy, progressive web app), the data design with 23 relational tables and an ER diagram generated from the code, the logic design with architecture, sign-in flow, grading flow and security design, the user-interface design with a screen map and colour tokens for both themes, and a work break-down structure.",
    outcomes: "We learned to design a system step by step and to make each module responsible for one thing. We learned relational design: foreign keys, unique constraints, cascading deletes and why a stable curriculum key keeps progress safe when lessons change. We understood spaced repetition (Leitner boxes), the idea of a security design with several layers, and how to describe flows in numbered steps. We learned to keep design colours in tokens so two themes can share one code base.",
    challenges: "Designing 23 tables and their relations without duplication was difficult. Deciding what must be deleted when a user deletes an account (and what must stay, such as an anonymous audit entry) needed several discussions. Designing the unlocking rules so that old progress is not lost, and designing the grading flow so that the answers never reach the browser, were the hardest logic problems. Drawing clear diagrams that fit on a page also took time.",
  });
}

module.exports = { ch4, ch4Report };
