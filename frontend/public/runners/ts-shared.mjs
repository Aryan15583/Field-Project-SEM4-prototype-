// TypeScript for the in-browser runner AND the curriculum validator: type-check (strict) and compile one
// learner program with the real TypeScript compiler, entirely in memory. Callers pass in `ts` (the compiler)
// and `libs` (the standard library .d.ts files), so the browser and Node produce identical results.

export const ROOT_LIB = "lib.es2022.d.ts";

/** Declarations for the few runtime globals a learner's program can use (there is no DOM in the runner). */
export const RUNNER_DTS = `
interface Console { log(...data: any[]): void; error(...data: any[]): void; warn(...data: any[]): void; info(...data: any[]): void; }
declare var console: Console;
declare function setTimeout(handler: (...args: any[]) => void, timeout?: number, ...args: any[]): number;
declare function clearTimeout(id: number | undefined): void;
declare function setInterval(handler: (...args: any[]) => void, timeout?: number, ...args: any[]): number;
declare function clearInterval(id: number | undefined): void;
declare function queueMicrotask(callback: () => void): void;
declare function structuredClone<T>(value: T): T;
`;

/** Every lib file reachable from ROOT_LIB through `/// <reference lib="..." />`. */
export function collectLibs(readLib) {
  const libs = {};
  const queue = [ROOT_LIB];
  while (queue.length) {
    const name = queue.pop();
    if (name in libs) continue;
    const text = readLib(name);
    libs[name] = text;
    for (const m of text.matchAll(/\/\/\/\s*<reference\s+lib="([^"]+)"/g)) queue.push(`lib.${m[1].toLowerCase()}.d.ts`);
  }
  return libs;
}

const FILE = "main.ts";
const cache = new Map(); // parsed lib files never change, so parse them once

function options(ts) {
  return {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.ESNext,
    strict: true,
    noLib: true, // we hand the compiler the exact lib files instead
    noEmitOnError: true,
    noUnusedLocals: false,
    skipLibCheck: true,
    types: [],
    newLine: ts.NewLineKind.LineFeed,
  };
}

/** Returns { js } or { errors: ["Line 3: Type 'string' is not assignable to type 'number'."] }. */
export function compileTs(ts, libs, source) {
  const files = { ...libs, "runner.d.ts": RUNNER_DTS };
  let js = "";
  const strip = (n) => n.replace(/^\/+/, "");
  const host = {
    getSourceFile(name, languageVersion) {
      name = strip(name);
      if (name === FILE) return ts.createSourceFile(FILE, source, languageVersion, true);
      if (!(name in files)) return undefined;
      if (!cache.has(name)) cache.set(name, ts.createSourceFile(name, files[name], languageVersion, true));
      return cache.get(name);
    },
    writeFile(name, text) {
      if (name.endsWith(".js")) js = text;
    },
    getDefaultLibFileName: () => ROOT_LIB,
    useCaseSensitiveFileNames: () => true,
    getCanonicalFileName: (n) => n,
    getCurrentDirectory: () => "",
    getNewLine: () => "\n",
    fileExists: (n) => strip(n) === FILE || strip(n) in files,
    readFile: (n) => (strip(n) === FILE ? source : files[strip(n)]),
    directoryExists: () => true,
    getDirectories: () => [],
  };
  const program = ts.createProgram([FILE, ...Object.keys(files)], options(ts), host);
  const main = program.getSourceFile(FILE);
  const diags = [...program.getSyntacticDiagnostics(main), ...program.getSemanticDiagnostics(main)];
  if (diags.length) {
    return {
      errors: diags.slice(0, 5).map((d) => {
        const msg = ts.flattenDiagnosticMessageText(d.messageText, "\n");
        if (d.file && d.start !== undefined) return `Line ${d.file.getLineAndCharacterOfPosition(d.start).line + 1}: ${msg}`;
        return msg;
      }),
    };
  }
  program.emit(main);
  // a file with import/export would emit module syntax the runner can't execute
  if (/^\s*(import|export)\s/m.test(js)) return { errors: ["import/export aren't available here - keep everything in one file."] };
  return { js };
}
