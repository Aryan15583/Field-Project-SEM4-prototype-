"use client";

import { AnimatePresence, motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Confetti from "@/components/Confetti";
import Exercise, { initialValue, isAnswered } from "@/components/Exercise";
import { prepareRunAnswer } from "@/components/RunExercise";
import { AnimatedNumber, ErrorNote, Icon, Mascot, Modal, NoCopy, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { sfx } from "@/lib/feedback";
import { getMascot } from "@/lib/mascots";
import { useRandomMascot } from "@/lib/mascotPref";
import { useTheme } from "@/lib/theme";

const PRAISE = ["Nice!", "Great job!", "Awesome!", "You got it!", "Correct!", "Brilliant!", "Amazing!"];
const EASE = [0.2, 0.8, 0.2, 1];
const SHEET_SPRING = { type: "spring", stiffness: 760, damping: 48, mass: 0.8 };

function formatTime(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

/* ---------------------------------------------------------------- header */
function Hearts({ hearts }) {
  const prev = useRef(hearts);
  const lost = hearts < prev.current;
  useEffect(() => {
    prev.current = hearts;
  }, [hearts]);
  return (
    <span className="relative flex items-center gap-1 text-lg font-black text-bad" aria-label={`${hearts} hearts left`}>
      <motion.span
        key={hearts}
        initial={lost ? { scale: 1.5, rotate: -12 } : false}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 12 }}
      >
        <Icon name="heart" className="h-7 w-7" />
      </motion.span>
      <AnimatedNumber value={hearts} duration={0.3} />
      <AnimatePresence>
        {lost && (
          <motion.span
            key={`lost-${hearts}`}
            className="pointer-events-none absolute -top-2 left-1"
            initial={{ y: 0, opacity: 1, scale: 1 }}
            animate={{ y: -34, opacity: 0, scale: 0.7 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <Icon name="heart" className="h-5 w-5" />
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );
}

function Combo({ count }) {
  return (
    <AnimatePresence>
      {count >= 3 && (
        <motion.span
          key={count}
          className="absolute -top-7 left-1/2 whitespace-nowrap text-sm font-black uppercase tracking-wide text-flame"
          initial={{ x: "-50%", y: 8, scale: 0.6, opacity: 0 }}
          animate={{ x: "-50%", y: 0, scale: 1, opacity: 1 }}
          exit={{ x: "-50%", opacity: 0 }}
          transition={{ type: "spring", stiffness: 600, damping: 18 }}
        >
          🔥 {count} in a row!
        </motion.span>
      )}
    </AnimatePresence>
  );
}

/* ---------------------------------------------------------------- finished screen */
function Finished({ result, elapsed, accuracy, onContinue }) {
  const { dark } = useTheme();
  const colors = useMemo(
    () => (dark ? ["#22c55e", "#16a34a", "#facc15", "#e8f5ec", "#ff8c1e"] : ["#254ec4", "#7f9be0", "#e29e0e", "#1d1b18", "#e86a10"]),
    [dark],
  );
  useEffect(() => sfx.complete(), []);
  const stats = [
    { label: "Total XP", tone: "bg-gold", text: "text-gold", icon: "bolt", value: <AnimatedNumber value={result.xp_awarded} duration={1} />, prefix: "+" },
    { label: result.perfect ? "Perfect!" : "Accuracy", tone: "bg-primary", text: "text-primary", icon: "target", value: `${accuracy}%` },
    { label: "Time", tone: "bg-flame", text: "text-flame", icon: "star", value: formatTime(elapsed) },
  ];
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-lg flex-col px-4 pb-8 pt-10 text-center">
      <Confetti colors={colors} />
      <div className="flex flex-1 flex-col items-center justify-center">
        <motion.div initial={{ scale: 0, rotate: -20 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: "spring", stiffness: 260, damping: 14 }}>
          <Mascot size={170} mood="celebrate" />
        </motion.div>
        <motion.h1
          className="mt-6 text-3xl font-black text-gold sm:text-4xl"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.25, duration: 0.35, ease: EASE }}
        >
          {result.perfect ? "Perfect lesson!" : "Lesson complete!"}
        </motion.h1>
        <div className="mt-8 grid w-full grid-cols-3 gap-3">
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              className={`overflow-hidden rounded-2xl border-2 ${s.tone} border-transparent`}
              initial={{ y: 30, opacity: 0, scale: 0.9 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              transition={{ delay: 0.45 + i * 0.12, type: "spring", stiffness: 420, damping: 22 }}
            >
              <p className="py-1 text-[0.6875rem] font-black uppercase text-white">{s.label}</p>
              <p className={`m-[0.125rem] mt-0 flex items-center justify-center gap-1 rounded-xl bg-bg py-3 text-xl font-black ${s.text}`}>
                <Icon name={s.icon} className="h-5 w-5" />
                <span>
                  {s.prefix}
                  {s.value}
                </span>
              </p>
            </motion.div>
          ))}
        </div>
        {result.certificate && (
          <motion.a
            href={`/certificate/${result.certificate.code}`}
            className="card mt-5 flex w-full items-center gap-3 p-4 text-left"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <span className="text-3xl" aria-hidden="true">
              🎓
            </span>
            <span>
              <span className="block font-black text-gold">Course complete - certificate earned!</span>
              <span className="text-sm font-semibold text-muted">View and share your {result.certificate.course} certificate</span>
            </span>
          </motion.a>
        )}
        {result.new_badges.length > 0 && (
          <motion.div className="card mt-5 w-full p-4" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
            <p className="label mb-2">New badge{result.new_badges.length > 1 && "s"} unlocked!</p>
            {result.new_badges.map((b) => (
              <p key={b.key} className="font-extrabold">
                <span aria-hidden="true">{b.icon}</span> {b.name} <span className="text-sm font-semibold text-muted">- {b.desc}</span>
              </p>
            ))}
          </motion.div>
        )}
      </div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}>
        <button className="btn-primary w-full" onClick={onContinue} autoFocus>
          Continue
        </button>
      </motion.div>
    </div>
  );
}

