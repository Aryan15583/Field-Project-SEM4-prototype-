"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import Codi from "@/components/Codi";
import { retryWake, useWakeState } from "@/lib/serverWake";
import { QUESTIONS } from "@/lib/wakeQuiz";

/*
 * Shown while the (free, sleepy) API server wakes up - usually 30-60 seconds. Instead of a blank wait it offers a
 * tiny Snake game with coding questions, and carries on by itself the moment the server answers (lib/serverWake.js).
 */
const TIPS = [
  "Fun fact: the first computer bug was a real moth stuck in a machine in 1947.",
  "Tip: read an error message from the top - it usually tells you the line.",
  "Tip: small steps beat big leaps. Run your code after every few lines.",
  "Tip: when stuck, explain the problem out loud. It works surprisingly often.",
  "Fun fact: Python is named after Monty Python, not the snake.",
  "Fun fact: JavaScript was written in just 10 days.",
  "Tip: a variable is just a labelled box that holds a value.",
  "Fun fact: the very first website is still online.",
];

// Snake with a question: three lettered foods sit on the board - eat the right answer to grow, a wrong one costs a life.
const SIZE = 12;
const CELL = 24;
const TICK_MS = 190;
const LIVES = 3;
const DIRS = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
const KEYS = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right", w: "up", s: "down", a: "left", d: "right" };
const LETTERS = ["A", "B", "C"];

const at = (list, x, y) => list.some((p) => p.x === x && p.y === y);

function newRound(snake, previous) {
  let q;
  do q = QUESTIONS[Math.floor(Math.random() * QUESTIONS.length)];
  while (q === previous && QUESTIONS.length > 1);
  const order = shuffle([0, 1, 2]); // option positions are shuffled each time
  const foods = [];
  order.forEach((optionIndex, n) => {
    let x, y;
    do {
      x = Math.floor(Math.random() * SIZE);
      y = Math.floor(Math.random() * SIZE);
    } while (at(snake, x, y) || at(foods, x, y));
    foods.push({ x, y, letter: LETTERS[n], text: q[1][optionIndex], right: optionIndex === q[2] });
  });
  return { question: q, foods };
}

const fresh = () => {
  const snake = [{ x: 5, y: 6 }, { x: 4, y: 6 }, { x: 3, y: 6 }];
  return { snake, dir: "right", next: "right", lives: LIVES, score: 0, ...newRound(snake, null) };
};

const shuffle = (a) => {
  const x = [...a];
  for (let i = x.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [x[i], x[j]] = [x[j], x[i]];
  }
  return x;
};

