"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { usePwa } from "@/lib/pwa";
import { Icon, Logo, StatPill, ThemeToggle } from "./ui";

// each section has its own colour (a .tint-* class re-colours "primary" inside it - see globals.css)
const NAV = [
  { to: "/learn", label: "Learn", icon: "learn", tint: "" },
  { to: "/daily", label: "Daily", icon: "target", tint: "tint-orange" },
  { to: "/practice", label: "Practice", icon: "review", tint: "tint-violet" },
  { to: "/leaderboard", label: "Leagues", icon: "trophy", tint: "tint-gold" },
  { to: "/contests", label: "Contests", icon: "bolt", tint: "tint-pink", desktopOnly: true }, // phones reach it from Leagues
  { to: "/stats", label: "Progress", icon: "chart", tint: "tint-teal" },
  { to: "/profile", label: "Profile", icon: "user", tint: "tint-sky" },
];

function NavLink({ to, tint = "", className, children, pill }) {
  const pathname = usePathname();
  const isActive = pathname === to || pathname.startsWith(`${to}/`);
  return (
    <Link href={to} className={`relative ${tint} ${className({ isActive })}`} aria-current={isActive ? "page" : undefined}>
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
    <div className="flex items-center gap-0.5 sm:gap-1 [&_.chip]:px-2 [&_.chip]:py-1 sm:[&_.chip]:px-3 sm:[&_.chip]:py-1.5">
      {user.debug && (
        <span className="chip bg-gold/20 text-ink" title="Admin debug mode: everything unlocked, nothing is saved">
          DEBUG
        </span>
      )}
      <StatPill icon="flame" value={user.streak} tone="flame" label="Day streak" infinite={user.debug} />
      <StatPill icon="bolt" value={user.xp_total} tone="gold" label="Total XP" infinite={user.debug} />
      <StatPill icon="heart" value={user.hearts} tone="bad" label="Hearts" infinite={user.debug} />
    </div>
  );
}

function InstallButton() {
  const { canInstall, install } = usePwa();
  if (!canInstall) return null;
  return (
    <button onClick={install} className="btn-ghost mb-4 w-full text-sm">
      Install the app
    </button>
  );
}

export default function AppShell({ children }) {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const items = isAdmin ? [...NAV, { to: "/admin", label: "Admin", icon: "shield", tint: "tint-red" }] : NAV;

  return (
    <div className="min-h-screen text-ink">
      {/* desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r-2 border-line px-4 py-6 lg:flex">
        <Logo className="mb-8 px-3" />
        <nav className="flex flex-1 flex-col gap-2" aria-label="Main">
          {items.map((n) => (
            <NavLink key={n.to} to={n.to} tint={n.tint} className={navClass} pill="side-pill">
              <Icon name={n.icon} className="h-6 w-6 text-primary" />
              {n.label}
            </NavLink>
          ))}
        </nav>
        <InstallButton />
        <div className="flex items-center justify-between px-2">
          <span className="label">Theme</span>
          <ThemeToggle />
        </div>
      </aside>

      {/* top bar */}
      <header className="sticky top-0 z-30 border-b-2 border-line bg-bg/90 pt-[env(safe-area-inset-top)] backdrop-blur lg:ml-64">
        <div className="mx-auto flex h-14 max-w-5xl 3xl:max-w-6xl items-center justify-between gap-2 px-3 sm:h-16 sm:px-4">
          <Logo compact className="text-xl lg:hidden" />
          <span className="hidden lg:block" />
          <div className="flex items-center gap-2">
            <UserStats />
            {isAdmin && (
              <Link href="/admin" aria-label="Admin" className="tint-red grid h-10 w-10 place-items-center rounded-xl text-primary hover:bg-surface lg:hidden">
                <Icon name="shield" className="h-6 w-6" />
              </Link>
            )}
            <ThemeToggle className="lg:hidden" />
          </div>
        </div>
      </header>

      <main className="overflow-x-clip px-4 pb-[calc(6.5rem+env(safe-area-inset-bottom))] pt-5 sm:pt-6 lg:ml-64 lg:pb-10">
        <div className="mx-auto max-w-5xl 3xl:max-w-6xl">
          {children}
        </div>
      </main>

      {/* mobile bottom nav: five tabs + profile, big tap targets, clear of the phone's home indicator */}
      <nav className="fixed inset-x-0 bottom-0 z-30 border-t-2 border-line bg-bg/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden" aria-label="Main">
        <div className="mx-auto flex max-w-xl items-stretch justify-around gap-0.5 px-1.5 py-1.5">
          {items.filter((n) => !n.desktopOnly && n.to !== "/admin").map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              tint={n.tint}
              className={({ isActive }) =>
                `flex min-h-[3.25rem] min-w-0 flex-1 flex-col items-center justify-center gap-0.5 rounded-2xl px-0.5 text-[0.6875rem] font-extrabold leading-none transition-colors ${
                  isActive ? "bg-primary/10 text-primary" : "text-muted active:bg-surface"
                }`
              }
            >
              <Icon name={n.icon} className="h-6 w-6" />
              <span className="max-w-full truncate">{n.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
