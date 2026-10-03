"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import QuizRunner, { QuizMessage, QuizSkeleton } from "@/components/QuizRunner";
import { Icon, Logo, Mascot, nameTint } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { timeLeft } from "./Contests";

const MEDALS = ["🥇", "🥈", "🥉"];
const POLL_MS = 5000;

const fmtTime = (ms) => {
  const s = Math.round(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

function Board({ board }) {
  if (board.entries.length === 0) return <p className="card p-8 text-center font-semibold text-muted">No entries yet - be the first on the board!</p>;
  return (
    <ol className="card divide-y-2 divide-line overflow-hidden" aria-label="Contest leaderboard">
      {board.entries.map((e, i) => (
        <li key={`${e.name}-${i}`} className={`flex items-center gap-3 px-4 py-3 ${e.me ? "bg-primary/10" : ""}`}>
          <span className="w-8 shrink-0 text-center text-lg font-black text-muted">{e.rank ? MEDALS[e.rank - 1] || e.rank : "·"}</span>
          <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/15 font-black text-primary ${nameTint(e.name)}`}>{e.name.slice(0, 1).toUpperCase()}</span>
          <span className="min-w-0 flex-1">
            <span className={`block truncate font-bold ${e.me ? "text-primary" : ""}`}>
              {e.name} {e.me && <span className="text-xs">(you)</span>}
            </span>
            {!e.finished && (
              <span className="flex items-center gap-1.5 text-xs font-bold text-bad">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-bad" aria-hidden="true" /> answering · {e.answered}/{board.questions}
              </span>
            )}
          </span>
          <span className="shrink-0 text-right">
            <span className="block font-black">
              {e.score}/{board.questions}
            </span>
            {e.finished && <span className="block font-mono text-xs font-bold text-muted">{fmtTime(e.time_ms)}</span>}
          </span>
        </li>
      ))}
    </ol>
  );
}

export default function Contest({ id }) {
  const router = useRouter();
  const { reload } = useAuth();
  const [board, setBoard] = useState(null);
  const [run, setRun] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const loadBoard = useCallback(() => api(`/api/contests/${id}/leaderboard`).then(setBoard), [id]);

  useEffect(() => {
    loadBoard().catch((e) => setError(e.status === 404 ? "This contest doesn't exist." : e.message));
  }, [loadBoard]);

  // live leaderboard: poll while the contest runs and the tab is visible (not while playing)
  useEffect(() => {
    if (!board?.live || run) return;
    const t = setInterval(() => document.visibilityState === "visible" && loadBoard().catch(() => {}), POLL_MS);
    return () => clearInterval(t);
  }, [board?.live, run, loadBoard]);

  const onFinished = useCallback(
    async (res) => {
      setRun(null);
      setResult(res);
      reload();
      loadBoard().catch(() => {});
    },
    [reload, loadBoard],
  );

  const enter = async () => {
    setError("");
    try {
      const r = await api(`/api/contests/${id}/enter`, { method: "POST" });
      const answered = r.answered || {};
      if (r.questions.every((q) => String(q.id) in answered)) {
        // everything answered already (e.g. closed the tab on the last question) - just finish
        onFinished(await api(`/api/contests/${id}/finish`, { method: "POST" }));
        return;
      }
      setRun({
        ...r,
        attempt_id: r.contest_id,
        questions: r.questions.filter((q) => !(String(q.id) in answered)),
        initialScore: Object.values(answered).filter(Boolean).length,
        resumed: Object.keys(answered).length > 0,
      });
    } catch (e) {
      setError(e.message);
    }
  };

  if (error && !board) return <QuizMessage message={error} action="All contests" onAction={() => router.push("/contests")} />;
  if (!board) return <QuizSkeleton />;

  if (run) {
    return (
      <QuizRunner
        key={run.contest_id}
        session={run}
        basePath="/api/contests"
        completePath="finish"
        deadline={run.deadline}
        startPlaying={run.resumed}
        initialScore={run.initialScore}
        startLabel="Start the clock"
        icon="bolt"
        quit={{
          label: "Leave contest",
          title: "Leave the contest?",
          body: "The clock keeps running - you can come back before it hits 0:00. Unanswered questions count as wrong.",
          action: "Leave for now",
        }}
        onExit={() => (setRun(null), loadBoard().catch(() => {}))}
        onFinished={onFinished}
        intro={
          <>
            <Mascot size={120} mood="think" className="mx-auto" />
            <p className="label mb-1 mt-4">Weekly contest</p>
            <h1 className="text-3xl font-black">{run.title}</h1>
            <p className="mx-auto mt-3 max-w-md font-semibold text-muted">
              {run.questions.length} questions. Your 10-minute clock started when you entered - each question can be answered once. No hints.
            </p>
          </>
        }
      />
    );
  }

  const mine = board.entries.find((e) => e.me);
  return (
    <div className="min-h-screen px-4 pb-16 pt-6 text-ink">
      <div className="mx-auto max-w-2xl space-y-5">
        <div className="flex items-center justify-between">
          <Link href="/contests" className="flex items-center gap-1 text-sm font-extrabold uppercase text-muted hover:text-ink">
            ‹ Contests
          </Link>
          <Logo compact className="text-xl" />
        </div>

        <div className="text-center">
          <h1 className="text-2xl font-black">{board.title}</h1>
          <p className="mt-1 inline-flex items-center gap-1.5 text-sm font-bold text-muted">
            {board.live ? (
              <>
                <span className="h-2 w-2 animate-pulse rounded-full bg-bad" aria-hidden="true" /> Live · {timeLeft(board.ends_at)} · updates every few seconds
              </>
            ) : (
              <>Final standings · week {board.week.split("-W")[1]}</>
            )}
          </p>
        </div>

        {result && (
          <div className="card p-5 text-center" role="status">
            <Mascot size={90} mood={result.score >= result.total * 0.7 ? "celebrate" : "think"} className="mx-auto" interactive={false} />
            <p className="mt-2 text-xl font-black">
              {result.score}/{result.total} in {fmtTime(result.time_ms)}
            </p>
            <p className="font-bold text-muted">
              {result.rank ? `You're #${result.rank} of ${result.entrants}` : "Finished"}
              {result.xp ? ` · +${result.xp} XP` : ""}
            </p>
          </div>
        )}

        {board.live && (!mine || !mine.finished) && (
          <div className="card flex flex-wrap items-center justify-between gap-3 p-5">
            <div>
              <p className="font-extrabold">{mine ? "Your run is in progress" : "Ready when you are"}</p>
              <p className="text-sm font-semibold text-muted">
                {mine ? "The clock is still running - jump back in." : `${board.questions} questions · 10 minutes · one try this week`}
              </p>
            </div>
            <button className="btn-primary" onClick={enter}>
              <Icon name="bolt" className="h-5 w-5" /> {mine ? "Resume" : "Enter contest"}
            </button>
          </div>
        )}
        {error && <p className="text-center text-sm font-bold text-bad">{error}</p>}

        <Board board={board} />
      </div>
    </div>
  );
}
