"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, clearCache, ensureCsrf } from "./api";

const AuthContext = createContext(null);

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
        return me;
      } catch (e) {
        if (e?.status === 401 || e?.status === 403) break;
        await new Promise((r) => setTimeout(r, 3000));
      }
    }
    setUser(null);
    setStatus("anon");
    return null;
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const logout = useCallback(async (everywhere = false) => {
    try {
      clearCache();
      await api(everywhere ? "/api/auth/logout-all" : "/api/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
      setStatus("anon");
    }
  }, []);

  return <AuthContext.Provider value={{ user, setUser, status, reload, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
