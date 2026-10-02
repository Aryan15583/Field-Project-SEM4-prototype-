"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Logo, Mascot, Spinner } from "@/components/ui";
import { api } from "@/lib/api";

/** Public, printable certificate. Anyone with the link can verify it - no sign-in needed. */
export default function Certificate({ code }) {
  const [cert, setCert] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api(`/api/public/certificates/${encodeURIComponent(code)}`)
      .then(setCert)
      .catch((e) => setError(e.status === 404 ? "We couldn't find a certificate with this code." : e.message));
  }, [code]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard blocked - the address bar still has the link */
    }
  };

  if (error)
    return (
      <div className="grid min-h-screen place-items-center bg-bg p-6 text-center text-ink">
        <div>
          <Mascot size={110} mood="sad" className="mx-auto" />
          <p className="my-5 text-lg font-bold">{error}</p>
          <Link href="/" className="btn-primary">
            Go to Codeingo
          </Link>
        </div>
      </div>
    );
  if (!cert) return <Spinner />;

  const date = new Date(cert.issued_at).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="min-h-screen bg-surface px-4 py-8 text-ink print:bg-white print:p-0">
      <div className="mx-auto max-w-4xl">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 print:hidden">
          <Link href="/">
            <Logo />
          </Link>
          <div className="flex flex-wrap gap-2">
            <button className="btn-ghost" onClick={copy}>
              {copied ? "Link copied!" : "Copy link"}
            </button>
            <button className="btn-primary" onClick={() => window.print()}>
              Print / save as PDF
            </button>
          </div>
        </div>

        <article
          className="relative overflow-hidden rounded-3xl border-[0.375rem] border-primary bg-white p-8 text-center text-neutral-900 shadow-xl sm:p-14 print:rounded-none print:shadow-none"
          aria-label={`Certificate: ${cert.name} completed ${cert.course}`}
        >
          <div className="pointer-events-none absolute inset-3 rounded-2xl border-2 border-primary/30 print:rounded-none" aria-hidden="true" />
          <div className="flex justify-center">
            <Logo />
          </div>
          <p className="mt-8 text-sm font-black uppercase tracking-[0.3em] text-primary">Certificate of completion</p>
          <p className="mt-6 font-semibold text-neutral-600">This certifies that</p>
          <h1 className="mt-2 break-words text-4xl font-black sm:text-5xl">{cert.name}</h1>
          <p className="mx-auto mt-5 max-w-xl text-lg font-semibold text-neutral-700">
            has completed the <strong className="text-neutral-900">{cert.course}</strong> course on Codeingo - {cert.lessons} lessons from
            beginner to advanced, three hands-on projects, and every chapter test.
          </p>
          <div className="mt-10 grid gap-6 text-sm sm:grid-cols-3">
            <div>
              <p className="font-black text-neutral-900">{date}</p>
              <p className="font-semibold text-neutral-500">Date issued</p>
            </div>
            <div className="flex justify-center">
              <Mascot size={84} mood="celebrate" interactive={false} />
            </div>
            <div>
              <p className="break-all font-mono font-bold text-neutral-900">{cert.code}</p>
              <p className="font-semibold text-neutral-500">Verification code</p>
            </div>
          </div>
          <p className="mt-8 break-all text-xs font-semibold text-neutral-500">Verify at {typeof window === "undefined" ? "" : window.location.href}</p>
        </article>

        <p className="mt-5 text-center text-sm font-semibold text-muted print:hidden">
          Anyone with this link can verify the certificate. It shows only the holder's display name.
        </p>
      </div>
    </div>
  );
}
