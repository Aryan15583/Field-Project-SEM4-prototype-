# Making Codeingo respond in about a second

Most of the waiting is **distance and sleeping**, not code. Check these in order.

1. **Same region for everything.** Each answer you check is website -> API -> database. If they are in different
   continents every hop costs 100-300 ms. Put them in one region:
   - Neon: project region (Settings -> General). Pick the one closest to your learners.
   - Render: the service region (set when created - recreate the service if it is wrong).
   - Vercel: Project -> Settings -> Functions -> **Function Region** = the same region as Render.
2. **Keep the API awake.** Render's free plan sleeps after 15 minutes idle; the next visitor waits 30-60 s. The
   `Uptime monitor` GitHub workflow pings it every 10 minutes. A paid Render instance never sleeps.
3. **Neon wakes up too.** Neon's free compute suspends after 5 minutes idle (first query then takes ~1 s). Keep the
   API pinged (above) and use the **pooled** connection string (`-pooler` in the host).
4. **Render free is a small CPU.** If a page is still slow after 1-3, upgrade the Render instance (the cheapest paid
   plan is much faster than free).

What the code already does: compressed responses, an in-memory copy of the course structure (refreshed every minute
and when an admin edits), cached exercise data for answer checking, no needless database writes, and no extra
connection check before each request.
