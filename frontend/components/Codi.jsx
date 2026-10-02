"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useId, useRef, useState } from "react";

/*
 * Codi - Codeingo's pixel-art mascot: a little screen-faced bot with </> bracket arms.
 * Drawn on a 16x16 pixel grid (crisp edges), coloured from the theme: blue in light mode,
 * green in dark mode (the screen turns into a dark terminal with glowing eyes).
 *
 * Moods: idle | happy | sad | think | celebrate | wave
 * Alive by default: bobs, blinks at random, antenna glows, eyes follow the pointer, and it
 * reacts when tapped. Every animation is transform/opacity only (60 fps) and it holds still
 * for users who prefer reduced motion.
 */

// ---------------------------------------------------------------- pixel art
// Each string is one row, 16 pixels wide:  P body  S shade/outline  W screen  G gold  . empty
const BODY = [
  ".......GG.......",
  ".......SS.......",
  "...PPPPPPPPPP...",
  "..PPPPPPPPPPPP..",
  "..PWWWWWWWWWWP..",
  "..PWWWWWWWWWWP..",
  "..PWWWWWWWWWWP..",
  "..PWWWWWWWWWWP..",
  "..PWWWWWWWWWWP..",
  "..PWWWWWWWWWWP..",
  "..PPPPPPPPPPPP..",
  "...SSSSSSSSSS...",
  "..PPPPPPPPPPPP..",
  "..PPPPPPPPPPPP..",
  "..PPPPPPPPPPPP..",
  "....SSS..SSS....",
];

/** Turns rows of characters into one SVG path per colour (a few DOM nodes, not 200 rects). */
function toPaths(rows, colors = "PSWG") {
  const out = {};
  for (const c of colors) out[c] = "";
  rows.forEach((row, y) => {
    for (let x = 0; x < row.length; x++) {
      const c = row[x];
      if (c in out) out[c] += `M${x} ${y}h1v1h-1z`;
    }
  });
  return out;
}

const px = (list) => list.map(([x, y]) => `M${x} ${y}h1v1h-1z`).join("");
const BODY_PATHS = toPaths(BODY);
const ARM_LEFT = px([[1, 12], [0, 13], [1, 14]]); //  <
const ARM_RIGHT = px([[14, 12], [15, 13], [14, 14]]); //  >

// Faces live on the screen (x 3..12, y 4..9)
const EYES = {
  open: px([[5, 6], [6, 6], [5, 7], [6, 7], [9, 6], [10, 6], [9, 7], [10, 7]]),
  happy: px([[4, 7], [5, 6], [6, 7], [9, 7], [10, 6], [11, 7]]), // ^ ^
  sad: px([[5, 7], [6, 7], [9, 7], [10, 7], [4, 5], [5, 6], [11, 5], [10, 6]]), // eyes + sloped brows
  up: px([[6, 5], [7, 5], [6, 6], [7, 6], [10, 5], [11, 5], [10, 6], [11, 6]]), // thinking: looking up-right
  star: px([[5, 6], [4, 7], [5, 7], [6, 7], [5, 8], [10, 6], [9, 7], [10, 7], [11, 7], [10, 8]]), // + +
};
const MOUTH = {
  idle: px([[7, 9], [8, 9]]),
  happy: px([[5, 8], [6, 9], [7, 9], [8, 9], [9, 9], [10, 8]]),
  sad: px([[6, 9], [7, 8], [8, 8], [9, 9]]),
  think: px([[8, 9], [9, 9]]),
  open: px([[6, 8], [7, 8], [8, 8], [9, 8], [6, 9], [7, 9], [8, 9], [9, 9]]),
};
const FACE = {
  idle: { eyes: "open", mouth: "idle", track: true },
  wave: { eyes: "happy", mouth: "happy", track: false },
  happy: { eyes: "happy", mouth: "happy", track: false },
  sad: { eyes: "sad", mouth: "sad", track: false },
  think: { eyes: "up", mouth: "think", track: false },
  celebrate: { eyes: "star", mouth: "open", track: false },
};

// Body motion per mood (in grid pixels - the whole drawing is 16 units tall)
const BODY_MOTION = {
  idle: { y: 0, x: 0, rotate: 0 },
  wave: { y: [0, -1.5, 0], transition: { duration: 0.5, repeat: 1 } },
  happy: { y: [0, -3, 0, -1.5, 0], transition: { duration: 0.7, ease: "easeOut" } },
  sad: { x: [0, -0.8, 0.8, -0.5, 0.5, 0], y: 0.8, transition: { duration: 0.5 } },
  think: { rotate: [0, -4, -4], transition: { duration: 0.4 } },
  celebrate: { y: [0, -4, 0], transition: { duration: 0.55, repeat: Infinity, repeatDelay: 0.15, ease: "easeOut" } },
};

// ---------------------------------------------------------------- pointer tracking (shared)
const trackers = new Set();
let pointer = null;
let frame = 0;
function onPointerMove(e) {
  pointer = { x: e.clientX, y: e.clientY };
  if (!frame) {
    frame = requestAnimationFrame(() => {
      frame = 0;
      trackers.forEach((fn) => fn(pointer));
    });
  }
}
function subscribe(fn) {
  if (!trackers.size) window.addEventListener("pointermove", onPointerMove, { passive: true });
  trackers.add(fn);
  return () => {
    trackers.delete(fn);
    if (!trackers.size) window.removeEventListener("pointermove", onPointerMove);
  };
}

