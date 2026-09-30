"use client";

import { useEffect, useRef } from "react";

/** One-shot confetti burst on a single <canvas>: one draw call loop per frame, no DOM nodes per
 *  particle, so it holds 60 fps even on low-end phones. Skipped for prefers-reduced-motion. */
export default function Confetti({ colors, count = 140, duration = 2600 }) {
  const ref = useRef(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const canvas = ref.current;
    const c = canvas.getContext("2d");
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const resize = () => {
      canvas.width = innerWidth * dpr;
      canvas.height = innerHeight * dpr;
    };
    resize();
    window.addEventListener("resize", resize);

    const W = () => canvas.width;
    const H = () => canvas.height;
    const parts = Array.from({ length: count }, (_, i) => {
      const fromLeft = i % 2 === 0;
      const angle = (fromLeft ? -60 : -120) + (Math.random() * 30 - 15);
      const speed = (12 + Math.random() * 10) * dpr;
      return {
        x: fromLeft ? 0 : W(),
        y: H() * 0.75,
        vx: Math.cos((angle * Math.PI) / 180) * speed,
        vy: Math.sin((angle * Math.PI) / 180) * speed,
        w: (6 + Math.random() * 6) * dpr,
        h: (10 + Math.random() * 8) * dpr,
        rot: Math.random() * Math.PI,
        vr: (Math.random() - 0.5) * 0.3,
        color: colors[i % colors.length],
      };
    });

    let raf;
    const t0 = performance.now();
    const frame = (now) => {
      const t = now - t0;
      c.clearRect(0, 0, W(), H());
      c.globalAlpha = t > duration - 600 ? Math.max(0, (duration - t) / 600) : 1;
      for (const p of parts) {
        p.vy += 0.35 * dpr; // gravity
        p.vx *= 0.985; // drag
        p.vy *= 0.985;
        p.x += p.vx;
        p.y += p.vy;
        p.rot += p.vr;
        c.save();
        c.translate(p.x, p.y);
        c.rotate(p.rot);
        c.fillStyle = p.color;
        c.fillRect(-p.w / 2, (-p.h / 2) * Math.abs(Math.cos(p.rot * 2)), p.w, p.h * Math.abs(Math.cos(p.rot * 2)) + 1);
        c.restore();
      }
      if (t < duration) raf = requestAnimationFrame(frame);
      else c.clearRect(0, 0, W(), H());
    };
    raf = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, [colors, count, duration]);

  return <canvas ref={ref} className="pointer-events-none fixed inset-0 z-50 h-full w-full" aria-hidden="true" />;
}
