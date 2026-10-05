import { ensureAwake, isWakeResponse } from "./serverWake";

// Thin fetch wrapper: same-origin cookies, CSRF double-submit header, one transparent token refresh.

export class ApiError extends Error {
  constructor(status, message, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function csrfToken() {
  const row = document.cookie.split("; ").find((c) => c.startsWith("cg_csrf="));
  return row ? decodeURIComponent(row.slice("cg_csrf=".length)) : "";
}

export async function ensureCsrf() {
  if (csrfToken()) return;
  const res = await fetch("/api/auth/csrf", { credentials: "same-origin" }).catch(() => null);
  if (!res || isWakeResponse(res, "/api/auth/csrf")) {
    await ensureAwake().catch(() => {}); // the server was asleep: wait for it, then ask again
    await fetch("/api/auth/csrf", { credentials: "same-origin" }).catch(() => {});
  }
}

let refreshing = null;

async function refreshSession() {
  if (!refreshing) {
    // After the browser was closed the (session) CSRF cookie may be gone - get a new one first,
    // otherwise returning users would be rejected and signed out.
    const attempt = () =>
      ensureCsrf().then(() =>
        fetch("/api/auth/refresh", {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRF-Token": csrfToken() },
        }),
      );
    refreshing = attempt()
      .catch(() => null)
      .then(async (r) => {
        if (!r || isWakeResponse(r, "/api/auth/refresh")) {
          await ensureAwake(); // the server was asleep: wait for it, then renew once more
          r = await attempt();
        }
        // Only a clear "no" from the server means signed out. A server hiccup must never log anyone out.
        if (r.status === 401 || r.status === 403) return false;
        if (!r.ok) throw new ApiError(r.status, "The server had a problem. Please try again.");
        return true;
      })
      .finally(() => setTimeout(() => (refreshing = null), 0));
  }
  return refreshing;
}

const NO_REFRESH = ["/api/auth/refresh", "/api/auth/2fa", "/api/auth/dev-login", "/api/auth/logout"];

// The last successful GET answers, kept in memory only. Screens use them to show the previous data at once
// (while the fresh answer loads), so going back to a page after a lesson doesn't start from a blank skeleton.
const memo = new Map();
export const cached = (path) => memo.get(path) ?? null;
export const clearCache = () => memo.clear(); // call on sign-out: never show one account's data to the next

export async function api(path, { method = "GET", body, retry = true, wakes = 0 } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (method !== "GET") {
    await ensureCsrf();
    headers["X-CSRF-Token"] = csrfToken();
  }
  let res;
  try {
    res = await fetch(path, {
      method,
      headers,
      credentials: "same-origin",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (networkError) {
    if (wakes < 2) {
      await ensureAwake(); // offline blip or sleeping server: wait for it, then try the same request again
      return api(path, { method, body, retry, wakes: wakes + 1 });
    }
    throw new ApiError(0, "Can't reach the server. Check your connection and try again.");
  }
  if (isWakeResponse(res, path) && wakes < 2) {
    await ensureAwake(); // shows the waking screen, resolves when the server is up
    return api(path, { method, body, retry, wakes: wakes + 1 });
  }

  if (res.status === 401 && retry && !NO_REFRESH.some((p) => path.startsWith(p))) {
    if (await refreshSession()) return api(path, { method, body, retry: false });
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const msg =
      res.status === 429
        ? data?.detail || "You're going too fast - take a breather and try again."
        : data?.detail || `Request failed (${res.status})`;
    throw new ApiError(res.status, typeof msg === "string" ? msg : "Request failed", data);
  }
  if (method === "GET") memo.set(path, data);
  return data;
}
