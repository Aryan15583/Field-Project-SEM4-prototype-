"use client";

import { animate, AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { useTheme } from "@/lib/theme";
import Codi from "./Codi";

/* ------------------------------------------------------------------ learn by typing */
/**
 * Answer boxes don't accept pasted or dragged-in text: typing an answer out is how it sticks
 * (and stops copying the revealed answer straight back in). Returns props for the input plus a
 * short note to show after a blocked paste.
 */
export function usePasteGuard() {
  const [blocked, setBlocked] = useState(0);
  useEffect(() => {
    if (!blocked) return;
    const t = setTimeout(() => setBlocked(0), 4000);
    return () => clearTimeout(t);
  }, [blocked]);
  const block = (e) => {
    e.preventDefault();
    setBlocked((n) => n + 1);
  };
  const note = blocked ? (
    <p role="status" className="mt-2 text-sm font-bold text-gold">
      Pasting is turned off here - type it out yourself, that's how it sticks!
    </p>
  ) : null;
  return { guard: { onPaste: block, onDrop: block }, note };
}

/** Readable but not selectable or copyable - used for revealed answers. */
export function NoCopy({ as: Tag = "div", className = "", children, ...rest }) {
  const stop = (e) => e.preventDefault();
  return (
    <Tag className={`select-none ${className}`} onCopy={stop} onCut={stop} onContextMenu={stop} onDragStart={stop} {...rest}>
      {children}
    </Tag>
  );
}

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
  review: "M12 5V1.5L7.5 6 12 10.5V7a5 5 0 1 1-5 5H5a7 7 0 1 0 7-7z",
  users:
    "M9 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4zm7 0a3 3 0 1 0-3-3 3 3 0 0 0 3 3zM9 13c-3.9 0-7 1.8-7 4v2h14v-2c0-2.2-3.1-4-7-4zm7 0c-.5 0-1 0-1.4.1A4.4 4.4 0 0 1 18 17v2h4v-2c0-2.2-2.7-4-6-4z",
  key: "M7 14a2 2 0 1 1 2-2 2 2 0 0 1-2 2zm5.6-4A6 6 0 1 0 12.6 14H17v4h4v-4h2v-4z",
  mail: "M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1 2.4V17h16V7.4l-8 5.3z",
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
/** Codi, the pixel-art mascot - see components/Codi.jsx. mood: idle | happy | sad | think | celebrate | wave */
export function Mascot(props) {
  return <Codi {...props} />;
}

// Codi's face for the logo, on the same 16x16 grid as the mascot (see Codi.jsx): white head, dark screen, idle face.
const px = (list) => list.map(([x, y]) => `M${x} ${y}h1v1h-1z`).join("");
const rect = (x0, y0, x1, y1) => px(Array.from({ length: (y1 - y0 + 1) * (x1 - x0 + 1) }, (_, i) => [x0 + (i % (x1 - x0 + 1)), y0 + Math.floor(i / (x1 - x0 + 1))]));
const LOGO_HEAD = rect(3, 2, 12, 2) + rect(2, 3, 13, 10); // crown + head
const LOGO_SCREEN = rect(3, 4, 12, 9);
const LOGO_ANTENNA = px([[7, 0], [8, 0], [7, 1], [8, 1]]);
const LOGO_FACE = px([[5, 6], [6, 6], [5, 7], [6, 7], [9, 6], [10, 6], [9, 7], [10, 7], [7, 9], [8, 9]]); // Codi's idle face: two square eyes and a small mouth

/** The logo mark: Codi's face on a chunky rounded tile with a "pressed button" edge. */
export function LogoMark({ className = "h-10 w-10" }) {
  return (
    <span
      className={`grid shrink-0 place-items-center rounded-[0.8rem] bg-primary shadow-[0_3px_0_rgb(var(--primary-strong))] ${className}`}
      aria-hidden="true"
    >
      <svg viewBox="1 -0.6 14 12.2" className="h-[72%] w-[72%]" shapeRendering="crispEdges">
        <path d={LOGO_ANTENNA} fill="rgb(var(--gold))" />
        <path d={LOGO_HEAD} fill="#fff" />
        <path d={LOGO_SCREEN} fill="rgb(var(--primary-strong))" />
        <path d={LOGO_FACE} fill="#fff" />
      </svg>
    </span>
  );
}

export function Logo({ className = "", compact = false }) {
  return (
    <span className={`inline-flex items-center gap-2.5 text-[1.7rem] font-black leading-none tracking-[-0.03em] text-primary ${className}`}>
      <LogoMark />
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
      <Mascot size={80} mood="think" interactive={false} />
      <span className="mt-3 text-sm font-bold text-muted">{label}…</span>
    </div>
  );
}

/** Spring-animated bar. The fill scales on X (compositor-only) instead of animating width. */
export function ProgressBar({ value, max = 100, className = "" }) {
  const pct = Math.max(0, Math.min(1, value / Math.max(1, max)));
  return (
    <div
      className={`relative h-4 overflow-hidden rounded-full bg-primary/15 ${className}`}
      role="progressbar"
      aria-valuenow={Math.round(pct * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <motion.div
        className="absolute inset-0 origin-left rounded-full bg-primary"
        initial={false}
        animate={{ scaleX: pct }}
        transition={{ type: "spring", stiffness: 260, damping: 26 }}
      >
        <div className="absolute inset-x-2 top-1 h-1 rounded-full bg-white/30" />
      </motion.div>
    </div>
  );
}

/** Counts up/down to `value`, writing text directly to the DOM (no React re-render per frame). */
export function AnimatedNumber({ value, duration = 0.6 }) {
  const ref = useRef(null);
  const prev = useRef(value);
  const reduce = useReducedMotion();
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (reduce || prev.current === value) {
      el.textContent = String(value);
      prev.current = value;
      return;
    }
    const controls = animate(prev.current, value, {
      duration,
      ease: [0.2, 0.8, 0.2, 1],
      onUpdate: (v) => (el.textContent = String(Math.round(v))),
    });
    prev.current = value;
    return () => controls.stop();
  }, [value, duration, reduce]);
  return <span ref={ref}>{value}</span>;
}

export function StatPill({ icon, value, tone, label, infinite = false }) {
  const tones = { flame: "bg-flame/10 text-flame", bad: "bg-bad/10 text-bad", primary: "bg-primary/10 text-primary", gold: "bg-gold/10 text-gold" };
  return (
    <span className={`chip ${tones[tone]}`} title={label} aria-label={`${label}: ${infinite ? "unlimited" : value}`}>
      <motion.span key={value} initial={{ scale: 1.35 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 500, damping: 15 }}>
        <Icon name={icon} className="h-5 w-5" />
      </motion.span>
      {infinite ? <span className="text-xl leading-none">∞</span> : <AnimatedNumber value={value} />}
    </span>
  );
}

/** Each course's colour (a .tint-* class), used for its tabs, rows and cards. */
const COURSE_TINTS = {
  python: "tint-sky", javascript: "tint-gold", typescript: "", java: "tint-orange", cpp: "tint-violet", c: "tint-teal",
  sql: "tint-pink", "html-css": "tint-orange", git: "tint-pink", dsa: "tint-violet",
};
export const courseTint = (slug) => COURSE_TINTS[slug] ?? "";

/** A stable colour per person (from their name), for initials avatars on leaderboards. */
const PEOPLE_TINTS = ["", "tint-violet", "tint-pink", "tint-orange", "tint-teal", "tint-sky", "tint-gold"];
export function nameTint(name = "") {
  let h = 0;
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return PEOPLE_TINTS[h % PEOPLE_TINTS.length];
}

/** A rounded, tinted square holding an icon - takes the colour of the nearest .tint-* wrapper (or primary). */
export function IconTile({ icon, size = "md", className = "" }) {
  const box = { sm: "h-9 w-9 rounded-xl", md: "h-11 w-11 rounded-2xl", lg: "h-16 w-16 rounded-2xl" }[size];
  const glyph = { sm: "h-5 w-5", md: "h-6 w-6", lg: "h-9 w-9" }[size];
  return (
    <span className={`grid shrink-0 place-items-center bg-primary/15 text-primary ${box} ${className}`} aria-hidden="true">
      <Icon name={icon} className={glyph} />
    </span>
  );
}

/** Page heading with a coloured icon tile - wrap the page in a .tint-* class to pick its colour. */
export function PageTitle({ icon, title, subtitle, center = false }) {
  return (
    <div className={`mb-6 flex items-center gap-4 ${center ? "flex-col text-center" : ""}`}>
      <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-primary text-on-primary shadow-[0_4px_0_rgb(var(--primary-strong))]" aria-hidden="true">
        <Icon name={icon} className="h-9 w-9" />
      </span>
      <div>
        <h1 className="text-2xl font-black">{title}</h1>
        {subtitle && <p className="text-sm font-semibold text-muted">{subtitle}</p>}
      </div>
    </div>
  );
}

export function Modal({ open, onClose, children, label }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose?.();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4"
          role="dialog"
          aria-modal="true"
          aria-label={label}
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <motion.div
            className="card w-full max-w-md p-6"
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.9, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.95, y: 10, opacity: 0 }}
            transition={{ type: "spring", stiffness: 420, damping: 30 }}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
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
