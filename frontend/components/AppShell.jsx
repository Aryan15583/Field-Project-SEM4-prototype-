"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Icon, Logo, StatPill, ThemeToggle } from "./ui";

const NAV = [
  { to: "/learn", label: "Learn", icon: "learn" },
  { to: "/daily", label: "Daily", icon: "target" },
  { to: "/leaderboard", label: "Leagues", icon: "trophy" },
  { to: "/stats", label: "Progress", icon: "chart" },
  { to: "/profile", label: "Profile", icon: "user" },
];

function NavLink({ to, className, children, pill }) {
  const pathname = usePathname();
  const isActive = pathname === to || pathname.startsWith(`${to}/`);
  return (
    <Link href={to} className={`relative ${className({ isActive })}`} aria-current={isActive ? "page" : undefined}>
      {isActive && pill && (
        // one highlight that glides between items (shared layout animation, transform-only)
        <motion.span layoutId={pill} className="absolute inset-0 rounded-2xl border-2 border-primary/50 bg-primary/10" transition={{ type: "spring", stiffness: 500, damping: 38 }} />
      )}
      {pill ? <span className="relative flex items-center gap-4">{children}</span> : children}
    </Link>
  );
}

function navClass({ isActive }) {
  return `flex items-center gap-4 rounded-2xl px-4 py-3 text-sm font-extrabold uppercase tracking-wide transition-colors ${
    isActive ? "text-primary" : "text-muted hover:bg-surface hover:text-ink"
  }`;
}

export function UserStats() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <div className="flex items-center gap-1">
      <StatPill icon="flame" value={user.streak} tone="flame" label="Day streak" />
      <StatPill icon="bolt" value={user.xp_total} tone="gold" label="Total XP" />
      <StatPill icon="heart" value={user.hearts} tone="bad" label="Hearts" />
    </div>
  );
}

export default function AppShell({ children }) {
  const { user } = useAuth();
  const items = user?.role === "admin" ? [...NAV, { to: "/admin", label: "Admin", icon: "shield" }] : NAV;

  return (
    <div className="min-h-screen bg-bg text-ink">
      {/* desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r-2 border-line px-4 py-6 lg:flex">
        <Logo className="mb-8 px-3" />
        <nav className="flex flex-1 flex-col gap-2" aria-label="Main">
          {items.map((n) => (
            <NavLink key={n.to} to={n.to} className={navClass} pill="side-pill">
              <Icon name={n.icon} className="h-6 w-6" />
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center justify-between px-2">
          <span className="label">Theme</span>
          <ThemeToggle />
        </div>
      </aside>

      {/* top bar */}
      <header className="sticky top-0 z-30 border-b-2 border-line bg-bg/90 backdrop-blur lg:ml-64">
        <div className="mx-auto flex h-16 max-w-5xl 3xl:max-w-6xl items-center justify-between px-4">
          <Logo compact className="text-xl lg:hidden" />
          <span className="hidden lg:block" />
          <div className="flex items-center gap-2">
            <UserStats />
            <ThemeToggle className="lg:hidden" />
          </div>
        </div>
      </header>

      <main className="overflow-x-clip px-4 pb-28 pt-6 lg:ml-64 lg:pb-10">
        <div className="mx-auto max-w-5xl 3xl:max-w-6xl">
          {children}
        </div>
      </main>

      {/* mobile bottom nav */}
      <nav className="fixed inset-x-0 bottom-0 z-30 flex justify-around border-t-2 border-line bg-bg py-2 lg:hidden" aria-label="Main">
        {items.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            className={({ isActive }) =>
              `flex min-w-0 flex-1 flex-col items-center gap-0.5 rounded-xl py-1 text-[0.625rem] font-extrabold uppercase ${isActive ? "text-primary" : "text-muted"}`
            }
          >
            <Icon name={n.icon} className="h-6 w-6" />
            {n.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
