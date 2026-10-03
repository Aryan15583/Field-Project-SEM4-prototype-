"use client";

import Link from "next/link";
import { useState } from "react";
import Codi from "@/components/Codi";
import { MASCOTS } from "@/lib/mascots";
import { setMascot, useMascotId } from "@/lib/mascotPref";

const MOODS = ["idle", "wave", "happy", "think", "sad", "celebrate"];

/** Public gallery of the whole mascot cast; tap a card to make that mascot your study buddy. */
export default function Mascots() {
  const chosen = useMascotId();
  const [mood, setMoodState] = useState("idle");
  return (
    <main className="mx-auto max-w-5xl space-y-6 px-4 py-10">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-extrabold">Meet the Codeingo crew</h1>
        <p className="font-semibold text-muted">Sixteen pixel buddies. Tap one to pick your study buddy - it follows you through every lesson.</p>
        <div className="flex flex-wrap justify-center gap-2" role="group" aria-label="Mood">
          {MOODS.map((m) => (
            <button key={m} type="button" onClick={() => setMoodState(m)} aria-pressed={mood === m} className={mood === m ? "btn-primary" : "btn-ghost"}>
              {m}
            </button>
          ))}
        </div>
      </header>
      <ul className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {MASCOTS.map((m) => (
          <li key={m.id}>
            <button
              type="button"
              onClick={() => setMascot(m.id)}
              aria-pressed={m.id === chosen}
              className={`card flex w-full flex-col items-center gap-2 border-2 p-4 text-center transition ${m.id === chosen ? "border-primary" : "border-transparent hover:border-primary/40"}`}
            >
              <Codi mascot={m.id} size={110} mood={mood} interactive={false} />
              <span className="font-extrabold">{m.name}</span>
              <span className="text-xs font-semibold text-muted">{m.tagline}</span>
              {m.id === chosen && <span className="text-xs font-extrabold text-primary">Your buddy</span>}
            </button>
          </li>
        ))}
      </ul>
      <p className="text-center">
        <Link href="/" className="btn-ghost">Back to Codeingo</Link>
      </p>
    </main>
  );
}
