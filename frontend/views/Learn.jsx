"use client";

import { AnimatePresence, motion } from "motion/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { courseTint, ErrorNote, Icon, IconTile, Mascot, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const COURSE_KEY = "cg_course";
// Winding path offsets in rem (scale with the UI on big screens)
const OFFSETS = [0, 2.8, 4.4, 2.8, 0, -2.8, -4.4, -2.8];
const rem = (n) => `${n}rem`;
const SECTION_BLURB = {
  Beginner: "Syntax, variables, control flow and your first real programs.",
  Intermediate:
    "Data structures, deeper functions and objects, and handling errors.",
  Advanced: "Professional patterns, performance and classic algorithms.",
};

/** Groups consecutive units by their section, keeping per-section lesson counts. */
const UNIT_TINTS = ["", "tint-violet", "tint-pink", "tint-orange", "tint-teal", "tint-sky"];

function groupSections(units) {
  const sections = [];
  for (const u of units) {
    const name = u.section || "Beginner";
    let s = sections[sections.length - 1];
    if (!s || s.name !== name) {
      s = {
        name,
        id: `section-${sections.length + 1}`,
        number: sections.length + 1,
        units: [],
        total: 0,
        done: 0,
      };
      sections.push(s);
    }
    s.units.push(u);
    s.total += u.lessons.length;
    s.done += u.lessons.filter((l) => l.status === "completed").length;
  }
  return sections;
}

