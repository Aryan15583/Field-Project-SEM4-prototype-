"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorNote, Spinner } from "@/components/ui";

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

function Users() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");
  const load = useCallback(() => api("/api/admin/users").then(setUsers).catch((e) => setError(e.message)), []);
  useEffect(() => {
    load();
  }, [load]);
  const toggle = async (u) => {
    try {
      await api(`/api/admin/users/${u.id}/active`, { method: "POST", body: { active: !u.active } });
      load();
    } catch (e) {
      setError(e.message);
    }
  };
  if (!users) return <Spinner />;
  return (
    <div className="card overflow-x-auto">
      <ErrorNote>{error}</ErrorNote>
      <table className="w-full text-left text-sm">
        <thead className="text-muted">
          <tr>
            {["User", "Role", "XP", "2FA", "Last login", ""].map((h) => (
              <th key={h} className="px-4 py-3 font-bold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-t-2 border-line">
              <td className="px-4 py-3">
                <p className="font-bold">{u.name}</p>
                <p className="text-xs text-muted">{u.email}</p>
              </td>
              <td className="px-4 py-3">{u.role}</td>
              <td className="px-4 py-3">{u.xp}</td>
              <td className="px-4 py-3">{u.mfa ? "✓" : "-"}</td>
              <td className="px-4 py-3 text-xs">{u.last_login_at ? new Date(u.last_login_at).toLocaleString() : "never"}</td>
              <td className="px-4 py-3">
                <button className={u.active ? "btn-link text-bad" : "btn-link"} onClick={() => toggle(u)}>
                  {u.active ? "Disable" : "Enable"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
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

export default function Admin() {
  const [tab, setTab] = useState("content");
  return (
    <div>
      <h1 className="mb-4 text-2xl font-black">Admin</h1>
      <div className="mb-6 flex gap-2" role="tablist">
        {[
          ["content", "Content"],
          ["users", "Users"],
          ["audit", "Security log"],
        ].map(([k, label]) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)} className={`chip border-2 ${tab === k ? "border-primary bg-primary/10 text-primary" : "border-line text-muted"}`}>
            {label}
          </button>
        ))}
      </div>
      {tab === "content" && <Content />}
      {tab === "users" && <Users />}
      {tab === "audit" && <Audit />}
    </div>
  );
}
