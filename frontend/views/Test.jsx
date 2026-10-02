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

const EASE = [0.2, 0.8, 0.2, 1];

/* ---------------------------------------------------------------- result screen */
function Result({ test, result, onRetry, onDone }) {
  const { dark } = useTheme();
  const colors = useMemo(
    () => (dark ? ["#22c55e", "#16a34a", "#facc15", "#e8f5ec", "#ff8c1e"] : ["#1d6ff2", "#60a5fa", "#f5b00b", "#0a0a0a", "#ff7a00"]),
    [dark],
  );
  useEffect(() => {
    if (result.passed) sfx.complete();
  }, [result.passed]);
  const section = test.kind === "section";
  const headline = result.passed ? (section ? "You're ready!" : "Chapter passed!") : "Not quite yet";
  const detail = result.passed
    ? section
      ? `${test.title.replace(/^Ready for |\?$/g, "")} is unlocked. ${result.lessons_skipped} earlier lessons are marked as tested out - you can still replay any of them.`
      : result.certificate
        ? "That was the final chapter - you've finished the whole course!"
        : "The next unit is unlocked. Keep going!"
    : `You need ${result.pass_mark} of ${result.total} to pass. Review the lessons, then try again - each attempt has new questions.`;

  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-lg flex-col px-4 pb-8 pt-10 text-center">
      {result.passed && <Confetti colors={colors} />}
      <div className="flex flex-1 flex-col items-center justify-center">
        <motion.div initial={{ scale: 0, rotate: -20 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: "spring", stiffness: 260, damping: 14 }}>
          <Mascot size={160} mood={result.passed ? "celebrate" : "sad"} />
        </motion.div>
        <motion.h1
          className={`mt-6 text-3xl font-black sm:text-4xl ${result.passed ? "text-gold" : "text-ink"}`}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.35, ease: EASE }}
        >
          {headline}
        </motion.h1>
        <motion.p className="mt-2 font-semibold text-muted" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }}>
          {detail}
        </motion.p>
        <motion.div
          className="mt-8 grid w-full grid-cols-2 gap-3"
          initial={{ y: 24, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.45, type: "spring", stiffness: 420, damping: 22 }}
        >
          <div className={`overflow-hidden rounded-2xl ${result.passed ? "bg-primary" : "bg-bad"}`}>
            <p className="py-1 text-[0.6875rem] font-black uppercase text-white">Score</p>
            <p className={`m-[0.125rem] mt-0 rounded-xl bg-bg py-3 text-xl font-black ${result.passed ? "text-primary" : "text-bad"}`}>
              {result.score}/{result.total}
            </p>
          </div>
          <div className="overflow-hidden rounded-2xl bg-gold">
            <p className="py-1 text-[0.6875rem] font-black uppercase text-white">XP</p>
            <p className="m-[0.125rem] mt-0 flex items-center justify-center gap-1 rounded-xl bg-bg py-3 text-xl font-black text-gold">
              <Icon name="bolt" className="h-5 w-5" />+{result.xp_awarded}
            </p>
          </div>
        </motion.div>
        {result.passed && result.xp_awarded === 0 && <p className="mt-3 text-sm font-semibold text-muted">Retakes are practice - XP is awarded on your first pass.</p>}
        {result.certificate && (
          <a href={`/certificate/${result.certificate.code}`} className="card mt-5 flex w-full items-center gap-3 p-4 text-left">
            <span className="text-3xl" aria-hidden="true">
              🎓
            </span>
            <span>
              <span className="block font-black text-gold">Course complete - certificate earned!</span>
              <span className="text-sm font-semibold text-muted">View and share your {result.certificate.course} certificate</span>
            </span>
          </a>
        )}
        {result.new_badges.length > 0 && (
          <motion.div className="card mt-5 w-full p-4" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
            <p className="label mb-2">New badge{result.new_badges.length > 1 && "s"} unlocked!</p>
            {result.new_badges.map((b) => (
              <p key={b.key} className="font-extrabold">
                <span aria-hidden="true">{b.icon}</span> {b.name} <span className="text-sm font-semibold text-muted">- {b.desc}</span>
              </p>
            ))}
          </motion.div>
        )}
      </div>
      <div className="space-y-3">
        {!result.passed && (
          <button className="btn-primary w-full" onClick={onRetry} autoFocus>
            Try again
          </button>
        )}
        <button className={result.passed ? "btn-primary w-full" : "btn-ghost w-full"} onClick={onDone} autoFocus={result.passed}>
          {result.passed ? "Continue" : "Back to lessons"}
        </button>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------- test */
export default function Test({ course, unitId, section }) {
  const router = useRouter();
  const { reload } = useAuth();
  const [test, setTest] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [sitting, setSitting] = useState(0); // bump to start a fresh attempt

  useEffect(() => {
    setTest(null);
    setResult(null);
    setError("");
    const body = { course, ...(unitId ? { unit_id: Number(unitId) } : { section }) };
    api("/api/tests/start", { method: "POST", body })
      .then(setTest)
      .catch((e) => setError(e.message));
  }, [course, unitId, section, sitting]);

  const onFinished = useCallback(
    (res) => {
      setResult(res);
      reload();
    },
    [reload],
  );

  const back = () => router.push("/learn");

  if (error) return <QuizMessage message={error} action="Back to learning" onAction={back} />;
  if (!test) return <QuizSkeleton />;
  if (result) return <Result test={test} result={result} onRetry={() => setSitting((n) => n + 1)} onDone={back} />;

  return (
    <QuizRunner
      key={test.attempt_id}
      session={test}
      basePath="/api/tests"
      startLabel="Start test"
      footerNote={` · pass ${test.pass_mark}`}
      quit={{ label: "Quit test", title: "Leave the test?", body: "Your answers so far won't count. You can take it again any time.", action: "Leave test" }}
      onExit={back}
      onFinished={onFinished}
      intro={
        <>
          <Mascot size={120} mood="think" className="mx-auto" />
          <p className="label mb-1 mt-4">
            {test.course_title} · {test.kind === "section" ? "Readiness test" : "Chapter test"}
          </p>
          <h1 className="text-3xl font-black">{test.title}</h1>
          <ul className="mx-auto mt-6 max-w-sm space-y-2 text-left font-semibold">
            <li className="flex items-center gap-2">
              <Icon name="target" className="h-5 w-5 text-primary" /> {test.questions.length} questions - get {test.pass_mark} right to pass
            </li>
            <li className="flex items-center gap-2">
              <Icon name="heart" className="h-5 w-5 text-bad" /> No hearts lost - mistakes are free here
            </li>
            <li className="flex items-center gap-2">
              <Icon name="bulb" className="h-5 w-5 text-gold" /> No hints - show what you know
            </li>
            <li className="flex items-center gap-2">
              <Icon name="bolt" className="h-5 w-5 text-gold" /> +{test.xp} XP the first time you pass
            </li>
          </ul>
          {test.kind === "section" && (
            <p className="mx-auto mt-5 max-w-sm text-sm font-semibold text-muted">
              Pass to jump straight here. The lessons before it will be marked as tested out - you can still replay them any time.
            </p>
          )}
        </>
      }
    />
  );
}
