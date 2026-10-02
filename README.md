# Codeingo `</>`

**Duolingo, but for coding.** Codeingo is a gamified coding-learning platform: bite-sized lessons,
instant feedback, XP, streaks, hearts, badges, daily challenges, a weekly leaderboard and AI hints,
across **Python, JavaScript, TypeScript, Java, C++, C, SQL, HTML/CSS, Git and Data Structures & Algorithms**.

Built to the Codeingo project specification (Chapters 1–3): **Next.js (App Router, React 19) + Tailwind + Recharts**
frontend, **FastAPI (Python) + PostgreSQL** backend, REST + JWT, optional LLM tutor
(OpenAI / Mistral / Llama 3 through any OpenAI-compatible API).

| Light - white · blue · black | Dark - black · green |
|---|---|
| ![Learning path, light](docs/screenshots/learn-light.png) | ![Learning path, dark](docs/screenshots/learn-dark.png) |
| ![Lesson feedback](docs/screenshots/lesson-light.png) | ![Progress dashboard](docs/screenshots/progress-dark.png) |
| ![Mandatory 2-step verification](docs/screenshots/2fa-setup.png) | ![Wrong answer feedback](docs/screenshots/lesson-wrong.png) |
| ![Lesson popover on the path](docs/screenshots/path-popover.png) | ![Word bank](docs/screenshots/word-bank.png) |
| ![Lesson complete with confetti](docs/screenshots/lesson-complete.png) | ![Mobile](docs/screenshots/mobile.png) |

---

## Features

- **Sign in with Google (Gmail)** - OpenID Connect with PKCE, `state` and `nonce`; ID tokens verified against Google's keys.
- **Mandatory 2-step verification** for every account - a 6-digit code **emailed** at sign-in (default, no app needed), or an
  authenticator app (Google Authenticator, Authy, 1Password…) with 10 single-use recovery codes for extra security.
- **Passkeys** - add one in your profile, then sign in with Face ID, a fingerprint, your screen lock or a security
  key (WebAuthn, user verification required - so it counts as both factors and skips the emailed code).
- **Installable app (PWA)** - "Install the app" in the sidebar/profile (or Add to Home Screen on iPhone): full-screen,
  its own icon and shortcuts, an offline page, and cached static files and code runtimes for fast starts. The API is
  never cached.
- **Beginner → Intermediate → Advanced** - 10 courses, **438 lessons / 2,130 exercises** (incl. 30 projects): 7 languages
  × 16 units, plus 8-unit courses in TypeScript, Git and DSA - from "Hello, World" to generators, async/await, generics,
  templates & move semantics, window functions, `:has()`, ARIA, merge conflicts and dynamic programming (tables below).
- **Real code, really run** - every lesson ends with a program the learner writes and runs:
  Python (Pyodide/WebAssembly), JavaScript, SQL (SQLite/WebAssembly) and HTML/CSS run **in the browser**;
  Java, C and C++ run in an optional **sandboxed server runner** (Piston) - or fall back to pattern checks.
- **Learning path** - courses → sections → units → lessons, unlocked in order, on a winding Duolingo-style map with
  section headers, per-section progress and quick jumps between sections.
- **Chapter tests** - every unit ends with an 8-question test (6 to pass) drawn from its lessons; passing unlocks the
  next unit. **Readiness tests** - 15 questions (12 to pass) on everything before Intermediate or Advanced: pass to
  jump straight there. Tests are graded on the server, never cost hearts, allow no hints and give new questions each try.
- **Practice (spaced repetition)** - every question you miss in a lesson, test or daily challenge goes on your review
  list; questions you know come back after 1, 3, 7, 16 and 35 days (Leitner boxes). 10-question sessions serve what's
  due first, then your weakest items; they earn +10 XP (5 sessions a day) and a heart back, and never cost hearts.
- **Projects** - every section ends with a 3-step build project (21 in all: a grade book, a shopping cart, a route
  planner, an event-booking database, an accessible landing page...). Each step starts from your own code of the step
  before, so you finish with one real program; a wrong step is retried in place.
- **Certificates** - finish every lesson, project and chapter test of a course to get a certificate with a public,
  printable verify page (`/certificate/<code>`, no sign-in needed) - listed on your profile.
- **5 exercise types** - multiple choice, fill-in-the-blank, arrange-the-code, write-a-snippet, write-and-run a program.
- **Gamification** - XP, daily goal, streaks, 5 hearts that refill over time, 14 badges, daily challenge, weekly league.
- **Friends** - everyone gets a friend code (`ABCD-2345`) and an invite link (`/leaderboard?add=CODE`); follow friends
  (or anyone from the league) to race them in your own **friends league**. Only display names are ever shown.
