// Shared by the in-browser runners AND the curriculum validator (backend/scripts/validate_curriculum.py
// drives it through Node/Playwright), so what a learner's program "prints" is computed identically
// in both places.

export const OUTPUT_CAP = 4000;

/** console.log-style formatting (Node-like for simple values). */
export function formatJs(value, nested = false) {
  if (typeof value === "string") return nested ? `'${value}'` : value;
  if (value === null) return "null";
  if (value === undefined) return "undefined";
  if (typeof value === "function") return `[Function: ${value.name || "(anonymous)"}]`;
  if (typeof value === "bigint") return `${value}n`;
  if (Array.isArray(value)) return value.length ? `[ ${value.map((v) => formatJs(v, true)).join(", ")} ]` : "[]";
  if (value instanceof Map) return `Map(${value.size}) { ${[...value].map(([k, v]) => `${formatJs(k, true)} => ${formatJs(v, true)}`).join(", ")} }`;
  if (value instanceof Set) return `Set(${value.size}) { ${[...value].map((v) => formatJs(v, true)).join(", ")} }`;
  if (value instanceof Error) return `${value.name}: ${value.message}`;
  if (typeof value === "object") {
    const name = value.constructor && value.constructor !== Object ? `${value.constructor.name} ` : "";
    const entries = Object.entries(value).map(([k, v]) => `${/^[A-Za-z_$][\w$]*$/.test(k) ? k : `'${k}'`}: ${formatJs(v, true)}`);
    return entries.length ? `${name}{ ${entries.join(", ")} }` : `${name}{}`;
  }
  return String(value);
}

/** Rows of the LAST result set, values joined by "|" (NULL for null). */
export function formatSqlResult(results) {
  if (!results || !results.length) return "";
  const last = results[results.length - 1];
  return last.values.map((row) => row.map((v) => (v === null ? "NULL" : String(v))).join("|")).join("\n");
}

/** Evaluates one HTML/CSS check against a rendered document. */
export function htmlOutput(doc, win, test) {
  const els = doc.querySelectorAll(test.selector);
  if (test.prop === "count") return String(els.length);
  const el = els[0];
  if (!el) return "(not found)";
  if (test.prop === "text") return el.textContent.replace(/\s+/g, " ").trim();
  if (test.prop.startsWith("attr:")) return el.getAttribute(test.prop.slice(5)) ?? "(none)";
  return win.getComputedStyle(el).getPropertyValue(test.prop).trim();
}

// Browser APIs a learner's program never needs. Removing them means code run in a runner can't
// make network requests or touch storage even if it tries (the worker's own CSP also blocks it).
export const BLOCKED_GLOBALS = [
  "fetch", "XMLHttpRequest", "WebSocket", "EventSource", "indexedDB", "caches", "BroadcastChannel",
  "Worker", "SharedWorker", "importScripts", "navigator", "WebTransport", "RTCPeerConnection",
];

export function lockDown(scope) {
  for (const k of BLOCKED_GLOBALS) {
    try {
      Object.defineProperty(scope, k, { value: undefined, configurable: false, writable: false });
    } catch {
      try {
        scope[k] = undefined;
      } catch {
        /* not present */
      }
    }
  }
}

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const errText = (ex) => `${ex && ex.name ? ex.name : "Error"}: ${ex && ex.message ? ex.message : String(ex)}\n`;

/**
 * Runs one JavaScript test: the learner's code + the test's `append` code, as an async function
 * (so top-level `await` works). setTimeout is tracked so async programs can finish before we
 * report; delays are compressed 10x (order preserved) so "wait 1 second" lessons stay snappy.
 * Used by BOTH the browser worker and the curriculum validator, so outputs always match.
 * Sloppy mode on purpose: beginners' `x = 5` should work, as it does in a browser console.
 */
export async function runJsProgram(code, t, { settleMs = 3000 } = {}) {
  let out = "";
  let err = "";
  const write = (isErr) => (...args) => {
    const line = args.map((a) => formatJs(a)).join(" ") + "\n";
    if (isErr) err += line;
    else out += line;
  };
  const con = { log: write(false), info: write(false), warn: write(true), error: write(true), table: write(false) };
  const lines = t.stdin ? t.stdin.split("\n") : [];
  const input = () => (lines.length ? lines.shift() : null);

  const timers = new Map();
  let nextId = 1;
  const fakeSetTimeout = (fn, ms = 0, ...args) => {
    const id = nextId++;
    const real = setTimeout(() => {
      timers.delete(id);
      try {
        fn(...args);
      } catch (ex) {
        err += errText(ex);
      }
    }, Math.min(Math.max(+ms || 0, 0), 1000) / 10);
    timers.set(id, real);
    return id;
  };
  const fakeClearTimeout = (id) => {
    if (timers.has(id)) {
      clearTimeout(timers.get(id));
      timers.delete(id);
    }
  };

  try {
    const fn = new AsyncFunction("console", "input", "prompt", "alert", "setTimeout", "clearTimeout", `${code}\n;\n${t.append || ""}`);
    await fn(con, input, input, () => {}, fakeSetTimeout, fakeClearTimeout);
  } catch (ex) {
    err += errText(ex);
  }
  // let pending timers and promise callbacks finish (bounded)
  const deadline = Date.now() + settleMs;
  while (timers.size && Date.now() < deadline) await new Promise((r) => setTimeout(r, 2));
  await new Promise((r) => setTimeout(r, 0));
  return { stdout: out, stderr: err };
}

export const cap = (s) => (s.length > OUTPUT_CAP ? s.slice(0, OUTPUT_CAP) + "\n…(output truncated)" : s);
