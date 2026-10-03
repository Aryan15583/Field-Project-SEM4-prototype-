"""Renders real rows from the demo database as an HTML page and screenshots it (emails are masked)."""
import sqlite3, html, subprocess, pathlib
db = sqlite3.connect("/tmp/claude-0/doc.db"); db.row_factory = sqlite3.Row
def table(title, sql, mask=()):
    rows = db.execute(sql).fetchall()
    cols = rows[0].keys()
    def cell(c, v):
        v = "" if v is None else str(v)
        if c in mask: v = v[0] + "•••@" + v.split("@")[-1]
        return html.escape(v[:40])
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{cell(c, r[c])}</td>" for c in cols) + "</tr>" for r in rows)
    return f"<h2>{title}</h2><table><tr>{head}</tr>{body}</table>"
page = "<html><head><style>body{font:13px 'Liberation Sans',sans-serif;margin:18px;background:#fff;color:#111}h2{font-size:14px;margin:16px 0 6px;color:#1d4ed8}table{border-collapse:collapse;width:100%}th{background:#1d4ed8;color:#fff;text-align:left;padding:5px 8px;font-weight:600}td{border-bottom:1px solid #dbe4f3;padding:4px 8px;font-family:'DejaVu Sans Mono',monospace;font-size:11.5px}tr:nth-child(even) td{background:#f4f7ff}</style></head><body>"
page += table("users  (SELECT id, email, name, role, mfa_method, xp_total, streak_current FROM users)", "select id, email, name, role, mfa_method, xp_total, streak_current, friend_code from users order by xp_total desc", mask=("email",))
page += table("courses and their size  (JOIN units / lessons)", "select c.slug, c.title, count(distinct u.id) units, count(l.id) lessons, sum(l.is_project) projects from courses c join units u on u.course_id=c.id join lessons l on l.unit_id=u.id group by c.id order by c.position")
page += table("audit_log  (latest security events)", "select id, user_id, event, created_at from audit_log order by id desc limit 6")
page += table("certificates", "select id as code, holder_name, course_title, lessons, issued_at from certificates")
page += "</body></html>"
p = pathlib.Path("/tmp/db.html"); p.write_text(page)
