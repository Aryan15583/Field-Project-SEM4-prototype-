"use client";

// Runs learner code in the browser, never on the main thread:
//   python -> Pyodide in a module Web Worker      javascript -> Web Worker
//   typescript -> real compiler (type-check) + the JS runner, in a Worker
//   sql    -> sql.js (SQLite/WASM) in a Worker    html       -> iframe with scripts disabled
// Each worker is served with its own restrictive CSP (see next.config.mjs) and is terminated if a
// run exceeds its time limit, so an infinite loop can't freeze the page.

export const BROWSER_LANGS = new Set(["python", "javascript", "typescript", "sql", "html"]);
export const SERVER_LANGS = new Set(["java", "c", "cpp"]);

const WORKERS = {
  python: "/runners/py-worker.mjs",
  javascript: "/runners/js-worker.mjs",
  typescript: "/runners/ts-worker.mjs",
  sql: "/runners/sql-worker.mjs",
};
const TIME_LIMIT_MS = { python: 8000, javascript: 4000, typescript: 8000, sql: 4000 };
const LOAD_LIMIT_MS = 60000; // Pyodide is ~13 MB the first time; it's cached afterwards

const pool = {};
let seq = 0;

function getWorker(lang) {
  if (!pool[lang]) {
    const w = new Worker(WORKERS[lang], { type: "module", name: `codeingo-${lang}` });
    pool[lang] = w;
  }
  return pool[lang];
}

function kill(lang) {
  pool[lang]?.terminate();
  delete pool[lang];
}

/** Start downloading a runtime early (e.g. when a lesson with a Python exercise opens). */
export function preloadRunner(lang) {
  if (WORKERS[lang] && typeof Worker !== "undefined") getWorker(lang);
}

/** Returns { results: [{name, stdout, stderr}] } or { error }. */
export function runInBrowser(lang, { code, tests, setup }) {
  if (lang === "html") return runHtml(code, tests);
  if (!WORKERS[lang]) return Promise.resolve({ error: `Can't run ${lang} in the browser.` });
  const w = getWorker(lang);
  const id = ++seq;
  return new Promise((resolve) => {
    let runTimer;
    const loadTimer = setTimeout(() => finish({ error: "The code runner took too long to load. Check your connection and try again." }, true), LOAD_LIMIT_MS);
    const finish = (result, terminate = false) => {
      clearTimeout(loadTimer);
      clearTimeout(runTimer);
      w.removeEventListener("message", onMessage);
      w.removeEventListener("error", onError);
      if (terminate) kill(lang);
      resolve(result);
    };
    const onMessage = (e) => {
      const d = e.data || {};
      if (d.id !== id) return;
      if (d.type === "started") {
        clearTimeout(loadTimer);
        runTimer = setTimeout(
          () => finish({ error: `Time limit exceeded (${TIME_LIMIT_MS[lang] / 1000}s). Is there an infinite loop?` }, true),
          TIME_LIMIT_MS[lang],
        );
        return;
      }
      finish(d.error ? { error: d.error } : { results: d.results });
    };
    const onError = () => finish({ error: "The code runner stopped unexpectedly. Try again." }, true);
    w.addEventListener("message", onMessage);
    w.addEventListener("error", onError);
    w.postMessage({ id, code, tests, setup });
  });
}

async function runHtml(code, tests) {
  const { htmlOutput } = await import(/* webpackIgnore: true */ /* turbopackIgnore: true */ "/runners/shared.mjs");
  const frame = document.createElement("iframe");
  // allow-same-origin WITHOUT allow-scripts: we can read the rendered DOM, the page can't run code.
  frame.setAttribute("sandbox", "allow-same-origin");
  frame.setAttribute("aria-hidden", "true");
  frame.tabIndex = -1;
  frame.style.cssText = "position:fixed;left:-10000px;top:0;width:600px;height:400px;border:0;visibility:hidden";
  frame.srcdoc = code;
  const loaded = new Promise((r) => (frame.onload = r));
  document.body.appendChild(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    return { results: tests.map((t) => ({ name: t.name, stdout: htmlOutput(doc, win, t), stderr: "" })) };
  } catch {
    return { error: "Couldn't render your HTML." };
  } finally {
    frame.remove();
  }
}
