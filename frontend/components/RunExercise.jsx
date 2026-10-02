"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "@/lib/api";
import { BROWSER_LANGS, preloadRunner, runInBrowser, SERVER_LANGS } from "@/lib/runners";
import { Icon } from "./ui";

const LANG_LABEL = { python: "Python", javascript: "JavaScript", sql: "SQL", html: "HTML/CSS", java: "Java", c: "C", cpp: "C++" };
const FILE = { python: "main.py", javascript: "main.js", sql: "query.sql", html: "index.html", java: "Main.java", c: "main.c", cpp: "main.cpp" };

/** Value shape for a run exercise: { code, run: null | { results, error } }. */
export function runInitialValue(exercise) {
  return { code: exercise.data?.starter || "", run: null };
}

/**
 * Turns the learner's code into the answer the API grades. Browser languages are executed here
 * first (the API compares the printed output with expected results it never reveals); compiled
 * languages are run by the server's sandbox.
 */
export async function prepareRunAnswer(exercise, value, onChange) {
  const { language, tests, setup } = exercise.data;
  if (SERVER_LANGS.has(language)) return { code: value.code };
  const run = await runInBrowser(language, { code: value.code, tests, setup });
  onChange({ ...value, run });
  return { code: value.code, outputs: run.results ? run.results.map((r) => r.stdout) : tests.map(() => "") };
}

