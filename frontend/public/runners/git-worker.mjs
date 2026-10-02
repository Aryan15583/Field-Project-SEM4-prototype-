// Runs learner Git scripts in the in-memory Git simulator (git-sim.mjs) off the main thread. Nothing touches a
// real disk or network; the worker is served with a CSP that forbids all requests.
import { cap, lockDown } from "./shared.mjs";
import { runGitProgram } from "./git-sim.mjs";

lockDown(self);

self.onmessage = (e) => {
  const { id, code, tests, setup } = e.data;
  self.postMessage({ id, type: "started" });
  const results = tests.map((t) => {
    try {
      const r = runGitProgram(code, t, setup);
      return { name: t.name, stdout: cap(r.stdout), stderr: cap(r.stderr), transcript: cap(r.transcript) };
    } catch (ex) {
      return { name: t.name, stdout: "", stderr: `Simulator error: ${ex && ex.message}` };
    }
  });
  self.postMessage({ id, results });
};

self.postMessage({ type: "ready" });
