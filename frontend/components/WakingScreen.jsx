"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import Codi from "@/components/Codi";
import { retryWake, useWakeState } from "@/lib/serverWake";
import { MIX_QUIZ, MIX_TIPS, TOPICS, TOPIC_IDS, topicForCourse } from "@/lib/wakeTopics";

/*
 * Shown while the (free, sleepy) API server wakes up - usually 30-60 seconds. Instead of a blank wait it offers a
 * tiny game and a quiz, and carries on by itself the moment the server answers (lib/serverWake.js).
 */
const GENERAL_TIPS = [
  "Fun fact: the first computer bug was a real moth stuck in a machine in 1947.",
  "Tip: read an error message from the top - it usually tells you the line.",
  "Tip: small steps beat big leaps. Run your code after every few lines.",
  "Tip: when stuck, explain the problem out loud. It works surprisingly often.",
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

function Quiz({ topic }) {
  const list = topic === "mix" ? MIX_QUIZ : TOPICS[topic].quiz;
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  useEffect(() => {
    setI(Math.floor(Math.random() * list.length));
    setPicked(null);
    setScore(0);
  }, [topic, list.length]);
  const [q, options, answer] = list[i % list.length];
  const choose = (n) => {
    if (picked !== null) return;
    setPicked(n);
    if (n === answer) setScore((x) => x + 1);
    setTimeout(() => {
      setPicked(null);
      setI((x) => (x + 1) % list.length);
    }, 1100);
  };
  return (
    <div>
      <p className="mb-3 font-bold">{q}</p>
      <div className="grid gap-2">
        {options.map((text, n) => {
          const state = picked === null ? "" : n === answer ? "border-primary bg-primary/10" : n === picked ? "border-bad bg-bad/10" : "opacity-60";
          return (
            <button key={text} type="button" onClick={() => choose(n)} className={`rounded-2xl border-2 border-line bg-raised px-4 py-3 text-left text-sm font-semibold ${state}`}>
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
  const [tab, setTab] = useState("quiz");
  const [topic, setTopic] = useState("mix");
  useEffect(() => {
    try {
      const saved = localStorage.getItem("cg_wake_topic"); // an explicit choice wins ...
      const fromCourse = topicForCourse(localStorage.getItem("cg_course")); // ... else the course they were last in
      setTopic(saved === "mix" || saved in TOPICS ? saved : fromCourse);
    } catch {}
  }, []);
  const pickTopic = (id) => {
    setTopic(id);
    setTip(0);
    try {
      localStorage.setItem("cg_wake_topic", id);
    } catch {}
  };
  const tips = [...(topic === "mix" ? MIX_TIPS : TOPICS[topic].tips), ...GENERAL_TIPS];

  useEffect(() => {
    if (!waking) return;
    const t = setInterval(() => setSecs(Math.floor((Date.now() - startedAt) / 1000)), 500);
    const r = setInterval(() => setTip((x) => x + 1), 6000);
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

            <label className="mt-6 flex items-center gap-2 text-xs font-extrabold uppercase tracking-widest text-muted">
              Quiz topic
              <select
                value={topic}
                onChange={(e) => pickTopic(e.target.value)}
                className="max-w-[12rem] rounded-full border-2 border-line bg-raised px-3 py-1.5 text-sm font-bold normal-case tracking-normal text-ink"
              >
                <option value="mix">🎲 Mix of everything</option>
                {TOPIC_IDS.map((id) => (
                  <option key={id} value={id}>
                    {TOPICS[id].label}
                  </option>
                ))}
              </select>
            </label>

            <div className="card mt-4 w-full p-4 text-left">
              <div className="mb-3 flex gap-2">
                {[
                  ["quiz", "🧠 Topic quiz"],
                  ["bugs", "🐛 Squash bugs"],
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
              {tab === "bugs" ? <Bugs /> : <Quiz topic={topic} />}
            </div>

            <p className="mt-5 min-h-[2.5rem] text-sm text-muted">{tips[tip % tips.length]}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
