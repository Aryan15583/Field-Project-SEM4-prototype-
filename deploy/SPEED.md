# Making Codeingo respond in about a second

Most of the waiting is **distance and sleeping**, not code. Check these in order.

1. **Same region for everything.** Each answer you check is website -> API -> database. If they are in different
   continents every hop costs 100-300 ms. Put them in one region:
   - Neon: project region (Settings -> General). Pick the one closest to your learners.
   - Render: the service region (set when created - recreate the service if it is wrong).
   - Vercel: Project -> Settings -> Functions -> **Function Region** = the same region as Render.
2. **Keep the API awake.** Render's free plan sleeps after 15 minutes idle; the next visitor waits 30-60 s. Ping it
   every few minutes (details in "Keeping the API awake" below). A paid Render instance never sleeps.
3. **Neon wakes up too.** Neon's free compute suspends after 5 minutes idle (first query then takes ~1 s). Keep the
   API pinged (above) and use the **pooled** connection string (`-pooler` in the host).
4. **Render free is a small CPU.** If a page is still slow after 1-3, upgrade the Render instance (the cheapest paid
   plan is much faster than free).

What the code already does: compressed responses, an in-memory copy of the course structure (refreshed every minute
and when an admin edits), cached exercise data for answer checking, no needless database writes, and no extra
connection check before each request.

## Redis is optional on a single server
If you run ONE API instance (Render free/starter), set `ALLOW_NO_REDIS=true` and leave `REDIS_URL` empty: rate limits
then live in the server's memory. They reset when the server restarts and aren't shared between several instances -
add a Redis (`REDIS_URL`) as soon as you scale to more than one instance. (Render's free plan allows only one free
Key Value per account.)

## Keeping the API awake
Two pingers are better than one. Use both:

1. **UptimeRobot (recommended, free, no GitHub minutes).** uptimerobot.com -> sign up -> **Add New Monitor** ->
   Monitor Type **HTTP(s)** -> URL `https://YOUR-API.onrender.com/api/health` -> Monitoring Interval **5 minutes** ->
   Create. (cron-job.org works the same way.) It also emails you when the API is down.
2. **The `Uptime monitor` GitHub workflow** (every 10 minutes) as a backup. GitHub's scheduler is "best effort" and
   often runs 10-30 minutes late, so it alone can miss the 15-minute window. In a *private* repository each run also
   uses one of your free Actions minutes (about 4,300 a month at this rate, over the 2,000 free) - if the repo is
   private, rely on UptimeRobot and disable the workflow (Actions -> Uptime monitor -> ... -> Disable workflow).

Only ping the main API. The code runner (see RUNNER.md) should sleep when idle: Render's free plan gives about 750
service-hours a month in total, and one service awake around the clock already uses about 744 of them.

## What a wake-up costs, and what was removed
Waking a sleeping service = Render starting the container + Python importing the libraries + the app starting.
Start-up used to also re-check all ~950 lessons against the database (one query each, 1,200 queries in total). It now
compares one fingerprint of the curriculum and skips that work while the lessons are unchanged (it runs again by
itself after you deploy changed lessons). Our own Python code is also compiled when the image is built.

## Each learner loads only the course they use
- **Server:** the course list is a few light rows. The full lesson tree of a course is built only when someone opens that
  course (and kept for a minute), so a Python learner makes the server build Python, not all ten courses.
- **Browser:** the course you are on is fetched first. Once it is on screen, the other courses are fetched quietly one at a
  time in the background (the first after ~3 s, then one every ~1.5 s), so switching later is instant. Skipped when the
  device asks to save data.
- **Code runners** already load per language: opening a Python lesson loads Python, a Java lesson wakes the Java runner.
- **Not per user:** Render runs ONE server process for everybody, so it cannot start "a Python server" for one person and
  "a C server" for another. What is shared is only the part that has to be (the libraries and database connection).
