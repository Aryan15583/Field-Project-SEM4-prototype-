"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import Codi from "@/components/Codi";
import { retryWake, useWakeState } from "@/lib/serverWake";

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

// Quiz + tips per course topic: [question, [options], index of the right one]
const TOPICS = {
  python: {
    label: "Python",
    tips: ["Python is named after Monty Python, not the snake.", "Indentation is part of Python's syntax - it marks blocks of code.", "Tip: len(x) tells you how many items a list or text has."],
    quiz: [
      ["Which symbol starts a comment in Python?", ["//", "#", "<!--"], 1],
      ["What does print(2 + 3 * 2) show?", ["10", "8", "12"], 1],
      ["Which one makes a list?", ["[1, 2, 3]", "{1, 2, 3}", "(1 2 3)"], 0],
      ["What does len(\"code\") return?", ["3", "4", "5"], 1],
      ["Which keyword starts a function?", ["func", "def", "fun"], 1],
      ["What is the type of 3.14?", ["int", "str", "float"], 2],
    ],
  },
  javascript: {
    label: "JavaScript",
    tips: ["JavaScript was written in just 10 days.", "Use === instead of == to compare without surprises.", "Tip: console.log() is your best friend for checking values."],
    quiz: [
      ["Which keyword makes a variable you can't reassign?", ["var", "let", "const"], 2],
      ["What does [1, 2, 3].length give?", ["2", "3", "4"], 1],
      ["Which prints to the console?", ["console.log()", "print()", "echo()"], 0],
      ["What is typeof \"hi\" ?", ["string", "text", "char"], 0],
      ["Which is an arrow function?", ["(x) => x * 2", "function => x", "x -> x * 2"], 0],
      ["What does '5' + 3 give?", ["8", "'53'", "error"], 1],
    ],
  },
  sql: {
    label: "SQL",
    tips: ["SQL is usually pronounced 'sequel' or letter by letter - both are fine.", "Always add WHERE to UPDATE and DELETE unless you mean every row!", "Tip: SELECT * is handy for peeking, but name the columns you need."],
    quiz: [
      ["Which command reads rows from a table?", ["SELECT", "FETCHALL", "READ"], 0],
      ["Which clause filters rows?", ["WHERE", "ORDER", "GROUP"], 0],
      ["What does ORDER BY age DESC do?", ["Oldest first", "Youngest first", "Deletes ages"], 0],
      ["Which function counts rows?", ["COUNT()", "TOTAL()", "NUMBER()"], 0],
      ["What does a PRIMARY KEY do?", ["Uniquely identifies a row", "Encrypts the table", "Sorts the table"], 0],
      ["Which adds a new row?", ["INSERT INTO", "ADD ROW", "PUT"], 0],
    ],
  },
  htmlcss: {
    label: "HTML & CSS",
    tips: ["The very first website is still online.", "Tip: one <h1> per page is a good habit for headings.", "Tip: browser DevTools (F12) let you edit CSS live."],
    quiz: [
      ["What does HTML stand for?", ["HyperText Markup Language", "High Tech Modern Logic", "Home Tool Making Language"], 0],
      ["Which tag makes a link?", ["<a>", "<link>", "<url>"], 0],
      ["What does CSS mostly control?", ["How a page looks", "The database", "Internet speed"], 0],
      ["Which CSS property changes text colour?", ["color", "font-paint", "text-style"], 0],
      ["Which tag is the biggest heading?", ["<h1>", "<h6>", "<head>"], 0],
      ["Which layout system arranges items in a row or column?", ["Flexbox", "Floatbox", "Rowbox"], 0],
    ],
  },
  git: {
    label: "Git",
    tips: ["Git was created by Linus Torvalds in 2005, in about two weeks.", "Tip: commit small and often, with a message that says why.", "Tip: git status tells you what's going on - use it a lot."],
    quiz: [
      ["Which command saves a snapshot to history?", ["git commit", "git cook", "git paint"], 0],
      ["Which command shows what changed?", ["git status", "git where", "git look"], 0],
      ["What does git clone do?", ["Copies a repository", "Deletes a branch", "Makes a backup of Git"], 0],
      ["What is a branch?", ["A parallel line of work", "A type of error", "A file format"], 0],
      ["Which stages files for the next commit?", ["git add", "git push", "git pull"], 0],
      ["Which uploads your commits to a remote?", ["git push", "git pull", "git fetch"], 0],
    ],
  },
  java: {
    label: "Java / C / C++",
    tips: ["Java's mascot is called Duke.", "In C and C++, every statement ends with a semicolon.", "Tip: these languages are compiled - read the compiler's first error first."],
    quiz: [
      ["Which Java method is the program's entry point?", ["main", "start", "run"], 0],
      ["What does int x = 5; do?", ["Stores 5 in a whole-number variable", "Prints 5", "Makes a loop"], 0],
      ["Which loop runs a set number of times?", ["for", "if", "else"], 0],
      ["What ends a statement in C?", [";", ".", ":"], 0],
      ["Which prints in C++?", ["std::cout", "print()", "echo"], 0],
      ["What does 7 / 2 give with whole numbers?", ["3", "3.5", "4"], 0],
    ],
  },
};
const TOPIC_IDS = Object.keys(TOPICS);

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
  const list = TOPICS[topic].quiz;
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
  const [topic, setTopic] = useState("python");
  useEffect(() => {
    try {
      const saved = localStorage.getItem("cg_wake_topic");
      if (saved in TOPICS) setTopic(saved);
    } catch {}
  }, []);
  const pickTopic = (id) => {
    setTopic(id);
    setTip(0);
    try {
      localStorage.setItem("cg_wake_topic", id);
    } catch {}
  };
  const tips = [...TOPICS[topic].tips, ...GENERAL_TIPS];

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

            <p className="mt-6 text-xs font-extrabold uppercase tracking-widest text-muted">Pick your topic</p>
            <div className="mt-2 flex flex-wrap justify-center gap-2">
              {TOPIC_IDS.map((id) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => pickTopic(id)}
                  className={`rounded-full border-2 px-3 py-1 text-xs font-bold ${topic === id ? "border-primary bg-primary/10 text-primary" : "border-line text-muted"}`}
                >
                  {TOPICS[id].label}
                </button>
              ))}
            </div>

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
