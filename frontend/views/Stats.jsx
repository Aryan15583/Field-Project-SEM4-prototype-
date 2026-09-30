"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ErrorNote, Icon, Spinner } from "@/components/ui";
import { chartColors, useTheme } from "@/lib/theme";

function StatTile({ icon, tone, value, label }) {
  return (
    <div className="card flex items-center gap-3 p-4">
      <Icon name={icon} className={`h-8 w-8 ${tone}`} />
      <div>
        <p className="text-2xl font-black leading-none">{value}</p>
        <p className="mt-1 text-xs font-bold text-muted">{label}</p>
      </div>
    </div>
  );
}

function ChartTooltip({ active, payload, label, unit }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border-2 border-line bg-raised px-3 py-2 text-sm shadow-lg">
      <p className="font-bold text-muted">{label}</p>
      <p className="font-black text-ink">
        {payload[0].value} {unit}
      </p>
    </div>
  );
}

function DataTable({ rows, cols }) {
  return (
    <details className="mt-3 text-sm">
      <summary className="btn-link cursor-pointer text-xs">View as table</summary>
      <table className="mt-2 w-full text-left">
        <thead>
          <tr className="text-muted">
            {cols.map(([, label]) => (
              <th key={label} className="py-1 font-bold">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t border-line">
              {cols.map(([k]) => (
                <td key={k} className="py-1">
                  {r[k]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}

export default function Stats() {
  const { user } = useAuth();
  const { dark } = useTheme();
  const c = chartColors(dark);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/stats").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorNote>{error}</ErrorNote>;
  if (!data) return <Spinner label="Crunching your numbers" />;

  const axis = { stroke: c.axis, fontSize: 12, tickLine: false, axisLine: false };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-black">Your progress</h1>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatTile icon="flame" tone="text-flame" value={user.streak} label="Day streak" />
        <StatTile icon="bolt" tone="text-gold" value={user.xp_total} label="Total XP" />
        <StatTile icon="check" tone="text-primary" value={data.lessons_completed} label="Lessons done" />
        <StatTile icon="star" tone="text-primary" value={user.streak_best} label="Best streak" />
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <section className="card p-5 lg:col-span-3">
          <h2 className="font-extrabold">XP earned · last 14 days</h2>
          <div className="mt-4 h-60">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.xp_by_day} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="xpFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={c.primary} stopOpacity={0.35} />
                    <stop offset="100%" stopColor={c.primary} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke={c.grid} strokeDasharray="3 3" />
                <XAxis dataKey="day" {...axis} interval="preserveStartEnd" minTickGap={24} />
                <YAxis {...axis} allowDecimals={false} />
                <Tooltip content={<ChartTooltip unit="XP" />} cursor={{ stroke: c.axis, strokeDasharray: "3 3" }} />
                <Area type="monotone" dataKey="xp" stroke={c.primary} strokeWidth={2} fill="url(#xpFill)" activeDot={{ r: 5, stroke: c.surface, strokeWidth: 2 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <DataTable rows={data.xp_by_day} cols={[["day", "Day"], ["xp", "XP"]]} />
        </section>

        <section className="card p-5 lg:col-span-2">
          <h2 className="font-extrabold">Lessons by language</h2>
          {data.lessons_by_course.length === 0 ? (
            <p className="mt-6 text-sm text-muted">Finish a lesson to see it here.</p>
          ) : (
            <>
              <div className="mt-4 h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.lessons_by_course} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }} barCategoryGap={8}>
                    <CartesianGrid horizontal={false} stroke={c.grid} strokeDasharray="3 3" />
                    <XAxis type="number" {...axis} allowDecimals={false} />
                    <YAxis type="category" dataKey="course" {...axis} width={90} />
                    <Tooltip content={<ChartTooltip unit="lessons" />} cursor={{ fill: c.grid, opacity: 0.4 }} />
                    <Bar dataKey="lessons" fill={c.primary} radius={[0, 4, 4, 0]} maxBarSize={22} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <DataTable rows={data.lessons_by_course} cols={[["course", "Language"], ["lessons", "Lessons"]]} />
            </>
          )}
        </section>
      </div>

      <section>
        <h2 className="mb-3 text-xl font-black">Achievements</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {data.badges.map((b) => (
            <div key={b.key} className={`card p-4 text-center ${b.earned ? "" : "opacity-45 grayscale"}`}>
              <div className="text-4xl" aria-hidden="true">
                {b.icon}
              </div>
              <p className="mt-2 font-extrabold">{b.name}</p>
              <p className="text-xs text-muted">{b.desc}</p>
              <p className="mt-1 text-[11px] font-bold uppercase text-primary">{b.earned ? "Unlocked" : "Locked"}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