/* ---------------------------------------------------------------- lesson */
/** The helper who gives hints: a different mascot for every question (the parent re-keys it per exercise). */
function HintHelper({ hint, askHint }) {
  const buddyId = useRandomMascot();
  const buddy = getMascot(buddyId).name;
  return (
    <AnimatePresence mode="wait" initial={false}>
      {hint ? (
        <motion.div
          key="hint"
          className="flex items-start gap-3"
          initial={{ opacity: 0, y: 10, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 420, damping: 30 }}
        >
          <Mascot size={60} mascot={buddyId} mood={hint.loading ? "think" : "idle"} className="shrink-0" />
          <div className="card relative flex-1 p-4 text-sm font-semibold">
            {hint.loading ? <span className="animate-pulse">{buddy} is thinking…</span> : hint.hint}
            {hint.source === "ai" && <span className="mt-2 block text-[0.6875rem] font-bold uppercase text-muted">AI hint</span>}
            {!hint.loading && hint.more && (
              <button type="button" className="btn-link mt-2 block text-sm" onClick={() => askHint(2)}>
                I need a bigger hint
              </button>
            )}
          </div>
        </motion.div>
      ) : (
        <motion.button key="ask" type="button" className="btn-link inline-flex items-center gap-1 text-sm" onClick={() => askHint(1)} exit={{ opacity: 0 }}>
          <Icon name="bulb" className="h-4 w-4" /> Stuck? Ask {buddy} for a hint
        </motion.button>
      )}
    </AnimatePresence>
  );
}