function useLook(ref, enabled) {
  const [look, setLook] = useState({ x: 0, y: 0 });
  useEffect(() => {
    if (!enabled) {
      setLook({ x: 0, y: 0 });
      return;
    }
    return subscribe((p) => {
      const el = ref.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const dx = p.x - (r.left + r.width / 2);
      const dy = p.y - (r.top + r.height * 0.4);
      // discrete, pixel-art style: -1, 0 or 1 grid pixel in each direction
      // (eyes only look up or sideways - looking down would overlap the mouth)
      const next = { x: Math.abs(dx) < r.width * 0.4 ? 0 : Math.sign(dx), y: dy < -r.height * 0.4 ? -1 : 0 };
      setLook((cur) => (cur.x === next.x && cur.y === next.y ? cur : next));
    });
  }, [ref, enabled]);
  return look;
}

// ---------------------------------------------------------------- component
export default function Codi({ size = 120, mood = "idle", className = "", interactive = true, title = "Codi, the Codeingo mascot" }) {
  const reduce = useReducedMotion();
  const ref = useRef(null);
  const uid = useId().replace(/:/g, "");
  const [poke, setPoke] = useState(0); // tapping Codi makes it hop
  const [pokeMood, setPokeMood] = useState(null);
  const current = pokeMood || (FACE[mood] ? mood : "idle");
  const face = FACE[current];
  const look = useLook(ref, face.track && !reduce);

  useEffect(() => {
    if (!pokeMood) return;
    const t = setTimeout(() => setPokeMood(null), 900);
    return () => clearTimeout(t);
  }, [pokeMood, poke]);

  const onTap = () => {
    if (!interactive) return;
    setPoke((n) => n + 1);
    setPokeMood(Math.random() < 0.5 ? "happy" : "wave");
  };

  // random blink timing so several Codis on screen don't blink in sync
  const blinkDelay = useRef(`${(Math.random() * 3).toFixed(2)}s`).current;
  const waving = current === "wave" || current === "celebrate";
  const idleLoops = !reduce && current !== "sad";

  return (
    <svg
      ref={ref}
      viewBox="-4 -5 24 24"
      width={size}
      height={size}
      style={{ width: `${size / 16}rem`, height: `${size / 16}rem` }}
      className={`codi ${className} ${interactive ? "cursor-pointer" : ""}`}
      shapeRendering="crispEdges"
      role="img"
      aria-label={title}
      onClick={onTap}
    >
      <title>{title}</title>
      {/* ground shadow shrinks as Codi jumps */}
      <ellipse cx="8" cy="16.6" rx="6" ry="0.8" className="fill-ink/10" shapeRendering="auto" />

      <motion.g
        key={`${current}-${poke}`}
        initial={false}
        animate={reduce ? { x: 0, y: 0, rotate: 0 } : BODY_MOTION[current]}
        style={{ originX: "50%", originY: "100%" }}
      >
        <g className={idleLoops ? "codi-bob" : ""}>
          {/* arms: </> brackets - they wave when happy/celebrating */}
          <g className={waving && !reduce ? "codi-arm-l" : ""}>
            <path d={ARM_LEFT} className="fill-primary-strong" />
          </g>
          <g className={waving && !reduce ? "codi-arm-r" : ""}>
            <path d={ARM_RIGHT} className="fill-primary-strong" />
          </g>

          <path d={BODY_PATHS.P} className="fill-primary" />
          <path d={BODY_PATHS.S} className="fill-primary-strong" />
          <path d={BODY_PATHS.W} style={{ fill: "rgb(var(--codi-screen))" }} />
          <path d={BODY_PATHS.G} className={`fill-gold ${idleLoops ? "codi-glow" : ""}`} />
          {/* screen highlight */}
          <path d={px([[3, 4], [4, 4]])} style={{ fill: "rgb(var(--codi-shine))" }} />

          {/* face */}
          <g style={{ fill: "rgb(var(--codi-eye))" }}>
            <g transform={`translate(${look.x} ${look.y})`}>
              <g className={face.eyes === "open" && idleLoops ? "codi-blink" : ""} style={{ animationDelay: blinkDelay }}>
                <path d={EYES[face.eyes]} />
              </g>
            </g>
            <path d={MOUTH[face.mouth]} />
          </g>
        </g>
      </motion.g>

      {/* thinking dots */}
      <AnimatePresence>
        {current === "think" && (
          <motion.g key="dots" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fill-muted">
            {[0, 1, 2].map((i) => (
              <rect key={i} x={11 + i * 2} y={-3} width="1" height="1" className={reduce ? "" : "codi-dot"} style={{ animationDelay: `${i * 0.2}s` }} />
            ))}
          </motion.g>
        )}
      </AnimatePresence>

      {/* celebration sparkles */}
      {current === "celebrate" && !reduce && (
        <g className="fill-gold" aria-hidden="true">
          {[
            [-2, 2, 0],
            [17, 1, 0.3],
            [-3, 9, 0.6],
            [18, 8, 0.15],
            [1, -3, 0.45],
            [14, -4, 0.75],
          ].map(([x, y, d]) => (
            <path key={`${uid}-${x}-${y}`} d={px([[x, y], [x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]])} className="codi-spark" style={{ animationDelay: `${d}s` }} />
          ))}
        </g>
      )}
    </svg>
  );
}
