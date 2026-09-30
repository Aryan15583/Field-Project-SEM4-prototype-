"use client";

import { LayoutGroup, motion } from "motion/react";
import { useEffect, useRef } from "react";
import { sfx } from "@/lib/feedback";

const TITLES = {
  mcq: "Select the correct answer",
  fill: "Fill in the blank",
  order: "Tap the lines in the right order",
  code: "Write the code",
};

// Snappy spring used for tiles flying between the word bank and the answer row.
const TILE_SPRING = { type: "spring", stiffness: 700, damping: 42, mass: 0.7 };

/**
 * Renders any exercise kind. `value` is the learner's answer; `result` is null before checking,
 * then "right" | "wrong" (tiles colour themselves accordingly and lock).
 */
export default function Exercise({ exercise, value, onChange, result }) {
  const locked = result != null;
  return (
    <div>
      <p className="label mb-2">{TITLES[exercise.kind]}</p>
      <h2 className="mb-6 text-2xl font-extrabold leading-snug sm:text-[28px]">{exercise.prompt}</h2>
      {exercise.kind === "mcq" && <Mcq exercise={exercise} value={value} onChange={onChange} locked={locked} result={result} />}
      {exercise.kind === "fill" && <Fill exercise={exercise} value={value} onChange={onChange} locked={locked} result={result} />}
      {exercise.kind === "order" && <Order exercise={exercise} value={value} onChange={onChange} locked={locked} result={result} />}
      {exercise.kind === "code" && <Code value={value} onChange={onChange} locked={locked} result={result} />}
    </div>
  );
}

export function isAnswered(kind, value) {
  if (kind === "mcq") return Number.isInteger(value);
  if (kind === "order") return Array.isArray(value) && value.length > 0;
  return typeof value === "string" && value.trim().length > 0;
}

export function initialValue(exercise) {
  if (exercise.kind === "order") return [];
  if (exercise.kind === "code") return exercise.data?.starter || "";
  if (exercise.kind === "fill") return "";
  return null;
}

const resultClass = (result) => (result === "right" ? "tile-right" : result === "wrong" ? "tile-wrong" : "tile-selected");

