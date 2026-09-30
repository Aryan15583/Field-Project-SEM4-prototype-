"use client";

import { useEffect } from "react";
import { useTheme } from "@/lib/theme";

/* ------------------------------------------------------------------ icons */
const paths = {
  learn: "M3 10.5 12 4l9 6.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
  target: "M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 4a6 6 0 1 1-6 6 6 6 0 0 1 6-6zm0 4a2 2 0 1 0 2 2 2 2 0 0 0-2-2z",
  chart: "M4 20V10h3v10zm6.5 0V4h3v16zM17 20v-7h3v7z",
  trophy: "M7 3h10v2h3v3a4 4 0 0 1-4 4h-.4A5 5 0 0 1 13 14.9V18h3v3H8v-3h3v-3.1A5 5 0 0 1 8.4 12H8a4 4 0 0 1-4-4V5h3zm0 4H6v1a2 2 0 0 0 1 1.7zm10 0v2.7A2 2 0 0 0 18 8V7z",
  user: "M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm0 2c-4.4 0-8 2.2-8 5v2h16v-2c0-2.8-3.6-5-8-5z",
  shield: "M12 2 4 5v6c0 5 3.4 9.6 8 11 4.6-1.4 8-6 8-11V5zm-1.2 14.2-3.5-3.5 1.4-1.4 2.1 2.1 4.9-4.9 1.4 1.4z",
  flame: "M13.5 1.5s1 3-1.5 6c-1.4 1.7-3.5 3-3.5 6a3.5 3.5 0 0 0 7 0c0-1.5-.8-2.5-.8-2.5S18 12 18 15a6 6 0 0 1-12 0c0-6 7.5-8 7.5-13.5z",
  heart: "M12 21s-8-5.3-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.7-8 11-8 11z",
  bolt: "M13 2 4 14h6l-1 8 9-12h-6z",
  sun: "M12 7a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0-5 1 3h-2zm0 20-1-3h2zM2 12l3-1v2zm20 0-3 1v-2zM4.9 4.9l2.8 1.4-1.4 1.4zm14.2 14.2-2.8-1.4 1.4-1.4zM4.9 19.1l1.4-2.8 1.4 1.4zM19.1 4.9l-1.4 2.8-1.4-1.4z",
  moon: "M21 14.5A8.5 8.5 0 0 1 9.5 3 9 9 0 1 0 21 14.5z",
  lock: "M7 10V7a5 5 0 0 1 10 0v3h1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V11a1 1 0 0 1 1-1zm2 0h6V7a3 3 0 0 0-6 0z",
  check: "M9.5 16.2 5.3 12l-1.4 1.4 5.6 5.6L20.1 8.4 18.7 7z",
  star: "M12 2.5l2.9 6 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.2 1.3-6.6L2.5 9.3l6.6-.8z",
  x: "M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7l-1.4-1.4L9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z",
  bulb: "M9 21h6v-1H9zm3-19a7 7 0 0 0-4 12.7V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.3A7 7 0 0 0 12 2z",
  logout: "M10 17l1.4-1.4-2.6-2.6H20v-2H8.8l2.6-2.6L10 7l-5 5zM4 3h8v2H4v14h8v2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z",
  code: "M8.6 16.6 4 12l4.6-4.6L7.2 6 1.2 12l6 6zm6.8 0L20 12l-4.6-4.6L16.8 6l6 6-6 6z",
};

export function Icon({ name, className = "h-5 w-5", title }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden={title ? undefined : true} role={title ? "img" : undefined}>
      {title && <title>{title}</title>}
      <path d={paths[name]} />
    </svg>
  );
}