function SnakeGame() {
  const canvas = useRef(null);
  const game = useRef(fresh());
  const [phase, setPhase] = useState("ready"); // ready | playing | over
  const [view, setView] = useState({ score: 0, lives: LIVES, question: game.current.question, foods: game.current.foods, note: "" });
  const [best, setBest] = useState(0);
  const phaseRef = useRef("ready");
  const colors = useRef({});

  const sync = (note = "") => {
    const g = game.current;
    setView({ score: g.score, lives: g.lives, question: g.question, foods: g.foods, note });
  };

  const draw = useCallback(() => {
    const el = canvas.current;
    if (!el) return;
    const ctx = el.getContext("2d");
    const g = game.current;
    const c = colors.current;
    ctx.fillStyle = c.bg;
    ctx.fillRect(0, 0, SIZE * CELL, SIZE * CELL);
    ctx.fillStyle = c.line;
    for (let x = 0; x < SIZE; x++) for (let y = 0; y < SIZE; y++) if ((x + y) % 2) ctx.fillRect(x * CELL, y * CELL, CELL, CELL);
    g.snake.forEach((p, i) => {
      ctx.fillStyle = i === 0 ? c.primaryStrong : c.primary;
      ctx.beginPath();
      ctx.roundRect(p.x * CELL + 2, p.y * CELL + 2, CELL - 4, CELL - 4, 6);
      ctx.fill();
    });
    ctx.font = "800 14px ui-rounded, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    g.foods.forEach((f) => {
      ctx.fillStyle = c.gold;
      ctx.beginPath();
      ctx.arc(f.x * CELL + CELL / 2, f.y * CELL + CELL / 2, CELL / 2 - 1, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = c.ink;
      ctx.fillText(f.letter, f.x * CELL + CELL / 2, f.y * CELL + CELL / 2 + 1);
    });
  }, []);

  const readColors = () => {
    const css = getComputedStyle(document.documentElement);
    const rgb = (n) => `rgb(${css.getPropertyValue(`--${n}`).trim().split(/\s+/).join(" ")})`;
    colors.current = { bg: rgb("raised"), line: rgb("surface"), primary: rgb("primary"), primaryStrong: rgb("primary-strong"), gold: rgb("gold"), ink: rgb("ink") };
  };

  useEffect(() => {
    readColors();
    setBest(store.get("cg_snake_best"));
    draw();
  }, [draw]);

  const turn = useCallback((d) => {
    const g = game.current;
    const [dx, dy] = DIRS[d];
    const [cx, cy] = DIRS[g.dir];
    if (dx + cx !== 0 || dy + cy !== 0) g.next = d; // no instant U-turn
  }, []);

  const start = () => {
    game.current = fresh();
    phaseRef.current = "playing";
    setPhase("playing");
    sync();
    draw();
  };

  const loseLife = (g, note) => {
    g.lives -= 1;
    if (g.lives <= 0) {
      phaseRef.current = "over";
      setPhase("over");
      if (g.score > store.get("cg_snake_best")) {
        store.set("cg_snake_best", g.score);
        setBest(g.score);
      }
    }
    return note;
  };

  useEffect(() => {
    const step = () => {
      if (phaseRef.current !== "playing") return;
      const g = game.current;
      g.dir = g.next;
      const [dx, dy] = DIRS[g.dir];
      const head = { x: (g.snake[0].x + dx + SIZE) % SIZE, y: (g.snake[0].y + dy + SIZE) % SIZE }; // walls wrap around
      let note = "";
      if (at(g.snake.slice(0, -1), head.x, head.y)) {
        note = loseLife(g, "Ouch - you bit yourself!");
        g.snake = g.snake.slice(0, 3);
        g.snake.forEach((p, i) => ((p.x = 5 - i), (p.y = 6)));
        g.dir = g.next = "right";
      } else {
        const food = g.foods.find((f) => f.x === head.x && f.y === head.y);
        g.snake.unshift(head);
        if (!food) g.snake.pop();
        else if (food.right) {
          g.score += 1;
          note = "Correct! 🎉";
          Object.assign(g, newRound(g.snake, g.question));
        } else {
          g.snake.pop();
          const answer = g.foods.find((f) => f.right);
          note = loseLife(g, `Not quite - it was ${answer.letter}: ${answer.text}`);
          Object.assign(g, newRound(g.snake, g.question));
        }
      }
      sync(note);
      draw();
    };
    const timer = setInterval(step, TICK_MS);
    return () => clearInterval(timer);
  }, [draw]);

  useEffect(() => {
    const onKey = (e) => {
      const d = KEYS[e.key];
      if (!d || phaseRef.current !== "playing") return;
      e.preventDefault();
      turn(d);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [turn]);

  const touch = useRef(null);
  const onTouchStart = (e) => (touch.current = [e.touches[0].clientX, e.touches[0].clientY]);
  const onTouchEnd = (e) => {
    if (!touch.current) return;
    const dx = e.changedTouches[0].clientX - touch.current[0];
    const dy = e.changedTouches[0].clientY - touch.current[1];
    touch.current = null;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) return;
    turn(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "right" : "left") : dy > 0 ? "down" : "up");
  };

  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm font-bold">
        <span>Score {view.score}{best ? <span className="font-normal text-muted"> · best {best}</span> : null}</span>
        <span aria-label={`${view.lives} lives left`}>{"❤️".repeat(view.lives)}{"🖤".repeat(LIVES - view.lives)}</span>
      </div>
      <p className="mb-2 min-h-[2.5rem] text-sm font-bold leading-snug">{view.question[0]}</p>
      <div className="mb-2 grid gap-1 text-sm">
        {view.foods.slice().sort((a, b) => a.letter.localeCompare(b.letter)).map((f) => (
          <p key={f.letter} className="flex items-center gap-2">
            <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-gold text-xs font-extrabold text-ink">{f.letter}</span>
            {f.text}
          </p>
        ))}
      </div>
      <div className="relative mx-auto" style={{ width: SIZE * CELL, maxWidth: "100%" }}>
        <canvas
          ref={canvas}
          width={SIZE * CELL}
          height={SIZE * CELL}
          onTouchStart={onTouchStart}
          onTouchEnd={onTouchEnd}
          className="w-full rounded-2xl border-2 border-line"
          style={{ touchAction: "none" }}
          aria-label="Snake game board"
        />
        {phase !== "playing" && (
          <div className="absolute inset-0 grid place-items-center rounded-2xl bg-bg/85 p-3 text-center">
            <div>
              <p className="font-bold">{phase === "over" ? `Game over - score ${view.score}` : "Eat the right answer to grow!"}</p>
              <p className="mt-1 text-xs text-muted">Swipe, use the arrows or WASD. The walls wrap around.</p>
              <button type="button" onClick={start} className="btn-primary mt-3">{phase === "over" ? "Play again" : "Start"}</button>
            </div>
          </div>
        )}
      </div>
      <p className="mt-2 min-h-[1.25rem] text-center text-sm font-semibold text-muted" aria-live="polite">{view.note}</p>
      <div className="mx-auto mt-1 grid w-40 grid-cols-3 gap-1.5 sm:hidden">
        {[[null], ["up"], [null], ["left"], ["down"], ["right"]].map(([d], i) =>
          d ? (
            <button key={i} type="button" onClick={() => turn(d)} aria-label={d} className="grid h-10 place-items-center rounded-xl border-2 border-line bg-surface text-lg active:scale-95">
              {{ up: "▲", down: "▼", left: "◀", right: "▶" }[d]}
            </button>
          ) : (
            <span key={i} />
          ),
        )}
      </div>
    </div>
  );
}

