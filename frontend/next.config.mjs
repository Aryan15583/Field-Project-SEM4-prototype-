/** @type {import('next').NextConfig} */
const API_ORIGIN = process.env.API_ORIGIN || "http://127.0.0.1:8000";

const nextConfig = {
  output: "standalone", // small self-contained server for the Docker image
  poweredByHeader: false, // don't advertise the framework
  reactStrictMode: true,
  productionBrowserSourceMaps: false,
  // In development the FastAPI backend is reached through Next so the browser sees ONE origin
  // (same-origin cookies, no CORS). In production nginx routes /api straight to FastAPI.
  async rewrites() {
    return process.env.NODE_ENV === "development" ? [{ source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` }] : [];
  },
  // Static security headers for every response (CSP with a per-request nonce is set in proxy.js).
  async headers() {
    // Code-runner workers get their OWN, very tight CSP (a worker's policy comes from its script's
    // response): learner JavaScript may not make any network request at all; the Python/SQL
    // runtimes may only fetch their own files from this origin. 'unsafe-eval' / 'wasm-unsafe-eval'
    // are needed to execute code and WebAssembly - inside the worker only, never on the page.
    const worker = (extra) => [
      { key: "Content-Security-Policy", value: `default-src 'none'; ${extra}` },
      { key: "Cross-Origin-Resource-Policy", value: "same-origin" },
    ];
    return [
      { source: "/runners/js-worker.mjs", headers: worker("script-src 'self' 'unsafe-eval'; connect-src 'none'") },
      { source: "/runners/py-worker.mjs", headers: worker("script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'; connect-src 'self'") },
      { source: "/runners/sql-worker.mjs", headers: worker("script-src 'self' 'wasm-unsafe-eval'; connect-src 'self'") },
      // the service worker must always be re-checked so updates roll out; it may only load itself
      {
        source: "/sw.js",
        headers: [
          { key: "Cache-Control", value: "no-cache, no-store, must-revalidate" },
          { key: "Content-Security-Policy", value: "default-src 'self'; script-src 'self'" },
        ],
      },
      // runtimes never change for a given build -> cache hard
      { source: "/:dir(pyodide|sqljs)/:file*", headers: [{ key: "Cache-Control", value: "public, max-age=604800" }] },
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=()" },
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
