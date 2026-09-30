// Copies the WebAssembly language runtimes into /public so they are served from our own origin
// (no third-party CDN at runtime -> the strict CSP stays 'self'). Runs before `dev` and `build`.
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const nm = join(root, "node_modules");

const py = join(root, "public/pyodide");
mkdirSync(py, { recursive: true });
for (const f of ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]) {
  copyFileSync(join(nm, "pyodide", f), join(py, f));
}

const sq = join(root, "public/sqljs");
mkdirSync(sq, { recursive: true });
copyFileSync(join(nm, "sql.js/dist/sql-wasm.wasm"), join(sq, "sql-wasm.wasm"));
// sql.js ships UMD; wrap it as an ES module so it can be imported from a module worker.
const umd = readFileSync(join(nm, "sql.js/dist/sql-wasm.js"), "utf8");
writeFileSync(join(sq, "sql-wasm.mjs"), `var module = { exports: {} };\nvar exports = module.exports;\n${umd}\nexport default module.exports;\n`);

console.log("copied Pyodide + sql.js runtimes into public/");
