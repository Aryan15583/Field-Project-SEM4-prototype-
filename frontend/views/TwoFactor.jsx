"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ErrorNote, Icon, Logo, Mascot, Spinner } from "@/components/ui";

function Shell({ children }) {
  return (
    <div className="grid min-h-screen place-items-center px-4 py-10 text-ink">
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
  const router = useRouter();
  const [state, setState] = useState(null);
  useEffect(() => {
    api("/api/auth/2fa/status")
      .then((s) => (s.stage === expected ? setState(s) : router.replace(`/2fa/${s.stage}`)))
      .catch(() => router.replace("/?error=expired"));
  }, [expected, router]);
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

/** Seconds left before "Resend" is allowed again. */
function useCountdown() {
  const [left, setLeft] = useState(0);
  useEffect(() => {
    if (left <= 0) return;
    const t = setTimeout(() => setLeft((n) => n - 1), 1000);
    return () => clearTimeout(t);
  }, [left]);
  return [left, setLeft];
}

/**
 * Emails a 6-digit code as soon as it mounts, then lets the learner type it in or ask for another.
 * `onSubmit(code)` should throw an Error with a readable message when the code is wrong.
 */
function EmailCodeForm({ status, onSubmit, footer }) {
  const [code, setCode] = useState("");
  const [sentTo, setSentTo] = useState(status.email_masked);
  const [sending, setSending] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [left, setLeft] = useCountdown();
  const started = useRef(false);

  const send = async (manual) => {
    setSending(true);
    setError("");
    setNote("");
    try {
      const res = await api("/api/auth/2fa/email/send", { method: "POST", body: { resend: manual } });
      setSentTo(res.sent_to);
      setLeft(res.resend_in);
      if (manual) setNote("New code sent. Codes from earlier emails no longer work.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  };

  useEffect(() => {
    if (started.current) return; // React dev mode mounts twice - send only once
    started.current = true;
    send(false);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setNote("");
    try {
      await onSubmit(code);
    } catch (err) {
      setError(err.message);
      setCode("");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <p className="mb-5 mt-1 text-center text-sm text-muted">
        {sending && !sentTo ? (
          "Sending a code to your email…"
        ) : (
          <>
            We emailed a 6-digit code to <strong className="text-ink">{sentTo}</strong>. It expires in 10 minutes.
          </>
        )}
      </p>
      {status.codes_in_console && (
        <p className="mb-4 rounded-xl border-2 border-dashed border-line p-3 text-center text-xs font-bold text-muted">
          Development mode: no mail server is set up, so the code is printed in the backend terminal (look for EMAIL).
        </p>
      )}
      <form onSubmit={submit} className="space-y-3">
        <CodeInput value={code} onChange={setCode} />
        <ErrorNote>{error || (status.locked && "Too many attempts. Please wait 15 minutes.")}</ErrorNote>
        {note && <p className="text-center text-sm font-bold text-primary">{note}</p>}
        <button className="btn-primary w-full" disabled={busy || code.length !== 6}>
          Verify
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-muted">
        Didn't get it? Check your spam folder, or{" "}
        <button type="button" className="btn-link" disabled={sending || left > 0} onClick={() => send(true)}>
          {left > 0 ? `resend in ${left}s` : "send a new code"}
        </button>
      </p>
      {footer}
    </>
  );
}

function AppSetup({ status, onDone }) {
  const [setup, setSetup] = useState(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api("/api/auth/2fa/setup", { method: "POST" })
      .then(setSetup)
      .catch((e) => setError(e.message));
  }, []);

  const enable = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api("/api/auth/2fa/enable", {
        method: "POST",
        body: { code },
      });
      onDone(res.recovery_codes);
    } catch (err) {
      setError(err.message);
      setCode("");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
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
        <CodeInput value={code} onChange={setCode} autoFocus={false} />
        <ErrorNote>{error}</ErrorNote>
        <button className="btn-primary w-full" disabled={busy || code.length !== 6}>
          Verify & enable
        </button>
      </form>
    </>
  );
}

export function TwoFactorSetup() {
  const status = useMfaStage("setup");
  const { reload } = useAuth();
  const router = useRouter();
  const [method, setMethod] = useState("email");
  const [codes, setCodes] = useState(null);

  const finish = async () => {
    await reload();
    router.replace("/learn");
  };

  if (!status) return <Spinner />;

  if (codes)
    return (
      <Shell>
        <div className="mb-4 flex justify-center">
          <Mascot size={100} mood="celebrate" />
        </div>
        <h1 className="text-center text-2xl font-black">You're protected!</h1>
        <p className="mb-5 mt-2 text-center text-muted">
          Save these recovery codes somewhere safe. Each one can be used once if you lose your phone.{" "}
          <strong className="text-ink">They won't be shown again.</strong>
        </p>
        <RecoveryCodes codes={codes} />
        <button className="btn-primary mt-6 w-full" onClick={finish}>
          I saved them - start learning
        </button>
      </Shell>
    );

  const switchTo = (m) => (
    <button type="button" className="btn-link mt-5 block w-full text-center text-sm" onClick={() => setMethod(m)}>
      {m === "app" ? "Use an authenticator app instead (extra secure)" : "Email me a code instead"}
    </button>
  );

  return (
    <Shell>
      <div className="mb-3 flex items-center gap-3">
        <span className="grid h-11 w-11 place-items-center rounded-2xl bg-primary/10 text-primary">
          <Icon name="shield" className="h-6 w-6" />
        </span>
        <div>
          <h1 className="text-xl font-black">{method === "email" ? "Verify your email" : "Set up an authenticator app"}</h1>
          <p className="text-sm text-muted">{status.email}</p>
        </div>
      </div>
      {method === "email" ? (
        <EmailCodeForm
          status={status}
          onSubmit={async (code) => {
            await api("/api/auth/2fa/email/enable", {
              method: "POST",
              body: { code },
            });
            await finish();
          }}
          footer={switchTo("app")}
        />
      ) : (
        <>
          <AppSetup status={status} onDone={setCodes} />
          {switchTo("email")}
        </>
      )}
    </Shell>
  );
}

export function TwoFactorVerify() {
  const status = useMfaStage("verify");
  const { reload } = useAuth();
  const router = useRouter();
  const [code, setCode] = useState("");
  const [recovery, setRecovery] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const verify = async (body) => {
    await api("/api/auth/2fa/verify", { method: "POST", body });
    await reload();
    router.replace("/learn");
  };

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await verify(recovery ? { recovery_code: code } : { code });
    } catch (err) {
      setError(err.message);
      setCode("");
    } finally {
      setBusy(false);
    }
  };

  if (!status) return <Spinner />;

  const header = (
    <>
      <div className="mb-4 flex justify-center">
        <Mascot size={90} mood="think" />
      </div>
      <h1 className="text-center text-2xl font-black">{status.method === "email" && !recovery ? "Check your email" : "2-step verification"}</h1>
    </>
  );
  const links = (
    <div className="mt-5 flex justify-between text-sm">
      {status.has_recovery_codes ? (
        <button type="button" className="btn-link" onClick={() => (setRecovery(!recovery), setCode(""), setError(""))}>
          {recovery ? (status.method === "email" ? "Use an emailed code" : "Use authenticator code") : "Use a recovery code"}
        </button>
      ) : (
        <span />
      )}
      <Link href="/" className="btn-link">
        Cancel
      </Link>
    </div>
  );

  if (status.method === "email" && !recovery)
    return (
      <Shell>
        {header}
        <EmailCodeForm status={status} onSubmit={(c) => verify({ code: c })} footer={links} />
      </Shell>
    );

  return (
    <Shell>
      {header}
      <p className="mb-5 mt-1 text-center text-sm text-muted">
        {recovery ? "Enter one of your recovery codes." : "Enter the 6-digit code from your authenticator app."}
      </p>
      <form onSubmit={submit} className="space-y-3">
        {recovery ? (
          <input
            className="input text-center font-mono"
            autoFocus
            maxLength={20}
            placeholder="XXXXXXXX-XXXXXXXX"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            aria-label="Recovery code"
          />
        ) : (
          <CodeInput value={code} onChange={setCode} />
        )}
        <ErrorNote>{error || (status.locked && "Too many attempts. Please wait 15 minutes.")}</ErrorNote>
        <button className="btn-primary w-full" disabled={busy || (!recovery && code.length !== 6) || (recovery && code.length < 8)}>
          Verify
        </button>
      </form>
      {links}
    </Shell>
  );
}
