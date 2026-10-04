"use client";

import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import Confetti from "@/components/Confetti";
import QuizRunner, { QuizMessage, QuizSkeleton } from "@/components/QuizRunner";
import { Icon, Mascot } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { sfx } from "@/lib/feedback";
import { useTheme } from "@/lib/theme";

function nextDueText(iso) {
  if (!iso) return null;
  const hours = (new Date(iso) - Date.now()) / 36e5;
  if (hours < 1) return "within the hour";
  if (hours < 20) return `in ${Math.round(hours)} hours`;
  const days = Math.round(hours / 24);
  return days === 1 ? "tomorrow" : `in ${days} days`;
}

function Result({ result, onAgain, onDone }) {
  const { dark } = useTheme();
  const colors = useMemo(
    () => (dark ? ["#22c55e", "#16a34a", "#facc15", "#e8f5ec", "#ff8c1e"] : ["#254ec4", "#7f9be0", "#e29e0e", "#1d1b18", "#e86a10"]),
    [dark],
  );
  useEffect(() => sfx.complete(), []);
  const s = result.summary;
  const due = nextDueText(s.next_due_at);
  const cards = [
    { label: "Score", tone: "bg-primary", text: "text-primary", value: `${result.score}/${result.total}` },
    { label: "XP", tone: "bg-gold", text: "text-gold", value: `+${result.xp_awarded}`, icon: "bolt" },
    { label: "Hearts", tone: "bg-bad", text: "text-bad", value: result.heart_awarded ? "+1" : "Full", icon: "heart" },
  ];
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-lg flex-col px-4 pb-8 pt-10 text-center">
      <Confetti colors={colors} />
      <div className="flex flex-1 flex-col items-center justify-center">
        <motion.div initial={{ scale: 0, rotate: -20 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: "spring", stiffness: 260, damping: 14 }}>
          <Mascot size={150} mood="celebrate" />
        </motion.div>
        <h1 className="mt-6 text-3xl font-black text-gold sm:text-4xl">Practice complete!</h1>
        <p className="mt-2 font-semibold text-muted">
          {s.due > 0
            ? `${s.due} item${s.due === 1 ? "" : "s"} still due - another round will lock them in.`
            : due
              ? `All caught up! Your next review is due ${due}.`
              : "All caught up!"}
        </p>
        <div className="mt-8 grid w-full grid-cols-3 gap-3">
          {cards.map((c, i) => (
            <motion.div
              key={c.label}
              className={`overflow-hidden rounded-2xl ${c.tone}`}
              initial={{ y: 30, opacity: 0, scale: 0.9 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + i * 0.12, type: "spring", stiffness: 420, damping: 22 }}
            >
              <p className="py-1 text-[0.6875rem] font-black uppercase text-white">{c.label}</p>
              <p className={`m-[0.125rem] mt-0 flex items-center justify-center gap-1 rounded-xl bg-bg py-3 text-xl font-black ${c.text}`}>
                {c.icon && <Icon name={c.icon} className="h-5 w-5" />}
                {c.value}
              </p>
            </motion.div>
          ))}
        </div>
        {result.xp_capped && <p className="mt-3 text-sm font-semibold text-muted">You've earned today's practice XP - practising more still strengthens your memory.</p>}
        <p className="mt-5 text-sm font-bold text-muted">
          {s.strong > 0
            ? `${s.strong} of ${s.total} items are strong - in your long-term memory`
            : "Every correct review strengthens your memory - items turn strong after 3 spaced reviews."}
        </p>
        {result.new_badges.length > 0 && (
          <div className="card mt-5 w-full p-4">
            <p className="label mb-2">New badge unlocked!</p>
            {result.new_badges.map((b) => (
              <p key={b.key} className="font-extrabold">
                <span aria-hidden="true">{b.icon}</span> {b.name} <span className="text-sm font-semibold text-muted">- {b.desc}</span>
              </p>
            ))}
          </div>
        )}
      </div>
      <div className="space-y-3">
        <button className="btn-primary w-full" onClick={onDone} autoFocus>
          Continue
        </button>
        {s.total >= 3 && (
          <button className="btn-ghost w-full" onClick={onAgain}>
            Practise again
          </button>
        )}
      </div>
    </div>
  );
}

export default function Practice({ course }) {
  const router = useRouter();
  const { reload } = useAuth();
  const [session, setSession] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [round, setRound] = useState(0);

  useEffect(() => {
    setSession(null);
    setResult(null);
    setError(null);
    api("/api/practice/start", { method: "POST", body: course ? { course } : {} })
      .then(setSession)
      .catch((e) => setError(e));
  }, [course, round]);

  const onFinished = useCallback(
    (res) => {
      setResult(res);
      reload();
    },
    [reload],
  );

  const back = () => router.push(course ? "/learn" : "/practice");

  if (error)
    return <QuizMessage message={error.message} mood={error.status === 409 ? "think" : "sad"} action={error.status === 409 ? "Go to lessons" : "Back"} onAction={() => router.push(error.status === 409 ? "/learn" : "/practice")} />;
  if (!session) return <QuizSkeleton />;
  if (result) return <Result result={result} onAgain={() => setRound((n) => n + 1)} onDone={back} />;

  const reviews = session.questions.filter((q) => q.review).length;
  return (
    <QuizRunner
      key={session.attempt_id}
      session={session}
      basePath="/api/practice"
      icon="review"
      startLabel="Start practice"
      quit={{ label: "Quit practice", title: "Stop practising?", body: "Answers so far still count toward your review schedule.", action: "Stop" }}
      onExit={back}
      onFinished={onFinished}
      intro={
        <>
          <Mascot size={120} mood="wave" className="mx-auto" />
          <p className="label mb-1 mt-4">Spaced repetition</p>
          <h1 className="text-3xl font-black">{session.title}</h1>
          <ul className="mx-auto mt-6 max-w-sm space-y-2 text-left font-semibold">
            <li className="flex items-center gap-2">
              <Icon name="review" className="h-5 w-5 text-flame" />
              {reviews > 0 ? `${reviews} question${reviews === 1 ? "" : "s"} due for review` : "Refresh what you've learned"}
            </li>
            <li className="flex items-center gap-2">
              <Icon name="target" className="h-5 w-5 text-primary" /> Mistakes come back until they stick
            </li>
            <li className="flex items-center gap-2">
              <Icon name="heart" className="h-5 w-5 text-bad" /> No hearts lost - finish to earn one back
            </li>
            <li className="flex items-center gap-2">
              <Icon name="bolt" className="h-5 w-5 text-gold" /> +{session.xp} XP
            </li>
          </ul>
        </>
      }
    />
  );
}
