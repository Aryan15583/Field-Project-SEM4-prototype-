"use client";

import { motion } from "motion/react";

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