export default function Lesson({ id }) {
  const router = useRouter();
  const { reload } = useAuth();
  const [session, setSession] = useState(null); // { attempt_id, lesson, exercises, hearts }
  const [phase, setPhase] = useState("loading"); // loading | intro | play | done | error
  const [queue, setQueue] = useState([]);
  const [round, setRound] = useState(0); // bumps on every new card so re-queued items animate in again
  const [solved, setSolved] = useState(0);
  const [value, setValue] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [hearts, setHearts] = useState(5);
  const [combo, setCombo] = useState(0);
  const [stats, setStats] = useState({ answers: 0, firstTry: 0 });
  const [hint, setHint] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmExit, setConfirmExit] = useState(false);
  const [outOfHearts, setOutOfHearts] = useState(false);
  const startedAt = useRef(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    api(`/api/lessons/${encodeURIComponent(id)}/start`, { method: "POST" })
      .then((s) => {
        setSession(s);
        setQueue(s.exercises);
        setHearts(s.hearts);
        setValue(initialValue(s.exercises[0]));
        setPhase(s.lesson.intro ? "intro" : "play");
        startedAt.current = Date.now();
      })
      .catch((e) => {
        setError(e.message);
        setPhase("error");
      });
  }, [id]);

  const current = queue[0];
  const total = session?.exercises.length ?? 1;

  const finish = useCallback(async () => {
    setBusy(true);
    try {
      const res = await api(`/api/attempts/${session.attempt_id}/complete`, { method: "POST" });
      setElapsed(Date.now() - startedAt.current);
      setResult(res);
      setPhase("done");
      reload();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [session, reload]);

  const check = useCallback(async () => {
    if (!current || busy || feedback || !isAnswered(current.kind, value)) return;
    setBusy(true);
    setError("");
    try {
      // Programs are executed first (in the browser, or by the server's sandbox) and graded on their output.
      const answer = current.kind === "run" ? await prepareRunAnswer(current, value, setValue) : value;
      const res = await api(`/api/attempts/${session.attempt_id}/answer`, { method: "POST", body: { exercise_id: current.id, answer } });
      if (res.close) {
        // "Almost" - a free second chance: nothing is lost, the answer stays editable
        sfx.tap();
        setFeedback({ ...res });
        return;
      }
      (res.correct ? sfx.correct : sfx.wrong)();
      setFeedback({ ...res, praise: PRAISE[Math.floor(Math.random() * PRAISE.length)] });
      setHearts(res.hearts);
      setCombo((c) => (res.correct ? c + 1 : 0));
      setStats((s) => ({ answers: s.answers + 1, firstTry: s.firstTry + (res.correct ? 1 : 0) }));
      if (res.correct) setSolved((n) => n + 1);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [current, busy, feedback, value, session]);

  const next = useCallback(() => {
    if (!feedback || busy) return;
    if (feedback.close) {
      setFeedback(null); // try again with the same answer on screen
      return;
    }
    if (feedback.out_of_hearts) {
      setOutOfHearts(true);
      return;
    }
    const project = session.lesson.project;
    // Wrong answers go to the back of the queue - you must get every one right. In a project the
    // steps build on each other, so a wrong step is retried straight away with the learner's code.
    if (project && !feedback.correct) {
      setFeedback(null);
      setHint(null);
      setValue((v) => ({ ...v, run: null }));
      return;
    }
    const rest = feedback.correct ? queue.slice(1) : [...queue.slice(1), queue[0]];
    setFeedback(null);
    setHint(null);
    if (rest.length === 0) {
      finish();
      return;
    }
    setQueue(rest);
    setRound((r) => r + 1);
    const fresh = initialValue(rest[0]);
    // project steps continue from the learner's own code of the previous step
    if (rest[0].kind === "run" && rest[0].data?.carry && typeof value?.code === "string" && value.code.trim()) fresh.code = value.code;
    setValue(fresh);
  }, [feedback, busy, queue, finish, session, value]);

  // Enter = check / continue (buttons handle their own Enter; textareas need it for newlines)
  useEffect(() => {
    const onKey = (e) => {
      if (e.key !== "Enter" || e.shiftKey || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLButtonElement) return;
      if (phase === "intro") setPhase("play");
      else if (phase === "play") feedback ? next() : check();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, feedback, next, check]);

  const askHint = async (level = 1) => {
    setHint((h) => ({ ...(h || {}), loading: true }));
    try {
      const attempt = typeof value === "string" ? value : typeof value?.code === "string" ? value.code : undefined;
      setHint(await api("/api/ai/hint", { method: "POST", body: { exercise_id: current.id, attempt, level } }));
    } catch (e) {
      setHint({ hint: e.message, source: "error" });
    }
  };

  if (phase === "loading")
    return (
      <div className="mx-auto max-w-3xl px-4 py-6" aria-busy="true">
        <div className="flex items-center gap-4">
          <div className="skeleton h-7 w-7 rounded-lg" />
          <div className="skeleton h-4 flex-1 rounded-full" />
          <div className="skeleton h-7 w-12 rounded-lg" />
        </div>
        <div className="skeleton mt-12 h-4 w-40" />
        <div className="skeleton mt-4 h-9 w-3/4" />
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
          <button className="btn-primary" onClick={() => router.push("/learn")}>
            Back to learning
          </button>
        </div>
      </div>
    );

  if (phase === "done")
    return (
      <Finished
        result={result}
        elapsed={elapsed}
        accuracy={stats.answers ? Math.round((stats.firstTry / stats.answers) * 100) : 100}
        onContinue={() => router.push("/learn")}
      />
    );

  const verdict = feedback && !feedback.close ? (feedback.correct ? "right" : "wrong") : null;

  return (
    <div className="flex min-h-[100dvh] flex-col text-ink">
      {/* header */}
      <div className="mx-auto flex w-full max-w-3xl items-center gap-3 px-4 pb-1 pt-[max(0.875rem,env(safe-area-inset-top))] sm:gap-4 sm:pb-2 sm:pt-9">
        <button className="-m-2 grid h-11 w-11 place-items-center rounded-xl text-muted transition-colors hover:text-ink active:bg-surface" onClick={() => setConfirmExit(true)} aria-label="Quit lesson">
          <Icon name="x" className="h-7 w-7" />
        </button>
        <div className="relative flex-1">
          <Combo count={combo} />
          <ProgressBar value={solved} max={total} />
        </div>
        <Hearts hearts={hearts} />
      </div>

      {/* body */}
      <div className="mx-auto w-full max-w-3xl flex-1 overflow-x-hidden px-4 pb-44 pt-4 sm:pb-56 sm:pt-6">
        <AnimatePresence mode="wait" initial={false}>
          {phase === "intro" ? (
            <motion.div key="intro" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -48 }} transition={{ duration: 0.22, ease: EASE }}>
              <p className="label mb-2">
                {session.lesson.course_title} · {session.lesson.project ? "Project - 3 steps" : "New concept"}
              </p>
              <h1 className="mb-6 text-3xl font-black">{session.lesson.title}</h1>
              <div className="flex items-start gap-4">
                <Mascot size={96} mood="wave" className="hidden shrink-0 sm:block" />
                <pre className="code flex-1">{session.lesson.intro}</pre>
              </div>
            </motion.div>
          ) : (
            current && (
              <motion.div
                key={`${current.id}-${round}`}
                initial={{ opacity: 0, x: 28 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -28, transition: { duration: 0.1 } }}
                transition={{ duration: 0.14, ease: EASE }}
              >
                <motion.div animate={verdict === "wrong" ? { x: [0, -10, 10, -6, 6, 0] } : { x: 0 }} transition={{ duration: 0.35 }}>
                  {session.lesson.project && (
                    <p className="mb-3 inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-black uppercase tracking-wider text-primary">
                      <Icon name="code" className="h-4 w-4" /> Step {solved + 1} of {total}
                      {current.data?.carry && solved > 0 ? " - continuing your code" : ""}
                    </p>
                  )}
                  <Exercise exercise={current} value={value} onChange={setValue} result={verdict} />
                </motion.div>
                {!feedback && (
                  <div className="mt-8">
                    <HintHelper key={current.id} hint={hint} askHint={askHint} />
                  </div>
                )}
                <div className="mt-4">
                  <ErrorNote>{error}</ErrorNote>
                </div>
              </motion.div>
            )
          )}
        </AnimatePresence>
      </div>

      {/* footer: Check bar, with the feedback sheet sliding up over it */}
      <div className="fixed inset-x-0 bottom-0 z-20 border-t-2 border-line bg-bg pb-[env(safe-area-inset-bottom)]">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-3 sm:py-7">
          {phase === "intro" ? (
            <>
              <span className="hidden sm:block" />
              <button className="btn-primary w-full sm:w-48" onClick={() => setPhase("play")}>
                Let's go
              </button>
            </>
          ) : (
            <>
              <button className="btn-ghost hidden sm:inline-flex" onClick={() => askHint(1)} disabled={!!hint || !!feedback}>
                Hint
              </button>
              <button
                className={current && isAnswered(current.kind, value) ? "btn-primary w-full sm:w-48" : "btn-disabled w-full sm:w-48"}
                onClick={check}
                disabled={busy || !current || !isAnswered(current.kind, value)}
              >
                {busy ? "Checking…" : "Check"}
              </button>
            </>
          )}
        </div>
      </div>

      <AnimatePresence>
        {feedback && (
          <motion.div
            key="sheet"
            className="fixed inset-x-0 bottom-0 z-30 bg-bg"
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={SHEET_SPRING}
            aria-live="polite"
          >
            <div className={`pb-[env(safe-area-inset-bottom)] ${feedback.close ? "border-t-4 border-gold bg-gold/20" : feedback.correct ? "bg-ok/15" : "bg-bad/15"}`}>
              <div className="mx-auto flex max-h-[75dvh] max-w-3xl flex-col gap-3 overflow-y-auto px-4 py-4 sm:max-h-none sm:flex-row sm:items-center sm:justify-between sm:gap-4 sm:py-7">
                <div className={`flex items-start gap-3 ${feedback.close ? "text-ink" : feedback.correct ? "text-ok" : "text-bad"}`}>
                  <motion.span
                    className="relative shrink-0"
                    initial={{ scale: 0.4, y: 12 }}
                    animate={{ scale: 1, y: 0 }}
                    transition={{ type: "spring", stiffness: 700, damping: 18 }}
                  >
                    <Mascot size={56} mood={feedback.close ? "think" : feedback.correct ? "happy" : "sad"} interactive={false} className="sm:hidden" />
                    <Mascot size={72} mood={feedback.close ? "think" : feedback.correct ? "happy" : "sad"} interactive={false} className="hidden sm:block" />
                    <span className="absolute -bottom-1 -right-1 grid h-7 w-7 place-items-center rounded-full bg-raised shadow">
                      <Icon name={feedback.close ? "bulb" : feedback.correct ? "check" : "x"} className="h-5 w-5" />
                    </span>
                  </motion.span>
                  <div className="min-w-0">
                    <p className="text-xl font-black sm:text-2xl">{feedback.close ? "Almost there!" : feedback.correct ? feedback.praise : "Not quite"}</p>
                    {feedback.close && <p className="mt-1 text-sm font-bold text-ink">{feedback.message}</p>}
                    {feedback.close && <p className="mt-1 text-xs font-semibold text-muted">No heart lost - fix it and press Check again.</p>}
                    {!feedback.correct && !feedback.close && (
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
                <button className={`${feedback.close ? "btn-primary" : feedback.correct ? "btn-ok" : "btn-bad"} w-full sm:w-48`} onClick={next} disabled={busy} autoFocus>
                  {feedback.close ? "Try again" : "Continue"}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <Modal open={confirmExit} onClose={() => setConfirmExit(false)} label="Quit lesson?">
        <div className="text-center">
          <Mascot size={90} mood="sad" className="mx-auto" />
          <h2 className="mt-3 text-xl font-black">Wait, don't go!</h2>
          <p className="mb-6 mt-1 font-semibold text-muted">You'll lose your progress in this lesson.</p>
          <button className="btn-primary w-full" onClick={() => setConfirmExit(false)}>
            Keep learning
          </button>
          <button className="btn-link mt-4 text-bad" onClick={() => router.push("/learn")}>
            End session
          </button>
        </div>
      </Modal>

      <Modal open={outOfHearts} onClose={() => router.push("/learn")} label="Out of hearts">
        <div className="text-center">
          <Mascot size={90} mood="sad" className="mx-auto" />
          <h2 className="mt-3 text-xl font-black">You ran out of hearts</h2>
          <p className="mb-6 mt-1 font-semibold text-muted">
            Finish a practice session to earn one back right away - or wait, they refill over time (one every 30 minutes).
          </p>
          <button className="btn-primary w-full" onClick={() => (reload(), router.push("/review"))}>
            Practise to earn a heart
          </button>
          <button className="btn-link mt-4" onClick={() => (reload(), router.push("/learn"))}>
            Back to path
          </button>
        </div>
      </Modal>
    </div>
  );
}
