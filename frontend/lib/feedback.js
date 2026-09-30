"use client";

// Sound effects + haptics, synthesized with Web Audio (no audio files to download).
// Everything is a no-op on the server, when the user turned sounds off, or when unsupported.

const KEY = "cg_sound";
let ctx = null;

export function soundEnabled() {
  try {
    return localStorage.getItem(KEY) !== "off";
  } catch {
    return true;
  }
}

export function setSoundEnabled(on) {
  try {
    localStorage.setItem(KEY, on ? "on" : "off");
  } catch {
    /* private mode */
  }
}

function audio() {
  if (typeof window === "undefined" || !soundEnabled()) return null;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  ctx ??= new AC();
  if (ctx.state === "suspended") ctx.resume();
  return ctx;
}

function tone(ac, { freq, start = 0, dur = 0.15, type = "sine", gain = 0.18, slideTo }) {
  const t0 = ac.currentTime + start;
  const osc = ac.createOscillator();
  const g = ac.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, t0);
  if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, t0 + dur);
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime(gain, t0 + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  osc.connect(g).connect(ac.destination);
  osc.start(t0);
  osc.stop(t0 + dur + 0.02);
}

function vibrate(pattern) {
  try {
    if (soundEnabled()) navigator.vibrate?.(pattern);
  } catch {
    /* unsupported */
  }
}

export const sfx = {
  correct() {
    const ac = audio();
    if (ac) {
      tone(ac, { freq: 880, dur: 0.12, type: "triangle" });
      tone(ac, { freq: 1318.5, start: 0.09, dur: 0.22, type: "triangle" });
    }
    vibrate(15);
  },
  wrong() {
    const ac = audio();
    if (ac) {
      tone(ac, { freq: 220, dur: 0.18, type: "square", gain: 0.07, slideTo: 150 });
      tone(ac, { freq: 180, start: 0.12, dur: 0.22, type: "square", gain: 0.06, slideTo: 110 });
    }
    vibrate([30, 40, 30]);
  },
  tap() {
    const ac = audio();
    if (ac) tone(ac, { freq: 660, dur: 0.05, type: "sine", gain: 0.06 });
  },
  complete() {
    const ac = audio();
    if (ac) [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => tone(ac, { freq: f, start: i * 0.1, dur: 0.28, type: "triangle", gain: 0.16 }));
    vibrate([20, 60, 20, 60, 40]);
  },
};