function Mcq({ exercise, value, onChange, locked, result }) {
  const options = exercise.data.options || [];
  const pick = (i) => {
    if (locked) return;
    sfx.tap();
    onChange(i);
  };
  const pickRef = useRef(pick);
  pickRef.current = pick;

  useEffect(() => {
    const onKey = (e) => {
      const n = Number(e.key);
      if (n >= 1 && n <= options.length && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) pickRef.current(n - 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [options.length]);

  return (
    <>
      {exercise.code && <pre className="code mb-6">{exercise.code}</pre>}
      <div className="grid gap-3 sm:grid-cols-2" role="radiogroup">
        {options.map((opt, i) => {
          const selected = value === i;
          return (
            <motion.button
              key={i}
              type="button"
              role="radio"
              aria-checked={selected}
              disabled={locked && !selected}
              onClick={() => pick(i)}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.04 * i, duration: 0.2, ease: "easeOut" }}
              className={`tile flex items-center gap-3 ${selected ? resultClass(result) : ""} ${locked && !selected ? "opacity-60" : ""}`}
            >
              <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg border-2 border-current text-xs font-black opacity-70">{i + 1}</span>
              <span className="font-mono">{opt}</span>
            </motion.button>
          );
        })}
      </div>
    </>
  );
}

function Fill({ exercise, value, onChange, locked, result }) {
  const ref = useRef(null);
  useEffect(() => ref.current?.focus({ preventScroll: true }), [exercise.id]);
  const [before, after = ""] = (exercise.code || "___").split("___");
  const tone = result === "right" ? "border-ok bg-ok/15 text-ok" : result === "wrong" ? "border-bad bg-bad/10 text-bad" : "border-primary bg-primary/10 text-primary";
  return (
    <div className="code flex flex-wrap items-center text-base">
      <span className="whitespace-pre-wrap">{before}</span>
      <input
        ref={ref}
        value={value}
        disabled={locked}
        maxLength={60}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Your answer for the blank"
        spellCheck={false}
        autoComplete="off"
        autoCapitalize="off"
        className={`mx-1 w-32 rounded-lg border-b-4 px-2 py-1 font-mono transition-colors focus:outline-none ${tone}`}
      />
      <span className="whitespace-pre-wrap">{after}</span>
    </div>
  );
}

/**
 * Duolingo-style word bank. Each line is ONE motion element with a shared layoutId, so tapping it
 * animates it (FLIP, transform-only) from the bank into the answer row and back. The bank keeps
 * an empty slot where a used tile was, so nothing else jumps around.
 */
function Order({ exercise, value, onChange, locked, result }) {
  const lines = exercise.data.lines || [];
  const byId = Object.fromEntries(lines.map((l) => [l.id, l.text]));
  const toggle = (id) => {
    if (locked) return;
    sfx.tap();
    onChange(value.includes(id) ? value.filter((v) => v !== id) : [...value, id]);
  };
  const tileClass = "tile block w-full whitespace-pre font-mono text-sm";

  return (
    <LayoutGroup id={`order-${exercise.id}`}>
      <div className="space-y-6">
        <div className="min-h-[10rem] space-y-2 border-y-2 border-line py-3" aria-label="Your answer">
          {value.map((id) => (
            <motion.button
              key={id}
              layoutId={`line-${exercise.id}-${id}`}
              transition={TILE_SPRING}
              type="button"
              disabled={locked}
              onClick={() => toggle(id)}
              className={`${tileClass} ${result ? resultClass(result) : ""}`}
            >
              {byId[id]}
            </motion.button>
          ))}
        </div>
        <div className="space-y-2">
          {lines.map((l) =>
            value.includes(l.id) ? (
              // placeholder keeps the bank's shape while the tile lives in the answer row
              <div key={l.id} className="rounded-2xl bg-line px-4 py-3 font-mono text-sm text-transparent" aria-hidden="true">
                <span className="whitespace-pre">{l.text || " "}</span>
              </div>
            ) : (
              <motion.button
                key={l.id}
                layoutId={`line-${exercise.id}-${l.id}`}
                transition={TILE_SPRING}
                type="button"
                disabled={locked}
                onClick={() => toggle(l.id)}
                className={tileClass}
              >
                {l.text}
              </motion.button>
            ),
          )}
        </div>
      </div>
    </LayoutGroup>
  );
}

function Code({ value, onChange, locked, result }) {
  const onKeyDown = (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const el = e.target;
      const { selectionStart: s, selectionEnd: end } = el;
      onChange(value.slice(0, s) + "    " + value.slice(end));
      requestAnimationFrame(() => (el.selectionStart = el.selectionEnd = s + 4));
    }
  };
  const border = result === "right" ? "border-ok" : result === "wrong" ? "border-bad" : "border-line focus-within:border-primary";
  return (
    <div className={`overflow-hidden rounded-2xl border-2 transition-colors ${border}`}>
      <div className="flex items-center gap-1.5 border-b-2 border-line bg-surface px-4 py-2">
        <span className="h-3 w-3 rounded-full bg-bad/70" />
        <span className="h-3 w-3 rounded-full bg-gold/70" />
        <span className="h-3 w-3 rounded-full bg-primary/70" />
        <span className="ml-2 text-xs font-bold text-muted">editor</span>
      </div>
      <textarea
        value={value}
        disabled={locked}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        maxLength={2000}
        rows={6}
        spellCheck={false}
        autoCapitalize="off"
        autoComplete="off"
        aria-label="Code editor"
        placeholder="Type your code here…"
        className="block w-full resize-y bg-raised p-4 font-mono text-[15px] leading-relaxed text-ink placeholder:text-muted focus:outline-none"
      />
    </div>
  );
}
