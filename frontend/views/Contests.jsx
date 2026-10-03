"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { courseTint, ErrorNote, Icon, PageTitle, Spinner } from "@/components/ui";
import { api } from "@/lib/api";

const MEDALS = ["🥇", "🥈", "🥉"];

export function timeLeft(iso) {
  const ms = Date.parse(iso) - Date.now();
  if (ms <= 0) return "ended";
  const h = Math.floor(ms / 3600000);
  return h >= 24 ? `${Math.floor(h / 24)}d ${h % 24}h left` : h >= 1 ? `${h}h ${Math.floor((ms % 3600000) / 60000)}m left` : `${Math.ceil(ms / 60000)}m left`;
}

function ContestCard({ c }) {
  const { status, score, rank } = c.me;
  const action = status === "open" ? "Enter" : status === "running" ? "Resume" : "Results";
  return (
    <Link href={`/contest/${c.id}`} className={`card card-accent flex items-center gap-4 p-4 transition-colors hover:bg-primary/5 ${courseTint(c.course)}`}>
      <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-primary/15 text-2xl" aria-hidden="true">
        {c.icon}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate font-extrabold">{c.course_title}</span>
        <span className="block text-xs font-bold text-muted">
          {c.entrants} {c.entrants === 1 ? "entrant" : "entrants"}
          {c.leader ? ` · leader ${c.leader.name} (${c.leader.score}/${c.questions})` : " · be the first!"}
        </span>
        {status === "finished" && (
          <span className="block text-xs font-black text-primary">
            You: {score}/{c.questions}
            {rank ? ` · #${rank}` : ""}
          </span>
        )}
      </span>
      <span className={`shrink-0 ${status === "finished" ? "btn-ghost" : "btn-primary"} px-4 py-2 text-sm`}>{action}</span>
    </Link>
  );
}

export default function Contests() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api("/api/contests")
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorNote>{error}</ErrorNote>;
  if (!data) return <Spinner />;
  const ends = data.current[0]?.ends_at;

  return (
    <div className="tint-pink mx-auto max-w-2xl space-y-6">
      <div className="text-center">
        <PageTitle
          icon="bolt"
          title="Weekly contests"
          subtitle={`${data.questions} questions · ${data.minutes} minutes · one try per week. Ranked by score, then speed.`}
          center
        />
        {ends && (
          <p className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-bad/10 px-3 py-1 text-xs font-black uppercase tracking-wide text-bad">
            <span className="h-2 w-2 animate-pulse rounded-full bg-bad" aria-hidden="true" /> Live · {timeLeft(ends)}
          </p>
        )}
      </div>

      <section className="space-y-3">
        {data.current.map((c) => (
          <ContestCard key={c.id} c={c} />
        ))}
      </section>

      {data.previous.length > 0 && (
        <section className="space-y-3">
          <h2 className="font-extrabold">Last week</h2>
          {data.previous.map((c) => (
            <Link key={c.id} href={`/contest/${c.id}`} className="card flex items-center gap-3 p-4 hover:bg-surface">
              <span className="text-xl" aria-hidden="true">
                {c.icon}
              </span>
              <span className="flex-1 font-bold">{c.course_title}</span>
              <span className="text-sm font-bold text-muted">
                {c.leader ? `${MEDALS[0]} ${c.leader.name}` : ""}
                {c.me.rank ? ` · you #${c.me.rank}` : ""}
              </span>
            </Link>
          ))}
        </section>
      )}
      <p className="text-center text-xs font-semibold text-muted">
        +3 XP per correct answer, +10 for a perfect score. Only right or wrong is shown during a contest - questions you miss go on your Practice list.
      </p>
    </div>
  );
}
