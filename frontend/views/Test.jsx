"use client";

import { AnimatePresence, motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import Confetti from "@/components/Confetti";
import Exercise, { initialValue, isAnswered } from "@/components/Exercise";
import { ErrorNote, Icon, Mascot, Modal, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { sfx } from "@/lib/feedback";
import { useTheme } from "@/lib/theme";

const EASE = [0.2, 0.8, 0.2, 1];
const SHEET_SPRING = { type: "spring", stiffness: 520, damping: 40 };

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
  const [phase, setPhase] = useState("loading"); // loading | intro | play | done | error
  const [index, setIndex] = useState(0);
  const [value, setValue] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmExit, setConfirmExit] = useState(false);
  const [sitting, setSitting] = useState(0); // bump to start a fresh attempt

  useEffect(() => {
    setPhase("loading");
    setError("");
    const body = { course, ...(unitId ? { unit_id: Number(unitId) } : { section }) };
    api("/api/tests/start", { method: "POST", body })
      .then((t) => {
        setTest(t);
        setIndex(0);
        setScore(0);
        setFeedback(null);
        setResult(null);
        setValue(initialValue(t.questions[0]));
        setPhase("intro");
      })
      .catch((e) => {
        setError(e.message);
        setPhase("error");
      });
  }, [course, unitId, section, sitting]);

  const current = test?.questions[index];
  const total = test?.questions.length ?? 1;

  const finish = useCallback(async () => {
    setBusy(true);
    try {
      const res = await api(`/api/tests/${test.attempt_id}/complete`, { method: "POST" });
      setResult(res);
      setPhase("done");
      reload();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [test, reload]);

  const check = useCallback(async () => {
    if (!current || busy || feedback || !isAnswered(current.kind, value)) return;
    setBusy(true);
    setError("");
    try {
      const res = await api(`/api/tests/${test.attempt_id}/answer`, { method: "POST", body: { exercise_id: current.id, answer: value } });
      (res.correct ? sfx.correct : sfx.wrong)();
      setFeedback(res);
      setScore(res.score);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [current, busy, feedback, value, test]);

  const next = useCallback(() => {
    if (!feedback || busy) return;
    setFeedback(null);
    if (index + 1 >= total) {
      finish();
      return;
    }
    setIndex(index + 1);
    setValue(initialValue(test.questions[index + 1]));
  }, [feedback, busy, index, total, test, finish]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key !== "Enter" || e.shiftKey || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLButtonElement) return;
      if (phase === "intro") setPhase("play");
      else if (phase === "play") feedback ? next() : check();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, feedback, next, check]);

  const back = () => router.push("/learn");

  if (phase === "loading")
    return (
      <div className="mx-auto max-w-3xl px-4 py-6" aria-busy="true">
        <div className="skeleton h-4 w-full rounded-full" />
        <div className="skeleton mt-12 h-9 w-3/4" />
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-16" />
          ))}
        </div>
      </div>
    );

  if (phase === "error")
    return (
      <div className="mx-auto grid min-h-[100dvh] max-w-md place-items-center p-6 text-center">
        <div>
          <Mascot size={110} mood="sad" className="mx-auto" />
          <p className="my-5 text-lg font-bold">{error}</p>
          <button className="btn-primary" onClick={back}>
            Back to learning
          </button>
        </div>
      </div>
    );

  if (phase === "done") return <Result test={test} result={result} onRetry={() => setSitting((n) => n + 1)} onDone={back} />;

  const verdict = feedback ? (feedback.correct ? "right" : "wrong") : null;

  return (
    <div className="flex min-h-[100dvh] flex-col bg-bg text-ink">
      <div className="mx-auto flex w-full max-w-3xl items-center gap-4 px-4 pb-2 pt-9">
        <button className="text-muted transition-colors hover:text-ink" onClick={() => setConfirmExit(true)} aria-label="Quit test">
          <Icon name="x" className="h-7 w-7" />
        </button>
        <div className="flex-1">
          <ProgressBar value={index + (feedback ? 1 : 0)} max={total} />
        </div>
        <span className="flex items-center gap-1 text-lg font-black text-gold" aria-label={phase === "intro" ? `${total} questions` : `Question ${index + 1} of ${total}`}>
          <Icon name="trophy" className="h-6 w-6" />
          {phase === "intro" ? total : `${index + 1}/${total}`}
        </span>
      </div>

      <div className="mx-auto w-full max-w-3xl flex-1 overflow-x-hidden px-4 pb-56 pt-6">
        <AnimatePresence mode="wait" initial={false}>
          {phase === "intro" ? (
            <motion.div key="intro" className="text-center" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -48 }} transition={{ duration: 0.22, ease: EASE }}>
              <Mascot size={120} mood="think" className="mx-auto" />
              <p className="label mb-1 mt-4">
                {test.course_title} · {test.kind === "section" ? "Readiness test" : "Chapter test"}
              </p>
              <h1 className="text-3xl font-black">{test.title}</h1>
              <ul className="mx-auto mt-6 max-w-sm space-y-2 text-left font-semibold">
                <li className="flex items-center gap-2">
                  <Icon name="target" className="h-5 w-5 text-primary" /> {total} questions - get {test.pass_mark} right to pass
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
            </motion.div>
          ) : (
            current && (
              <motion.div key={current.id} initial={{ opacity: 0, x: 56 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -56 }} transition={{ duration: 0.22, ease: EASE }}>
                <motion.div animate={verdict === "wrong" ? { x: [0, -10, 10, -6, 6, 0] } : { x: 0 }} transition={{ duration: 0.35 }}>
                  <Exercise exercise={current} value={value} onChange={setValue} result={verdict} />
                </motion.div>
                <div className="mt-4">
                  <ErrorNote>{error}</ErrorNote>
                </div>
              </motion.div>
            )
          )}
        </AnimatePresence>
      </div>

      <div className="fixed inset-x-0 bottom-0 z-20 border-t-2 border-line bg-bg pb-[env(safe-area-inset-bottom)]">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-5 sm:py-7">
          {phase === "intro" ? (
            <>
              <button className="btn-ghost hidden sm:inline-flex" onClick={back}>
                Not now
              </button>
              <button className="btn-primary w-full sm:w-48" onClick={() => setPhase("play")} autoFocus>
                Start test
              </button>
            </>
          ) : (
            <>
              <span className="hidden text-sm font-bold text-muted sm:block">
                Score: {score}/{total} · pass {test.pass_mark}
              </span>
              <button
                className={current && isAnswered(current.kind, value) ? "btn-primary w-full sm:w-48" : "btn-disabled w-full sm:w-48"}
                onClick={check}
                disabled={busy || !current || !isAnswered(current.kind, value)}
              >
                Check
              </button>
            </>
          )}
        </div>
      </div>

      <AnimatePresence>
        {feedback && (
          <motion.div key="sheet" className="fixed inset-x-0 bottom-0 z-30 bg-bg" initial={{ y: "100%" }} animate={{ y: 0 }} exit={{ y: "100%" }} transition={SHEET_SPRING} aria-live="polite">
            <div className={`pb-[env(safe-area-inset-bottom)] ${feedback.correct ? "bg-ok/15" : "bg-bad/15"}`}>
              <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:py-7">
                <div className={`flex items-start gap-3 ${feedback.correct ? "text-ok" : "text-bad"}`}>
                  <span className="relative shrink-0">
                    <Mascot size={64} mood={feedback.correct ? "happy" : "sad"} interactive={false} />
                  </span>
                  <div className="min-w-0">
                    <p className="text-2xl font-black">{feedback.correct ? "Correct!" : "Not quite"}</p>
                    {!feedback.correct && (
                      <>
                        <p className="text-sm font-extrabold">Correct answer:</p>
                        <pre className="whitespace-pre-wrap break-words font-mono text-sm">{feedback.correct_answer}</pre>
                      </>
                    )}
                    {feedback.explanation && <p className="mt-1 text-sm font-semibold text-ink/80">{feedback.explanation}</p>}
                  </div>
                </div>
                <button className={`${feedback.correct ? "btn-ok" : "btn-bad"} w-full sm:w-48`} onClick={next} disabled={busy} autoFocus>
                  {index + 1 >= total ? "See results" : "Continue"}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <Modal open={confirmExit} onClose={() => setConfirmExit(false)} label="Quit test?">
        <div className="text-center">
          <Mascot size={90} mood="sad" className="mx-auto" />
          <h2 className="mt-3 text-xl font-black">Leave the test?</h2>
          <p className="mb-6 mt-1 font-semibold text-muted">Your answers so far won't count. You can take it again any time.</p>
          <button className="btn-primary w-full" onClick={() => setConfirmExit(false)}>
            Keep going
          </button>
          <button className="btn-link mt-4 text-bad" onClick={back}>
            Leave test
          </button>
        </div>
      </Modal>
    </div>
  );
}
