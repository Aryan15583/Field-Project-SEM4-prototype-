"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { Spinner } from "./ui";

/** Client-side route guards. The API enforces every permission itself - these only steer the UI. */
export function RequireAuth({ children, admin = false }) {
  const { status, user } = useAuth();
  const router = useRouter();
  const denied = status === "anon" || (status === "authed" && admin && user.role !== "admin");
  useEffect(() => {
    if (status === "anon") router.replace("/");
    else if (denied) router.replace("/learn");
  }, [status, denied, router]);
  if (status !== "authed" || denied) return <Spinner />;
  return children;
}

export function PublicOnly({ children }) {
  const { status } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (status === "authed") router.replace("/learn");
  }, [status, router]);
  if (status === "authed") return <Spinner />;
  return children; // public content renders (and server-renders) while the session check runs
}
