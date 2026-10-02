// Runs learner TypeScript off the main thread: type-check + compile with the real compiler (strict mode),
// then run the JavaScript exactly like the JavaScript runner. Served with its own CSP; the page terminates
// the worker if a run exceeds its time limit.
import { cap, lockDown, runJsProgram } from "./shared.mjs";
import { compileTs } from "./ts-shared.mjs";

let ts;
let libs;
// The ~9 MB compiler and the standard-library declarations come from our own origin. The message handler is
// attached right away (below) so no run request is missed while they load; fetch is locked away afterwards.
const ready = Promise.all([import("../typescript/typescript.mjs"), fetch("/typescript/libs.json").then((r) => r.json())]).then(([mod, l]) => {
  ts = mod.default;
  libs = l;
  lockDown(self);
  self.postMessage({ type: "ready" });
});

let stray = "";
self.addEventListener("unhandledrejection", (e) => {
  const r = e.reason;
  stray += `${r && r.name ? r.name : "Error"}: ${r && r.message ? r.message : String(r)}\n`;
  e.preventDefault();
});

self.onmessage = async (e) => {
  const { id, code, tests } = e.data;
  try {
    await ready;
  } catch {
    self.postMessage({ id, error: "TypeScript failed to load. Check your connection and try again." });
    return;
  }
  self.postMessage({ id, type: "started" });
  const results = [];
  for (const t of tests) {
    stray = "";
    const out = compileTs(ts, libs, `${code}\n${t.append || ""}`);
    if (out.errors) {
      results.push({ name: t.name, stdout: "", stderr: cap(`Type error - your program didn't run:\n${out.errors.join("\n")}\n`) });
      continue;
    }
    const r = await runJsProgram(out.js, { ...t, append: "" });
    results.push({ name: t.name, stdout: cap(r.stdout), stderr: cap(r.stderr + stray) });
  }
  self.postMessage({ id, results });
};
