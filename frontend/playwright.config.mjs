// Browser tests: `npm run e2e` (needs Python deps installed in ../backend and `npx playwright install chromium`).
// It starts its own API (SQLite, dev sign-in, emails written to a file) and the production build of the site on
// port 3100, then drives real Chromium through the main flows.
import { defineConfig } from "@playwright/test";
import path from "node:path";

const PORT = 3100;
const API_PORT = 8100;
const root = path.resolve(import.meta.dirname, "..");
export const OUTBOX = path.join(root, "backend", "e2e-outbox.jsonl");
const python = process.env.E2E_PYTHON || (process.env.CI ? "python" : path.join(root, "backend/.venv/bin/python"));

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {},
  },
  webServer: [
    {
      command: `${python} -m uvicorn app.main:app --port ${API_PORT}`,
      cwd: path.join(root, "backend"),
      url: `http://127.0.0.1:${API_PORT}/api/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ENV: "development",
        DATABASE_URL: "sqlite:///./e2e.db",
        DEV_LOGIN_ENABLED: "true",
        ADMIN_EMAILS: '["owner@e2e.example.com"]',
        PUBLIC_URL: `http://localhost:${PORT}`,
        ALLOWED_HOSTS: '["localhost","127.0.0.1"]',
        MAIL_OUTBOX_FILE: OUTBOX,
        STREAK_REMINDERS: "false",
        RATE_LIMIT_AUTH_PER_MINUTE: "1000",
        RATE_LIMIT_GLOBAL_PER_MINUTE: "100000",
      },
    },
    {
      // production build, with /api forwarded to the API exactly like on Vercel
      command: `npx next build && npx next start -p ${PORT}`,
      url: `http://localhost:${PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 300_000,
      env: { API_ORIGIN: `http://127.0.0.1:${API_PORT}`, NEXT_TELEMETRY_DISABLED: "1" },
    },
  ],
});
