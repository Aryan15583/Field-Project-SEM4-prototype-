// Runs learner JavaScript off the main thread. This worker is served with its own CSP
// (connect-src 'none'), and dangerous globals are removed before any learner code runs.
// The page terminates the worker if a run exceeds its time limit (infinite loops).
import { cap, formatJs, lockDown } from "./shared.mjs";

// Sloppy mode on purpose: beginners' `x = 5` should work, as it does in a browser console.
const compile = (src) => new Function("console", "input", "prompt", "alert", src);
lockDown(self);

self.onmessage = (e) => {
  const { id, code, tests } = e.data;
  self.postMessage({ id, type: "started" });
  const results = [];
  for (const t of tests) {
    let out = "";
    let err = "";
    const write = (stream) => (...args) => {
      const line = args.map((a) => formatJs(a)).join(" ") + "\n";
      if (stream === "err") err += line;
      else out += line;
    };
    const fakeConsole = { log: write("out"), info: write("out"), warn: write("err"), error: write("err"), table: write("out") };
    const lines = t.stdin ? t.stdin.split("\n") : [];
    const input = () => (lines.length ? lines.shift() : null);
    try {
      compile(`${code}\n;\n${t.append || ""}`)(fakeConsole, input, input, () => {});
    } catch (ex) {
      err += `${ex && ex.name ? ex.name : "Error"}: ${ex && ex.message ? ex.message : String(ex)}\n`;
    }
    results.push({ name: t.name, stdout: cap(out), stderr: cap(err) });
  }
  self.postMessage({ id, results });
};

self.postMessage({ type: "ready" });
