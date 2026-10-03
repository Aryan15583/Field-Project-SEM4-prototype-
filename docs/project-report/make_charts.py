"""Charts for the Requirement-gathering survey (reads the exported Google Form CSV). Run: python make_charts.py"""
import csv, collections, sys, zipfile, io, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/survey/Coding Platform Interest Survey.csv")
rows = list(csv.DictReader(open(src, encoding="utf-8")))
N = len(rows)
cols = list(rows[0].keys())
out = pathlib.Path(__file__).parent / "figures"
BLUE, VIOLET, PINK, ORANGE, TEAL, SKY, GOLD, GREY = "#1d6ff2", "#7c3aed", "#be185d", "#c2410c", "#0f766e", "#0369a1", "#b45309", "#8a94a6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

def count(i, drop=("",)):
    c = collections.Counter(r[cols[i]].strip() for r in rows)
    for d in drop: c.pop(d, None)
    return c

def hbar(name, title, c, color, order=None, note=None):
    items = [(k, c[k]) for k in order if k in c] if order else c.most_common()
    items = items[::-1]
    fig, ax = plt.subplots(figsize=(6.4, 0.55 * len(items) + 1.2))
    bars = ax.barh([k for k, _ in items], [v for _, v in items], color=color, height=0.62)
    total = sum(v for _, v in items)
    for b, (_, v) in zip(bars, items):
        ax.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2, f"{v}  ({v / total:.0%})", va="center", fontsize=9)
    ax.set_xlim(0, max(v for _, v in items) * 1.28)
    ax.set_xlabel("Number of respondents")
    ax.set_title(title, loc="left", fontweight="bold", fontsize=11)
    if note: fig.text(0.01, 0.01, note, fontsize=8, color=GREY)
    fig.tight_layout()
    fig.savefig(out / f"{name}.png", dpi=170)
    plt.close(fig)

def donut(name, title, c, colors):
    items = c.most_common()
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    wedges, _ = ax.pie([v for _, v in items], colors=colors[: len(items)], startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor="white"))
    total = sum(v for _, v in items)
    ax.legend(wedges, [f"{k} - {v} ({v / total:.0%})" for k, v in items], loc="center left", bbox_to_anchor=(0.98, 0.5), frameon=False)
    ax.set_title(title, loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout()
    fig.savefig(out / f"{name}.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

donut("survey_age", "Q1. Age group of the respondents", count(3), [BLUE, VIOLET, GOLD])
donut("survey_experience", "Q2. Have you tried learning programming before?", count(4), [TEAL, ORANGE, SKY])
hbar("survey_difficulty", "Q3. What made learning difficult or boring?", count(5), PINK, note="Only respondents who had tried before answered (blank answers excluded).")
hbar("survey_style", "Q4. How do you prefer to learn new skills?", count(6), BLUE)
# Q5 - appeal of game-like learning, 1..5
c = count(8)
fig, ax = plt.subplots(figsize=(6.4, 3.3))
vals = [c.get(str(i), 0) for i in range(1, 6)]
bars = ax.bar(["1\nnot appealing", "2", "3", "4", "5\nvery appealing"], vals, color=[GREY, GREY, GOLD, BLUE, VIOLET], width=0.62)
for b, v in zip(bars, vals): ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v} ({v / N:.0%})", ha="center", fontsize=9)
ax.set_ylim(0, max(vals) * 1.25); ax.set_ylabel("Respondents")
avg = sum(i * v for i, v in zip(range(1, 6), vals)) / sum(vals)
ax.set_title(f"Q5. How appealing is learning to code through a game? (average {avg:.2f} / 5)", loc="left", fontweight="bold", fontsize=11)
fig.tight_layout(); fig.savefig(out / "survey_appeal.png", dpi=170); plt.close(fig)
print("appeal average", round(avg, 2), "| 4-5:", vals[3] + vals[4], f"{(vals[3] + vals[4]) / N:.0%}")
hbar("survey_language", "Q6. Which language would you like to learn first?", count(9), TEAL)
hbar("survey_motivation", "Q7. What would keep you learning?", count(10), ORANGE)
donut("survey_social", "Q8. Solo or community?", count(11), [VIOLET, BLUE, GOLD])
hbar("survey_quit", "Q9. Biggest reason you would stop using such a platform", count(12), SKY)
print("charts written:", sorted(p.name for p in out.glob("survey_*.png")))
