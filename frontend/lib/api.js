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
  if (!csrfToken()) await fetch("/api/auth/csrf", { credentials: "same-origin" });
}

let refreshing = null;

async function refreshSession() {
  if (!refreshing) {
    refreshing = fetch("/api/auth/refresh", {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRF-Token": csrfToken() },
    })
      .then((r) => r.ok)
      .catch(() => false)
      .finally(() => setTimeout(() => (refreshing = null), 0));
  }
  return refreshing;
}

const NO_REFRESH = ["/api/auth/refresh", "/api/auth/2fa", "/api/auth/dev-login", "/api/auth/logout"];

export async function api(path, { method = "GET", body, retry = true } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (method !== "GET") {
    await ensureCsrf();
    headers["X-CSRF-Token"] = csrfToken();
  }
  const res = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    body: body === undefined ? undefined : JSON.stringify(body),
  });

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
  return data;
}