- **Weekly contests** - every language gets a new contest each Monday: the same 10 questions for everyone, one
  10-minute timed run each, ranked by score then speed, with a **live leaderboard** (shows who's answering right now).
  Graded on the server; only right/wrong is shown while it's live; no hints; +3 XP per correct answer.
- **Streak reminder emails** - one evening email when your streak would end tonight (at most once a day, never if
  you already practised). Turn them off in your profile or with the signed one-click unsubscribe link in each email.
- **AI tutor "Codi"** - hints that nudge without giving away the answer (falls back to author hints if no AI is configured).
- **Progress dashboard** - XP over time and lessons per language (Recharts), achievements.
- **Admin panel** - edit lessons/exercises (validated server-side), enable/disable users, security audit log.
- **Responsive, phone to QHD/4K** - mobile bottom navigation, desktop sidebar; on big monitors the whole UI scales up
  (root size 112.5% at 1920px, 125% at 2400px - e.g. 2560×1440 - and 150% at 3200px). Everything is vector, so it stays sharp.
- **Codi, the pixel-art mascot** - blue in light mode, green-on-terminal in dark mode; bobs, blinks, follows your
  cursor, reacts to right/wrong answers, thinks while a hint loads, celebrates finished lessons and hops when tapped.
- **Duolingo-style feel at 60 fps** - springy 3D buttons, tap-to-open lesson popovers, sticky unit banners,
  word-bank tiles that fly into place, sliding exercise cards, slide-up feedback sheet, "N in a row" combos,
  heart-loss and XP count-up animations, confetti finish, sound effects & haptics (toggle in Profile).
  Every animation moves only `transform`/`opacity` (compositor-only) via [Motion](https://motion.dev), respects
  `prefers-reduced-motion`, and measured a steady 60 fps in a headless-Chromium frame-timing run.

## Security

See **[SECURITY.md](SECURITY.md)** for the full threat model. Highlights:

- Google sign-in + **required 2FA**: emailed one-time codes (hashed, 10-minute, single-use, resend-throttled) or TOTP with replay protection; lockout after 5 failures; hashed single-use recovery codes; TOTP secrets **encrypted at rest** (Fernet).
- Short-lived JWT access tokens (15 min) + **rotating refresh tokens with theft/reuse detection**; "log out of all devices" revokes everything instantly.
- Cookies are `HttpOnly`, `Secure`, `SameSite=Strict`; **CSRF** double-submit token + Origin check.
- **Rate limiting at two layers** (nginx `limit_req`/`limit_conn` + Redis-backed app limits), request-size caps, slowloris timeouts, bounded DB pool and statement timeouts → application-layer DDoS resistance. Put Cloudflare (or similar) in front for volumetric DDoS.
- Strict **Content-Security-Policy with a fresh nonce per request** (Next.js `proxy.js`), HSTS, `X-Frame-Options: DENY`, `nosniff`, COOP, Permissions-Policy.
- Answers are graded **server-side only** and never sent to the browser before answering; user code is **never executed** (pattern-matched with ReDoS-safe timeouts).
- ORM-only DB access (no SQL injection), strict Pydantic validation, no stack traces leaked, audit log of security events.
- Production **refuses to start** with weak secrets, dev login enabled, non-HTTPS URL, or SQLite.

## Curriculum

Every course has three sections: **Beginner**, **Intermediate** and **Advanced** - units 1-8 / 9-12 / 13-16 in the
16-unit courses, 1-4 / 5-6 / 7-8 in TypeScript, Git and DSA.

### Beginner

| Course | Units (3 lessons each) |
|---|---|
| Python | First steps · Variables & input · Text · Decisions · Loops · Lists · Dicts, tuples & sets · Functions & errors |
| JavaScript | First steps · Variables & types · Decisions · Loops · Functions · Arrays (map/filter/reduce) · Objects & JSON · Strings, classes & errors |
| Java | First programs · Types · Decisions · Loops · Methods · Arrays & ArrayList · Classes & objects · Inheritance, interfaces & exceptions |
| C++ | First programs · Types & strings · Input & decisions · Loops · Functions & references · Vectors & algorithms · Classes · Pointers, maps & smart pointers |
| C | First programs · Types & printf · scanf & decisions · Loops · Functions & recursion · Arrays & strings · Pointers · Structs & malloc |
| SQL | SELECT · WHERE · ORDER BY & NULL · Aggregates · HAVING & CASE · Joins · INSERT/UPDATE/DELETE · Schema, constraints & subqueries |
| HTML & CSS | HTML basics · Links, images & lists · Semantic structure, tables & forms · Selectors & text · Box model · Flexbox & Grid · Styling & positioning · Responsive & accessible |

### Intermediate & Advanced

| Course | Intermediate (units 9-12) | Advanced (units 13-16) |
|---|---|---|
| Python | Comprehensions & iteration · Functions in depth · Modules & files · Object-oriented Python | Pythonic objects · Iterators & generators · Functional tools & decorators · Professional Python |
| JavaScript | Modern syntax · Functions as values · Arrays & objects in depth · Classes in depth | Asynchronous JavaScript · Errors, iterators & generators · Functional patterns · Data structures & algorithms |
| Java | Strings & utilities · Collections · Polymorphism & interfaces · Exceptions in depth | Generics · Lambdas & streams · Modern Java · Algorithms & concurrency |
| C++ | STL containers · References & memory · Classes in depth · Streams & strings | Templates · Modern C++ · STL algorithms · Algorithms |
| C | Safer strings · Pointers in depth · Dynamic memory in depth · Types & sorting | Linked data structures · Bits & bytes · Preprocessor & program structure · Algorithms in C |
| SQL | Functions · Combining queries · Subqueries & CTEs · Window functions | Schema design · Indexes, views & performance · Transactions & triggers · Advanced querying |
| HTML & CSS | Forms in depth · Selectors & the cascade · Layout in depth · Responsive design | Custom properties & theming · Motion · Modern CSS · Accessibility & production |

### TypeScript, Git and Data Structures & Algorithms (8 units each)

| Course | Beginner (1-4) | Intermediate (5-6) | Advanced (7-8) |
|---|---|---|---|
| TypeScript | Types basics · Functions · Objects & interfaces · Unions & narrowing | Classes & enums · Generics | Type-level tools (utility, mapped & conditional types) · Real-world TS (unknown & guards, async, never) |
| Git | Getting started · History & changes · Undoing things · Branches | Merging & conflicts · Stash, tags & remotes | Rewriting history (reset, revert) · Team workflows (PRs, rebase, secrets) |
| DSA (Python) | Big-O · Arrays & two pointers · Hashing · Stacks & queues | Searching & sorting · Recursion & linked lists | Trees & heaps · Graphs & dynamic programming |

Projects - TypeScript: typed shopping cart · generic data store · type-safe API client. Git: first website repo ·
hotfix during a feature · team release. DSA: undo/redo editor · library catalogue · metro route planner.

Each lesson: a short concept intro, quick-check exercises, and a program to write. Lessons live in
`backend/app/curriculum/<language>.py` and are synced into the database at start-up (new lessons are
added, changed ones updated in place, admin-edited ones left alone). Intermediate and advanced units
live in `<language>_adv.py`; learners' existing progress is kept when new units are added.
Section projects live in `projects_<language>.py` (`project()` + `run(..., carry=True)` in `curriculum/dsl.py`)
and are added as the last lesson of each section's final unit.

**Every runnable exercise is verified by execution** - `python backend/scripts/validate_curriculum.py`
runs each reference solution with the real toolchain (python3, Node + the browser runners' own code,
sql.js, the TypeScript compiler, the Git simulator, Chromium, javac, gcc, g++), checks it prints exactly the expected output, and checks the
starter code does *not* pass. CI runs it on every push.

### How code is run and graded

- **Browser languages** run in the learner's own browser inside Web Workers (never on the page's
  main thread, so the UI stays at 60 fps) with a time limit, no network access and their own tight CSP.
  The browser reports what the program printed; the **server compares it with expected output it
  never sends to the browser**, plus optional structure checks (e.g. "must use a loop").
- **TypeScript** is type-checked (strict) by the real TypeScript compiler inside the worker, then run like JavaScript;
  a type error fails the exercise. Tests can append `// @ts-expect-error` lines, so overly loose types (`any`) fail too.
- **Git** runs in an in-memory Git simulator (`public/runners/git-sim.mjs`: init, add, commit, log, branch, switch,
  merge with conflicts, restore, reset, revert, stash, tag, .gitignore, simulated remotes). Only the output of each
  test's check commands is graded, so learners can explore with extra commands freely.
- **Java / C / C++** go to a self-hosted [Piston](https://github.com/engineer-man/piston) sandbox if
  `CODE_RUNNER_URL` is set (`docker compose --profile runner up -d`, then
  `docker compose exec runner piston ppm install java c c++`). Otherwise they're graded with patterns.
- The API server itself **never executes learner code**.

## Project layout

```
backend/            FastAPI app
  app/security/     tokens, 2FA, CSRF, rate limiting, headers
  app/routers/      auth, learn, stats, ai, admin
  app/services/     Google OAuth, grading, gamification, AI tutor
  app/curriculum/   the 7 courses (one module per language)
  app/seed.py       idempotent curriculum sync
  scripts/validate_curriculum.py   runs every reference solution
  tests/            pytest suite (security + learning flows)
frontend/           Next.js 16 app (App Router) + Tailwind + Recharts
  app/              routes: /, /2fa/*, /learn, /lesson/[id], /daily, /leaderboard, /stats, /profile, /admin
  proxy.js          per-request CSP nonce + security headers
  public/runners/   sandboxed code-runner workers (Python/JS/SQL) + shared output formatting
  lib/runners.js    starts/kills runner workers, renders HTML/CSS checks
  views/            page components   components/  shared UI   lib/  API client, auth, theme
deploy/             nginx (edge limits, headers), Caddy (automatic HTTPS)
docker-compose.yml  caddy -> nginx -> Next.js / FastAPI -> postgres/redis
```

## Run locally (development)

Requirements: Python 3.11+, Node 20.19+.

```bash
# 1. API
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cat > .env <<'EOF'
ENV=development
DEV_LOGIN_ENABLED=true            # password-less dev login (still requires 2FA). Never in production.
ADMIN_EMAILS=["you@example.com"]
PUBLIC_URL=http://localhost:3000
# Optional: real Google sign-in locally
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
# GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/google/callback
EOF
uvicorn app.main:app --reload --port 8000

# 2. Web (new terminal)
cd frontend
npm install
npm run dev          # http://localhost:3000  (Next rewrites /api to :8000)
```

On Windows, if `npm run dev` says *"Turbopack is not supported on this platform … native bindings are not available"*
(Smart App Control / Application Control blocks Next's native compiler), use the Webpack bundler instead:
`npm run dev:webpack` (and `npm run build:webpack` for production builds).

Windows PowerShell: activate the venv with `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

Open http://localhost:3000 and use **Dev sign in**. You'll be asked for a 6-digit code: with no mail server configured,
development mode prints it in the API terminal (look for a line starting `EMAIL (dev, not sent)`). To really send email,
add SMTP settings to `backend/.env` - for Gmail:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=you@gmail.com
# App password: Google Account → Security → 2-Step Verification → App passwords (remove the spaces)
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM=Codeingo <you@gmail.com>
```

Run the tests:

```bash
cd backend && pytest -q
```

## Deploy (production)

1. **Google OAuth client** - Google Cloud Console → *APIs & Services → Credentials → Create OAuth client ID → Web application*.
   Authorized redirect URI: `https://YOUR_DOMAIN/api/auth/google/callback`. Configure the OAuth consent screen (scopes: `openid email profile`).
2. **Configure** - `cp .env.example .env` and fill in every value (the file explains how to generate each secret).
3. **DNS** - point `DOMAIN` at your server; open ports 80/443.
4. **Start** - `docker compose up -d --build`. Caddy obtains an HTTPS certificate automatically.
5. **DDoS** - put the domain behind Cloudflare (proxied, "Under Attack" mode available) or another CDN/WAF for network-level floods.

Only Caddy publishes ports; nginx, the API, PostgreSQL and Redis sit on private networks, and the containers run read-only, as non-root, with all Linux capabilities dropped.

## Adding content

Sign in with an email listed in `ADMIN_EMAILS` → **Admin → Content**. Lessons are JSON:

| kind | public `data` | private `solution` |
|---|---|---|
| `mcq` | `{"options": [...]}` | `{"index": 0}` |
| `fill` | - (use `___` in `code`) | `{"accepted": ["print"]}` |
| `order` | `{"lines": [... in correct order ...]}` | `{}` (lines are shuffled when served) |
| `code` | `{"starter": ""}` | `{"patterns": ["regex", ...], "forbid": [], "example": "..."}` |
| `run` | `{"language": "python", "starter": "", "tests": [{"name", "stdin"/"append"/"selector"+"prop"}], "setup": "(sql)"}` | `{"expected": ["output per test"], "example": "reference", "require": [], "forbid": [], "fallback": [] (java/c/cpp)}` |

## Roadmap (from the specification)

Interview-prep tracks, collaborative coding, WebSocket push for contests (they poll today),
personalised recommendations (scikit-learn / PyTorch).
