"use client";

import { useSyncExternalStore } from "react";

/*
 * The API runs on a free host that falls asleep when nobody is using it and needs up to a minute to wake.
 * While that happens the website shows a "waking up" screen (components/WakingScreen.jsx), keeps asking the
 * server whether it is ready, and then carries on by itself. This module holds that state and does the waiting.
 */
// The wait is capped at one minute: after that the screen says it is taking longer and offers "Try again" (which starts
// another minute). A cold start of the free host takes about 30-60 s.
const LIMIT_MS = 60 * 1000;
// true: the full loading screen (with the game) while the server wakes - the page waits for it.
// false: the page stays visible and only a small notice shows (see WakingScreen). Callers can still choose per call.
const BLOCK_PAGE_WHILE_WAKING = true;
const POLL_MS = 2500;

// blocking: a full-screen wait (the user clicked something that needs the server right now). Otherwise the page stays
// visible and usable and only a small notice shows - the data simply arrives when the server does.
let state = { waking: false, failed: false, startedAt: 0, checks: 0, last: "", blocking: false };
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
const wakeTimeout = () => Object.assign(new Error("The server is taking longer than a minute to wake up. Please try again."), { wake: true });

export function ensureAwake(blocking = BLOCK_PAGE_WHILE_WAKING, force = false) {
  // After the minute is up we stay on "taking longer" until the learner presses Try again (force): other requests that
  // fail meanwhile must not quietly start another wait behind their back.
  if (state.failed && !force) return Promise.reject(wakeTimeout());
  if (running) {
    if (blocking && !state.blocking) set({ blocking: true }); // someone now really needs it: promote the notice to the full screen
    return running;
  }
  const startedAt = Date.now();
  set({ waking: true, failed: false, startedAt, checks: 0, last: "", blocking });
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
        set({ waking: false, failed: false, blocking: false });
        return;
      }
      await new Promise((r) => {
        const t = setTimeout(r, POLL_MS);
        poke = () => (clearTimeout(t), r());
      });
    }
    set({ failed: true });
    throw wakeTimeout();
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

/** Resolves once the API is up (full-screen wait if it was asleep). Use before leaving the site for a full-page /api navigation. */
export async function whenAwake() {
  if (await healthy()) return;
  await ensureAwake(true);
}

/** "Try again" on the failed screen. */
export function retryWake() {
  // once the server answers, load the page afresh so every part of it asks again (the calls that gave up are not resumed)
  return ensureAwake(true, true)
    .then(() => typeof window !== "undefined" && window.location.reload())
    .catch(() => {});
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
