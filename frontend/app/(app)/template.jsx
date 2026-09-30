"use client";

import { motion } from "motion/react";

/** Re-mounts on every navigation inside the app shell: a quick fade + rise (transform/opacity only). */
export default function Template({ children }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22, ease: [0.2, 0.8, 0.2, 1] }}>
      {children}
    </motion.div>
  );
}
