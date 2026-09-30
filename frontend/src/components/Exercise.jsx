import { useEffect, useRef } from "react";

const TITLES = {
  mcq: "Select the correct answer",
  fill: "Fill in the blank",
  order: "Put the code in order",
  code: "Write the code",
};

/** Renders any exercise kind. `value` is the learner's answer; `locked` after checking. */
export default function Exercise({ exercise, value, onChange, locked }) {
  return (
    <div className="animate-pop">
      <p className="label mb-2">{TITLES[exercise.kind]}</p>
      <h2 className="mb-5 text-2xl font-extrabold leading-snug">{exercise.prompt}</h2>
      {exercise.kind === "mcq" && <Mcq exercise={exercise} value={value} onChange={onChange} locked={locked} />}
      {exercise.kind === "fill" && <Fill exercise={exercise} value={value} onChange={onChange} locked={locked} />}
      {exercise.kind === "order" && <Order exercise={exercise} value={value} onChange={onChange} locked={locked} />}
      {exercise.kind === "code" && <Code exercise={exercise} value={value} onChange={onChange} locked={locked} />}
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

function Mcq({ exercise, value, onChange, locked }) {
  const options = exercise.data.options || [];
  useEffect(() => {
    if (locked) return;
    const onKey = (e) => {
      const n = Number(e.key);
      if (n >= 1 && n <= options.length && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) onChange(n - 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [locked, options.length, onChange]);

  return (
    <>
      {exercise.code && <pre className="code mb-5">{exercise.code}</pre>}
      <div className="grid gap-3 sm:grid-cols-2" role="radiogroup">
        {options.map((opt, i) => (
          <button
            key={i}
            type="button"
            role="radio"
            aria-checked={value === i}
            disabled={locked}
            onClick={() => onChange(i)}
            className={`tile flex items-center gap-3 ${value === i ? "tile-selected" : ""}`}
          >
            <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg border-2 border-current text-xs font-black opacity-70">{i + 1}</span>
            <span className="font-mono">{opt}</span>
          </button>
        ))}
      </div>
    </>
  );
}

function Fill({ exercise, value, onChange, locked }) {
  const ref = useRef(null);
  useEffect(() => ref.current?.focus(), [exercise.id]);
  const [before, after = ""] = (exercise.code || "___").split("___");
  return (
    <div className="code flex flex-wrap items-center">
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
        className="mx-1 w-32 rounded-lg border-b-4 border-primary bg-primary/10 px-2 py-1 font-mono text-primary focus:outline-none"
      />
      <span className="whitespace-pre-wrap">{after}</span>
    </div>
  );
}

function Order({ exercise, value, onChange, locked }) {
  const lines = exercise.data.lines || [];
  const byId = Object.fromEntries(lines.map((l) => [l.id, l.text]));
  const remaining = lines.filter((l) => !value.includes(l.id));
  return (
    <div className="space-y-5">
      <div className="min-h-[9rem] space-y-2 rounded-2xl border-2 border-dashed border-line p-3" aria-label="Your answer">
        {value.length === 0 && <p className="p-2 text-sm text-muted">Tap the lines below in the right order.</p>}
        {value.map((id) => (
          <button
            key={id}
            type="button"
            disabled={locked}
            onClick={() => onChange(value.filter((v) => v !== id))}
            className="tile tile-selected block w-full whitespace-pre font-mono text-sm"
          >
            {byId[id]}
          </button>
        ))}
      </div>
      <div className="space-y-2">
        {remaining.map((l) => (
          <button key={l.id} type="button" disabled={locked} onClick={() => onChange([...value, l.id])} className="tile block w-full whitespace-pre font-mono text-sm">
            {l.text}
          </button>
        ))}
      </div>
    </div>
  );
}

function Code({ value, onChange, locked }) {
  const onKeyDown = (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const el = e.target;
      const { selectionStart: s, selectionEnd: end } = el;
      const next = value.slice(0, s) + "    " + value.slice(end);
      onChange(next);
      requestAnimationFrame(() => (el.selectionStart = el.selectionEnd = s + 4));
    }
  };
  return (
    <div className="overflow-hidden rounded-2xl border-2 border-line">
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
