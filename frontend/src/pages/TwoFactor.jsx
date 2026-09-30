import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorNote, Icon, Logo, Mascot, Spinner } from "../components/ui";

function Shell({ children }) {
  return (
    <div className="grid min-h-screen place-items-center bg-bg px-4 py-10 text-ink">
      <div className="w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <Logo />
        </div>
        <div className="card p-6 sm:p-8">{children}</div>
      </div>
    </div>
  );
}

function CodeInput({ value, onChange, autoFocus = true }) {
  return (
    <input
      className="input text-center font-mono text-3xl tracking-[0.5em]"
      inputMode="numeric"
      autoComplete="one-time-code"
      pattern="[0-9]{6}"
      maxLength={6}
      autoFocus={autoFocus}
      aria-label="6-digit verification code"
      placeholder="••••••"
      value={value}
      onChange={(e) => onChange(e.target.value.replace(/\D/g, "").slice(0, 6))}
    />
  );
}

function useMfaStage(expected) {
  const navigate = useNavigate();
  const [state, setState] = useState(null);
  useEffect(() => {
    api("/api/auth/2fa/status")
      .then((s) => (s.stage === expected ? setState(s) : navigate(`/2fa/${s.stage}`, { replace: true })))
      .catch(() => navigate("/?error=expired", { replace: true }));
  }, [expected, navigate]);
  return state;
}

export function RecoveryCodes({ codes }) {
  const download = () => {
    const blob = new Blob([`Codeingo recovery codes\nEach code works once.\n\n${codes.join("\n")}\n`], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "codeingo-recovery-codes.txt";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 rounded-2xl border-2 border-line bg-surface p-4 font-mono text-sm">
        {codes.map((c) => (
          <span key={c}>{c}</span>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <button type="button" className="btn-ghost flex-1" onClick={() => navigator.clipboard?.writeText(codes.join("\n"))}>
          Copy
        </button>
        <button type="button" className="btn-ghost flex-1" onClick={download}>
          Download
        </button>
      </div>
    </div>
  );
}

export function TwoFactorSetup() {
  const status = useMfaStage("setup");
  const { reload } = useAuth();
  const navigate = useNavigate();
  const [setup, setSetup] = useState(null);
  const [code, setCode] = useState("");
  const [codes, setCodes] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (status && !setup) api("/api/auth/2fa/setup", { method: "POST" }).then(setSetup).catch((e) => setError(e.message));
  }, [status, setup]);

  const enable = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api("/api/auth/2fa/enable", { method: "POST", body: { code } });
      setCodes(res.recovery_codes);
    } catch (err) {
      setError(err.message);
      setCode("");
    } finally {
      setBusy(false);
    }
  };

  if (!status) return <Spinner />;

  if (codes)
    return (
      <Shell>
        <div className="mb-4 flex justify-center">
          <Mascot size={90} />
        </div>
        <h1 className="text-center text-2xl font-black">You're protected!</h1>
        <p className="mb-5 mt-2 text-center text-muted">
          Save these recovery codes somewhere safe. Each one can be used once if you lose your phone. <strong className="text-ink">They won't be shown again.</strong>
        </p>
        <RecoveryCodes codes={codes} />
        <button className="btn-primary mt-6 w-full" onClick={async () => (await reload(), navigate("/learn", { replace: true }))}>
          I saved them - start learning
        </button>
      </Shell>
    );

  return (
    <Shell>
      <div className="mb-3 flex items-center gap-3">
        <span className="grid h-11 w-11 place-items-center rounded-2xl bg-primary/10 text-primary">
          <Icon name="shield" className="h-6 w-6" />
        </span>
        <div>
          <h1 className="text-xl font-black">Set up 2-step verification</h1>
          <p className="text-sm text-muted">{status.email}</p>
        </div>
      </div>
      <ol className="mb-5 list-decimal space-y-1 pl-5 text-sm text-muted">
        <li>Open Google Authenticator, Microsoft Authenticator, Authy or 1Password.</li>
        <li>Scan the QR code (or enter the key manually).</li>
        <li>Type the 6-digit code it shows.</li>
      </ol>
      {setup ? (
        <>
          <div className="mx-auto mb-3 w-48 rounded-2xl bg-white p-3">
            <img src={setup.qr} alt="QR code for your authenticator app" className="h-full w-full" />
          </div>
          <details className="mb-5 text-center text-sm">
            <summary className="btn-link cursor-pointer">Can't scan? Enter key manually</summary>
            <code className="mt-2 block break-all rounded-xl bg-surface p-2 font-mono text-xs">{setup.secret}</code>
          </details>
        </>
      ) : (
        !error && <Spinner label="Generating key" />
      )}
      <form onSubmit={enable} className="space-y-3">
        <CodeInput value={code} onChange={setCode} />
        <ErrorNote>{error}</ErrorNote>
        <button className="btn-primary w-full" disabled={busy || code.length !== 6}>
          Verify & enable
        </button>
      </form>
    </Shell>
  );
}

export function TwoFactorVerify() {
  const status = useMfaStage("verify");
  const { reload } = useAuth();
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [recovery, setRecovery] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api("/api/auth/2fa/verify", { method: "POST", body: recovery ? { recovery_code: code } : { code } });
      await reload();
      navigate("/learn", { replace: true });
    } catch (err) {
      setError(err.message);
      setCode("");
    } finally {
      setBusy(false);
    }
  };

  if (!status) return <Spinner />;
  return (
    <Shell>
      <div className="mb-4 flex justify-center">
        <Mascot size={90} mood="think" />
      </div>
      <h1 className="text-center text-2xl font-black">2-step verification</h1>
      <p className="mb-5 mt-1 text-center text-sm text-muted">
        {recovery ? "Enter one of your recovery codes." : "Enter the 6-digit code from your authenticator app."}
      </p>
      <form onSubmit={submit} className="space-y-3">
        {recovery ? (
          <input className="input text-center font-mono" autoFocus maxLength={20} placeholder="XXXXXXXX-XXXXXXXX" value={code} onChange={(e) => setCode(e.target.value)} aria-label="Recovery code" />
        ) : (
          <CodeInput value={code} onChange={setCode} />
        )}
        <ErrorNote>{error || (status.locked && "Too many attempts. Please wait 15 minutes.")}</ErrorNote>
        <button className="btn-primary w-full" disabled={busy || (!recovery && code.length !== 6) || (recovery && code.length < 8)}>
          Verify
        </button>
      </form>
      <div className="mt-5 flex justify-between text-sm">
        <button type="button" className="btn-link" onClick={() => (setRecovery(!recovery), setCode(""), setError(""))}>
          {recovery ? "Use authenticator code" : "Use a recovery code"}
        </button>
        <Link to="/" className="btn-link">
          Cancel
        </Link>
      </div>
    </Shell>
  );
}
