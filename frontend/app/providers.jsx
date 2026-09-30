"use client";

import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/lib/theme";

export default function Providers({ children }) {
  return (
    <ThemeProvider>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  );
}
