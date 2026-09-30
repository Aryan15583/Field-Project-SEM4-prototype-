// Runs learner SQL against a fresh in-memory SQLite database (sql.js / WebAssembly) per test.
import initSqlJs from "/sqljs/sql-wasm.mjs";
import { cap, formatSqlResult, lockDown } from "./shared.mjs";

let SQL;
const ready = initSqlJs({ locateFile: (f) => `/sqljs/${f}` }).then((s) => {
  SQL = s;
  lockDown(self);
  self.postMessage({ type: "ready" });
});

self.onmessage = async (e) => {
  const { id, code, tests, setup } = e.data;
  try {
    await ready;
  } catch {
    self.postMessage({ id, error: "SQL engine failed to load." });
    return;
  }
  self.postMessage({ id, type: "started" });
  const results = [];
  for (const t of tests) {
    const db = new SQL.Database();
    let out = "";
    let err = "";
    try {
      if (setup) db.exec(setup);
      let res = db.exec(code);
      if (t.append) res = db.exec(t.append);
      out = formatSqlResult(res);
    } catch (ex) {
      err = `Error: ${ex.message || ex}`;
    } finally {
      db.close();
    }
    results.push({ name: t.name, stdout: cap(out), stderr: cap(err) });
  }
  self.postMessage({ id, results });
};
