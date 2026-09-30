import { NextResponse } from "next/server";

/**
 * Runs before every page render: creates a fresh random nonce and a strict
 * Content-Security-Policy. Next.js reads the nonce from the request CSP header and stamps
 * it on its own scripts, so only scripts we emitted can run - injected ones (XSS) are refused.
 */
export function proxy(request) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  const isDev = process.env.NODE_ENV === "development";

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ""}`,
    // Inline style attributes are needed by charts/animations; styles can't execute code.
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https://lh3.googleusercontent.com",
    "font-src 'self'",
    `connect-src 'self'${isDev ? " ws:" : ""}`,
    // code runners (see lib/runners.js) - each worker script carries its own stricter CSP
    "worker-src 'self'",
    // HTML/CSS exercises: sandboxed, script-less preview frames built from srcdoc
    "frame-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self' https://accounts.google.com",
    "frame-ancestors 'none'",
    ...(isDev ? [] : ["upgrade-insecure-requests"]),
  ].join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", csp);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp);
  if (!isDev) response.headers.set("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload");
  return response;
}

export const config = {
  matcher: [
    {
      // pages only - not the API (FastAPI sets its own headers) or immutable static assets
      source: "/((?!api|_next/static|_next/image|favicon.svg|runners/|pyodide/|sqljs/).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
