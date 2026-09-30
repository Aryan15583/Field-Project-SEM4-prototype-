"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import Exercise, { initialValue, isAnswered } from "@/components/Exercise";
import { ErrorNote, Icon, Mascot, Modal, ProgressBar, Spinner } from "@/components/ui";

const PRAISE = ["Nice!", "Great job!", "Awesome!", "You got it!", "Correct!", "Brilliant!"];

export default function Lesson({ id }) {
  const router = useRouter();
  const navigate = router.push;
  const { reload } = useAuth();
  const [session, setSession] = useState(null); // { attempt_id, lesson, exercises, hearts }
  const [phase, setPhase] = useState("loading"); // loading | intro | play | done | error
  const [queue, setQueue] = useState([]);
  const [solved, setSolved] = useState(0);
  const [value, setValue] = useState(null);
  const [feedback, setFeedback] = useState(null); // { correct, correct_answer, explanation }
  const [hearts, setHearts] = useState(5);
  const [hint, setHint] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmExit, setConfirmExit] = useState(false);
  const [outOfHearts, setOutOfHearts] = useState(false);

  useEffect(() => {
    api(`/api/lessons/${encodeURIComponent(id)}/start`, { method: "POST" })
      .then((s) => {
        setSession(s);
        setQueue(s.exercises);
        setHearts(s.hearts);
        setValue(initialValue(s.exercises[0]));
        setPhase(s.lesson.intro ? "intro" : "play");
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
      const res = await api(`/api/attempts/${session.attempt_id}/answer`, { method: "POST", body: { exercise_id: current.id, answer: value } });
      setFeedback({ ...res, praise: PRAISE[Math.floor(Math.random() * PRAISE.length)] });
      setHearts(res.hearts);
      if (res.correct) setSolved((n) => n + 1);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [current, busy, feedback, value, session]);

  const next = useCallback(() => {
    if (!feedback) return;
    if (feedback.out_of_hearts) {
      setOutOfHearts(true);
      return;
    }
    // Wrong answers go to the back of the queue - you must get every one right.
    const rest = feedback.correct ? queue.slice(1) : [...queue.slice(1), queue[0]];
    setFeedback(null);
    setHint(null);
    if (rest.length === 0) {
      setQueue([]);
      finish();
      return;
    }
    setQueue(rest);
    setValue(initialValue(rest[0]));
  }, [feedback, queue, finish]);

  // Enter = check / continue
  useEffect(() => {
    const onKey = (e) => {
      // Buttons handle Enter themselves (native click) - handling it here too would double-fire.
      if (e.key !== "Enter" || e.shiftKey || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLButtonElement) return;
      if (phase === "intro") setPhase("play");
      else if (phase === "play") feedback ? next() : check();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, feedback, next, check]);

  const askHint = async () => {
    setHint({ loading: true });
    try {
      const attempt = typeof value === "string" ? value : undefined;
      setHint(await api("/api/ai/hint", { method: "POST", body: { exercise_id: current.id, attempt } }));
    } catch (e) {
      setHint({ hint: e.message, source: "error" });
    }
  };

  if (phase === "loading") return <Spinner label="Preparing your lesson" />;

  if (phase === "error")
    return (
      <div className="mx-auto grid min-h-screen max-w-md place-items-center p-6 text-center">
        <div>
          <Mascot size={110} mood="sad" className="mx-auto" />
          <p className="my-5 text-lg font-bold">{error}</p>
          <button className="btn-primary" onClick={() => navigate("/learn")}>
            Back to learning
          </button>
        </div>
      </div>
    );

  if (phase === "done")
    return (
      <div className="mx-auto grid min-h-screen max-w-md place-items-center p-6 text-center">
        <div className="w-full animate-pop">
          <Mascot size={150} className="mx-auto animate-bob" />
          <h1 className="mt-4 text-3xl font-black text-primary">{result.perfect ? "Perfect lesson!" : "Lesson complete!"}</h1>
          <div className="mt-6 grid grid-cols-3 gap-3">
            {[
              ["Total XP", `+${result.xp_awarded}`, "text-gold", "bolt"],
              ["Streak", result.streak, "text-flame", "flame"],
              ["Mistakes", result.mistakes, "text-primary", "target"],
            ].map(([label, val, tone, icon]) => (
              <div key={label} className="card overflow-hidden">
                <p className={`py-1 text-[11px] font-black uppercase ${tone}`}>{label}</p>
                <p className={`flex items-center justify-center gap-1 py-3 text-xl font-black ${tone}`}>
                  <Icon name={icon} className="h-5 w-5" />
                  {val}
                </p>
              </div>
            ))}
          </div>
          {result.new_badges.length > 0 && (
            <div className="card mt-5 p-4">
              <p className="label mb-2">New badge{result.new_badges.length > 1 && "s"} unlocked!</p>
              {result.new_badges.map((b) => (
                <p key={b.key} className="font-extrabold">
                  <span aria-hidden="true">{b.icon}</span> {b.name} <span className="text-sm font-normal text-muted">- {b.desc}</span>
                </p>
              ))}
            </div>
          )}
          <button className="btn-primary mt-8 w-full" onClick={() => navigate("/learn")}>
            Continue
          </button>
        </div>
      </div>
    );

  return (
    <div className="flex min-h-screen flex-col bg-bg text-ink">
      {/* header */}
      <div className="mx-auto flex w-full max-w-3xl items-center gap-4 px-4 py-5">
        <button className="text-muted hover:text-ink" onClick={() => setConfirmExit(true)} aria-label="Quit lesson">
          <Icon name="x" className="h-7 w-7" />
        </button>
        <ProgressBar value={solved} max={total} className="flex-1" />
        <span className="chip text-bad" aria-label={`${hearts} hearts left`}>
          <Icon name="heart" className="h-6 w-6" /> {hearts}
        </span>
      </div>

      {/* body */}
      <div className="mx-auto w-full max-w-3xl flex-1 px-4 pb-48 pt-4">
        {phase === "intro" ? (
          <div className="animate-pop">
            <p className="label mb-2">
              {session.lesson.course_title} · New concept
            </p>
            <h1 className="mb-5 text-3xl font-black">{session.lesson.title}</h1>
            <div className="flex items-start gap-4">
              <Mascot size={84} className="hidden shrink-0 sm:block" />
              <pre className="code flex-1">{session.lesson.intro}</pre>
            </div>
          </div>
        ) : (
          current && (
            <div key={`${current.id}-${queue.length}`}>
              <Exercise exercise={current} value={value} onChange={setValue} locked={!!feedback} />
              {!feedback && (
                <div className="mt-6">
                  {hint ? (
                    <div className="flex items-start gap-3 animate-pop">
                      <Mascot size={52} mood="think" className="shrink-0" />
                      <div className="card relative flex-1 p-4 text-sm">
                        {hint.loading ? "Codi is thinking…" : hint.hint}
                        {hint.source === "ai" && <span className="mt-2 block text-[11px] font-bold uppercase text-muted">AI hint</span>}
                      </div>
                    </div>
                  ) : (
                    <button type="button" className="btn-link inline-flex items-center gap-1 text-sm" onClick={askHint}>
                      <Icon name="bulb" className="h-4 w-4" /> Stuck? Ask Codi for a hint
                    </button>
                  )}
                </div>
              )}
              <div className="mt-4">
                <ErrorNote>{error}</ErrorNote>
              </div>
            </div>
          )
        )}
      </div>

      {/* footer / feedback */}
      <div
        className={`fixed inset-x-0 bottom-0 border-t-2 ${
          feedback ? (feedback.correct ? "animate-rise border-transparent bg-ok/15" : "animate-rise border-transparent bg-bad/15") : "border-line bg-bg"
        }`}
      >
        <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between">
          {feedback ? (
            <div className={`flex items-start gap-3 ${feedback.correct ? "text-ok" : "text-bad animate-shake"}`} aria-live="polite">
              <span className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-raised">
                <Icon name={feedback.correct ? "check" : "x"} className="h-7 w-7" />
              </span>
              <div className="min-w-0">
                <p className="text-xl font-black">{feedback.correct ? feedback.praise : "Not quite"}</p>
                {!feedback.correct && (
                  <>
                    <p className="text-sm font-bold">Correct answer:</p>
                    <pre className="whitespace-pre-wrap break-words font-mono text-sm">{feedback.correct_answer}</pre>
                  </>
                )}
                {feedback.explanation && <p className="mt-1 text-sm text-ink/80">{feedback.explanation}</p>}
              </div>
            </div>
          ) : (
            <span className="hidden sm:block" />
          )}
          {phase === "intro" ? (
            <button className="btn-primary sm:w-48" onClick={() => setPhase("play")}>
              Let's go
            </button>
          ) : feedback ? (
            <button className={`${feedback.correct ? "btn-ok" : "btn-bad"} sm:w-48`} onClick={next} disabled={busy} autoFocus>
              Continue
            </button>
          ) : (
            <button className="btn-primary sm:w-48" onClick={check} disabled={busy || !current || !isAnswered(current.kind, value)}>
              Check
            </button>
          )}
        </div>
      </div>

      <Modal open={confirmExit} onClose={() => setConfirmExit(false)} label="Quit lesson?">
        <div className="text-center">
          <Mascot size={90} mood="sad" className="mx-auto" />
          <h2 className="mt-3 text-xl font-black">Wait, don't go!</h2>
          <p className="mb-6 mt-1 text-muted">You'll lose your progress in this lesson.</p>
          <button className="btn-primary w-full" onClick={() => setConfirmExit(false)}>
            Keep learning
          </button>
          <button className="btn-link mt-4 text-bad" onClick={() => navigate("/learn")}>
            End session
          </button>
        </div>
      </Modal>

      <Modal open={outOfHearts} onClose={() => navigate("/learn")} label="Out of hearts">
        <div className="text-center">
          <Mascot size={90} mood="sad" className="mx-auto" />
          <h2 className="mt-3 text-xl font-black">You ran out of hearts</h2>
          <p className="mb-6 mt-1 text-muted">Hearts refill over time (one every 30 minutes). Practising completed lessons is always free.</p>
          <button className="btn-primary w-full" onClick={() => (reload(), navigate("/learn"))}>
            Back to path
          </button>
        </div>
      </Modal>
    </div>
  );
}
