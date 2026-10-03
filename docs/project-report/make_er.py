"""Draws the database diagram straight from the SQLAlchemy models (so it never drifts from the code). Output: diagrams/er.dot"""
import os, sys
sys.path.insert(0, "/home/user/.vscode/backend")
os.environ.setdefault("ENV", "test")
from app.models import Base

show = ["users","courses","units","lessons","exercises","user_lessons","user_tests","review_items","certificates","follows","contests","contest_entries","passkeys","audit_log","xp_events","user_badges","lesson_attempts","test_attempts","refresh_tokens"]
tables = {t.name: t for t in Base.metadata.sorted_tables}
lines = ['digraph G { rankdir=TB; nodesep=0.22; ranksep=0.9; newrank=true; bgcolor="white"; node [shape=plain, fontname="Liberation Sans"]; edge [color="#64748b", arrowsize=0.7];']
for name in show:
    t = tables[name]
    cols = list(t.columns)
    rows = "".join(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">{"<B>PK </B>" if c.primary_key else ("<I>FK </I>" if c.foreign_keys else "     ")}{c.name}</FONT></TD></TR>' for c in cols[:9])
    more = f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="#64748b">+ {len(cols)-9} more</FONT></TD></TR>' if len(cols) > 9 else ""
    lines.append(f'{name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" COLOR="#1d4ed8"><TR><TD BGCOLOR="#1d4ed8"><FONT COLOR="white" POINT-SIZE="11"><B>{name}</B></FONT></TD></TR>{rows}{more}</TABLE>>];')
for name in show:
    for fk in tables[name].foreign_keys:
        tgt = fk.column.table.name
        if tgt in show: lines.append(f"{name} -> {tgt};")
lines.append("}")
open(os.path.join(os.path.dirname(__file__), "diagrams/er.dot"), "w").write("\n".join(lines))
print(len(Base.metadata.sorted_tables), "tables in the models;", len(show), "drawn")
