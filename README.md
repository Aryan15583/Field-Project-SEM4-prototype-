# Codeingo `</>`

**Duolingo, but for coding.** Codeingo is a gamified coding-learning platform: bite-sized lessons,
instant feedback, XP, streaks, hearts, badges, daily challenges, a weekly leaderboard and AI hints,
across **Python, JavaScript, Java, C++, C, SQL and HTML/CSS**.

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
- **Mandatory 2-step verification** for every account - TOTP (Google Authenticator, Authy, 1Password…), 10 single-use recovery codes.
- **Beginner → Intermediate → Advanced** - 7 languages × 16 units × 3 lessons = **336 lessons / 1,680 exercises**, from
  "Hello, World" to generators, async/await, generics, templates & move semantics, linked structures, window functions,
  recursive CTEs, `:has()` and ARIA (see the tables below).
- **Real code, really run** - every lesson ends with a program the learner writes and runs:
  Python (Pyodide/WebAssembly), JavaScript, SQL (SQLite/WebAssembly) and HTML/CSS run **in the browser**;
  Java, C and C++ run in an optional **sandboxed server runner** (Piston) - or fall back to pattern checks.
- **Learning path** - courses → sections → units → lessons, unlocked in order, on a winding Duolingo-style map with
  section headers, per-section progress and quick jumps between sections.
- **5 exercise types** - multiple choice, fill-in-the-blank, arrange-the-code, write-a-snippet, write-and-run a program.
- **Gamification** - XP, daily goal, streaks, 5 hearts that refill over time, 8 badges, daily challenge, weekly league.
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

- Google sign-in + **required TOTP 2FA**, replay protection, lockout after 5 failures, hashed single-use recovery codes, TOTP secrets **encrypted at rest** (Fernet).
- Short-lived JWT access tokens (15 min) + **rotating refresh tokens with theft/reuse detection**; "log out of all devices" revokes everything instantly.
- Cookies are `HttpOnly`, `Secure`, `SameSite=Strict`; **CSRF** double-submit token + Origin check.
- **Rate limiting at two layers** (nginx `limit_req`/`limit_conn` + Redis-backed app limits), request-size caps, slowloris timeouts, bounded DB pool and statement timeouts → application-layer DDoS resistance. Put Cloudflare (or similar) in front for volumetric DDoS.
- Strict **Content-Security-Policy with a fresh nonce per request** (Next.js `proxy.js`), HSTS, `X-Frame-Options: DENY`, `nosniff`, COOP, Permissions-Policy.
- Answers are graded **server-side only** and never sent to the browser before answering; user code is **never executed** (pattern-matched with ReDoS-safe timeouts).
- ORM-only DB access (no SQL injection), strict Pydantic validation, no stack traces leaked, audit log of security events.
- Production **refuses to start** with weak secrets, dev login enabled, non-HTTPS URL, or SQLite.

## Curriculum

Every course has three sections: **Beginner** (units 1-8), **Intermediate** (9-12) and **Advanced** (13-16).

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

Each lesson: a short concept intro, quick-check exercises, and a program to write. Lessons live in
`backend/app/curriculum/<language>.py` and are synced into the database at start-up (new lessons are
added, changed ones updated in place, admin-edited ones left alone). Intermediate and advanced units
live in `<language>_adv.py`; learners' existing progress is kept when new units are added.

**Every runnable exercise is verified by execution** - `python backend/scripts/validate_curriculum.py`
runs each reference solution with the real toolchain (python3, Node + the browser runners' own code,
sql.js, Chromium, javac, gcc, g++), checks it prints exactly the expected output, and checks the
starter code does *not* pass. CI runs it on every push.

### How code is run and graded

- **Browser languages** run in the learner's own browser inside Web Workers (never on the page's
  main thread, so the UI stays at 60 fps) with a time limit, no network access and their own tight CSP.
  The browser reports what the program printed; the **server compares it with expected output it
  never sends to the browser**, plus optional structure checks (e.g. "must use a loop").
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

Open http://localhost:3000, use **Developer login**, scan the QR code with an authenticator app and start learning.

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

Interview-prep tracks, "jump ahead" placement tests, collaborative coding & real-time contests (WebSockets),
personalised recommendations (scikit-learn / PyTorch), WebAuthn passkeys.
