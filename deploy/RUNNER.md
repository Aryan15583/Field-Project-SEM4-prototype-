# Make Java, C and C++ programs really run (the code runner)

Python, JavaScript, SQL and HTML run inside the learner's browser. Java, C and C++ need a compiler, so they run on a
small **separate service** (`runner/` folder): it has no database, no user data and no secrets except one shared key,
so a hostile program finds nothing worth taking.

Without it the three courses still work, but there is no **Run** button and answers are checked by patterns only.

## What the runner does to every program
- starts it as the unprivileged user `nobody` (it can't read the runner's own environment or key)
- fresh private folder per run, deleted afterwards; empty environment
- limits: CPU time, memory, number of processes, open files, output size, and a wall-clock timeout
- no network, **when the host allows it** (`/api/health` shows `"network_isolated": true/false`)
- only the Codeingo API can call it (shared key); the API already requires sign-in and rate-limits runs

On Render's free plan the host usually does *not* allow the network wall (`network_isolated: false`). The programs
still run as `nobody` with all the limits above, but they could open outbound connections. Nothing sensitive is on
the runner, and only signed-in learners reach it through the API, which is acceptable for a project like this.
For a public launch, put the runner on a host that allows network namespaces or use a paid sandbox service.

## Set it up (about 10 minutes)

1. Make a random key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. **Render** -> New -> **Web Service** -> pick this repo ->
   Name `codeingo-runner`, Region **Singapore**, Language **Docker**, **Root Directory `runner`**, Instance type Free.
   Add environment variable `RUNNER_KEY` = the key. Create. The first build takes a few minutes (it installs the
   compilers). (If you use the Blueprint, `render.yaml` already describes this service.)
3. When it says Live, open `https://codeingo-runner.onrender.com/api/health` (use your own address). You should see
   `{"status":"ok","languages":["c","cpp","java"],...,"configured":true}`.
4. **Render** -> `codeingo-redis-sg` (the API) -> Environment -> add
   `CODE_RUNNER_URL` = `https://codeingo-runner.onrender.com` (your runner's address, no trailing slash) and
   `CODE_RUNNER_KEY` = the same key. Save (it redeploys).
5. Open a Java, C or C++ lesson on the site: the **Run** button appears next to the editor.

## Notes
- The free runner sleeps when idle like the API. Opening a lesson with Java/C/C++ programs wakes it in the background,
  so it is usually ready by the time the learner reaches the program. If it is still asleep, **Run** shows
  "The code runner isn't available right now" and **Check** falls back to pattern checking, so nobody is blocked.
- Each request compiles once and runs all the test inputs. Java is slower than C (the JVM starts for every test).
- Changing the key: change it on both services.
