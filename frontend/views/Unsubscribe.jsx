"use client";

import Link from "next/link";
import { useState } from "react";
import { Icon, Logo, Mascot } from "@/components/ui";
import { api } from "@/lib/api";

/** Landing page for the link in streak reminder emails. Nothing changes until the button is pressed,
 *  so link scanners that open every URL in an email can't unsubscribe anyone by accident. */
export default function Unsubscribe({ u, t }) {
  const [state, setState] = useState("ask"); // ask | busy | done | error
  const [error, setError] = useState("");

  const confirm = async () => {
    setState("busy");
    try {
      await api(`/api/public/unsubscribe?u=${encodeURIComponent(u)}&t=${encodeURIComponent(t)}`, { method: "POST", retry: false });
      setState("done");
    } catch (e) {
      setError(e.status === 400 || e.status === 422 ? "This link is invalid or incomplete. You can turn reminders off in your profile instead." : e.message);
      setState("error");
    }
  };

  return (
    <div className="grid min-h-screen place-items-center px-4 py-10 text-ink">
      <div className="card w-full max-w-md p-8 text-center">
        <div className="mb-6 flex justify-center">
          <Logo />
        </div>
        <Mascot size={96} mood={state === "done" ? "sad" : "wave"} className="mx-auto" />
        {state === "done" ? (
          <>
            <h1 className="mt-5 text-2xl font-black">You're unsubscribed</h1>
            <p className="mt-2 font-semibold text-muted">No more streak reminder emails. You can turn them back on any time in your profile.</p>
          </>
        ) : (
          <>
            <h1 className="mt-5 flex items-center justify-center gap-2 text-2xl font-black">
              <Icon name="mail" className="h-6 w-6 text-primary" /> Streak reminders
            </h1>
            <p className="mt-2 font-semibold text-muted">Stop the evening emails that remind you when your streak is about to end?</p>
            {state === "error" && <p className="mt-4 rounded-xl bg-red-500/10 p-3 text-sm font-bold text-red-600">{error}</p>}
            <button className="btn-primary mt-6 w-full" onClick={confirm} disabled={state === "busy" || !u || !t}>
              {state === "busy" ? "Saving…" : "Turn off reminder emails"}
            </button>
          </>
        )}
        <Link href="/learn" className="btn-ghost mt-3 w-full">
          Go to Codeingo
        </Link>
      </div>
    </div>
  );
}
