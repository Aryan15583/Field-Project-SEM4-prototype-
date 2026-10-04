"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorNote, Modal, PageTitle, Spinner } from "@/components/ui";
import { useAuth } from "@/lib/auth";

const TEMPLATE = (unitId) =>
  JSON.stringify(
    {
      unit_id: unitId,
      title: "New lesson",
      intro: "Explain the concept here.",
      xp_reward: 10,
      exercises: [
        { kind: "mcq", prompt: "Question?", code: null, data: { options: ["A", "B"] }, solution: { index: 0 }, explanation: "", hint: "" },
        { kind: "fill", prompt: "Fill the blank", code: "print(___)", data: {}, solution: { accepted: ["1"] }, explanation: "", hint: "" },
        { kind: "order", prompt: "Order these", code: null, data: { lines: ["first", "second"] }, solution: {}, explanation: "", hint: "" },
        { kind: "code", prompt: "Write code", code: null, data: { starter: "" }, solution: { patterns: ["^print\\(1\\)$"], example: "print(1)" }, explanation: "", hint: "" },
      ],
    },
    null,
    2,
  );

function Content() {
  const [tree, setTree] = useState(null);
  const [editing, setEditing] = useState(null); // { id|null, json }
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  const load = useCallback(() => api("/api/admin/tree").then(setTree).catch((e) => setError(e.message)), []);
  useEffect(() => {
    load();
  }, [load]);

  const open = async (id) => {
    setError("");
    setMsg("");
    const l = await api(`/api/admin/lessons/${id}`);
    const { id: _, ...body } = l;
    setEditing({ id, json: JSON.stringify(body, null, 2) });
  };

  const save = async () => {
    setError("");
    setMsg("");
    let body;
    try {
      body = JSON.parse(editing.json);
    } catch {
      return setError("Invalid JSON");
    }
    try {
      const res = editing.id
        ? await api(`/api/admin/lessons/${editing.id}`, { method: "PUT", body })
        : await api("/api/admin/lessons", { method: "POST", body });
      setEditing({ ...editing, id: res.id });
      setMsg("Saved");
      load();
    } catch (e) {
      setError(e.data?.errors ? e.data.errors.map((x) => `${x.loc?.join(".")}: ${x.msg}`).join("\n") : e.message);
    }
  };

  const remove = async () => {
    if (!editing?.id || !window.confirm("Delete this lesson permanently?")) return;
    await api(`/api/admin/lessons/${editing.id}`, { method: "DELETE" });
    setEditing(null);
    load();
  };

  if (!tree) return <Spinner />;
  return (
    <div className="grid gap-6 lg:grid-cols-[17.5rem_1fr]">
      <div className="card max-h-[70vh] overflow-y-auto p-4 text-sm">
        {tree.map((c) => (
          <div key={c.id} className="mb-4">
            <p className="font-black">{c.title}</p>
            {c.units.map((u) => (
              <div key={u.id} className="ml-2 mt-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-muted">{u.title}</span>
                  <button className="btn-link text-xs" onClick={() => setEditing({ id: null, json: TEMPLATE(u.id) })}>
                    + lesson
                  </button>
                </div>
                {u.lessons.map((l) => (
                  <button key={l.id} onClick={() => open(l.id)} className={`block w-full rounded-lg px-2 py-1 text-left hover:bg-surface ${editing?.id === l.id ? "text-primary" : ""}`}>
                    {l.title}
                  </button>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
      <div>
        {editing ? (
          <div className="space-y-3">
            <p className="label">{editing.id ? `Editing lesson #${editing.id}` : "New lesson"}</p>
            <textarea
              className="input h-[55vh] font-mono text-xs"
              spellCheck={false}
              value={editing.json}
              onChange={(e) => setEditing({ ...editing, json: e.target.value })}
              aria-label="Lesson JSON"
            />
            {error && <pre className="whitespace-pre-wrap rounded-2xl bg-bad/10 p-3 text-xs font-bold text-bad">{error}</pre>}
            {msg && <p className="text-sm font-bold text-primary">{msg}</p>}
            <div className="flex gap-2">
              <button className="btn-primary" onClick={save}>
                Save
              </button>
              {editing.id && (
                <button className="btn-bad" onClick={remove}>
                  Delete
                </button>
              )}
            </div>
          </div>
        ) : (
          <p className="text-muted">Select a lesson to edit, or add a new one. Answers are validated server-side; code exercises use regex patterns (user code is never executed).</p>
        )}
      </div>
    </div>
  );
}

function ConfirmRole({ target, onDone, onCancel }) {
  const [info, setInfo] = useState(null);
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const makeAdmin = target.role !== "admin";

  useEffect(() => {
    api("/api/admin/confirm-code", { method: "POST" })
      .then(setInfo)
      .catch((e) => setError(e.message));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api(`/api/admin/users/${target.id}/role`, { method: "POST", body: { role: makeAdmin ? "admin" : "learner", code: code.replace(/\s/g, "") } });
      onDone();
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <h2 className="text-xl font-black">{makeAdmin ? "Give admin access?" : "Remove admin access?"}</h2>
      <p className="font-semibold text-muted">
        <strong className="text-ink">{target.name}</strong> ({target.email}){" "}
        {makeAdmin ? "will be able to edit lessons, disable users and grant admin access." : "will become a normal learner again."}
      </p>
      <p className="text-sm font-semibold">
        {info?.method === "email"
          ? `Confirm it's you: enter the code we just emailed to ${info.sent_to}.`
          : info?.method === "totp"
            ? "Confirm it's you: enter the 6-digit code from your authenticator app."
            : "Sending a confirmation code…"}
      </p>
      <input
        className="input text-center font-mono text-2xl tracking-[0.4em]"
        inputMode="numeric"
        autoComplete="one-time-code"
        maxLength={8}
        value={code}
        onChange={(e) => setCode(e.target.value)}
        aria-label="Confirmation code"
        autoFocus
      />
      <ErrorNote>{error}</ErrorNote>
      <div className="flex gap-2">
        <button type="button" className="btn-ghost flex-1" onClick={onCancel}>
          Cancel
        </button>
        <button className={`${makeAdmin ? "btn-primary" : "btn-bad"} flex-1`} disabled={busy || code.replace(/\s/g, "").length < 6}>
          {makeAdmin ? "Make admin" : "Remove admin"}
        </button>
      </div>
    </form>
  );
}

function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState(null);
  const [q, setQ] = useState("");
  const [error, setError] = useState("");
  const [roleFor, setRoleFor] = useState(null);
  const load = useCallback(
    (query = "") =>
      api(`/api/admin/users${query ? `?q=${encodeURIComponent(query)}` : ""}`)
        .then(setUsers)
        .catch((e) => setError(e.message)),
    [],
  );
  useEffect(() => {
    load();
  }, [load]);
  const toggle = async (u) => {
    setError("");
    try {
      await api(`/api/admin/users/${u.id}/active`, { method: "POST", body: { active: !u.active } });
      load(q);
    } catch (e) {
      setError(e.message);
    }
  };
  if (!users) return <Spinner />;
  return (
    <div className="space-y-4">
      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          load(q.trim());
        }}
      >
        <input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name or email" aria-label="Search users" maxLength={120} />
        <button className="btn-primary shrink-0">Search</button>
      </form>
      <p className="text-sm font-semibold text-muted">
        Admins can edit lessons and manage users. Owners (the emails in ADMIN_EMAILS on the server) are always admins and can't be removed here. Every change
        needs your 2-step code and is written to the audit log.
      </p>
      <ErrorNote>{error}</ErrorNote>
      <div className="card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-muted">
            <tr>
              {["User", "Role", "XP", "2FA", "Last login", "", ""].map((h, i) => (
                <th key={i} className="px-4 py-3 font-bold">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const self = u.id === me?.id;
              return (
                <tr key={u.id} className="border-t-2 border-line">
                  <td className="px-4 py-3">
                    <p className="font-bold">
                      {u.name} {self && <span className="text-xs text-muted">(you)</span>}
                    </p>
                    <p className="text-xs text-muted">{u.email}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`chip text-xs ${u.role === "admin" ? "bg-primary/10 text-primary" : "text-muted"}`}>{u.owner ? "owner" : u.role}</span>
                  </td>
                  <td className="px-4 py-3">{u.xp}</td>
                  <td className="px-4 py-3">{u.mfa ? "✓" : "-"}</td>
                  <td className="px-4 py-3 text-xs">{u.last_login_at ? new Date(u.last_login_at).toLocaleString() : "never"}</td>
                  <td className="px-4 py-3">
                    {!self && !u.owner && (u.role === "admin" || (u.active && u.mfa)) && (
                      <button className={u.role === "admin" ? "btn-link text-bad" : "btn-link"} onClick={() => setRoleFor(u)}>
                        {u.role === "admin" ? "Remove admin" : "Make admin"}
                      </button>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {!self && !u.owner && (
                      <button className={u.active ? "btn-link text-bad" : "btn-link"} onClick={() => toggle(u)}>
                        {u.active ? "Disable" : "Enable"}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <Modal open={!!roleFor} onClose={() => setRoleFor(null)} label="Change admin access">
        {roleFor && (
          <ConfirmRole
            key={roleFor.id}
            target={roleFor}
            onCancel={() => setRoleFor(null)}
            onDone={() => {
              setRoleFor(null);
              load(q.trim());
            }}
          />
        )}
      </Modal>
    </div>
  );
}

function Audit() {
  const [rows, setRows] = useState(null);
  useEffect(() => {
    api("/api/admin/audit?limit=200").then(setRows);
  }, []);
  if (!rows) return <Spinner />;
  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-muted">
          <tr>
            {["Time", "Event", "User", "IP", "Detail"].map((h) => (
              <th key={h} className="px-4 py-3 font-bold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="font-mono">
          {rows.map((r) => (
            <tr key={r.id} className={`border-t border-line ${/fail|reuse|locked|blocked/.test(r.event) ? "text-bad" : ""}`}>
              <td className="whitespace-nowrap px-4 py-2">{new Date(r.at).toLocaleString()}</td>
              <td className="px-4 py-2">{r.event}</td>
              <td className="px-4 py-2">{r.user_id ?? "-"}</td>
              <td className="px-4 py-2">{r.ip}</td>
              <td className="max-w-xs truncate px-4 py-2" title={r.detail}>
                {r.detail}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Admin-only: unlock everything and play with unlimited hearts. Nothing is saved while it is on. */
function Debug() {
  const { user, setUser } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const toggle = async (on) => {
    setBusy(true);
    setError("");
    try {
      setUser(await api("/api/admin/debug", { method: "POST", body: { on } }));
    } catch (e) {
      setError(/not found/i.test(e.message) ? "The server doesn't know debug mode yet - redeploy the API on Render (it updates from GitHub), wait until it is live, and try again." : e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <section className="tint-red card card-accent space-y-3 p-5">
      <h2 className="flex items-center gap-3 font-extrabold">
        Debug mode <span className="chip bg-primary/10 text-primary">Admin only</span>
      </h2>
      <label className="flex cursor-pointer items-center justify-between gap-4">
        <span>
          <span className="label block">{user.debug ? "Debug mode is ON" : "Debug mode is off"}</span>
          <span className="text-sm font-semibold text-muted">
            Every lesson, test and certificate is open, hearts never run out, and XP and streak show as ∞. Nothing is saved: your real
            progress, XP and streak stay exactly as they are.
          </span>
        </span>
        <input type="checkbox" className="peer sr-only" checked={!!user.debug} disabled={busy} onChange={(e) => toggle(e.target.checked)} />
        <span className="relative h-8 w-14 shrink-0 rounded-full bg-line transition-colors peer-checked:bg-primary peer-focus-visible:ring-4 peer-focus-visible:ring-primary/30 after:absolute after:left-1 after:top-1 after:h-6 after:w-6 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-6" />
      </label>
      <ErrorNote>{error}</ErrorNote>
    </section>
  );
}

export default function Admin() {
  const [tab, setTab] = useState("content");
  return (
    <div className="tint-red">
      <PageTitle icon="shield" title="Admin" subtitle="Content, users and the security log." />
      <div className="mb-6 flex gap-2" role="tablist">
        {[
          ["content", "Content"],
          ["users", "Users"],
          ["audit", "Security log"],
          ["debug", "Debug mode"],
        ].map(([k, label]) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)} className={`chip border-2 ${tab === k ? "border-primary bg-primary/10 text-primary" : "border-line text-muted"}`}>
            {label}
          </button>
        ))}
      </div>
      {tab === "content" && <Content />}
      {tab === "users" && <Users />}
      {tab === "audit" && <Audit />}
      {tab === "debug" && <Debug />}
    </div>
  );
}