/* ------------------------------------------------------------------ mascot */
/** Codi - a friendly bracket-bot. mood: happy | sad | think */
export function Mascot({ size = 120, mood = "happy", className = "" }) {
  return (
    <svg viewBox="0 0 120 120" width={size} height={size} className={className} role="img" aria-label="Codi the Codeingo mascot">
      <ellipse cx="60" cy="112" rx="34" ry="5" className="fill-ink/10" />
      <rect x="18" y="22" width="84" height="80" rx="30" className="fill-primary" />
      <rect x="18" y="22" width="84" height="80" rx="30" fill="none" strokeWidth="4" className="stroke-primary-strong" />
      <path d="M44 12 L52 24 M76 12 L68 24" strokeWidth="5" strokeLinecap="round" className="stroke-primary-strong" />
      <circle cx="43" cy="11" r="5" className="fill-gold" />
      <circle cx="77" cy="11" r="5" className="fill-gold" />
      <circle cx="44" cy="52" r="15" fill="#fff" />
      <circle cx="76" cy="52" r="15" fill="#fff" />
      {mood === "sad" ? (
        <>
          <path d="M36 54 q8 -6 16 0" stroke="#0a0a0a" strokeWidth="4" fill="none" strokeLinecap="round" />
          <path d="M68 54 q8 -6 16 0" stroke="#0a0a0a" strokeWidth="4" fill="none" strokeLinecap="round" />
        </>
      ) : (
        <>
          <circle cx={mood === "think" ? 49 : 46} cy={mood === "think" ? 48 : 54} r="7" fill="#0a0a0a" />
          <circle cx={mood === "think" ? 81 : 78} cy={mood === "think" ? 48 : 54} r="7" fill="#0a0a0a" />
          <circle cx={mood === "think" ? 51 : 48} cy={mood === "think" ? 46 : 51} r="2.5" fill="#fff" />
          <circle cx={mood === "think" ? 83 : 80} cy={mood === "think" ? 46 : 51} r="2.5" fill="#fff" />
        </>
      )}
      <text x="60" y="92" textAnchor="middle" fontFamily="ui-monospace, monospace" fontWeight="800" fontSize="20" className="fill-on-primary">
        {mood === "sad" ? "</ >" : mood === "think" ? "{ ? }" : "</>"}
      </text>
    </svg>
  );
}

export function Logo({ className = "", compact = false }) {
  return (
    <span className={`inline-flex items-center gap-2 text-2xl font-black tracking-tight text-primary ${className}`}>
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-on-primary">
        <Icon name="code" className="h-5 w-5" />
      </span>
      <span className={compact ? "hidden sm:inline" : ""}>codeingo</span>
    </span>
  );
}

/* ------------------------------------------------------------------ bits */
export function ThemeToggle({ className = "" }) {
  const { dark, toggle } = useTheme();
  return (
    <button
      type="button"
      onClick={toggle}
      className={`grid h-10 w-10 place-items-center rounded-xl border-2 border-line text-muted hover:bg-surface hover:text-ink ${className}`}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      title={dark ? "Light mode" : "Dark mode"}
    >
      <Icon name={dark ? "sun" : "moon"} />
    </button>
  );
}

export function Spinner({ label = "Loading" }) {
  return (
    <div className="grid place-items-center py-16" role="status">
      <Mascot size={80} mood="think" className="animate-bob" />
      <span className="mt-3 text-sm font-bold text-muted">{label}…</span>
    </div>
  );
}

export function ProgressBar({ value, max = 100, className = "" }) {
  const pct = Math.max(0, Math.min(100, (value / Math.max(1, max)) * 100));
  return (
    <div
      className={`h-4 overflow-hidden rounded-full bg-line ${className}`}
      role="progressbar"
      aria-valuenow={Math.round(pct)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div className="relative h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${pct}%` }}>
        <div className="absolute inset-x-2 top-1 h-1 rounded-full bg-white/30" />
      </div>
    </div>
  );
}

export function StatPill({ icon, value, tone, label }) {
  const tones = { flame: "text-flame", bad: "text-bad", primary: "text-primary", gold: "text-gold" };
  return (
    <span className={`chip ${tones[tone]}`} title={label} aria-label={`${label}: ${value}`}>
      <Icon name={icon} className="h-5 w-5" />
      <span>{value}</span>
    </span>
  );
}

export function Modal({ open, onClose, children, label }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose?.();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4" role="dialog" aria-modal="true" aria-label={label} onClick={onClose}>
      <div className="card w-full max-w-md animate-pop p-6" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}

export function ErrorNote({ children }) {
  if (!children) return null;
  return (
    <p className="rounded-2xl border-2 border-bad/40 bg-bad/10 px-4 py-3 text-sm font-bold text-bad" role="alert">
      {children}
    </p>
  );
}
