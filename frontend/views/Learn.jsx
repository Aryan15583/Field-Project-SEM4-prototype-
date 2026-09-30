"use client";

import { AnimatePresence, motion } from "motion/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ErrorNote, Icon, Mascot, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const COURSE_KEY = "cg_course";
// Winding path offsets (px), Duolingo-style
const OFFSETS = [0, 45, 70, 45, 0, -45, -70, -45];

function readCourse() {
  try {
    return localStorage.getItem(COURSE_KEY) || "python";
  } catch {
    return "python";
  }
}

/* ---------------------------------------------------------------- path node + popover */
function LessonNode({ lesson, index, number, total, isCurrent, open, onToggle, nodeRef }) {
  const router = useRouter();
  const locked = lesson.status === "locked";
  const done = lesson.status === "completed";
  const x = OFFSETS[index % OFFSETS.length];

  return (
    <motion.div
      ref={nodeRef}
      className={`relative flex flex-col items-center ${open ? "z-30" : ""}`}
      data-path-node
      style={{ x }}
      initial={{ opacity: 0, scale: 0.6 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: Math.min(index, 10) * 0.04, type: "spring", stiffness: 420, damping: 24 }}
    >
      {isCurrent && !open && (
        <span className="absolute -top-[52px] z-10 animate-bob rounded-xl border-2 border-line bg-raised px-3 py-1.5 text-sm font-black uppercase tracking-wider text-primary">
          Start
          <span className="absolute -bottom-[7px] left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-b-2 border-r-2 border-line bg-raised" />
        </span>
      )}

      <div className="relative">
        {isCurrent && (
          // progress ring around the current lesson
          <svg className="pointer-events-none absolute -inset-[10px] h-[calc(100%+20px)] w-[calc(100%+20px)]" viewBox="0 0 100 100" aria-hidden="true">
            <circle cx="50" cy="50" r="46" fill="none" strokeWidth="7" className="stroke-line" />
          </svg>
        )}
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={open}
          aria-label={`${lesson.title} - ${lesson.status}`}
          title={lesson.title}
          className={`node ${locked ? "bg-line text-muted" : done ? "bg-gold text-white" : "bg-primary text-on-primary"}`}
          style={{ "--node-lip": locked ? "rgb(var(--muted) / .35)" : done ? "#c98a00" : "rgb(var(--primary-strong))" }}
        >
          <Icon name={locked ? "lock" : done ? "check" : "star"} className="h-9 w-9" />
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            className="absolute top-[90px] z-20 w-72"
            style={{ x: -x / 2 }}
            initial={{ opacity: 0, scale: 0.85, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -6 }}
            transition={{ type: "spring", stiffness: 520, damping: 32 }}
          >
            <div className={`relative rounded-2xl p-4 ${locked ? "border-2 border-line bg-raised" : done ? "bg-gold" : "bg-primary"}`}>
              <span
                className={`absolute -top-[7px] left-1/2 h-3.5 w-3.5 -translate-x-1/2 rotate-45 ${locked ? "border-l-2 border-t-2 border-line bg-raised" : done ? "bg-gold" : "bg-primary"}`}
                style={{ marginLeft: x / 2 }}
              />
              <p className={`text-lg font-black ${locked ? "text-ink" : "text-on-primary"}`}>{lesson.title}</p>
              <p className={`mb-4 text-sm font-bold ${locked ? "text-muted" : "text-on-primary/80"}`}>
                {locked ? "Complete all lessons above to unlock this!" : `Lesson ${number} of ${total}`}
              </p>
              {locked ? (
                <button className="btn-disabled w-full" disabled>
                  Locked
                </button>
              ) : (
                <button
                  className="btn w-full bg-raised text-primary"
                  style={{ boxShadow: "0 4px 0 rgb(0 0 0 / .18)" }}
                  onClick={() => router.push(`/lesson/${lesson.id}`)}
                  autoFocus
                >
                  {done ? "Practice +5 XP" : `Start +${lesson.xp} XP`}
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function PathSkeleton() {
  return (
    <div aria-busy="true">
      <div className="skeleton mb-10 h-24 w-full rounded-3xl" />
      <div className="flex flex-col items-center gap-9">
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton h-[70px] w-[76px] rounded-full" style={{ transform: `translateX(${OFFSETS[i]}px)` }} />
        ))}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------- page */
export default function Learn() {
  const { user } = useAuth();
  const [courses, setCourses] = useState(null);
  const [slug, setSlug] = useState(null);
  const [path, setPath] = useState(null);
  const [daily, setDaily] = useState(null);
  const [open, setOpen] = useState(null);
  const [error, setError] = useState("");
  const currentRef = useRef(null);
  const scrolledFor = useRef(null);

  useEffect(() => {
    setSlug(readCourse());
    api("/api/courses").then(setCourses).catch((e) => setError(e.message));
    api("/api/daily").then(setDaily).catch(() => {});
  }, []);

  useEffect(() => {
    if (!slug) return;
    setOpen(null);
    try {
      localStorage.setItem(COURSE_KEY, slug);
    } catch {
      /* ignore */
    }
    let alive = true;
    api(`/api/courses/${encodeURIComponent(slug)}`)
      .then((p) => alive && setPath(p))
      .catch((e) => (e.status === 404 ? setSlug("python") : setError(e.message)));
    return () => {
      alive = false;
    };
  }, [slug]);

  // Close the popover when tapping anywhere else. (The App Router mounts React on `document`,
  // so stopPropagation can't shield this listener - check the target instead. Taps on a node or
  // its popover are handled by the node itself.)
  useEffect(() => {
    if (open == null) return;
    const onDown = (e) => !e.target.closest?.("[data-path-node]") && setOpen(null);
    const onKey = (e) => e.key === "Escape" && setOpen(null);
    document.addEventListener("pointerdown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const all = path?.units.flatMap((u) => u.lessons) ?? [];
  const currentId = all.find((l) => l.status === "unlocked")?.id;
  const course = courses?.find((c) => c.slug === slug);

  // glide to the lesson you're on (once per course)
  useEffect(() => {
    if (!path || scrolledFor.current === path.slug) return;
    scrolledFor.current = path.slug;
    const el = currentRef.current;
    if (el && el.getBoundingClientRect().top > window.innerHeight * 0.6) {
      requestAnimationFrame(() => el.scrollIntoView({ behavior: "smooth", block: "center" }));
    }
  }, [path]);

  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div className="min-w-0">
        {/* course picker */}
        <div className="-mx-4 mb-6 flex gap-2 overflow-x-auto px-4 pb-2 [scrollbar-width:none]" role="tablist" aria-label="Courses">
          {(courses || Array.from({ length: 5 }, () => null)).map((c, i) =>
            c ? (
              <button
                key={c.slug}
                role="tab"
                aria-selected={c.slug === slug}
                onClick={() => (c.slug !== slug ? (setPath(null), setSlug(c.slug)) : null)}
                className={`chip shrink-0 border-2 border-b-4 transition-colors active:translate-y-[2px] ${
                  c.slug === slug ? "border-primary bg-primary/10 text-primary" : "border-line text-muted hover:bg-surface"
                }`}
              >
                <span aria-hidden="true">{c.icon}</span> {c.title}
              </button>
            ) : (
              <div key={i} className="skeleton h-9 w-28 shrink-0 rounded-xl" />
            ),
          )}
        </div>
        <ErrorNote>{error}</ErrorNote>

        {!path ? (
          <PathSkeleton />
        ) : (
          <motion.div key={path.slug} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
            {path.units.map((unit, ui) => {
              const offset = path.units.slice(0, ui).reduce((n, u) => n + u.lessons.length, 0);
              return (
                <section key={unit.id} className="mb-14">
                  {/* sticky unit banner, like Duolingo's section header */}
                  <div
                    className="sticky top-[76px] z-10 mb-14 flex items-center justify-between rounded-2xl bg-primary px-5 py-4 text-on-primary"
                    style={{ boxShadow: "0 5px 0 rgb(var(--primary-strong))" }}
                  >
                    <div>
                      <p className="text-xs font-black uppercase tracking-widest opacity-80">
                        {path.icon} {path.title} · Unit {ui + 1}
                      </p>
                      <h2 className="text-xl font-black">{unit.title.replace(/^Unit \d+ · /, "")}</h2>
                    </div>
                    <Icon name="code" className="h-8 w-8 opacity-70" />
                  </div>
                  <div className="relative flex flex-col items-center gap-[60px]">
                    {unit.lessons.map((l, li) => {
                      const idx = offset + li;
                      return (
                        <LessonNode
                          key={l.id}
                          lesson={l}
                          index={idx}
                          number={idx + 1}
                          total={all.length}
                          isCurrent={l.id === currentId}
                          open={open === l.id}
                          onToggle={() => setOpen(open === l.id ? null : l.id)}
                          nodeRef={l.id === currentId ? currentRef : undefined}
                        />
                      );
                    })}
                    {/* Codi hangs out beside the path */}
                    <Mascot size={96} mood={ui % 2 ? "think" : "happy"} className={`pointer-events-none absolute top-6 hidden animate-bob sm:block ${ui % 2 ? "left-[8%]" : "right-[8%]"}`} />
                  </div>
                </section>
              );
            })}
            {all.length > 0 && all.every((l) => l.status === "completed") && (
              <div className="card flex flex-col items-center p-8 text-center">
                <Mascot size={100} />
                <h3 className="mt-3 text-xl font-black">Course complete! 🎉</h3>
                <p className="font-semibold text-muted">Pick another language above or replay lessons for practice XP.</p>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* right rail */}
      <aside className="space-y-5 lg:sticky lg:top-[88px] lg:self-start">
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-extrabold">Daily goal</h3>
            <span className="text-sm font-bold text-muted">
              {Math.min(user.xp_today, user.daily_goal)}/{user.daily_goal} XP
            </span>
          </div>
          <ProgressBar value={user.xp_today} max={user.daily_goal} />
          <p className="mt-3 flex items-center gap-2 text-sm font-semibold text-muted">
            <Icon name="flame" className="h-5 w-5 text-flame" />
            {user.streak > 0 ? `${user.streak}-day streak - keep it going!` : "Complete a lesson to start a streak."}
          </p>
        </div>

        {daily?.exercise && (
          <div className="card p-5">
            <p className="label mb-1">Daily challenge · {daily.course}</p>
            <p className="mb-4 font-bold">{daily.exercise.prompt}</p>
            {daily.answered ? (
              <p className={`text-sm font-extrabold ${daily.correct ? "text-ok" : "text-muted"}`}>
                {daily.correct ? `✓ Solved! +${daily.bonus_xp} XP` : "Answered - come back tomorrow!"}
              </p>
            ) : (
              <Link href="/daily" className="btn-primary w-full">
                Solve for +{daily.bonus_xp} XP
              </Link>
            )}
          </div>
        )}

        {course && (
          <div className="card p-5">
            <h3 className="mb-2 font-extrabold">
              {course.icon} {course.title}
            </h3>
            <p className="mb-3 text-sm font-semibold text-muted">{course.description}</p>
            <ProgressBar value={course.completed} max={course.lessons} className="h-3" />
            <p className="mt-2 text-xs font-bold text-muted">
              {course.completed} of {course.lessons} lessons
            </p>
          </div>
        )}
      </aside>
    </div>
  );
}
