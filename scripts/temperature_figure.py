"""O-ring anomalies per Shuttle flight vs. joint temperature, redrawn from
Rogers Commission Vol. 1, Figure 2 (pp. 129-131). Data: data/oring_anomalies.csv.

Writes, each as {dark,light}.{png,svg} in figures/:
  oring_temperature_*                    all joints, all flights
  oring_temperature_incomplete_*         all joints, only flights with anomalies
  oring_temperature_field_*              field joints only, all flights (cf. Rogers Fig. 7)
  oring_temperature_field_incomplete_*   field joints only, only flights with anomalies (cf. Rogers Fig. 6)
Each also as *_nochallenger_*: identical frame without the Challenger line (for a fragment reveal).
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "oring_anomalies.csv"
OUT = ROOT / "figures"

ACCENT = "#d95926"
THEMES = {
    "dark": {"bg": "#000000", "ink": "#ffffff", "muted": "#9a9a9a", "grid": "#2a2a2a", "dot": "#e8e8e8"},
    "light": {"bg": "#ffffff", "ink": "#111111", "muted": "#666666", "grid": "#e4e4e4", "dot": "#222222"},
}


def f_to_c(f):
    return (f - 32) * 5 / 9


DOT = 80  # marker area (pt²)
CHALLENGER_TEMP = f_to_c(31)  # joint temperature of STS 51-L, same table (31 °F)


def load_flights(field_only=False):
    """Count distinct joints (booster + joint) with any anomaly (erosion, blow-by or heat) per Shuttle flight.

    A joint listed twice (primary and secondary ring, e.g. 51-C right center field) counts once.
    """
    rows = [r for r in csv.DictReader(l for l in DATA.open() if not l.startswith("#"))]
    temp, joints = {}, defaultdict(set)
    for r in rows:
        if r["type"] != "flight" or r["flight"] in ("STS-4", "STS 51-L"):
            continue  # STS-4 hardware lost at sea; 51-L has no post-flight data
        temp[r["flight"]] = f_to_c(int(r["joint_temp_F"]))
        if field_only and "Field" not in r["joint"]:
            continue
        if r["erosion"] not in ("-", "NA", "") or r["blowby"] == "X":
            joints[r["flight"]].add((r["booster"], r["joint"]))
    return [(f, temp[f], len(joints[f])) for f in temp]


def beeswarm(ax, xs, ys, size):
    """Keep every dot at its exact temperature; where dots would overlap, nudge them up or down
    within their row (in display space) until they clear each other."""
    d = size ** 0.5 * ax.figure.dpi / 72 * 1.05  # dot diameter in pixels, plus a hair of air
    pts = ax.transData.transform(list(zip(xs, ys)))
    placed = []
    for i in sorted(range(len(pts)), key=lambda i: pts[i][0]):
        x, y = pts[i]
        for k in range(0, 20):
            dy = (k + 1) // 2 * d * 0.62 * (1 if k % 2 else -1)
            if all((x - px) ** 2 + (y + dy - py) ** 2 >= d * d for px, py in placed):
                break
        placed.append((x, y + dy))
        pts[i] = (x, y + dy)
    return ax.transData.inverted().transform(pts).T


def draw(theme, flights, name, ymax, ylabel, challenger=True, square=False):
    """square=True: 4.2 x 4.0 in, for the 420 x 400 px picture slot of a timeline slide."""
    c = THEMES[theme]
    plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 16 if square else 15})
    fig, ax = plt.subplots(figsize=(4.2, 4.0) if square else (9.6, 5.4), dpi=300 if square else 200)
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["bg"])

    ax.set_xlim(-4, 29.5)
    ax.set_ylim(-0.75 if square else -0.4, ymax + 0.5)
    if challenger:
        ax.axvline(CHALLENGER_TEMP, color=ACCENT, linewidth=2.5, zorder=2)
        ax.text(CHALLENGER_TEMP + 0.6, ymax + 0.25, f"Challenger\n{CHALLENGER_TEMP:.1f} °C".replace("-", "−"),
                color=ACCENT, va="top", ha="left", fontsize=16, fontweight="bold")

    ax.set_xticks(range(0, 30, 10 if square else 5))
    ax.set_yticks(range(0, ymax + 1))
    ax.set_xlabel("Joint temperature (°C)" if square else "Joint temperature at launch (°C)",
                  color=c["muted"], labelpad=6 if square else 10)
    ax.set_ylabel(ylabel, color=c["muted"], labelpad=6 if square else 10)
    ax.grid(axis="y", color=c["grid"], linewidth=1)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c["muted"])
    ax.tick_params(colors=c["muted"], length=0, pad=8)

    fig.tight_layout()  # final layout first: the beeswarm works in display space
    dot = DOT * 0.65 if square else DOT
    xs, ys = beeswarm(ax, [x for _, x, _ in flights], [y for *_, y in flights], dot)
    ax.scatter(xs, ys, s=dot, color=c["dot"], edgecolor=c["bg"], linewidth=1.5 if square else 2, zorder=3)
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{name}_{theme}.{ext}", facecolor=c["bg"])
    plt.close(fig)


if __name__ == "__main__":
    # Each family: complete and incomplete (only flights with anomalies) share axes so the two stack.
    families = [
        ("oring_temperature", False, "Joints with O-ring anomalies"),
        ("oring_temperature_field", True, "Field joints with O-ring anomalies"),
    ]
    for name, field_only, ylabel in families:
        flights = load_flights(field_only)
        ymax = max(n for *_, n in flights) + 1  # headroom for the Challenger label
        damaged = [f for f in flights if f[2] > 0]
        for theme in THEMES:
            for variant, pts in (("", flights), ("_incomplete", damaged)):
                draw(theme, pts, f"{name}{variant}", ymax, ylabel)
                # Same frame without the Challenger line, to stack under it as a reveal.js fragment.
                draw(theme, pts, f"{name}{variant}_nochallenger", ymax, ylabel, challenger=False)
            if field_only:  # square pair for the "night before" timeline slide
                draw(theme, damaged, f"{name}_incomplete_square", ymax, "Damaged field joints", square=True)
                draw(theme, damaged, f"{name}_incomplete_nochallenger_square", ymax, "Damaged field joints",
                     challenger=False, square=True)
                draw(theme, flights, f"{name}_square", ymax, "Damaged field joints", square=True)
        print(f"== {name}: {len(damaged)} of {len(flights)} flights with anomalies")
        for f, x, y in sorted(flights, key=lambda f: f[1]):
            if y:
                print(f"  {f:10s} {x:5.1f} °C  {y}")