function SectionHeader({ section, jump, slug }) {
  const locked = section.units[0]?.lessons[0]?.status === "locked";
  const complete = section.total > 0 && section.done === section.total;
  return (
    <div
      id={section.id}
      className="card mb-10 scroll-mt-[6rem] overflow-hidden p-5"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="label mb-1">Section {section.number}</p>
          <h2 className="text-2xl font-black">{section.name}</h2>
          <p className="mt-1 text-sm font-semibold text-muted">
            {SECTION_BLURB[section.name] ?? ""}
          </p>
        </div>
        <span
          className={`chip shrink-0 border-2 ${complete ? "border-gold text-gold" : locked ? "border-line text-muted" : "border-primary text-primary"}`}
        >
          <Icon
            name={complete ? "check" : locked ? "lock" : "star"}
            className="h-4 w-4"
          />
          {complete ? "Complete" : locked ? "Locked" : "In progress"}
        </span>
      </div>
      <ProgressBar
        value={section.done}
        max={section.total}
        className="mt-4 h-3"
      />
      <p className="mt-2 text-xs font-bold text-muted">
        {section.done} of {section.total} lessons · {section.units.length} units
      </p>
      {jump?.status === "available" && (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border-2 border-dashed border-primary/40 bg-primary/5 p-3">
          <p className="min-w-0 flex-1 text-sm font-bold">
            Already know this? Pass a {jump.questions}-question readiness test ({jump.pass_mark} correct) to jump straight here.
          </p>
          <Link
            href={`/test?course=${encodeURIComponent(slug)}&section=${encodeURIComponent(section.name)}`}
            className="btn-primary shrink-0"
          >
            Jump here
          </Link>
        </div>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------- chapter test node */
function TestNode({ unit, slug, index, isCurrent, open, onToggle, nodeRef }) {
  const router = useRouter();
  const test = unit.test;
  const locked = test.status === "locked";
  const passed = test.status === "passed";
  const x = OFFSETS[index % OFFSETS.length];
  const name = unit.title.replace(/^Unit \d+ · /, "");
  return (
    <motion.div
      ref={nodeRef}
      className={`relative flex flex-col items-center ${open ? "z-30" : ""}`}
      data-path-node
      style={{ x: rem(x) }}
      initial={{ opacity: 0, scale: 0.6 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: Math.min(index, 10) * 0.04, type: "spring", stiffness: 420, damping: 24 }}
    >
      {isCurrent && !open && (
        <span className="absolute -top-[3.25rem] z-10 animate-bob whitespace-nowrap rounded-xl border-2 border-line bg-raised px-3 py-1.5 text-sm font-black uppercase tracking-wider text-gold">
          Chapter test
          <span className="absolute -bottom-[0.4375rem] left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-b-2 border-r-2 border-line bg-raised" />
        </span>
      )}
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-label={`Chapter test: ${name} - ${test.status}`}
        title={`Chapter test: ${name}`}
        className={`node ${locked ? "bg-line text-muted" : passed ? "bg-gold text-white" : "bg-gold text-white ring-4 ring-gold/30"}`}
        style={{ "--node-lip": locked ? "rgb(var(--muted) / .35)" : "#c98a00" }}
      >
        <Icon name={locked ? "lock" : passed ? "check" : "trophy"} className="h-9 w-9" />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            className="absolute top-[5.625rem] z-20 w-72"
            style={{ x: rem(-x / 2) }}
            initial={{ opacity: 0, scale: 0.85, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -6 }}
            transition={{ type: "spring", stiffness: 520, damping: 32 }}
          >
            <div className={`relative rounded-2xl p-4 ${locked ? "border-2 border-line bg-raised" : "bg-gold"}`}>
              <span
                className={`absolute -top-[0.4375rem] left-1/2 h-3.5 w-3.5 -translate-x-1/2 rotate-45 ${locked ? "border-l-2 border-t-2 border-line bg-raised" : "bg-gold"}`}
                style={{ marginLeft: rem(x / 2) }}
              />
              <p className={`text-lg font-black ${locked ? "text-ink" : "text-white"}`}>Chapter test · {name}</p>
              <p className={`mb-4 text-sm font-bold ${locked ? "text-muted" : "text-white/85"}`}>
                {locked
                  ? "Finish this unit's lessons to unlock its test."
                  : passed
                    ? "Passed! Retake it any time to practise."
                    : `${test.questions} questions · get ${test.pass_mark} right to unlock the next unit`}
              </p>
              {locked ? (
                <button className="btn-disabled w-full" disabled>
                  Locked
                </button>
              ) : (
                <button
                  className="btn w-full bg-raised text-gold"
                  style={{ boxShadow: "0 0.25rem 0 rgb(0 0 0 / .18)" }}
                  onClick={() => router.push(`/test?course=${encodeURIComponent(slug)}&unit=${unit.id}`)}
                  autoFocus
                >
                  {passed ? "Practice test" : `Take test +${test.xp} XP`}
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function readCourse() {
  try {
    return localStorage.getItem(COURSE_KEY) || "python";
  } catch {
    return "python";
  }
}

/* ---------------------------------------------------------------- path node + popover */
function LessonNode({
  lesson,
  index,
  number,
  total,
  isCurrent,
  open,
  onToggle,
  nodeRef,
}) {
  const router = useRouter();
  const locked = lesson.status === "locked";
  const done = lesson.status === "completed";
  const x = OFFSETS[index % OFFSETS.length];

  return (
    <motion.div
      ref={nodeRef}
      className={`relative flex flex-col items-center ${open ? "z-30" : ""}`}
      data-path-node
      style={{ x: rem(x) }}
      initial={{ opacity: 0, scale: 0.6 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        delay: Math.min(index, 10) * 0.04,
        type: "spring",
        stiffness: 420,
        damping: 24,
      }}
    >
      {isCurrent && !open && (
        <span className="absolute -top-[3.25rem] z-10 animate-bob rounded-xl border-2 border-line bg-raised px-3 py-1.5 text-sm font-black uppercase tracking-wider text-primary">
          Start
          <span className="absolute -bottom-[0.4375rem] left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-b-2 border-r-2 border-line bg-raised" />
        </span>
      )}

      <div className="relative">
        {isCurrent && (
          // progress ring around the current lesson
          <svg
            className="pointer-events-none absolute -inset-[0.625rem] h-[calc(100%+1.25rem)] w-[calc(100%+1.25rem)]"
            viewBox="0 0 100 100"
            aria-hidden="true"
          >
            <circle
              cx="50"
              cy="50"
              r="46"
              fill="none"
              strokeWidth="7"
              className="stroke-line"
            />
          </svg>
        )}
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={open}
          aria-label={`${lesson.title} - ${lesson.status}`}
          title={lesson.title}
          className={`node ${locked ? "bg-line text-muted" : done ? "bg-gold text-white" : "bg-primary text-on-primary"}`}
          style={{
            "--node-lip": locked
              ? "rgb(var(--muted) / .35)"
              : done
                ? "#c98a00"
                : "rgb(var(--primary-strong))",
          }}
        >
          <Icon
            name={locked ? "lock" : done ? "check" : lesson.project ? "code" : "star"}
            className="h-9 w-9"
          />
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            className="absolute top-[5.625rem] z-20 w-72"
            style={{ x: rem(-x / 2) }}
            initial={{ opacity: 0, scale: 0.85, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -6 }}
            transition={{ type: "spring", stiffness: 520, damping: 32 }}
          >
            <div
              className={`relative rounded-2xl p-4 ${locked ? "border-2 border-line bg-raised" : done ? "bg-gold" : "bg-primary"}`}
            >
              <span
                className={`absolute -top-[0.4375rem] left-1/2 h-3.5 w-3.5 -translate-x-1/2 rotate-45 ${locked ? "border-l-2 border-t-2 border-line bg-raised" : done ? "bg-gold" : "bg-primary"}`}
                style={{ marginLeft: rem(x / 2) }}
              />
              <p
                className={`text-lg font-black ${locked ? "text-ink" : "text-on-primary"}`}
              >
                {lesson.title}
              </p>
              <p
                className={`mb-4 text-sm font-bold ${locked ? "text-muted" : "text-on-primary/80"}`}
              >
                {locked
                  ? "Complete all lessons above to unlock this!"
                  : lesson.project
                    ? "Project · build something real in 3 steps"
                    : `Lesson ${number} of ${total}`}
              </p>
              {locked ? (
                <button className="btn-disabled w-full" disabled>
                  Locked
                </button>
              ) : (
                <button
                  className="btn w-full bg-raised text-primary"
                  style={{ boxShadow: "0 0.25rem 0 rgb(0 0 0 / .18)" }}
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
          <div
            key={i}
            className="skeleton h-[4.375rem] w-[4.75rem] rounded-full"
            style={{ transform: `translateX(${OFFSETS[i]}rem)` }}
          />
        ))}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------- page */
export default function Learn() {
  const { user } = useAuth();
  const [railOpen, setRailOpen] = useState(true); // the right-hand panel can be hidden (remembered in this browser)
  useEffect(() => {
    try {
      if (localStorage.getItem("cg_rail") === "0") setRailOpen(false);
    } catch {
      /* ignore */
    }
  }, []);
  const toggleRail = () =>
    setRailOpen((open) => {
      try {
        localStorage.setItem("cg_rail", open ? "0" : "1");
      } catch {
        /* ignore */
      }
      return !open;
    });
  const [courses, setCourses] = useState(null);
  const [slug, setSlug] = useState(null);
  const [path, setPath] = useState(null);
  const [daily, setDaily] = useState(null);
  const [practice, setPractice] = useState(null);
  const [open, setOpen] = useState(null);
  const [error, setError] = useState("");
  const currentRef = useRef(null);
  const scrolledFor = useRef(null);

  useEffect(() => {
    setSlug(readCourse());
    api("/api/courses")
      .then(setCourses)
      .catch((e) => setError(e.message));
    api("/api/daily")
      .then(setDaily)
      .catch(() => {});
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
    setPractice(null);
    api(`/api/practice/summary?course=${encodeURIComponent(slug)}`)
      .then((p) => alive && setPractice(p))
      .catch(() => {});
    api(`/api/courses/${encodeURIComponent(slug)}`)
      .then((p) => alive && setPath(p))
      .catch((e) =>
        e.status === 404 ? setSlug("python") : setError(e.message),
      );
    return () => {
      alive = false;
    };
  }, [slug]);

  // Close the popover when tapping anywhere else. (The App Router mounts React on `document`,
  // so stopPropagation can't shield this listener - check the target instead. Taps on a node or
  // its popover are handled by the node itself.)
  useEffect(() => {
    if (open == null) return;
    const onDown = (e) =>
      !e.target.closest?.("[data-path-node]") && setOpen(null);
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
  // when no lesson is open, the next step is the chapter test that unlocks the following unit
  const currentTestUnit = currentId
    ? null
    : path?.units.find((u, i) => u.test?.status === "unlocked" && (i + 1 === path.units.length || path.units[i + 1].lessons[0]?.status === "locked"))?.id;
  const course = courses?.find((c) => c.slug === slug);
  const sections = path ? groupSections(path.units) : [];

  // glide to the lesson you're on (once per course)
  useEffect(() => {
    if (!path || scrolledFor.current === path.slug) return;
    scrolledFor.current = path.slug;
    const el = currentRef.current;
    if (el && el.getBoundingClientRect().top > window.innerHeight * 0.6) {
      requestAnimationFrame(() =>
        el.scrollIntoView({ behavior: "smooth", block: "center" }),
      );
    }
  }, [path]);

  return (
    <div className={`grid grid-cols-[minmax(0,1fr)] gap-8 ${railOpen ? "lg:grid-cols-[minmax(0,1fr)_20rem]" : ""}`}>
      <div className="min-w-0">
        <div className="mb-3 flex justify-end">
          <button
            type="button"
            onClick={toggleRail}
            aria-expanded={railOpen}
            aria-controls="learn-side-panel"
            className="btn-ghost px-3 py-1.5 text-sm"
          >
            {railOpen ? "Hide side panel" : "Show side panel"}
          </button>
        </div>
        {/* course picker */}
        <div
          className="-mx-4 mb-6 flex gap-2 overflow-x-auto px-4 pb-3 [scrollbar-width:thin] sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0 sm:pb-0"
          role="tablist"
          aria-label="Courses"
        >
          {(courses || Array.from({ length: 5 }, () => null)).map((c, i) =>
            c ? (
              <button
                key={c.slug}
                role="tab"
                aria-selected={c.slug === slug}
                onClick={() =>
                  c.slug !== slug ? (setPath(null), setSlug(c.slug)) : null
                }
                className={`chip shrink-0 border-2 border-b-4 transition-colors active:translate-y-[0.125rem] ${courseTint(c.slug)} ${
                  c.slug === slug
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-line text-muted hover:border-primary/40 hover:bg-primary/5 hover:text-primary"
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
          <motion.div
            key={path.slug}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {path.units.map((unit, ui) => {
              const offset = path.units
                .slice(0, ui)
                .reduce((n, u) => n + u.lessons.length, 0);
              // path position for the zig-zag: every unit has its lessons plus a test node
              const slot = offset + ui;
              const startsSection = sections.find(
                (sec) => sec.units[0] === unit,
              );
              return (
                // every unit has its own colour, like Duolingo (re-colours its banner, nodes and bubbles)
                <section key={unit.id} className={`mb-14 ${UNIT_TINTS[ui % UNIT_TINTS.length]}`}>
                  {startsSection && (
                    <SectionHeader
                      section={startsSection}
                      jump={path.section_tests?.[startsSection.name]}
                      slug={path.slug}
                    />
                  )}
                  {/* sticky unit banner, like Duolingo's section header */}
                  <div
                    className="sticky top-[4.75rem] z-10 mb-14 flex items-center justify-between rounded-2xl bg-primary px-5 py-4 text-on-primary"
                    style={{
                      boxShadow: "0 0.3125rem 0 rgb(var(--primary-strong))",
                    }}
                  >
                    <div>
                      <p className="text-xs font-black uppercase tracking-widest opacity-80">
                        {path.icon} {unit.section || "Beginner"} · Unit {ui + 1}
                      </p>
                      <h2 className="text-xl font-black">
                        {unit.title.replace(/^Unit \d+ · /, "")}
                      </h2>
                    </div>
                    <Icon name="code" className="h-8 w-8 opacity-70" />
                  </div>
                  <div className="relative flex flex-col items-center gap-[3.75rem]">
                    {unit.lessons.map((l, li) => {
                      const idx = offset + li;
                      return (
                        <LessonNode
                          key={l.id}
                          lesson={l}
                          index={slot + li}
                          number={idx + 1}
                          total={all.length}
                          isCurrent={l.id === currentId}
                          open={open === l.id}
                          onToggle={() => setOpen(open === l.id ? null : l.id)}
                          nodeRef={l.id === currentId ? currentRef : undefined}
                        />
                      );
                    })}
                    {unit.test && (
                      <TestNode
                        unit={unit}
                        slug={path.slug}
                        index={slot + unit.lessons.length}
                        isCurrent={unit.id === currentTestUnit}
                        open={open === `test-${unit.id}`}
                        onToggle={() => setOpen(open === `test-${unit.id}` ? null : `test-${unit.id}`)}
                        nodeRef={unit.id === currentTestUnit ? currentRef : undefined}
                      />
                    )}
                    {/* Codi hangs out beside the path */}
                    <Mascot
                      size={104}
                      className={`absolute top-6 hidden sm:block ${ui % 2 ? "left-[8%]" : "right-[8%]"}`}
                    />
                  </div>
                </section>
              );
            })}
            {all.length > 0 && all.every((l) => l.status === "completed") && (
              <div className="card flex flex-col items-center p-8 text-center">
                <Mascot size={110} mood="celebrate" />
                <h3 className="mt-3 text-xl font-black">Course complete! 🎉</h3>
                <p className="font-semibold text-muted">
                  Pick another language above or replay lessons for practice XP.
                </p>
                <p className="mt-3 text-sm font-bold text-muted">
                  Pass every chapter test too, and your certificate appears on your{" "}
                  <Link href="/profile" className="btn-link">
                    Profile
                  </Link>
                  .
                </p>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* right rail */}
      <aside id="learn-side-panel" hidden={!railOpen} className="space-y-5 pr-1 lg:sticky lg:top-[5.5rem] lg:max-h-[calc(100vh-6.5rem)] lg:self-start lg:overflow-y-auto [scrollbar-width:thin]">
        <div className="card tint-orange card-accent p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="flex items-center gap-3 font-extrabold">
              <IconTile icon="target" size="sm" /> Daily goal
            </h3>
            <span className="text-sm font-bold text-muted">
              {Math.min(user.xp_today, user.daily_goal)}/{user.daily_goal} XP
            </span>
          </div>
          <ProgressBar value={user.xp_today} max={user.daily_goal} />
          <p className="mt-3 flex items-center gap-2 text-sm font-semibold text-muted">
            <Icon name="flame" className="h-5 w-5 text-flame" />
            {user.streak > 0
              ? `${user.streak}-day streak - keep it going!`
              : "Complete a lesson to start a streak."}
          </p>
        </div>

        {practice && (
          <div className="card tint-violet card-accent p-5">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="flex items-center gap-3 font-extrabold">
                <IconTile icon="review" size="sm" /> Practice
              </h3>
              {practice.due > 0 && <span className="chip border-2 border-flame text-flame">{practice.due} due</span>}
            </div>
            <p className="mb-4 text-sm font-semibold text-muted">
              {practice.total < 3
                ? "Finish a lesson - questions you miss will come back here."
                : practice.due > 0
                  ? `${practice.mistakes} mistake${practice.mistakes === 1 ? "" : "s"} to fix. Practice earns XP and a heart back.`
                  : "All caught up! A quick round keeps it fresh."}
            </p>
            {practice.total >= 3 && (
              <Link href={`/review?course=${encodeURIComponent(slug)}`} className={practice.due > 0 ? "btn-primary w-full" : "btn-ghost w-full"}>
                Practise +{practice.xp} XP
              </Link>
            )}
          </div>
        )}

        {daily?.exercise && (
          <div className="overflow-hidden rounded-3xl bg-primary p-5 text-on-primary shadow-[0_4px_0_rgb(var(--primary-strong))]">
            <p className="mb-1 flex items-center gap-2 text-xs font-black uppercase tracking-widest opacity-90">
              <Icon name="star" className="h-4 w-4" /> Daily challenge · {daily.course}
            </p>
            <p className="mb-4 font-bold">{daily.exercise.prompt}</p>
            {daily.answered ? (
              <p className="text-sm font-extrabold">
                {daily.correct
                  ? `✓ Solved! +${daily.bonus_xp} XP`
                  : "Answered - come back tomorrow!"}
              </p>
            ) : (
              <Link href="/daily" className="btn w-full bg-raised text-pink">
                Solve for +{daily.bonus_xp} XP
              </Link>
            )}
          </div>
        )}

        {course && (
          <div className="card card-accent p-5">
            <h3 className="mb-2 flex items-center gap-3 font-extrabold">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary/15 text-lg" aria-hidden="true">
                {course.icon}
              </span>
              {course.title}
            </h3>
            <p className="mb-3 text-sm font-semibold text-muted">
              {course.description}
            </p>
            <ProgressBar
              value={course.completed}
              max={course.lessons}
              className="h-3"
            />
            <p className="mt-2 text-xs font-bold text-muted">
              {course.completed} of {course.lessons} lessons
            </p>
          </div>
        )}

        {sections.length > 1 && (
          <nav className="card tint-teal card-accent p-5" aria-label="Course sections">
            <h3 className="mb-3 flex items-center gap-3 font-extrabold">
              <IconTile icon="chart" size="sm" /> Sections
            </h3>
            <ul className="space-y-3">
              {sections.map((sec) => (
                <li key={sec.id}>
                  <button
                    type="button"
                    className="w-full rounded-xl text-left transition-colors hover:bg-surface"
                    onClick={() =>
                      document
                        .getElementById(sec.id)
                        ?.scrollIntoView({ behavior: "smooth", block: "start" })
                    }
                  >
                    <span className="flex items-center justify-between text-sm font-extrabold">
                      <span>
                        {sec.number}. {sec.name}
                      </span>
                      <span className="text-muted">
                        {sec.done}/{sec.total}
                      </span>
                    </span>
                    <ProgressBar
                      value={sec.done}
                      max={sec.total}
                      className="mt-1.5 h-2"
                    />
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        )}
      </aside>
    </div>
  );
}
