"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

/** Registers the service worker and keeps the browser's "install this app" prompt for our own button. */
const PwaContext = createContext({ canInstall: false, installed: false, ios: false, install: async () => false });

export function PwaProvider({ children }) {
  const [deferred, setDeferred] = useState(null);
  const [installed, setInstalled] = useState(false);
  const [ios, setIos] = useState(false);

  useEffect(() => {
    if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
      navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
    }
    const standalone = matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
    setInstalled(standalone);
    // iOS Safari has no install prompt - people add it from the Share menu instead
    setIos(/iphone|ipad|ipod/i.test(navigator.userAgent) && !standalone);

    const onPrompt = (e) => {
      e.preventDefault(); // keep it for the button instead of the browser's mini-infobar
      setDeferred(e);
    };
    const onInstalled = () => {
      setInstalled(true);
      setDeferred(null);
    };
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  const install = useCallback(async () => {
    if (!deferred) return false;
    deferred.prompt();
    const { outcome } = await deferred.userChoice;
    setDeferred(null);
    return outcome === "accepted";
  }, [deferred]);

  return <PwaContext.Provider value={{ canInstall: !!deferred && !installed, installed, ios, install }}>{children}</PwaContext.Provider>;
}

export const usePwa = () => useContext(PwaContext);
