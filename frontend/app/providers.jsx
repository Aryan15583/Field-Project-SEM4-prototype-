"use client";

import { MotionConfig } from "motion/react";
import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/lib/theme";

export default function Providers({ children }) {
  return (
    // reducedMotion="user": springs/slides become instant for people who asked their OS for less motion
    <MotionConfig reducedMotion="user">
      <ThemeProvider>
        <AuthProvider>{children}</AuthProvider>
      </ThemeProvider>
    </MotionConfig>
  );
}
