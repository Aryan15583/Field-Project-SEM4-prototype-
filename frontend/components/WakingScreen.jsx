"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import Codi from "@/components/Codi";
import { retryWake, useWakeState } from "@/lib/serverWake";

/*
 * Shown while the (free, sleepy) API server wakes up - usually 30-60 seconds. Instead of a blank wait it offers a
 * tiny game and a quiz, and carries on by itself the moment the server answers (lib/serverWake.js).
 */
const TIPS = [
  "Fun fact: the first computer bug was a real moth stuck in a machine in 1947.",
  "Tip: read an error message from the top - it usually tells you the line.",
  "Tip: a variable is just a labelled box that holds a value.",
  "Fun fact: Python is named after Monty Python, not the snake.",
  "Tip: small steps beat big leaps. Run your code after every few lines.",
  "Fun fact: the very first website is still online.",
  "Tip: when stuck, explain the problem out loud. It works surprisingly often.",
  "Fun fact: JavaScript was written in just 10 days.",
];

const QUIZ = [
  { q: "Which symbol starts a comment in Python?", o: ["//", "#", "<!--"], a: 1 },
  { q: "What does HTML stand for?", o: ["HyperText Markup Language", "High Tech Modern Logic", "Home Tool Making Language"], a: 0 },
  { q: "What is 2 + 2 * 3 ?", o: ["12", "8", "10"], a: 1 },
  { q: "Which one is a loop?", o: ["for", "if", "print"], a: 0 },
  { q: "True or false: a string can hold text.", o: ["True", "False"], a: 0 },
  { q: "Which command saves your work in Git history?", o: ["git commit", "git cook", "git paint"], a: 0 },
  { q: "What does CSS mostly control?", o: ["How a page looks", "The database", "The internet speed"], a: 0 },
  { q: "An array is best described as…", o: ["A list of values", "A type of error", "A web browser"], a: 0 },
  { q: "What does a function do?", o: ["Reuses a block of code", "Deletes your file", "Turns off the computer"], a: 0 },
  { q: "SQL is used to talk to a…", o: ["Database", "Printer", "Monitor"], a: 0 },
];

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

function Bugs() {
  const [on, setOn] = useState(-1);
  const [score, setScore] = useState(0);
  const [best, setBest] = useState(0);
  const [miss, setMiss] = useState(false);
  const scoreRef = useRef(0);
  useEffect(() => setBest(store.get("cg_bugs_best")), []);
  useEffect(() => {
    const t = setInterval(() => setOn(Math.floor(Math.random() * 9)), 850);
    return () => clearInterval(t);
  }, []);
  const hit = (i) => {
    if (i !== on) {
      scoreRef.current = 0;
      setScore(0);
      setMiss(true);
      setTimeout(() => setMiss(false), 250);
      return;
    }
    scoreRef.current += 1;
    setScore(scoreRef.current);
    setOn(-1);
    if (scoreRef.current > best) {
      setBest(scoreRef.current);
      store.set("cg_bugs_best", scoreRef.current);
    }
  };
  return (
    <div>
      <p className="mb-3 text-sm text-muted">Squash the bugs! Tap a bug when it pops up. Missing resets your streak.</p>
      <div className={`mx-auto grid max-w-[260px] grid-cols-3 gap-2 ${miss ? "opacity-70" : ""}`}>
        {Array.from({ length: 9 }, (_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => hit(i)}
            aria-label={i === on ? "Bug" : "Empty hole"}
            className="grid aspect-square place-items-center rounded-2xl border-2 border-line bg-surface text-3xl active:scale-95"
          >
            {i === on ? "🐛" : ""}
          </button>
        ))}
      </div>
      <p className="mt-3 text-sm font-bold">
        Streak {score} <span className="font-normal text-muted">· best {best}</span>
      </p>
    </div>
  );
}

function Quiz() {
  const [i, setI] = useState(() => Math.floor(Math.random() * QUIZ.length));
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const item = QUIZ[i];
  const choose = (n) => {
    if (picked !== null) return;
    setPicked(n);
    if (n === item.a) setScore((s) => s + 1);
    setTimeout(() => {
      setPicked(null);
      setI((x) => (x + 1) % QUIZ.length);
    }, 1100);
  };
  return (
    <div>
      <p className="mb-3 font-bold">{item.q}</p>
      <div className="grid gap-2">
        {item.o.map((text, n) => {
          const state = picked === null ? "" : n === item.a ? "border-primary bg-primary/10" : n === picked ? "border-bad bg-bad/10" : "opacity-60";
          return (
            <button
              key={text}
              type="button"
              onClick={() => choose(n)}
              className={`rounded-2xl border-2 border-line bg-raised px-4 py-3 text-left text-sm font-semibold ${state}`}
            >
              {text}
            </button>
          );
        })}
      </div>
      <p className="mt-3 text-sm text-muted">Correct so far: {score}</p>
    </div>
  );
}

export default function WakingScreen() {
  const { waking, failed, startedAt } = useWakeState();
  const [secs, setSecs] = useState(0);
  const [tip, setTip] = useState(0);
  const [tab, setTab] = useState("bugs");

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
              <div className="mb-3 flex gap-2">
                {[
                  ["bugs", "🐛 Squash bugs"],
                  ["quiz", "🧠 Quick quiz"],
                ].map(([id, label]) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setTab(id)}
                    className={`rounded-full px-3 py-1.5 text-sm font-bold ${tab === id ? "bg-primary text-on-primary" : "bg-surface text-muted"}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
              {tab === "bugs" ? <Bugs /> : <Quiz />}
            </div>

            <p className="mt-5 min-h-[2.5rem] text-sm text-muted">{TIPS[tip]}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
