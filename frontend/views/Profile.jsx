"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ErrorNote, Icon, IconTile, Modal } from "@/components/ui";
import { setSoundEnabled, sfx, soundEnabled } from "@/lib/feedback";
import { usePwa } from "@/lib/pwa";
import { useTheme } from "@/lib/theme";
import { addPasskey, cancelled, deviceName, passkeysSupported } from "@/lib/webauthn";
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
    <div className="tint-sky mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4 rounded-3xl bg-gradient-to-r from-primary/15 via-violet/10 to-pink/10 p-5">
        {/* gradient ring around the avatar */}
        <span className="rounded-full bg-gradient-to-br from-primary via-violet to-pink p-1">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt="" referrerPolicy="no-referrer" className="h-20 w-20 rounded-full border-4 border-raised" />
          ) : (
            <span className="grid h-20 w-20 place-items-center rounded-full border-4 border-raised bg-raised text-3xl font-black text-primary">
              {user.name.slice(0, 1).toUpperCase()}
            </span>
          )}
        </span>
        <div>
          <h1 className="text-2xl font-black">{user.name}</h1>
          <p className="text-sm text-muted">{user.email}</p>
        </div>
      </div>

      <section className="tint-gold card card-accent space-y-3 p-5">
        <h2 className="flex items-center gap-3 font-extrabold">
          <IconTile icon="star" size="sm" /> Certificates
        </h2>
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

      <section className="card card-accent space-y-4 p-5">
        <h2 className="flex items-center gap-3 font-extrabold">
          <IconTile icon="user" size="sm" /> Profile
        </h2>
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

      <AppInstall />

      <YourData />

      <section className="tint-teal card card-accent space-y-4 p-5">
        <h2 className="flex items-center gap-3 font-extrabold">
          <IconTile icon="shield" size="sm" /> Security
        </h2>
        <p className="flex items-center gap-2 text-sm">
          <Icon name="check" className="h-5 w-5 text-primary" /> 2-step verification is on ·{" "}
          {user.mfa_method === "totp" ? "authenticator app" : "codes emailed to " + user.email}
        </p>
        <Passkeys />
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

