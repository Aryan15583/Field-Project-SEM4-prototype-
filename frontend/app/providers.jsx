"use client";

import { MotionConfig } from "motion/react";
import WakingScreen from "@/components/WakingScreen";
import { AuthProvider } from "@/lib/auth";
import { PwaProvider } from "@/lib/pwa";
import { ThemeProvider } from "@/lib/theme";

export default function Providers({ children }) {
  return (
    // reducedMotion="user": springs/slides become instant for people who asked their OS for less motion
    <MotionConfig reducedMotion="user">
      <ThemeProvider>
        <PwaProvider>
          <AuthProvider>{children}</AuthProvider>
          <WakingScreen />
        </PwaProvider>
      </ThemeProvider>
    </MotionConfig>
  );
}