const store = {
  get: (k) => {
    try {
      return Number(localStorage.getItem(k)) || 0;
    } catch {
      return 0;
    }
  },
  set: (k, v) => {
    try {
      localStorage.setItem(k, String(v));
    } catch {}
  },
};

export default function WakingScreen() {
  const { waking, failed, startedAt } = useWakeState();
  const [secs, setSecs] = useState(0);
  const [tip, setTip] = useState(0);

  useEffect(() => {
    if (!waking) return;
    const t = setInterval(() => setSecs(Math.floor((Date.now() - startedAt) / 1000)), 500);
    const r = setInterval(() => setTip((x) => (x + 1) % TIPS.length), 6000);
    return () => {
      clearInterval(t);
      clearInterval(r);
      setSecs(0);
    };
  }, [waking, startedAt]);

  const progress = Math.min(92, (1 - Math.exp(-secs / 28)) * 100); // eases towards 92% - never claims to be done
  const again = useCallback(() => retryWake(), []);

  return (
    <AnimatePresence>
      {waking && (
        <motion.div
          key="waking"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          role="status"
          aria-live="polite"
          className="fixed inset-0 z-[100] overflow-y-auto bg-bg"
        >
          <div className="mx-auto flex min-h-full max-w-md flex-col items-center justify-center px-4 py-4 text-center">
            <Codi size={64} mood={failed ? "sad" : "think"} />
            <h1 className="mt-2 text-2xl font-extrabold">
              {failed ? "Still asleep…" : "Waking the server up"}
            </h1>
            <p className="mt-1 text-sm text-muted">
              {failed
                ? "It's taking longer than usual."
                : "It naps when nobody is around. This takes up to a minute - play while you wait!"}
            </p>

            {failed ? (
              <button type="button" onClick={again} className="btn-primary mt-4">
                Try again
              </button>
            ) : (
              <div className="mt-4 w-full">
                <div className="h-3 overflow-hidden rounded-full bg-surface">
                  <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${progress}%` }} />
                </div>
                <p className="mt-1 text-xs text-muted">{secs}s</p>
              </div>
            )}

            <div className="card mt-4 w-full p-3 text-left">
              <SnakeGame />
            </div>

            <p className="mt-5 min-h-[2.5rem] text-sm text-muted">{TIPS[tip]}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
