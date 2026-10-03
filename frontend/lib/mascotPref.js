"use client";

import { useSyncExternalStore } from "react";
import { DEFAULT_MASCOT, MASCOT_IDS } from "./mascots";

// The learner's chosen mascot, remembered in this browser. Server render and first paint use the
// default, then the saved choice is applied (useSyncExternalStore avoids a hydration mismatch).
const KEY = "codeingo.mascot";
const listeners = new Set();

function read() {
  try {
    const v = window.localStorage.getItem(KEY);
    return MASCOT_IDS.includes(v) ? v : DEFAULT_MASCOT;
  } catch {
    return DEFAULT_MASCOT;
  }
}
function subscribe(fn) {
  listeners.add(fn);
  window.addEventListener("storage", fn);
  return () => {
    listeners.delete(fn);
    window.removeEventListener("storage", fn);
  };
}

export function setMascot(id) {
  if (!MASCOT_IDS.includes(id)) return;
  try {
    window.localStorage.setItem(KEY, id);
  } catch {}
  listeners.forEach((fn) => fn());
}

export const useMascotId = () => useSyncExternalStore(subscribe, read, () => DEFAULT_MASCOT);
