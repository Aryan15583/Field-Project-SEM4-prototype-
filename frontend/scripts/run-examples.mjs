// Used by backend/scripts/validate_curriculum.py: executes JavaScript, SQL and HTML reference
// solutions with EXACTLY the same logic as the in-browser runners (public/runners/*), so the
// expected outputs stored in the curriculum match what learners' browsers will produce.
// Input (stdin): JSON [{ lang, code, tests, setup }]  ->  output: JSON [[stdout per test] | {error}]
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { formatSqlResult, htmlOutput, runJsProgram } from "../public/runners/shared.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const jobs = JSON.parse(await new Promise((r) => {
  let s = "";
  process.stdin.on("data", (d) => (s += d));
  process.stdin.on("end", () => r(s));
}));

let SQL;
async function runSql(code, t, setup) {
  // Same sql.js package/version the browser worker loads (its Node build, since the ESM shim is browser-only).
  if (!SQL) SQL = await createRequire(import.meta.url)("sql.js")({ locateFile: (f) => join(root, "node_modules/sql.js/dist", f) });
  const db = new SQL.Database();
  try {
    if (setup) db.exec(setup);
    let res = db.exec(code);
    if (t.append) res = db.exec(t.append);
    return { stdout: formatSqlResult(res), stderr: "" };
  } catch (ex) {
    return { stdout: "", stderr: `Error: ${ex.message}` };
  } finally {
    db.close();
  }
}

let browser;
async function runHtml(code, tests) {
  if (!browser) {
    const require = createRequire(import.meta.url);
    const { chromium } = require(join(execSync("npm root -g").toString().trim(), "playwright"));
    const preinstalled = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
    const executablePath = process.env.CHROMIUM || (existsSync(preinstalled) ? preinstalled : undefined);
    browser = await chromium.launch(executablePath ? { executablePath } : {});
  }
  // same size as the hidden iframe in lib/runners.js
  const page = await browser.newPage({ viewport: { width: 600, height: 400 } });
  await page.setContent(code, { waitUntil: "load" });
  const fn = htmlOutput.toString();
  const outs = await page.evaluate(({ fn, tests }) => {
    const f = new Function(`return (${fn})`)();
    return tests.map((t) => f(document, window, t));
  }, { fn, tests });
  await page.close();
  return outs.map((o) => ({ stdout: o, stderr: "" }));
}

// same behaviour as the browser worker: un-awaited promise rejections are reported, not fatal
let stray = "";
process.on("unhandledRejection", (r) => (stray += `${r && r.name ? r.name : "Error"}: ${r && r.message ? r.message : String(r)}\n`));

const results = [];
for (const job of jobs) {
  try {
    if (job.lang === "javascript") {
      const outs = [];
      for (const t of job.tests) {
        stray = "";
        const r = await runJsProgram(job.code, t);
        outs.push({ stdout: r.stdout, stderr: r.stderr + stray });
      }
      results.push(outs);
    }
    else if (job.lang === "sql") results.push(await Promise.all(job.tests.map((t) => runSql(job.code, t, job.setup))));
    else if (job.lang === "html") results.push(await runHtml(job.code, job.tests));
    else results.push({ error: `unsupported ${job.lang}` });
  } catch (ex) {
    results.push({ error: String(ex) });
  }
}
if (browser) await browser.close();
process.stdout.write(JSON.stringify(results));
