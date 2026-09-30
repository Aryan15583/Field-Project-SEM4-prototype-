# Codeingo security design

This document lists the threats Codeingo defends against and where each control lives.

## 1. Authentication

| Control | Where |
|---|---|
| Google sign-in via OIDC authorization-code flow with **PKCE (S256)**, random `state` (login-CSRF) and `nonce` (token replay) held in a signed, 10-minute cookie | `backend/app/services/google_oauth.py`, `routers/auth.py` |
| ID token signature, `aud`, `iss`, `exp` verified with Google's published keys; `email_verified` required; optional domain allow-list | `google_oauth.verify_id_token` |
| **2-step verification is mandatory** - no session exists until a TOTP code is verified | `routers/auth.py` (`cg_mfa` token → `/2fa/*`) |
| TOTP secrets encrypted at rest (Fernet / AES-128-CBC + HMAC) | `security/mfa.py` |
| TOTP **replay protection** (a code/time-step is accepted once), ±30 s drift window, constant-time compare | `mfa.verify_totp` |
| **Lockout**: 5 failed codes → 15-minute lock, plus per-IP rate limit on every auth route | `mfa.register_failure`, `ratelimit.limit` |
| 10 recovery codes, SHA-256 hashed, single use; regenerating them needs a fresh TOTP code | `mfa.new_recovery_codes` |

## 2. Sessions

- Access token: HS256 JWT, 15 minutes, algorithm pinned (no `alg=none` / confusion), `typ` claim checked so MFA tokens can't be used as access tokens.
- Refresh token: 384-bit random opaque value, stored only as a SHA-256 hash, **rotated on every use**. Presenting an already-rotated token revokes the entire token family (stolen-token detection) and is audit-logged.
- `token_version` on the user: "log out of all devices" or an admin disabling an account invalidates **all** access tokens immediately.
- Cookies: `HttpOnly`, `Secure`, `SameSite=Strict` (the refresh cookie is also path-scoped to `/api/auth`).

## 3. Web attacks

| Threat | Control |
|---|---|
| CSRF | SameSite=Strict cookies **and** double-submit `X-CSRF-Token` header **and** Origin check on every POST/PUT/PATCH/DELETE (`security/middleware.py`). The token is rotated at login. |
| XSS | React escapes all output; no `dangerouslySetInnerHTML`; strict CSP `script-src 'self'` (the theme bootstrap is an external file so inline scripts stay forbidden); lesson content is rendered as text. |
| Clickjacking | `X-Frame-Options: DENY` + `frame-ancestors 'none'`. |
| SQL injection | SQLAlchemy ORM / bound parameters only. |
| Host-header attacks | `TrustedHostMiddleware` with an explicit host list. |
| Info leakage | Generic 500 handler (no stack traces), validation errors don't echo input, API docs disabled in production, `Server` header removed, `Cache-Control: no-store` on API responses. |
| Answer tampering / cheating | Solutions never leave the server before answering; XP is computed server-side; attempts are bound to the user; a lesson can't be completed faster than 2 s per exercise; practice XP is capped; daily challenge has a DB-unique claim; row locks prevent double-awarding from parallel requests. |
| Remote code execution | Learner code is **never executed** - it's matched against author regexes using the `regex` engine with a 200 ms timeout (ReDoS-safe) and a 2,000-character cap. |
| Privilege escalation | Admin routes require `role == admin` (granted only via `ADMIN_EMAILS`); admins can't disable themselves; every admin action is audit-logged. |
| AI abuse / prompt injection | Per-user hourly hint budget; learner text is delimited and marked untrusted; output is length-capped and rendered as plain text; the AI never sees solutions. |
| Privacy | The leaderboard exposes display names only (never emails); Google avatars are only accepted from `lh3.googleusercontent.com`. |

## 4. Denial of service

Layered, cheapest first:

1. **CDN / WAF (recommended)** - Cloudflare or similar absorbs volumetric L3/L4/L7 floods. Origin should only accept traffic from the CDN.
2. **Caddy** - TLS termination, HTTP/2/3.
3. **nginx** (`deploy/nginx.conf`) - per-IP `limit_req` (API 15 r/s, auth 2 r/s with small bursts), `limit_conn` 30 per IP, 64 KB body cap, 10 s header/body timeouts (slowloris), small header buffers.
4. **FastAPI** - Redis-backed per-IP global limit (240/min), stricter per-route limits (auth, answers, lesson starts, daily challenge, AI), streaming body-size limit, uvicorn `--limit-concurrency` and short keep-alive.
5. **Database** - bounded connection pool, 5 s `statement_timeout`, Postgres/Redis unreachable from the internet.

The rate limiter fails **open** if Redis is down (so a Redis outage doesn't take the site offline); nginx limits still apply.

## 5. Infrastructure

- Containers run as non-root, `read_only` root FS, `no-new-privileges`, all capabilities dropped.
- DB and Redis live on an `internal: true` network (no internet egress); Redis requires a password and doesn't persist.
- Secrets come only from environment variables; `.env` is git-ignored. Production start-up **fails** on weak or missing secrets, dev login, non-HTTPS URLs or SQLite (`config.validate_for_production`).
- CI runs the test suite, `bandit` (Python SAST), `pip-audit` and `npm audit`.

## Operational checklist

- [ ] Put the domain behind Cloudflare (or another CDN/WAF) and firewall the origin to CDN IPs.
- [ ] Generate unique `SECRET_KEY`, `ENCRYPTION_KEY`, DB and Redis passwords; store backups of `ENCRYPTION_KEY` (losing it means users must re-enrol 2FA).
- [ ] Restrict the Google OAuth client to your production redirect URI.
- [ ] Back up the Postgres volume and review the Admin → Security log regularly.

## Reporting a vulnerability

Please report privately to the maintainers instead of opening a public issue.
