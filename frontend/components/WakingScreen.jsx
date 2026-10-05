"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";
import Codi from "@/components/Codi";
import { retryWake, useWakeState } from "@/lib/serverWake";

/*
 * Shown while the (free, sleepy) API server wakes up - usually 30-60 seconds. Instead of a blank wait it offers a
 * tiny coding memory game, and carries on by itself the moment the server answers (lib/serverWake.js).
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

// Symbol Match: flip two cards - a coding symbol and its name - to pair them up.
const PAIRS = [
  ["{ }", "curly braces"],
  ["[ ]", "square brackets"],
  ["( )", "parentheses"],
  ["==", "equals?"],
  ["=", "assign"],
  ["//", "comment"],
  ["&&", "and"],
  ["||", "or"],
  ["!", "not"],
  ["< >", "tag"],
  [";", "end of line"],
  ["\" \"", "string"],
];

const shuffle = (a) => {
  const x = [...a];
  for (let i = x.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [x[i], x[j]] = [x[j], x[i]];
  }
  return x;
};

const deal = () =>
  shuffle(
    shuffle(PAIRS)
      .slice(0, 6)
      .flatMap(([sym, name], id) => [
        { key: `${id}a`, id, text: sym, code: true },
        { key: `${id}b`, id, text: name, code: false },
      ]),
  );

function SymbolMatch() {
  const [cards, setCards] = useState([]);
  const [open, setOpen] = useState([]); // keys of the face-up, not yet matched cards
  const [done, setDone] = useState([]); // matched pair ids
  const [moves, setMoves] = useState(0);
  const [best, setBest] = useState(0);
  const newGame = useCallback(() => {
    setCards(deal());
    setOpen([]);
    setDone([]);
    setMoves(0);
  }, []);
  useEffect(() => {
    newGame();
    setBest(store.get("cg_match_best"));
  }, [newGame]);

  const won = cards.length > 0 && done.length === cards.length / 2;
  useEffect(() => {
    if (won && (!best || moves < best)) {
      setBest(moves);
      store.set("cg_match_best", moves);
    }
  }, [won]); // eslint-disable-line react-hooks/exhaustive-deps

  const flip = (c) => {
    if (open.length === 2 || open.includes(c.key) || done.includes(c.id)) return;
    const next = [...open, c.key];
    setOpen(next);
    if (next.length < 2) return;
    setMoves((m) => m + 1);
    const [a, b] = next.map((k) => cards.find((x) => x.key === k));
    setTimeout(() => {
      if (a.id === b.id) setDone((d) => [...d, a.id]);
      setOpen([]);
    }, 750);
  };

  return (
    <div>
      <p className="mb-3 text-sm text-muted">Symbol match: flip two cards to pair a coding symbol with its name.</p>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
        {cards.map((c) => {
          const up = open.includes(c.key) || done.includes(c.id);
          return (
            <button
              key={c.key}
              type="button"
              onClick={() => flip(c)}
              aria-label={up ? c.text : "Hidden card"}
              className={`grid h-16 place-items-center rounded-2xl border-2 px-1 text-center text-sm font-bold active:scale-95 ${
                done.includes(c.id) ? "border-primary bg-primary/10" : up ? "border-primary bg-raised" : "border-line bg-surface text-muted"
              } ${up && c.code ? "font-mono text-lg" : ""}`}
            >
              {up ? c.text : "?"}
            </button>
          );
        })}
      </div>
      <div className="mt-3 flex items-center justify-between text-sm">
        <p className="font-bold">
          {won ? `Done in ${moves} moves! 🎉` : `Moves ${moves}`} <span className="font-normal text-muted">{best ? `· best ${best}` : ""}</span>
        </p>
        <button type="button" onClick={newGame} className="rounded-full bg-surface px-3 py-1.5 font-bold text-muted">
          New game
        </button>
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
          <div className="mx-auto flex min-h-full max-w-md flex-col items-center justify-center px-4 py-8 text-center">
            <Codi size={96} mood={failed ? "sad" : "think"} />
            <h1 className="mt-4 text-2xl font-extrabold">
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

            <div className="card mt-6 w-full p-4 text-left">
              <SymbolMatch />
            </div>

            <p className="mt-5 min-h-[2.5rem] text-sm text-muted">{TIPS[tip]}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
