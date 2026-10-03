"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorNote, Icon, nameTint, PageTitle, Spinner } from "@/components/ui";

const MEDALS = ["🥇", "🥈", "🥉"];
const TABS = [
  ["global", "Everyone"],
  ["friends", "Friends"],
];

function Avatar({ name, url, size = "h-10 w-10" }) {
  if (url) return <img src={url} alt="" referrerPolicy="no-referrer" className={`${size} rounded-full object-cover`} />;
  return <span className={`grid ${size} shrink-0 place-items-center rounded-full bg-primary/15 font-black text-primary ${nameTint(name)}`}>{name.slice(0, 1).toUpperCase()}</span>;
}

/** "ABCD2345" -> "ABCD-2345": easier to read out or type. */
const pretty = (code) => (code ? `${code.slice(0, 4)}-${code.slice(4)}` : "");

function Board({ entries, scope, onFollow }) {
  if (entries.length === 0) return <p className="card p-8 text-center text-muted">No XP earned this week yet - be the first!</p>;
  return (
    <ol className="card divide-y-2 divide-line overflow-hidden">
      {entries.map((e) => (
        <li key={e.code} className={`flex items-center gap-3 px-4 py-3 sm:gap-4 sm:px-5 ${e.me ? "bg-primary/10" : ""}`}>
          <span className="w-8 shrink-0 text-center text-lg font-black text-muted">{MEDALS[e.rank - 1] || e.rank}</span>
          <Avatar name={e.name} url={e.avatar_url} />
          <span className="min-w-0 flex-1">
            <span className={`block truncate font-bold ${e.me ? "text-primary" : ""}`}>
              {e.name} {e.me && <span className="text-xs">(you)</span>}
            </span>
            {e.streak > 0 && (
              <span className="flex items-center gap-1 text-xs font-bold text-muted">
                <Icon name="flame" className="h-3.5 w-3.5 text-flame" /> {e.streak}-day streak
              </span>
            )}
          </span>
          {scope === "global" && !e.me && !e.following && (
            <button className="chip shrink-0 border-2 border-line text-xs text-primary hover:bg-surface" onClick={() => onFollow(e.code)} aria-label={`Follow ${e.name}`}>
              + Follow
            </button>
          )}
          <span className="shrink-0 font-black text-muted">{e.xp} XP</span>
        </li>
      ))}
    </ol>
  );
}

function InviteCard({ invite, onFollow, onDone }) {
  const [error, setError] = useState("");
  return (
    <div className="card border-primary p-5" role="status">
      <div className="flex items-center gap-3">
        <Avatar name={invite.name} url={invite.avatar_url} size="h-12 w-12" />
        <p className="min-w-0 flex-1 font-bold">
          {invite.following ? `You already follow ${invite.name}.` : `${invite.name} invited you to be friends on Codeingo.`}
        </p>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {!invite.following && (
          <button className="btn-primary flex-1" onClick={() => onFollow(invite.code).then(onDone, (e) => setError(e.message))}>
            Follow {invite.name}
          </button>
        )}
        <button className="btn-ghost flex-1" onClick={onDone}>
          {invite.following ? "OK" : "Not now"}
        </button>
      </div>
      <ErrorNote>{error}</ErrorNote>
    </div>
  );
}

