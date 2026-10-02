// Runs learner JavaScript off the main thread. This worker is served with its own CSP
// (connect-src 'none'), and dangerous globals are removed before any learner code runs.
// The page terminates the worker if a run exceeds its time limit (infinite loops).
import { cap, lockDown, runJsProgram } from "./shared.mjs";

lockDown(self);
// learner code may call async functions without awaiting them - surface their errors too
let stray = "";
self.addEventListener("unhandledrejection", (e) => {
  const r = e.reason;
  stray += `${r && r.name ? r.name : "Error"}: ${r && r.message ? r.message : String(r)}\n`;
  e.preventDefault();
});

self.onmessage = async (e) => {
  const { id, code, tests } = e.data;
  self.postMessage({ id, type: "started" });
  const results = [];
  for (const t of tests) {
    stray = "";
    const r = await runJsProgram(code, t);
    results.push({ name: t.name, stdout: cap(r.stdout), stderr: cap(r.stderr + stray) });
  }
  self.postMessage({ id, results });
};

self.postMessage({ type: "ready" });
