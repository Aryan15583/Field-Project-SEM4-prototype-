"use client";

import { useEffect, useState } from "react";
import { DEFAULT_MASCOT, MASCOT_IDS } from "./mascots";

// Mascots take turns: each time a mascot appears (a new page, a new result screen) it is the next one
// from a shuffled deck, so learners see Codi, then someone else, then another friend - never the same
// one twice in a row. Server render and the first paint always use Codi (so hydration matches); the
// real pick is made right after mount.
let deck = [];
let last = null;

function nextMascot() {
  if (!deck.length) {
    deck = [...MASCOT_IDS];
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    if (deck[deck.length - 1] === last && deck.length > 1) [deck[0], deck[deck.length - 1]] = [deck[deck.length - 1], deck[0]];
  }
  last = deck.pop();
  return last;
}

/** A mascot id that stays the same for the lifetime of the component and changes on the next appearance. */
export function useRandomMascot(enabled = true) {
  const [id, setId] = useState(DEFAULT_MASCOT);
  useEffect(() => {
    if (enabled) setId(nextMascot());
  }, [enabled]);
  return id;
}
