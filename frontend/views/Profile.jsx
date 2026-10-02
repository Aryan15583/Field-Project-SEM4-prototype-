"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ErrorNote, Icon, Modal } from "@/components/ui";
import { setSoundEnabled, sfx, soundEnabled } from "@/lib/feedback";
import { useTheme } from "@/lib/theme";
import { RecoveryCodes } from "./TwoFactor";

const GOALS = [
  [10, "Casual"],
  [20, "Regular"],
  [30, "Serious"],
  [50, "Intense"],
];

export default function Profile() {
  const { user, setUser, logout } = useAuth();
  const { mode, setMode } = useTheme();
  const [sound, setSound] = useState(true);
  useEffect(() => setSound(soundEnabled()), []);
  const router = useRouter();
  const [name, setName] = useState(user.name);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [regen, setRegen] = useState(false);
  const [code, setCode] = useState("");
  const [codes, setCodes] = useState(null);
  const [certs, setCerts] = useState([]);
  useEffect(() => {
    api("/api/certificates")
      .then(setCerts)
      .catch(() => {});
  }, []);

  const save = async (patch) => {
    setError("");
    setMsg("");
    try {
      setUser(await api("/api/profile", { method: "PATCH", body: patch }));
      setMsg("Saved!");
    } catch (e) {
      setError(e.message);
    }
  };

  const regenerate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      setCodes((await api("/api/auth/recovery-codes", { method: "POST", body: { code } })).recovery_codes);
    } catch (err) {
      setError(err.message);
    }
    setCode("");
  };

  const signOut = async (everywhere) => {
    await logout(everywhere);
    router.replace("/");
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        {user.avatar_url ? (
          <img src={user.avatar_url} alt="" referrerPolicy="no-referrer" className="h-20 w-20 rounded-full" />
        ) : (
          <span className="grid h-20 w-20 place-items-center rounded-full bg-primary/15 text-3xl font-black text-primary">{user.name.slice(0, 1).toUpperCase()}</span>
        )}
        <div>
          <h1 className="text-2xl font-black">{user.name}</h1>
          <p className="text-sm text-muted">{user.email}</p>
        </div>
      </div>

      <section className="card space-y-3 p-5">
        <h2 className="font-extrabold">Certificates</h2>
        {certs.length ? (
          <ul className="space-y-2">
            {certs.map((c) => (
              <li key={c.code}>
                <a href={`/certificate/${c.code}`} className="flex items-center gap-3 rounded-xl border-2 border-line p-3 transition-colors hover:bg-surface">
                  <span className="text-2xl" aria-hidden="true">
                    🎓
                  </span>
                  <span className="flex-1">
                    <span className="block font-extrabold">{c.course}</span>
                    <span className="text-xs font-bold text-muted">Issued {new Date(c.issued_at).toLocaleDateString()}</span>
                  </span>
                  <span className="btn-link text-sm">View</span>
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm font-semibold text-muted">Finish every lesson, project and chapter test in a course to earn its certificate.</p>
        )}
      </section>

      <section className="card space-y-4 p-5">
        <h2 className="font-extrabold">Profile</h2>
        <form onSubmit={(e) => (e.preventDefault(), save({ name }))} className="flex gap-2">
          <input className="input" maxLength={60} value={name} onChange={(e) => setName(e.target.value)} aria-label="Display name" />
          <button className="btn-primary" disabled={!name.trim() || name === user.name}>
            Save
          </button>
        </form>
        <div>
          <p className="label mb-2">Daily goal</p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {GOALS.map(([xp, label]) => (
              <button key={xp} type="button" onClick={() => save({ daily_goal: xp })} className={`tile text-center ${user.daily_goal === xp ? "tile-selected" : ""}`}>
                <span className="block font-extrabold">{label}</span>
                <span className="text-xs text-muted">{xp} XP/day</span>
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="label mb-2">Theme</p>
          <div className="grid grid-cols-3 gap-2">
            {[
              ["light", "Light · blue"],
              ["dark", "Dark · green"],
              ["system", "System"],
            ].map(([m, label]) => (
              <button key={m} type="button" onClick={() => setMode(m)} className={`tile text-center text-sm ${mode === m ? "tile-selected" : ""}`}>
                {label}
              </button>
            ))}
          </div>
        </div>
        <label className="flex cursor-pointer items-center justify-between gap-4">
          <span>
            <span className="label block">Sound effects & haptics</span>
            <span className="text-sm font-semibold text-muted">Chimes and vibration on answers</span>
          </span>
          <input
            type="checkbox"
            className="peer sr-only"
            checked={sound}
            onChange={(e) => {
              setSound(e.target.checked);
              setSoundEnabled(e.target.checked);
              if (e.target.checked) sfx.correct();
            }}
          />
          <span className="relative h-8 w-14 shrink-0 rounded-full bg-line transition-colors peer-checked:bg-primary peer-focus-visible:ring-4 peer-focus-visible:ring-primary/30 after:absolute after:left-1 after:top-1 after:h-6 after:w-6 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-6" />
        </label>
        <label className="flex cursor-pointer items-center justify-between gap-4">
          <span>
            <span className="label block">Streak reminder emails</span>
            <span className="text-sm font-semibold text-muted">One email on evenings your streak is about to end</span>
          </span>
          <input type="checkbox" className="peer sr-only" checked={user.reminder_emails} onChange={(e) => save({ reminder_emails: e.target.checked })} />
          <span className="relative h-8 w-14 shrink-0 rounded-full bg-line transition-colors peer-checked:bg-primary peer-focus-visible:ring-4 peer-focus-visible:ring-primary/30 after:absolute after:left-1 after:top-1 after:h-6 after:w-6 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-6" />
        </label>
        {msg && <p className="text-sm font-bold text-primary">{msg}</p>}
        <ErrorNote>{!regen && error}</ErrorNote>
      </section>

      <section className="card space-y-4 p-5">
        <h2 className="flex items-center gap-2 font-extrabold">
          <Icon name="shield" className="h-5 w-5 text-primary" /> Security
        </h2>
        <p className="flex items-center gap-2 text-sm">
          <Icon name="check" className="h-5 w-5 text-primary" /> 2-step verification is on ·{" "}
          {user.mfa_method === "totp" ? "authenticator app" : "codes emailed to " + user.email}
        </p>
        <div className="flex flex-wrap gap-2">
          {user.mfa_method === "totp" && (
            <button className="btn-ghost" onClick={() => (setRegen(true), setCodes(null), setError(""))}>
              New recovery codes
            </button>
          )}
          <button className="btn-ghost" onClick={() => signOut(false)}>
            <Icon name="logout" className="h-4 w-4" /> Log out
          </button>
          <button className="btn-bad" onClick={() => signOut(true)}>
            Log out of all devices
          </button>
        </div>
      </section>

      <Modal open={regen} onClose={() => setRegen(false)} label="New recovery codes">
        {codes ? (
          <>
            <h2 className="mb-2 text-xl font-black">Your new recovery codes</h2>
            <p className="mb-4 text-sm text-muted">Old codes no longer work. Save these now.</p>
            <RecoveryCodes codes={codes} />
            <button className="btn-primary mt-4 w-full" onClick={() => setRegen(false)}>
              Done
            </button>
          </>
        ) : (
          <form onSubmit={regenerate} className="space-y-3">
            <h2 className="text-xl font-black">Confirm it's you</h2>
            <p className="text-sm text-muted">Enter a code from your authenticator app. This replaces all your old recovery codes.</p>
            <input className="input text-center font-mono text-2xl tracking-[0.4em]" inputMode="numeric" autoFocus maxLength={6} value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} aria-label="Verification code" />
            <ErrorNote>{error}</ErrorNote>
            <button className="btn-primary w-full" disabled={code.length !== 6}>
              Generate
            </button>
          </form>
        )}
      </Modal>
    </div>
  );
}
