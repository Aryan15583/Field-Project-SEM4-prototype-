"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { courseTint, ErrorNote, Icon, Mascot, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

function Stat({ value, label, tint }) {
  return (
    <div className={`rounded-2xl bg-primary/10 p-3 text-center ${tint}`}>
      <p className="text-2xl font-black text-primary">{value}</p>
      <p className="text-xs font-bold uppercase tracking-wider text-muted">{label}</p>
    </div>
  );
}

export default function PracticeHub() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/practice/overview")
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  const all = data?.all;
  const ready = all && all.total >= (data?.min_items ?? 3);

  return (
    <div className="tint-violet mx-auto max-w-2xl space-y-6">
      <div className="card card-accent flex flex-col items-center gap-5 bg-gradient-to-br from-primary/15 via-raised to-pink/10 p-6 text-center sm:flex-row sm:text-left">
        <Mascot size={110} mood={all?.due ? "think" : "happy"} />
        <div className="flex-1">
          <h1 className="text-2xl font-black">Practice</h1>
          <p className="mt-1 font-semibold text-muted">
            Questions you got wrong come back until they stick, and the ones you know return at growing gaps (1, 3, 7, 16, then 35 days) so
            they move into long-term memory.
          </p>
          <p className="mt-2 flex items-center justify-center gap-2 text-sm font-bold text-muted sm:justify-start">
            <Icon name="heart" className="h-4 w-4 text-bad" />
            {user.hearts < user.max_hearts ? "Finish a session to earn a heart back." : "No hearts lost while practising."}
          </p>
        </div>
      </div>

      <ErrorNote>{error}</ErrorNote>

      {!data ? (
        <div className="skeleton h-48 rounded-3xl" />
      ) : (
        <>
          <div className="card p-5">
            <div className="grid grid-cols-3 gap-3">
              <Stat value={all.due} label="Due now" tint="tint-orange" />
              <Stat value={all.mistakes} label="Mistakes" tint="tint-red" />
              <Stat value={`${all.strong}/${all.total}`} label="Strong" tint="tint-teal" />
            </div>
            {ready ? (
              <Link href="/review" className="btn-primary mt-5 w-full">
                Practise everything +{data.xp} XP
              </Link>
            ) : (
              <p className="mt-5 text-center text-sm font-bold text-muted">Finish a lesson first - what you learn (and miss) shows up here.</p>
            )}
          </div>

          <div className="card divide-y-2 divide-line">
            {data.courses.map((c) => {
              const canPractise = c.total >= data.min_items;
              return (
                <div key={c.slug} className={`flex items-center gap-4 p-4 ${courseTint(c.slug)}`}>
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-primary/15 text-2xl" aria-hidden="true">
                    {c.icon}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-extrabold">{c.title}</p>
                    {c.total ? (
                      <>
                        <ProgressBar value={c.strong} max={c.total} className="mt-1 h-2" />
                        <p className="mt-1 text-xs font-bold text-muted">
                          {c.due ? `${c.due} due` : "Nothing due"} · {c.strong}/{c.total} strong
                        </p>
                      </>
                    ) : (
                      <p className="text-xs font-bold text-muted">Not started yet</p>
                    )}
                  </div>
                  {canPractise ? (
                    <Link href={`/review?course=${encodeURIComponent(c.slug)}`} className={c.due ? "btn-primary shrink-0" : "btn-ghost shrink-0"}>
                      {c.due ? "Review" : "Practise"}
                    </Link>
                  ) : (
                    <Link href="/learn" className="btn-link shrink-0 text-sm">
                      Learn
                    </Link>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
