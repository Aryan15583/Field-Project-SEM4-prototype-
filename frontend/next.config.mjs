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
    return [
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
