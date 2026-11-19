"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, clearCache, ensureCsrf } from "./api";

const AuthContext = createContext(null);

// The last profile this device saw. It lets a returning learner's app frame paint at once, while a sleeping server
// wakes up; the real answer replaces it as soon as it arrives (and a 401 clears it). It is only for drawing the
// page - the API still decides everything, and the sign-in cookie is not readable by scripts.
const SNAPSHOT = "cg_me";
const readSnapshot = () => {
  try {
    const v = JSON.parse(localStorage.getItem(SNAPSHOT));
    return v && typeof v === "object" && v.id ? v : null;
  } catch {
    return null;
  }
};
const saveSnapshot = (me) => {
  try {
    localStorage.setItem(SNAPSHOT, JSON.stringify(me));
  } catch {
    /* private mode / full storage: just no head start next time */
  }
};
const dropSnapshot = () => {
  try {
    localStorage.removeItem(SNAPSHOT);
  } catch {
    /* ignore */
  }
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | authed | anon

  const reload = useCallback(async () => {
    // Only a real "not signed in" (401) shows the sign-in page. A sleeping or briefly unreachable server
    // must not look like a logout, so other errors are retried before giving up.
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        await ensureCsrf();
        const me = await api("/api/auth/me");
        setUser(me);
        setStatus("authed");
        saveSnapshot(me);
        return me;
      } catch (e) {
        if (e?.status === 401 || e?.status === 403) break;
        if (e?.wake) return null; // still waking after a minute: not a logout. The loading screen offers "Try again" (a fresh load).
        await new Promise((r) => setTimeout(r, 3000));
      }
    }
    dropSnapshot();
    setUser(null);
    setStatus("anon");
    return null;
  }, []);

  useEffect(() => {
    const known = readSnapshot(); // after hydration, so the server HTML and the first client render still match
    if (known) {
      setUser(known);
      setStatus("authed");
    }
    reload();
  }, [reload]);

  const logout = useCallback(async (everywhere = false) => {
    try {
      clearCache();
      await api(everywhere ? "/api/auth/logout-all" : "/api/auth/logout", { method: "POST" });
    } finally {
      dropSnapshot();
      setUser(null);
      setStatus("anon");
    }
  }, []);

  return <AuthContext.Provider value={{ user, setUser, status, reload, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
