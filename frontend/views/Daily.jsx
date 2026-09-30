"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import Exercise, { initialValue, isAnswered } from "@/components/Exercise";
import { ErrorNote, Mascot, Spinner } from "@/components/ui";

export default function Daily() {
  const { reload } = useAuth();
  const navigate = useRouter().push;
  const [daily, setDaily] = useState(null);
  const [value, setValue] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api("/api/daily")
      .then((d) => {
        setDaily(d);
        if (d.exercise) setValue(initialValue(d.exercise));
      })
      .catch((e) => setError(e.message));
  }, []);

  const submit = async () => {
    setBusy(true);
    setError("");
    try {
      setResult(await api("/api/daily/answer", { method: "POST", body: { exercise_id: daily.exercise.id, answer: value } }));
      reload();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (error && !daily) return <ErrorNote>{error}</ErrorNote>;
  if (!daily) return <Spinner />;
  if (!daily.exercise) return <p className="text-muted">No challenge today.</p>;

  if (daily.answered && !result)
    return (
      <div className="card mx-auto max-w-xl p-8 text-center">
        <Mascot size={100} mood={daily.correct ? "happy" : "think"} className="mx-auto" />
        <h1 className="mt-4 text-2xl font-black">{daily.correct ? "Challenge crushed!" : "See you tomorrow!"}</h1>
        <p className="mt-1 text-muted">A new daily challenge unlocks at midnight UTC.</p>
        <button className="btn-primary mt-6" onClick={() => navigate("/learn")}>
          Keep learning
        </button>
      </div>
    );

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center gap-3">
        <span className="chip bg-gold/15 text-gold">🎯 Daily challenge</span>
        <span className="text-sm font-bold text-muted">
          {daily.course} · +{daily.bonus_xp} XP · one attempt
        </span>
      </div>
      <div className="card p-6">
        <Exercise exercise={daily.exercise} value={value} onChange={setValue} locked={!!result} />
        <ErrorNote>{error}</ErrorNote>
        {result ? (
          <div className={`mt-6 rounded-2xl p-4 ${result.correct ? "bg-ok/15 text-ok" : "bg-bad/15 text-bad"}`} aria-live="polite">
            <p className="text-xl font-black">{result.correct ? `Correct! +${result.xp_awarded} XP` : "Not this time"}</p>
            {!result.correct && <pre className="mt-1 whitespace-pre-wrap font-mono text-sm">Answer: {result.correct_answer}</pre>}
            {result.explanation && <p className="mt-1 text-sm text-ink/80">{result.explanation}</p>}
            <button className="btn-primary mt-4" onClick={() => navigate("/learn")}>
              Continue
            </button>
          </div>
        ) : (
          <button className="btn-primary mt-6 w-full" disabled={busy || !isAnswered(daily.exercise.kind, value)} onClick={submit}>
            Submit answer
          </button>
        )}
      </div>
    </div>
  );
}
