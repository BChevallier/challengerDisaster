"""Timeline of the field-joint history, 1977-1986: each row pairs a warning sign (left) with the
response it got (right), ending with the launch. Rows are in order, not to time scale.

Sources (Rogers Commission Vol. 1, printed page numbers):
  1977     hydroburst test: joint opens at ignition; shims added, design kept ....... p. 122-123
  1978-79  Marshall memos: design "unacceptable"; certified Criticality 1R Nov 1980 . p. 123-125
  1981     STS-2 erosion; not reported at the Level I review for STS-3 ............. p. 125
  1982     tests: secondary ring may not seal; Criticality 1 Dec 1982, waived Mar 1983 p. 125-128
  1984     41-B erosion on two joints; "not a constraint", safety margin ............ p. 128-129
  Jan 1985 51-C at 53 °F, hot gas past the primary; "not desirable but acceptable" .. p. 134-136
  Apr 1985 51-B primary never sealed, secondary eroded; constraint, waived each flight p. 137-138
  27 Jan 1986 Thiokol engineers: no launch below 53 °F; management reverses ........ p. 87-93
  28 Jan 1986 36 °F at launch, breakup at 73 s ..................................... p. 19-21, 70

Writes figures/timeline_{dark,light}.{png,svg}.
"""
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "figures"
ACCENT = "#d95926"
THEMES = {
    "dark": {"bg": "#000000", "ink": "#ffffff", "muted": "#9a9a9a", "faint": "#333333"},
    "light": {"bg": "#ffffff", "ink": "#111111", "muted": "#666666", "faint": "#d6d6d6"},
}

# (date, warning sign, response)
ROWS = [
    ("1977", "Test: the joint opens at ignition", "Shims added, design kept"),
    ("1978–80", "Marshall engineers: “unacceptable”", "Certified as a redundant seal"),
    ("1981", "First O-ring erosion in flight", "Not reported at the next review"),
    ("1982", "Tests: the 2nd ring may not seal", "“No backup” rating, then waived"),
    ("1984", "Erosion on two joints", "“Acceptable”: within the safety margin"),
    ("Jan 1985", "Coldest launch, 12 °C: gas past ring 1", "“Not desirable but acceptable”"),
    ("Apr 1985", "Ring 1 never sealed, ring 2 eroded", "Launch constraint, waived every flight"),
    ("27 Jan 1986", "Engineers: no launch below 12 °C", "Overruled"),
]
FINAL = ("28 Jan 1986", "Launch at 2 °C. Breakup after 73 s.")


def draw(theme):
    c = THEMES[theme]
    plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 14})
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=200)
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["bg"])
    n = len(ROWS)
    ax.set_xlim(0, 1)
    ax.set_ylim(n + 1.1, -1.0)  # row 0 at top
    ax.axis("off")

    spine_x, gap = 0.5, 0.085
    ax.text(spine_x - gap, -0.6, "Warning sign", color=c["muted"], ha="right", va="center", fontsize=12, style="italic")
    ax.text(spine_x + gap, -0.6, "Response", color=c["muted"], ha="left", va="center", fontsize=12, style="italic")
    ax.plot([spine_x, spine_x], [-0.1, n + 0.35], color=c["faint"], linewidth=1.5, zorder=1)

    for i, (date, warning, response) in enumerate(ROWS):
        ax.text(spine_x, i, date, color=c["muted"], ha="center", va="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.25", facecolor=c["bg"], edgecolor="none"), zorder=2)
        ax.text(spine_x - gap, i, warning, color=c["ink"], ha="right", va="center")
        ax.text(spine_x + gap, i, response, color=c["ink"], ha="left", va="center")

    date, text = FINAL
    y = n + 0.5
    ax.text(spine_x, y, date, color=ACCENT, ha="center", va="center", fontsize=11,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=c["bg"], edgecolor="none"), zorder=2)
    ax.text(spine_x + gap, y, text, color=ACCENT, ha="left", va="center", fontsize=15, fontweight="bold")

    fig.tight_layout(pad=0.3)
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"timeline_{theme}.{ext}", facecolor=c["bg"])
    plt.close(fig)


if __name__ == "__main__":
    for theme in THEMES:
        draw(theme)
