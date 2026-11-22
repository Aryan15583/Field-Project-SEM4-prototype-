"use client";

import Lenis from "lenis";
import { useEffect } from "react";

/**
 * Eased, inertial scrolling for the public landing page: wheel and trackpad scrolling glides to a stop instead of
 * stepping. Touch scrolling stays native (it already has momentum). Skipped for people who asked for less motion.
 * Only the landing page mounts this - lessons and the app keep ordinary scrolling (editors and panels scroll natively).
 */
export default function SmoothScroll() {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const lenis = new Lenis({
      duration: 1.4, // how long a scroll takes to settle
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // fast start, long soft landing
      wheelMultiplier: 0.9,
    });
    let frame = requestAnimationFrame(function loop(time) {
      lenis.raf(time);
      frame = requestAnimationFrame(loop);
    });
    return () => {
      cancelAnimationFrame(frame);
      lenis.destroy();
    };
  }, []);
  return null;
}
