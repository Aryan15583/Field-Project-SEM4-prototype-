// Runs learner Python (CPython compiled to WebAssembly by Pyodide) off the main thread.
// Pyodide is self-hosted under /pyodide. After it loads, network/storage globals are removed so
// learner code (which can reach JS through `import js`) can't make requests; the worker's own CSP
// also restricts it to this origin. The page kills the worker on timeout (infinite loops).
import { loadPyodide } from "/pyodide/pyodide.mjs";
import { cap, lockDown } from "./shared.mjs";

const decoder = () => new TextDecoder();
let py;

const ready = loadPyodide({ indexURL: "/pyodide/", packages: [] }).then((p) => {
  py = p;
  lockDown(self);
  self.postMessage({ type: "ready" });
});

self.onmessage = async (e) => {
  const { id, code, tests } = e.data;
  try {
    await ready;
  } catch {
    self.postMessage({ id, error: "Python failed to load. Check your connection and try again." });
    return;
  }
  self.postMessage({ id, type: "started" });
  const results = [];
  for (const t of tests) {
    let out = "";
    let err = "";
    const dOut = decoder();
    const dErr = decoder();
    py.setStdout({ write: (buf) => ((out += dOut.decode(buf, { stream: true })), buf.length) });
    py.setStderr({ write: (buf) => ((err += dErr.decode(buf, { stream: true })), buf.length) });
    let fed = false;
    py.setStdin({ stdin: () => (fed ? null : ((fed = true), t.stdin ?? "")), autoEOF: true });
    const ns = py.globals.get("dict")();
    try {
      py.runPython(`${code}\n${t.append || ""}`, { globals: ns, filename: "main.py" });
    } catch (ex) {
      // keep the useful tail of the traceback (drop Pyodide's internal frames)
      const msg = String(ex.message || ex);
      const at = msg.lastIndexOf('File "main.py"');
      err += at >= 0 ? "Traceback (most recent call last):\n  " + msg.slice(at) : msg;
    } finally {
      try {
        py.runPython("import sys; sys.stdout.flush(); sys.stderr.flush()");
      } catch {
        /* ignore */
      }
      ns.destroy();
    }
    results.push({ name: t.name, stdout: cap(out), stderr: cap(err) });
  }
  self.postMessage({ id, results });
};
