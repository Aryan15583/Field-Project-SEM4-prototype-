"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import Exercise, { initialValue, isAnswered } from "@/components/Exercise";
import { ErrorNote, Icon, Mascot, Modal, NoCopy, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import { sfx } from "@/lib/feedback";

const EASE = [0.2, 0.8, 0.2, 1];
const SHEET_SPRING = { type: "spring", stiffness: 520, damping: 40 };

export function QuizSkeleton() {
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
}

export function QuizMessage({ message, mood = "sad", action, onAction }) {
  return (
    <div className="mx-auto grid min-h-[100dvh] max-w-md place-items-center p-6 text-center">
      <div>
        <Mascot size={110} mood={mood} className="mx-auto" />
        <p className="my-5 text-lg font-bold">{message}</p>
        <button className="btn-primary" onClick={onAction}>
          {action}
        </button>
      </div>
    </div>
  );
}

/** mm:ss left until `deadline` (ISO string), ticking every second; 0 when time is up. */
function useCountdown(deadline, running) {
  const [left, setLeft] = useState(() => (deadline ? Math.max(0, Date.parse(deadline) - Date.now()) : null));
  useEffect(() => {
    if (!deadline || !running) return;
    const tick = () => setLeft(Math.max(0, Date.parse(deadline) - Date.now()));
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, [deadline, running]);
  return left;
}

const mmss = (ms) => {
  const s = Math.ceil(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

/**
 * Plays a fixed list of questions once each (tests, practice, contests): Check -> feedback sheet -> next,
 * then calls `${basePath}/${attempt_id}/${completePath}` and hands the result to `onFinished`.
 * With a `deadline` (contests) a countdown replaces the counter and the run finishes itself at 0:00.
 */
export default function QuizRunner({
  session, basePath, intro, startLabel, icon = "trophy", footerNote, quit, onExit, onFinished,
  completePath = "complete", deadline = null, startPlaying = false, initialScore = 0,
}) {
  const [phase, setPhase] = useState(startPlaying ? "play" : "intro"); // intro | play
  const [index, setIndex] = useState(0);
  const [value, setValue] = useState(() => initialValue(session.questions[0]));
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(initialScore);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmExit, setConfirmExit] = useState(false);

  const current = session.questions[index];
  const total = session.questions.length;
  const url = `${basePath}/${session.attempt_id}`;

  const finishing = useRef(false); // the timer and a "time's up" answer can both ask to finish
  const finish = useCallback(async () => {
    if (finishing.current) return;
    finishing.current = true;
    setBusy(true);
    try {
      onFinished(await api(`${url}/${completePath}`, { method: "POST" }));
    } catch (e) {
      finishing.current = false;
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [url, completePath, onFinished]);

  const left = useCountdown(deadline, phase === "play");
  const timeUp = deadline !== null && left === 0;
  useEffect(() => {
    if (timeUp) finish();
  }, [timeUp, finish]);

  const check = useCallback(async () => {
    if (!current || busy || feedback || !isAnswered(current.kind, value)) return;
    setBusy(true);
    setError("");
    try {
      const res = await api(`${url}/answer`, { method: "POST", body: { exercise_id: current.id, answer: value } }).catch((e) => {
        if (e.status === 410) finish(); // time ran out on the server
        throw e;
      });
      (res.correct ? sfx.correct : sfx.wrong)();
      setFeedback(res);
      setScore(res.score);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [current, busy, feedback, value, url]);

  const next = useCallback(() => {
    if (!feedback || busy) return;
    setFeedback(null);
    if (index + 1 >= total) {
      finish();
      return;
    }
    setIndex(index + 1);
    setValue(initialValue(session.questions[index + 1]));
  }, [feedback, busy, index, total, session, finish]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key !== "Enter" || e.shiftKey || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLButtonElement) return;
      if (phase === "intro") setPhase("play");
      else feedback ? next() : check();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, feedback, next, check]);

  const verdict = feedback ? (feedback.correct ? "right" : "wrong") : null;

  return (
    <div className="flex min-h-[100dvh] flex-col text-ink">
      <div className="mx-auto flex w-full max-w-3xl items-center gap-4 px-4 pb-2 pt-9">
        <button className="text-muted transition-colors hover:text-ink" onClick={() => setConfirmExit(true)} aria-label={quit.label}>
          <Icon name="x" className="h-7 w-7" />
        </button>
        <div className="flex-1">
          <ProgressBar value={index + (feedback ? 1 : 0)} max={total} />
        </div>
        {deadline && phase === "play" ? (
          <span
            className={`flex items-center gap-1 font-mono text-lg font-black tabular-nums ${left < 60000 ? "text-bad" : "text-gold"}`}
            role="timer"
            aria-label={`${mmss(left ?? 0)} left`}
          >
            <Icon name="bolt" className="h-6 w-6" />
            {mmss(left ?? 0)}
          </span>
        ) : (
          <span className="flex items-center gap-1 text-lg font-black text-gold" aria-label={phase === "intro" ? `${total} questions` : `Question ${index + 1} of ${total}`}>
            <Icon name={icon} className="h-6 w-6" />
            {phase === "intro" ? total : `${index + 1}/${total}`}
          </span>
        )}
      </div>

      <div className="mx-auto w-full max-w-3xl flex-1 overflow-x-hidden px-4 pb-56 pt-6">
        <AnimatePresence mode="wait" initial={false}>
          {phase === "intro" ? (
            <motion.div key="intro" className="text-center" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -48 }} transition={{ duration: 0.22, ease: EASE }}>
              {intro}
            </motion.div>
          ) : (
            current && (
              <motion.div key={current.id} initial={{ opacity: 0, x: 56 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -56 }} transition={{ duration: 0.22, ease: EASE }}>
                {current.review && (
                  <p className="mb-3 inline-flex items-center gap-1 rounded-full bg-flame/15 px-3 py-1 text-xs font-black uppercase tracking-wider text-flame">
                    <Icon name="flame" className="h-4 w-4" /> Review - you missed this before
                  </p>
                )}
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
              <button className="btn-ghost hidden sm:inline-flex" onClick={onExit}>
                Not now
              </button>
              <button className="btn-primary w-full sm:w-48" onClick={() => setPhase("play")} autoFocus>
                {startLabel}
              </button>
            </>
          ) : (
            <>
              <span className="hidden text-sm font-bold text-muted sm:block">
                Score: {score}/{total}
                {footerNote}
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
                    {!feedback.correct && feedback.correct_answer !== undefined && (
                      <>
                        <p className="text-sm font-extrabold">Correct answer:</p>
                        <NoCopy as="pre" className="whitespace-pre-wrap break-words font-mono text-sm">
                          {feedback.correct_answer}
                        </NoCopy>
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

      <Modal open={confirmExit} onClose={() => setConfirmExit(false)} label={quit.label}>
        <div className="text-center">
          <Mascot size={90} mood="sad" className="mx-auto" />
          <h2 className="mt-3 text-xl font-black">{quit.title}</h2>
          <p className="mb-6 mt-1 font-semibold text-muted">{quit.body}</p>
          <button className="btn-primary w-full" onClick={() => setConfirmExit(false)}>
            Keep going
          </button>
          <button className="btn-link mt-4 text-bad" onClick={onExit}>
            {quit.action}
          </button>
        </div>
      </Modal>
    </div>
  );
}
