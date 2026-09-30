import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, ensureCsrf } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | authed | anon

  const reload = useCallback(async () => {
    try {
      await ensureCsrf();
      const me = await api("/api/auth/me");
      setUser(me);
      setStatus("authed");
      return me;
    } catch {
      setUser(null);
      setStatus("anon");
      return null;
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const logout = useCallback(async (everywhere = false) => {
    try {
      await api(everywhere ? "/api/auth/logout-all" : "/api/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
      setStatus("anon");
    }
  }, []);

  return <AuthContext.Provider value={{ user, setUser, status, reload, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
