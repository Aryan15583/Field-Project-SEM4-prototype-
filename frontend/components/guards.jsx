"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import NotFoundView from "./NotFoundView";
import { Spinner } from "./ui";

/** Client-side route guards. The API enforces every permission itself - these only steer the UI. */
export function RequireAuth({ children, admin = false }) {
  const { status, user } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (status === "anon") router.replace("/");
  }, [status, router]);
  if (status !== "authed") return <Spinner />;
  // admin pages are hidden: everyone else sees the ordinary 404 page, as if /admin didn't exist
  if (admin && user.role !== "admin") return <NotFoundView />;
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
