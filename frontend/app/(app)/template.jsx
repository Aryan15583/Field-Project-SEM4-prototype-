"use client";

import { motion } from "motion/react";
import { PREMIUM_EASE } from "@/components/Reveal";

/** Re-mounts on every navigation inside the app shell: the page rises gently into place (transform/opacity only).
 *  Lessons are outside this layout on purpose - answering stays instant there. */
export default function Template({ children }) {
  return (
    <motion.div initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: PREMIUM_EASE }}>
      {children}
    </motion.div>
  );
}
