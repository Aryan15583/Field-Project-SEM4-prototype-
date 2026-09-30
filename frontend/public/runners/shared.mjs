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

export const cap = (s) => (s.length > OUTPUT_CAP ? s.slice(0, OUTPUT_CAP) + "\n…(output truncated)" : s);