function Friends({ friends, onFollow, onUnfollow }) {
  const [code, setCode] = useState("");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const add = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await onFollow(code);
      setCode("");
    } catch (err) {
      setError(err.message);
    }
  };

  const copyInvite = async () => {
    const link = `${window.location.origin}/leaderboard?add=${friends.code}`;
    try {
      if (navigator.share) await navigator.share({ title: "Learn to code with me on Codeingo", url: link });
      else {
        await navigator.clipboard.writeText(link);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      /* share sheet dismissed or clipboard blocked */
    }
  };

  return (
    <div className="space-y-4">
      <section className="card space-y-4 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="label">Your friend code</p>
            <p className="font-mono text-2xl font-black tracking-wider">{pretty(friends.code)}</p>
            <p className="text-sm font-semibold text-muted">
              {friends.followers} follower{friends.followers === 1 ? "" : "s"}
            </p>
          </div>
          <button className="btn-ghost" onClick={copyInvite}>
            {copied ? "Link copied!" : "Share invite link"}
          </button>
        </div>
        <form onSubmit={add} className="flex gap-2">
          <input
            className="input font-mono uppercase placeholder:font-sans placeholder:normal-case"
            value={code}
            maxLength={20}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Friend's code, e.g. ABCD-2345"
            aria-label="Friend's code"
            autoComplete="off"
          />
          <button className="btn-primary shrink-0" disabled={code.replace(/[^a-z0-9]/gi, "").length < 8}>
            Follow
          </button>
        </form>
        <ErrorNote>{error}</ErrorNote>
      </section>

      <section className="card overflow-hidden">
        <h2 className="border-b-2 border-line px-5 py-3 font-extrabold">Following ({friends.following.length})</h2>
        {friends.following.length === 0 ? (
          <p className="p-5 text-sm font-semibold text-muted">Follow friends to race them in your own weekly league. Share your invite link or add their code above.</p>
        ) : (
          <ul className="divide-y-2 divide-line">
            {friends.following.map((f) => (
              <li key={f.code} className="flex items-center gap-3 px-5 py-3">
                <Avatar name={f.name} url={f.avatar_url} />
                <span className="min-w-0 flex-1">
                  <span className="block truncate font-bold">{f.name}</span>
                  <span className="text-xs font-bold text-muted">
                    {f.xp_week} XP this week{f.streak > 0 ? ` · ${f.streak}-day streak` : ""}
                    {f.follows_you ? " · follows you" : ""}
                  </span>
                </span>
                <button className="text-sm font-bold text-muted hover:text-red-500" onClick={() => onUnfollow(f.code)} aria-label={`Unfollow ${f.name}`}>
                  Unfollow
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default function Leaderboard() {
  const [scope, setScope] = useState("global");
  const [boards, setBoards] = useState({});
  const [friends, setFriends] = useState(null);
  const [invite, setInvite] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const [g, f, fr] = await Promise.all([api("/api/leaderboard"), api("/api/leaderboard?scope=friends"), api("/api/friends")]);
      setBoards({ global: g.entries, friends: f.entries });
      setFriends(fr);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    load();
    // invite links look like /leaderboard?add=CODE
    const add = new URLSearchParams(window.location.search).get("add");
    if (add) {
      setScope("friends");
      api(`/api/friends/lookup?code=${encodeURIComponent(add)}`)
        .then(setInvite)
        .catch((e) => setError(e.status === 400 ? "That's your own invite link - share it with a friend!" : e.message));
    }
  }, [load]);

  const follow = async (code) => {
    await api("/api/friends", { method: "POST", body: { code } });
    await load();
  };
  const unfollow = async (code) => {
    await api(`/api/friends/${encodeURIComponent(code)}`, { method: "DELETE" });
    await load();
  };
  const inviteDone = () => {
    setInvite(null);
    window.history.replaceState(null, "", "/leaderboard");
  };

  if (!friends && error) return <ErrorNote>{error}</ErrorNote>;
  if (!friends) return <Spinner />;

  return (
    <div className="tint-gold mx-auto max-w-2xl">
      <PageTitle icon="trophy" title="Weekly League" subtitle="Earn XP this week to climb the ranks. Resets every Monday." center />

      <Link href="/contests" className="tint-pink mb-5 flex items-center gap-4 rounded-3xl bg-gradient-to-r from-pink to-violet p-4 text-on-primary shadow-lg shadow-pink/20 transition-transform hover:-translate-y-0.5">
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-white/20">
          <Icon name="bolt" className="h-6 w-6" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block font-extrabold">Weekly contests</span>
          <span className="block text-sm font-semibold opacity-90">10 questions, 10 minutes, a live leaderboard for every language.</span>
        </span>
        <span className="text-xl font-black" aria-hidden="true">›</span>
      </Link>

      <div className="mb-4 flex justify-center gap-2" role="tablist" aria-label="League">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={scope === key}
            onClick={() => setScope(key)}
            className={`chip border-2 border-b-4 transition-colors active:translate-y-[0.125rem] ${
              scope === key ? "border-primary bg-primary/10 text-primary" : "border-line text-muted hover:bg-surface"
            }`}
          >
            {key === "friends" && <Icon name="users" className="mr-1 inline h-4 w-4" />}
            {label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4">
          <ErrorNote>{error}</ErrorNote>
        </div>
      )}

      <div className="space-y-4">
        {invite && <InviteCard invite={invite} onFollow={follow} onDone={inviteDone} />}
        <Board entries={boards[scope] || []} scope={scope} onFollow={(c) => follow(c).catch((e) => setError(e.message))} />
        {scope === "friends" && <Friends friends={friends} onFollow={follow} onUnfollow={unfollow} />}
      </div>
    </div>
  );
}
