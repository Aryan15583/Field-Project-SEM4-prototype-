import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorNote, Icon, Modal } from "../components/ui";
import { useTheme } from "../theme";
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
  const navigate = useNavigate();
  const [name, setName] = useState(user.name);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [regen, setRegen] = useState(false);
  const [code, setCode] = useState("");
  const [codes, setCodes] = useState(null);

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
    navigate("/", { replace: true });
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
        {msg && <p className="text-sm font-bold text-primary">{msg}</p>}
        <ErrorNote>{!regen && error}</ErrorNote>
      </section>

      <section className="card space-y-4 p-5">
        <h2 className="flex items-center gap-2 font-extrabold">
          <Icon name="shield" className="h-5 w-5 text-primary" /> Security
        </h2>
        <p className="flex items-center gap-2 text-sm">
          <Icon name="check" className="h-5 w-5 text-primary" /> Signed in with Google · 2-step verification is on
        </p>
        <div className="flex flex-wrap gap-2">
          <button className="btn-ghost" onClick={() => (setRegen(true), setCodes(null), setError(""))}>
            New recovery codes
          </button>
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
