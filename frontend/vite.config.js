import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development the API runs on :8000 and is proxied so the SPA and API share one origin
// (same-origin cookies, no CORS needed). In production nginx does the same job.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://127.0.0.1:8000", changeOrigin: false, xfwd: true } },
  },
  build: { sourcemap: false },
});