function Passkeys() {
  const [list, setList] = useState(null);
  const [supported, setSupported] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const load = () =>
    api("/api/auth/passkeys")
      .then(setList)
      .catch(() => setList([]));
  useEffect(() => {
    setSupported(passkeysSupported());
    load();
  }, []);

  const add = async () => {
    setBusy(true);
    setError("");
    try {
      await addPasskey(deviceName());
      await load();
    } catch (e) {
      if (!cancelled(e)) setError(e.name === "InvalidStateError" ? "This device already has a passkey for your account." : e.message);
    } finally {
      setBusy(false);
    }
  };
  const remove = async (pk) => {
    setError("");
    try {
      await api(`/api/auth/passkeys/${pk.id}`, { method: "DELETE" });
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-3 rounded-2xl border-2 border-line p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="flex items-center gap-2 font-extrabold">
            <Icon name="key" className="h-5 w-5 text-primary" /> Passkeys
          </p>
          <p className="text-sm font-semibold text-muted">Sign in with Face ID, your fingerprint or your screen lock - no code needed.</p>
        </div>
        {supported && (
          <button className="btn-primary" onClick={add} disabled={busy}>
            {busy ? "Waiting…" : "Add a passkey"}
          </button>
        )}
      </div>
      {!supported && <p className="text-sm font-semibold text-muted">This browser doesn't support passkeys.</p>}
      {list?.length > 0 && (
        <ul className="divide-y-2 divide-line">
          {list.map((pk) => (
            <li key={pk.id} className="flex items-center gap-3 py-2">
              <span className="min-w-0 flex-1">
                <span className="block truncate font-bold">{pk.name}</span>
                <span className="text-xs font-semibold text-muted">
                  Added {new Date(pk.created_at).toLocaleDateString()}
                  {pk.last_used_at ? ` · last used ${new Date(pk.last_used_at).toLocaleDateString()}` : " · not used yet"}
                  {pk.synced ? " · synced" : ""}
                </span>
              </span>
              <button className="text-sm font-bold text-muted hover:text-red-500" onClick={() => remove(pk)} aria-label={`Remove passkey ${pk.name}`}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      <ErrorNote>{error}</ErrorNote>
    </div>
  );
}

function AppInstall() {
  const { canInstall, installed, ios, install } = usePwa();
  return (
    <section className="tint-violet card card-accent flex flex-wrap items-center justify-between gap-4 p-5">
      <div className="min-w-0 flex-1">
        <h2 className="mb-1 flex items-center gap-3 font-extrabold">
          <IconTile icon="bolt" size="sm" /> Codeingo app
        </h2>
        <p className="text-sm font-semibold text-muted">
          {installed
            ? "You're using the installed app."
            : ios
              ? "On iPhone or iPad: tap Share, then “Add to Home Screen”."
              : canInstall
                ? "Install Codeingo for a full-screen app with its own icon - it opens straight to your lessons."
                : "Install Codeingo from your browser's menu (“Install app” or “Add to Home screen”)."}
        </p>
      </div>
      {canInstall && (
        <button className="btn-primary" onClick={install}>
          Install the app
        </button>
      )}
    </section>
  );
}

function YourData() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [open, setOpen] = useState(false);
  const [info, setInfo] = useState(null);
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const download = async () => {
    setError("");
    try {
      const res = await fetch("/api/account/export", { credentials: "same-origin" });
      if (!res.ok) throw new Error("Couldn't prepare your data. Please try again.");
      const url = URL.createObjectURL(await res.blob());
      const a = Object.assign(document.createElement("a"), { href: url, download: "codeingo-my-data.json" });
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message);
    }
  };

  const start = () => {
    setOpen(true);
    setCode("");
    setError("");
    setInfo(null);
    api("/api/account/confirm-code", { method: "POST" })
      .then(setInfo)
      .catch((e) => setError(e.message));
  };

  const remove = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api("/api/account/delete", { method: "POST", body: { code: code.replace(/\s/g, "") } });
      setUser(null);
      router.replace("/");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <section className="tint-sky card card-accent space-y-4 p-5">
      <h2 className="flex items-center gap-3 font-extrabold">
        <IconTile icon="shield" size="sm" /> Your data
      </h2>
      <p className="text-sm font-semibold text-muted">
        Download everything we hold about you, or delete your account and all of it for good. See the{" "}
        <a href="/privacy" className="btn-link">
          Privacy Policy
        </a>
        .
      </p>
      <div className="flex flex-wrap gap-2">
        <button className="btn-ghost" onClick={download}>
          Download my data
        </button>
        <button className="btn-bad" onClick={start}>
          Delete my account
        </button>
      </div>
      <ErrorNote>{!open && error}</ErrorNote>

      <Modal open={open} onClose={() => setOpen(false)} label="Delete account">
        <form onSubmit={remove} className="space-y-4">
          <h2 className="text-xl font-black">Delete your account?</h2>
          <p className="font-semibold text-muted">
            This permanently deletes your progress, streak, badges, certificates, friends and contest results. It can't be undone.
          </p>
          <p className="text-sm font-semibold">
            {info?.method === "email"
              ? `To confirm it's you, enter the code we just emailed to ${info.sent_to}.`
              : info?.method === "totp"
                ? "To confirm it's you, enter the 6-digit code from your authenticator app."
                : "Sending a confirmation code…"}
          </p>
          <input
            className="input text-center font-mono text-2xl tracking-[0.4em]"
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={8}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            aria-label="Confirmation code"
            autoFocus
          />
          <ErrorNote>{error}</ErrorNote>
          <div className="flex gap-2">
            <button type="button" className="btn-ghost flex-1" onClick={() => setOpen(false)}>
              Keep my account
            </button>
            <button className="btn-bad flex-1" disabled={busy || code.replace(/\s/g, "").length < 6}>
              Delete everything
            </button>
          </div>
        </form>
      </Modal>
    </section>
  );
}
