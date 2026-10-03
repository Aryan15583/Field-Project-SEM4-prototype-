"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);

function read() {
  try {
    return localStorage.getItem("cg_theme") || "system";
  } catch {
    return "system";
  }
}

const media = () => window.matchMedia("(prefers-color-scheme: dark)");

export function ThemeProvider({ children }) {
  // Browser-only values are read after mount: this component also renders on the server.
  // Until then, the <html> class set by the bootstrap script in app/layout.jsx is the truth.
  const [mounted, setMounted] = useState(false);
  const [mode, setModeState] = useState("system"); // "system" | "light" | "dark"
  const [systemDark, setSystemDark] = useState(false);

  useEffect(() => {
    const m = media();
    setModeState(read());
    setSystemDark(m.matches);
    setMounted(true);
    const onChange = (e) => setSystemDark(e.matches);
    m.addEventListener("change", onChange);
    return () => m.removeEventListener("change", onChange);
  }, []);

  const dark = mode === "dark" || (mode === "system" && systemDark);

  useEffect(() => {
    if (mounted) document.documentElement.classList.toggle("dark", dark);
  }, [dark, mounted]);

  const setMode = useCallback((m) => {
    setModeState(m);
    try {
      localStorage.setItem("cg_theme", m);
    } catch {
      /* private mode - theme just won't persist */
    }
  }, []);

  const toggle = useCallback(() => setMode(dark ? "light" : "dark"), [dark, setMode]);

  return <ThemeContext.Provider value={{ mode, dark, setMode, toggle }}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);

/** Concrete colours for SVG charts (Recharts can't resolve CSS variables in attributes). */
export function chartColors(dark) {
  return dark
    ? { primary: "#16a34a", teal: "#2dd4bf", grid: "#203025", axis: "#8aa596", surface: "#101712", ink: "#e8f5ec", gold: "#facc15" }
    : { primary: "#1d6ff2", teal: "#0f766e", grid: "#dbe4f5", axis: "#525b6e", surface: "#ffffff", ink: "#0a0a0a", gold: "#f5b00b" };
}
