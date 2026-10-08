# PROXY_SECRET - stop forged IP addresses (rate-limit bypass)

**Problem.** The API limits requests per visitor IP. It learns the IP from the `X-Forwarded-For` header, which a
visitor can write themselves when they call the API address directly (`...onrender.com`). Without this setting they
could dodge every per-IP limit by sending a made-up IP each time.

**Fix.** The website (Vercel) adds a secret header to every API call it forwards. The API believes the visitor IP
only when that secret is present; for anyone else it uses the last entry of the header, which the host's edge adds
from the real connection and cannot be forged.

## Set it up (5 minutes)

1. Make a random value: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. **Render** -> `codeingo-redis-sg` -> Environment -> add `PROXY_SECRET` = that value -> Save (it redeploys).
3. **Vercel** -> project -> Settings -> Environment Variables -> add `PROXY_SECRET` = the SAME value (type: Secret,
   Production) -> then **Redeploy** the latest deployment.
4. Check: open the site and use it normally (rate limits must not trigger for ordinary use).

## Order matters a little
Set both sides before testing. If only Render has the secret, every visitor looks like the website's own IP and
shares one rate-limit bucket until Vercel has it too. If only Vercel has it, nothing changes (the API ignores it).

## Notes
- The API logs a warning at startup in production while `PROXY_SECRET` is empty.
- Calls that skip the website (for example the uptime monitor hitting `/api/health` directly) are limited by the
  last `X-Forwarded-For` entry, i.e. their real IP.
- Rotating: change it on both sides, Render first is fine; the brief mismatch only affects rate-limit bucketing.
