"use client";

import { useSyncExternalStore } from "react";

/*
 * The API runs on a free host that falls asleep when nobody is using it and needs up to a minute to wake.
 * While that happens the website shows a "waking up" screen (components/WakingScreen.jsx), keeps asking the
 * server whether it is ready, and then carries on by itself. This module holds that state and does the waiting.
 */
const LIMIT_MS = 4 * 60 * 1000; // give up after four minutes
const POLL_MS = 2500;

let state = { waking: false, failed: false, startedAt: 0, checks: 0, last: "" };
let running = null;
const listeners = new Set();
const set = (next) => {
  state = { ...state, ...next };
  listeners.forEach((l) => l());
};

/** True when a response means "the server isn't up yet" (gateway errors, or the host's own HTML wake-up page). */
export function isWakeResponse(res, path = "") {
  if (!path.startsWith("/api")) return false;
  if ([502, 503, 504].includes(res.status)) return true;
  const type = res.headers.get("content-type") || "";
  return type.includes("text/html");
}

async function healthy() {
  let last = "no answer (network error)";
  let ok = false;
  try {
    // a timeout so one hung request (e.g. after the phone changed network) can't freeze the wait; the query string
    // keeps any proxy or CDN from replaying an old "bad gateway" answer
    const res = await fetch(`/api/health?t=${Date.now()}`, { cache: "no-store", credentials: "same-origin", signal: AbortSignal.timeout(8000) });
    const type = (res.headers.get("content-type") || "").split(";")[0] || "no content type";
    last = `${res.status} ${type}`;
    if (res.ok && !isWakeResponse(res, "/api/health")) {
      const data = await res.json().catch(() => null);
      ok = data?.status === "ok";
      if (!ok) last += " (unexpected reply)";
    }
  } catch {}
  set({ checks: state.checks + 1, last }); // shown on the waking screen so a stuck wait can be diagnosed
  return ok;
}

/** Shows the waking screen and resolves once the server answers /api/health. Rejects if it never does. */
export function ensureAwake() {
  if (running) return running;
  const startedAt = Date.now();
  set({ waking: true, failed: false, startedAt, checks: 0, last: "" });
  let poke = () => {};
  const wake = () => poke(); // tab visible again / back online / focused: check right now instead of waiting
  if (typeof window !== "undefined") {
    window.addEventListener("online", wake);
    window.addEventListener("focus", wake);
    document.addEventListener("visibilitychange", wake);
  }
  running = (async () => {
    while (Date.now() - startedAt < LIMIT_MS) {
      if (await healthy()) {
        set({ waking: false, failed: false });
        return;
      }
      await new Promise((r) => {
        const t = setTimeout(r, POLL_MS);
        poke = () => (clearTimeout(t), r());
      });
    }
    set({ failed: true });
    throw new Error("The server isn't responding right now. Please try again in a minute.");
  })().finally(() => {
    running = null;
    if (typeof window !== "undefined") {
      window.removeEventListener("online", wake);
      window.removeEventListener("focus", wake);
      document.removeEventListener("visibilitychange", wake);
    }
  });
  return running;
}

/** Resolves once the API is up (shows the waking screen if it was asleep). Use before leaving the site for a full-page /api navigation. */
export async function whenAwake() {
  if (await healthy()) return;
  await ensureAwake();
}

/** "Try again" on the failed screen. */
export function retryWake() {
  return ensureAwake().catch(() => {});
}

export function useWakeState() {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => state,
    () => state,
  );
}
