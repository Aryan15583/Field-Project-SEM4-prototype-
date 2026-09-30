"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorNote, Icon, Spinner } from "@/components/ui";

const MEDALS = ["🥇", "🥈", "🥉"];

function Avatar({ name, url }) {
  if (url) return <img src={url} alt="" referrerPolicy="no-referrer" className="h-10 w-10 rounded-full object-cover" />;
  return <span className="grid h-10 w-10 place-items-center rounded-full bg-primary/15 font-black text-primary">{name.slice(0, 1).toUpperCase()}</span>;
}

export default function Leaderboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api("/api/leaderboard").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorNote>{error}</ErrorNote>;
  if (!data) return <Spinner />;

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 grid h-16 w-16 place-items-center rounded-2xl bg-gold/15 text-gold">
          <Icon name="trophy" className="h-9 w-9" />
        </div>
        <h1 className="text-2xl font-black">Weekly League</h1>
        <p className="text-sm text-muted">Earn XP this week to climb the ranks. Resets every Monday.</p>
      </div>
      {data.entries.length === 0 ? (
        <p className="card p-8 text-center text-muted">No XP earned this week yet - be the first!</p>
      ) : (
        <ol className="card divide-y-2 divide-line overflow-hidden">
          {data.entries.map((e) => (
            <li key={e.rank} className={`flex items-center gap-4 px-5 py-3 ${e.me ? "bg-primary/10" : ""}`}>
              <span className="w-8 text-center text-lg font-black text-muted">{MEDALS[e.rank - 1] || e.rank}</span>
              <Avatar name={e.name} url={e.avatar_url} />
              <span className={`flex-1 truncate font-bold ${e.me ? "text-primary" : ""}`}>
                {e.name} {e.me && <span className="text-xs">(you)</span>}
              </span>
              <span className="font-black text-muted">{e.xp} XP</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
