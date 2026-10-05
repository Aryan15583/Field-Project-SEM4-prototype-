"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cancelled, passkeysSupported, signInWithPasskey } from "@/lib/webauthn";
import { ErrorNote, Icon, Logo, Mascot, ThemeToggle } from "@/components/ui";

const FEATURES = [
  { icon: "bolt", title: "Bite-sized lessons", text: "5-minute lessons with quizzes, fill-in-the-blanks and real code." },
  { icon: "flame", title: "Streaks & XP", text: "Build a daily habit. Earn XP, keep your streak alive, collect badges." },
  { icon: "bulb", title: "AI hints from {buddy}", text: "Stuck? {buddy} nudges you toward the answer without spoiling it." },
  { icon: "shield", title: "Secure by default", text: "Google sign-in with mandatory 2-step verification, or a passkey (Face ID, fingerprint or PIN)." },
];

const CHIP_TINTS = ["tint-sky", "tint-gold", "", "tint-orange", "tint-violet", "tint-teal", "tint-pink"];
const LANGS = ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "SQL", "HTML & CSS", "Git", "Algorithms"];

function GoogleG() {
  return (
    <svg viewBox="0 0 48 48" className="h-5 w-5" aria-hidden="true">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z" />
      <path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z" />
    </svg>
  );
}

export default function Landing() {
  const buddy = "Codi"; // the login page always shows the original mascot
  const params = useSearchParams();
  const router = useRouter();
  // null = not known yet. Until the server answers, assume Google sign-in works (a slow or waking server must not look "not configured").
  const [config, setConfig] = useState(null);
  const [dev, setDev] = useState({ email: "", name: "" });
  const [error, setError] = useState(params.get("error") ? "Sign-in failed or was cancelled. Please try again." : "");
  const [busy, setBusy] = useState(false);
  const [canPasskey, setCanPasskey] = useState(false);
  const { reload } = useAuth();
  useEffect(() => setCanPasskey(passkeysSupported()), []);
  const [greeting, setGreeting] = useState(true); // Codi waves hello, then watches your cursor
  useEffect(() => {
    const t = setTimeout(() => setGreeting(false), 1600);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    let alive = true;
    const load = (triesLeft) =>
      api("/api/auth/config")
        .then((c) => alive && setConfig(c))
        .catch(() => alive && triesLeft > 0 && setTimeout(() => load(triesLeft - 1), 3000)); // the server may be waking up
    load(5);
    return () => {
      alive = false;
    };
  }, []);

  const devLogin = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { stage } = await api("/api/auth/dev-login", { method: "POST", body: dev });
      router.push(`/2fa/${stage}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const passkeyLogin = async () => {
    setBusy(true);
    setError("");
    try {
      await signInWithPasskey();
      await reload();
      router.replace("/learn");
    } catch (err) {
      if (!cancelled(err)) setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen text-ink">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <Logo />
        <ThemeToggle />
      </header>

      <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-10 md:grid-cols-2 md:py-16">
        <div className="order-2 flex justify-center md:order-1">
          <div className="relative">
            <div className="absolute inset-0 -z-10 rounded-full bg-primary/15 blur-3xl" />
            <Mascot size={300} mascot="codi" mood={greeting ? "wave" : "idle"} />
          </div>
        </div>
        <div className="order-1 text-center md:order-2 md:text-left">
          <h1 className="text-4xl font-black leading-tight md:text-5xl">
            The free, fun and effective way to <span className="text-primary underline decoration-gold/70 decoration-[0.35rem] underline-offset-[0.35rem]">learn to code!</span>
          </h1>
          <p className="mt-4 text-lg text-muted">Short daily lessons, instant feedback and a streak you won't want to break.</p>

          <div className="mx-auto mt-8 flex max-w-sm flex-col gap-3 md:mx-0">
            <a
              href="/api/auth/google/login"
              aria-disabled={config?.google === false}
              onClick={(e) => config?.google === false && (e.preventDefault(), setError("Google sign-in isn't configured on this server yet."))}
              className="btn-primary w-full"
            >
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-white">
                <GoogleG />
              </span>
              Continue with Google
            </a>
            {canPasskey && (
              <button type="button" onClick={passkeyLogin} disabled={busy} className="btn-ghost w-full">
                <Icon name="key" className="h-6 w-6" />
                Sign in with a passkey
              </button>
            )}
            <p className="flex items-center justify-center gap-1.5 text-xs font-bold text-muted md:justify-start">
              <Icon name="shield" className="h-4 w-4 text-primary" /> 2-step verification is required for every account
            </p>
            <p className="text-center text-xs font-semibold text-muted md:text-left">
              By continuing you agree to our{" "}
              <Link href="/terms" className="btn-link">
                Terms
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="btn-link">
                Privacy Policy
              </Link>
              .
            </p>
            <ErrorNote>{error}</ErrorNote>

            {config?.devLogin && (
              <form onSubmit={devLogin} className="card mt-2 space-y-3 p-4 text-left">
                <p className="label">Developer login (local only)</p>
                <input className="input" type="email" required placeholder="you@example.com" value={dev.email} onChange={(e) => setDev({ ...dev, email: e.target.value })} />
                <input className="input" required maxLength={60} placeholder="Display name" value={dev.name} onChange={(e) => setDev({ ...dev, name: e.target.value })} />
                <button className="btn-ghost w-full" disabled={busy}>
                  Dev sign in
                </button>
              </form>
            )}
          </div>
        </div>
      </section>

      <section className="border-y-2 border-line bg-surface/70">
        <div className="mx-auto flex max-w-6xl flex-wrap justify-center gap-3 px-4 py-6">
          {LANGS.map((l, i) => (
            <span key={l} className={`chip border-2 border-primary/30 bg-primary/10 text-primary ${CHIP_TINTS[i % CHIP_TINTS.length]}`}>
              {l}
            </span>
          ))}
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-5 px-4 py-16 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f0, i) => {
          const f = { ...f0, title: f0.title.replace("{buddy}", buddy), text: f0.text.replace("{buddy}", buddy) };
          return (
          <div key={f.title} className={`card card-accent p-6 ${CHIP_TINTS[(i * 2 + 1) % CHIP_TINTS.length]}`}>
            <span className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-primary/15 text-primary">
              <Icon name={f.icon} className="h-6 w-6" />
            </span>
            <h3 className="text-lg font-extrabold">{f.title}</h3>
            <p className="mt-1 text-sm text-muted">{f.text}</p>
          </div>
          );
        })}
      </section>

      <footer className="border-t-2 border-line py-8 text-center text-sm text-muted">
        © {new Date().getFullYear()} Codeingo · Learn to code, one lesson a day.
        <span className="mt-2 flex justify-center gap-4 font-bold">
          <Link href="/privacy" className="btn-link">
            Privacy
          </Link>
          <Link href="/terms" className="btn-link">
            Terms
          </Link>
        </span>
      </footer>
    </div>
  );
}