function Editor({ value, onChange, locked, language, border }) {
  const lines = Math.max(6, (value.match(/\n/g) || []).length + 2);
  const onKeyDown = (e) => {
    const el = e.target;
    if (e.key === "Tab") {
      e.preventDefault();
      const { selectionStart: s, selectionEnd: end } = el;
      onChange(value.slice(0, s) + "    " + value.slice(end));
      requestAnimationFrame(() => (el.selectionStart = el.selectionEnd = s + 4));
    } else if (e.key === "Enter" && !e.shiftKey) {
      // keep the current line's indentation (and indent after ':' / '{')
      e.preventDefault();
      const s = el.selectionStart;
      const lineStart = value.lastIndexOf("\n", s - 1) + 1;
      const indent = value.slice(lineStart).match(/^[ \t]*/)[0];
      const extra = /[:{[(]\s*$/.test(value.slice(lineStart, s)) ? "    " : "";
      const ins = "\n" + indent + extra;
      onChange(value.slice(0, s) + ins + value.slice(el.selectionEnd));
      requestAnimationFrame(() => (el.selectionStart = el.selectionEnd = s + ins.length));
    }
  };
  return (
    <div className={`overflow-hidden rounded-2xl border-2 transition-colors ${border}`}>
      <div className="flex items-center gap-1.5 border-b-2 border-line bg-surface px-4 py-2">
        <span className="h-3 w-3 rounded-full bg-bad/70" />
        <span className="h-3 w-3 rounded-full bg-gold/70" />
        <span className="h-3 w-3 rounded-full bg-primary/70" />
        <span className="ml-2 font-mono text-xs font-bold text-muted">{FILE[language]}</span>
        <span className="ml-auto text-[0.6875rem] font-black uppercase tracking-wider text-muted">{LANG_LABEL[language]}</span>
      </div>
      <div className="flex bg-raised">
        <div aria-hidden="true" className="select-none border-r-2 border-line px-3 py-4 text-right font-mono text-[0.9375rem] leading-relaxed text-muted/60">
          {Array.from({ length: lines }, (_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>
        <textarea
          value={value}
          disabled={locked}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          maxLength={5000}
          rows={lines}
          spellCheck={false}
          autoCapitalize="off"
          autoComplete="off"
          autoCorrect="off"
          wrap="off"
          aria-label={`${LANG_LABEL[language]} code editor`}
          placeholder="Write your code here…"
          className="block min-w-0 flex-1 resize-none overflow-x-auto bg-transparent px-4 py-4 font-mono text-[0.9375rem] leading-relaxed text-ink placeholder:text-muted focus:outline-none"
        />
      </div>
    </div>
  );
}

function HtmlPreview({ code }) {
  const [doc, setDoc] = useState(code);
  useEffect(() => {
    const t = setTimeout(() => setDoc(code), 300); // debounce while typing
    return () => clearTimeout(t);
  }, [code]);
  return (
    <div className="overflow-hidden rounded-2xl border-2 border-line">
      <div className="border-b-2 border-line bg-surface px-4 py-2 text-xs font-black uppercase tracking-wider text-muted">Live preview</div>
      {/* sandbox="" : no scripts, no forms, no navigation, unique origin */}
      <iframe title="Preview of your page" sandbox="" srcDoc={doc} className="h-56 w-full bg-white" />
    </div>
  );
}

function Console({ run, running }) {
  return (
    <div className="overflow-hidden rounded-2xl border-2 border-line bg-surface" aria-live="polite">
      <div className="flex items-center gap-2 border-b-2 border-line px-4 py-2 text-xs font-black uppercase tracking-wider text-muted">
        <Icon name="code" className="h-4 w-4" /> Output
        {running && <span className="ml-auto animate-pulse normal-case tracking-normal">Running…</span>}
      </div>
      <div className="max-h-64 space-y-3 overflow-auto p-4 font-mono text-sm">
        {!run && !running && <p className="font-sans font-semibold text-muted">Press Run to try your code.</p>}
        {run?.error && <pre className="whitespace-pre-wrap text-bad">{run.error}</pre>}
        {run?.results?.map((r, i) => (
          <div key={i}>
            {run.results.length > 1 || r.name ? (
              <p className="mb-1 flex items-center gap-2 font-sans text-xs font-black uppercase tracking-wider text-muted">
                {r.passed === true && <Icon name="check" className="h-4 w-4 text-ok" />}
                {r.passed === false && <Icon name="x" className="h-4 w-4 text-bad" />}
                {r.name || `Test ${i + 1}`}
              </p>
            ) : null}
            <pre className="whitespace-pre-wrap break-words text-ink">{r.stdout || (r.stderr ? "" : "(no output)")}</pre>
            {r.stderr && <pre className="whitespace-pre-wrap break-words text-bad">{r.stderr}</pre>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function RunExercise({ exercise, value, onChange, locked, result }) {
  const { language, tests = [], setup } = exercise.data;
  const [running, setRunning] = useState(false);
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    preloadRunner(language);
    return () => {
      alive.current = false;
    };
  }, [language]);

  const serverRun = SERVER_LANGS.has(language);
  const canRun = BROWSER_LANGS.has(language) || (serverRun && exercise.data.server_runner);
  const border = result === "right" ? "border-ok" : result === "wrong" ? "border-bad" : "border-line focus-within:border-primary";

  const run = async () => {
    if (running || !value.code.trim()) return;
    setRunning(true);
    let outcome;
    if (serverRun) {
      try {
        outcome = await api("/api/run", { method: "POST", body: { exercise_id: exercise.id, code: value.code } });
      } catch (e) {
        outcome = { error: e.message };
      }
    } else {
      outcome = await runInBrowser(language, { code: value.code, tests, setup });
    }
    if (alive.current) {
      onChange({ ...value, run: outcome });
      setRunning(false);
    }
  };

  const testNames = useMemo(() => tests.map((t) => t.name).filter(Boolean), [tests]);

  return (
    <div className="space-y-4">
      {setup && (
        <details className="rounded-2xl border-2 border-line bg-surface px-4 py-3 text-sm">
          <summary className="cursor-pointer font-extrabold text-primary">Tables in this database</summary>
          <pre className="mt-2 overflow-x-auto whitespace-pre font-mono text-xs text-ink">{setup}</pre>
        </details>
      )}
      <Editor value={value.code} onChange={(code) => onChange({ ...value, code })} locked={locked} language={language} border={border} />
      <div className="flex flex-wrap items-center gap-3">
        {canRun ? (
          <button type="button" className="btn-ghost min-h-[2.5rem] px-4 py-2 text-sm" onClick={run} disabled={running || locked || !value.code.trim()}>
            <Icon name="star" className="h-4 w-4" /> {running ? "Running…" : "Run"}
          </button>
        ) : (
          <span className="text-xs font-bold text-muted">Press Check to test your program.</span>
        )}
        {testNames.length > 0 && (
          <span className="text-xs font-bold text-muted">
            Tests: {testNames.slice(0, 4).join(" · ")}
            {testNames.length > 4 ? " …" : ""}
          </span>
        )}
      </div>
      {language === "html" && <HtmlPreview code={value.code} />}
      <AnimatePresence initial={false}>
        {(value.run || running) && language !== "html" && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
            <Console run={value.run} running={running} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
