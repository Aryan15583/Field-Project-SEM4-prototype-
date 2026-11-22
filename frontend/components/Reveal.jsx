"use client";

import { motion, useReducedMotion, useScroll, useSpring, useTransform } from "motion/react";
import { Fragment } from "react";

/** Starts quickly and glides to a stop (easeOutQuint). Long durations with this curve read as "premium", not "slow". */
export const PREMIUM_EASE = [0.22, 1, 0.36, 1];

/**
 * Slowly moves its content into place as it scrolls into view: up (y > 0, the default) or down (y < 0),
 * fading in on the way. Runs once. People who asked their device for less motion get a plain fade
 * (the app's MotionConfig turns movement off).
 */
export default function Reveal({ children, y = 56, delay = 0, duration = 1.1, amount = 0.15, className }) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount, margin: "0px 0px -6% 0px" }}
      transition={{ duration, delay, ease: PREMIUM_EASE }}
    >
      {children}
    </motion.div>
  );
}

/** One piece of text that slides up out of a clipping mask (a headline "writing itself" in). */
export function Word({ children, delay = 0, duration = 1.1, className = "" }) {
  return (
    // pb/-mb keep letters like g and y from being clipped by the mask without changing the line height
    <span className="inline-block overflow-hidden pb-[0.14em] align-bottom -mb-[0.14em]">
      <motion.span
        className={`inline-block ${className}`}
        initial={{ y: "115%" }}
        animate={{ y: 0 }}
        transition={{ duration, delay, ease: PREMIUM_EASE }}
      >
        {children}
      </motion.span>
    </span>
  );
}

/** A sentence whose words rise one after another. */
export function Words({ children, delay = 0, step = 0.075, duration = 1.1 }) {
  const words = String(children).split(" ");
  return words.map((w, i) => (
    <Fragment key={i}>
      <Word delay={delay + i * step} duration={duration}>
        {w}
      </Word>
      {i < words.length - 1 && " "}
    </Fragment>
  ));
}

/** Moves slower than the page as you scroll (a depth effect), smoothed by a spring so it never jitters. */
export function Parallax({ children, distance = 80, className }) {
  const reduce = useReducedMotion();
  const { scrollY } = useScroll();
  const raw = useTransform(scrollY, [0, 900], [0, distance]); // positive: it trails behind the page
  const y = useSpring(raw, { stiffness: 90, damping: 24, mass: 0.6 });
  return (
    <motion.div className={className} style={reduce ? undefined : { y }}>
      {children}
    </motion.div>
  );
}

/** A thin line across the top that fills as you scroll down the page. */
export function ScrollProgress() {
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 120, damping: 28, mass: 0.4 });
  if (reduce) return null;
  return <motion.div aria-hidden style={{ scaleX }} className="fixed inset-x-0 top-0 z-50 h-[3px] origin-left bg-primary" />;
}
