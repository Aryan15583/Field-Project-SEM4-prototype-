"use client";

import { useSyncExternalStore } from "react";

/*
 * The API runs on a free host that falls asleep when nobody is using it and needs up to a minute to wake.
 * While that happens the website shows a "waking up" screen (components/WakingScreen.jsx), keeps asking the
 * server whether it is ready, and then carries on by itself. This module holds that state and does the waiting.
 */
const LIMIT_MS = 4 * 60 * 1000; // give up after four minutes
const POLL_MS = 2500;

let state = { waking: false, failed: false, startedAt: 0 };
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
  try {
    const res = await fetch("/api/health", { cache: "no-store", credentials: "same-origin" });
    if (!res.ok || isWakeResponse(res, "/api/health")) return false;
    const data = await res.json().catch(() => null);
    return data?.status === "ok";
  } catch {
    return false;
  }
}

/** Shows the waking screen and resolves once the server answers /api/health. Rejects if it never does. */
export function ensureAwake() {
  if (running) return running;
  const startedAt = Date.now();
  set({ waking: true, failed: false, startedAt });
  running = (async () => {
    while (Date.now() - startedAt < LIMIT_MS) {
      if (await healthy()) {
        set({ waking: false, failed: false });
        return;
      }
      await new Promise((r) => setTimeout(r, POLL_MS));
    }
    set({ failed: true });
    throw new Error("The server isn't responding right now. Please try again in a minute.");
  })().finally(() => {
    running = null;
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
