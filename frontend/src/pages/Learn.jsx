import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorNote, Icon, Mascot, ProgressBar, Spinner } from "../components/ui";

const COURSE_KEY = "cg_course";

function savedCourse() {
  try {
    return localStorage.getItem(COURSE_KEY) || "python";
  } catch {
    return "python";
  }
}

// Winding path offsets, Duolingo-style
const OFFSETS = [0, 44, 72, 44, 0, -44, -72, -44];

function LessonNode({ lesson, index, isCurrent }) {
  const navigate = useNavigate();
  const locked = lesson.status === "locked";
  const done = lesson.status === "completed";
  return (
    <div className="relative flex flex-col items-center" style={{ transform: `translateX(${OFFSETS[index % OFFSETS.length]}px)` }}>
      {isCurrent && (
        <span className="mb-2 animate-bob rounded-xl border-2 border-line bg-raised px-3 py-1 text-xs font-black uppercase tracking-wider text-primary">
          Start
        </span>
      )}
      <button
        type="button"
        disabled={locked}
        onClick={() => navigate(`/lesson/${lesson.id}`)}
        aria-label={`${lesson.title} - ${lesson.status}`}
        title={lesson.title}
        className={`grid h-[72px] w-[72px] place-items-center rounded-full transition active:translate-y-1 ${
          locked ? "cursor-not-allowed bg-line text-muted" : "bg-primary text-on-primary hover:brightness-110"
        } ${isCurrent ? "ring-8 ring-primary/20" : ""}`}
        style={{ boxShadow: locked ? "0 6px 0 rgb(var(--muted) / .35)" : "0 6px 0 rgb(var(--primary-strong))" }}
      >
        <Icon name={locked ? "lock" : done ? "check" : "star"} className="h-8 w-8" />
      </button>
      <span className={`mt-3 max-w-[9rem] text-center text-xs font-bold ${locked ? "text-muted" : "text-ink"}`}>{lesson.title}</span>
    </div>
  );
}

export default function Learn() {
  const { user } = useAuth();
  const [courses, setCourses] = useState(null);
  const [slug, setSlug] = useState(savedCourse);
  const [path, setPath] = useState(null);
  const [daily, setDaily] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/courses").then(setCourses).catch((e) => setError(e.message));
    api("/api/daily").then(setDaily).catch(() => {});
  }, []);

  useEffect(() => {
    setPath(null);
    try {
      localStorage.setItem(COURSE_KEY, slug);
    } catch {
      /* ignore */
    }
    api(`/api/courses/${encodeURIComponent(slug)}`)
      .then(setPath)
      .catch((e) => (e.status === 404 ? setSlug("python") : setError(e.message)));
  }, [slug]);

  const all = path?.units.flatMap((u) => u.lessons) ?? [];
  const currentId = all.find((l) => l.status === "unlocked")?.id;
  const course = courses?.find((c) => c.slug === slug);

  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-8 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className="min-w-0">
        {/* course picker */}
        <div className="-mx-4 mb-6 flex gap-2 overflow-x-auto px-4 pb-2" role="tablist" aria-label="Courses">
          {(courses || []).map((c) => (
            <button
              key={c.slug}
              role="tab"
              aria-selected={c.slug === slug}
              onClick={() => setSlug(c.slug)}
              className={`chip shrink-0 border-2 ${c.slug === slug ? "border-primary bg-primary/10 text-primary" : "border-line text-muted hover:bg-surface"}`}
            >
              <span aria-hidden="true">{c.icon}</span> {c.title}
            </button>
          ))}
        </div>
        <ErrorNote>{error}</ErrorNote>

        {!path ? (
          <Spinner label="Loading your path" />
        ) : (
          path.units.map((unit, ui) => {
            const offset = path.units.slice(0, ui).reduce((n, u) => n + u.lessons.length, 0);
            return (
              <section key={unit.id} className="mb-12">
                <div className="mb-8 flex items-center justify-between rounded-3xl bg-primary p-5 text-on-primary" style={{ boxShadow: "0 5px 0 rgb(var(--primary-strong))" }}>
                  <div>
                    <p className="text-xs font-black uppercase tracking-widest opacity-80">
                      {path.icon} {path.title}
                    </p>
                    <h2 className="text-xl font-black">{unit.title}</h2>
                  </div>
                  <Icon name="code" className="h-8 w-8 opacity-70" />
                </div>
                <div className="flex flex-col items-center gap-7">
                  {unit.lessons.map((l, li) => (
                    <LessonNode key={l.id} lesson={l} index={offset + li} isCurrent={l.id === currentId} />
                  ))}
                </div>
              </section>
            );
          })
        )}
        {path && all.every((l) => l.status === "completed") && (
          <div className="card flex flex-col items-center p-8 text-center">
            <Mascot size={100} />
            <h3 className="mt-3 text-xl font-black">Course complete! 🎉</h3>
            <p className="text-muted">Pick another language above or replay lessons for practice XP.</p>
          </div>
        )}
      </div>

      {/* right rail */}
      <aside className="space-y-5">
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-extrabold">Daily goal</h3>
            <span className="text-sm font-bold text-muted">
              {Math.min(user.xp_today, user.daily_goal)}/{user.daily_goal} XP
            </span>
          </div>
          <ProgressBar value={user.xp_today} max={user.daily_goal} />
          <p className="mt-3 flex items-center gap-2 text-sm text-muted">
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
              <Link to="/daily" className="btn-primary w-full">
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
            <p className="mb-3 text-sm text-muted">{course.description}</p>
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
