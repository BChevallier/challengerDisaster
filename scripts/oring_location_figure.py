"""Where the O-rings are: the Shuttle stack seen from the side (right booster in front), the joint
that failed, and a simplified cross-section of that joint with its two O-rings.

Built as four frames in one fixed layout, to stack as reveal.js fragments:
  1  stack, right booster highlighted
  2  + the aft field joint marked
  3  + zoomed cross-section: tang in clevis, primary and secondary O-ring
  4  same section with the joint opened (gap exaggerated): hot gas reaches the O-rings

Proportions of the stack roughly to scale (ET 46.9 m x 8.4 m, SRB 45.5 m x 3.7 m, orbiter ~37 m);
joint section schematic, after Rogers Commission Vol. 1, Figs. 13 and 14 (pp. 56-57).
Side view from the orbiter's right: the right booster is the one nearest the viewer.

Writes figures/oring_location_{1..4}_{dark,light}.{png,svg} (16:9), and
figures/oring_location_square_{2,3,4}_{dark,light}.{png,svg}: frames 2-4 in a near-square box (420 x 400 px on the
slide) for the picture slot of the timeline's context slide.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, ConnectionPatch, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent.parent / "figures"
ACCENT = "#d95926"
THEMES = {
    "dark": {"bg": "#000000", "ink": "#ffffff", "muted": "#9a9a9a", "faint": "#2c2c2c",
             "faint_edge": "#555555", "steel": "#6b6b6b", "booster": "#d9d9d9"},
    "light": {"bg": "#ffffff", "ink": "#111111", "muted": "#666666", "faint": "#ececec",
              "faint_edge": "#b5b5b5", "steel": "#9c9c9c", "booster": "#3a3a3a"},
}
FONT_SCALE = 1.0  # set per layout in draw()
SQUARE_BBOX = None  # crop shared by all square frames, taken from frame 3
JOINT_Y = 11.5  # aft field joint, metres above the booster's nozzle exit (approximate)


def label(ax, x, y, text, c, color=None, **kw):
    kw["fontsize"] = kw.get("fontsize", 14) * FONT_SCALE
    ax.text(x, y, text, color=color or c["ink"], **kw)


def draw_stack(ax, c, step):
    ax.set_xlim(-21, 13)
    ax.set_ylim(-2, 53)
    ax.set_aspect("equal")
    ax.axis("off")
    faint = dict(facecolor=c["faint"], edgecolor=c["faint_edge"], linewidth=1)

    # External tank (behind): cylinder with an ogive nose.
    et = [(-4.2, 4)] + [(-4.2, 41)] + [(-4.2 * (1 - t) ** 1.6, 41 + 9.9 * t) for t in (0.25, 0.5, 0.75, 1.0)]
    et = et + [(-x, y) for x, y in reversed(et)]
    ax.add_patch(Polygon(et, closed=True, **faint))

    # Orbiter in profile, belly against the tank, nose up, tail away from the tank.
    orbiter = [(-5.0, 7), (-5.0, 36), (-5.6, 40), (-7.0, 43.5), (-8.6, 43.8), (-10.2, 41.5), (-10.6, 37),
               (-10.6, 16), (-17.5, 8.5), (-17.5, 6.5), (-10.6, 7.5), (-10.6, 7)]
    ax.add_patch(Polygon(orbiter, closed=True, **faint))
    for dx in (-6.4, -8.0, -9.4):  # main engine bells
        ax.add_patch(Polygon([(dx - 0.5, 7), (dx + 0.5, 7), (dx + 0.9, 4.6), (dx - 0.9, 4.6)], closed=True, **faint))

    # Right solid rocket booster, in front of the tank.
    r = 1.85
    srb = [(-2.6, 0), (-r, 3.5), (-r, 41), (-1.2, 43.6), (-0.35, 45.3), (0.35, 45.3), (1.2, 43.6), (r, 41),
           (r, 3.5), (2.6, 0)]
    ax.add_patch(Polygon(srb, closed=True, facecolor=c["booster"], edgecolor=c["bg"], linewidth=1.5, zorder=3))
    for y in (19.5, 27.5):  # the other two field joints, for reference
        ax.plot([-r, r], [y, y], color=c["bg"], linewidth=1.2, zorder=4)

    if FONT_SCALE == 1.0:  # wide layout: label to the right of the stack
        label(ax, 5.2, 46, "right booster", c, va="center", ha="left")
        ax.plot([5.0, 1.3], [45.6, 38.5], color=c["muted"], linewidth=1, zorder=6)
    else:  # square layout: the zoom box is close on the right, so label above the orbiter's nose
        label(ax, -8.0, 51.5, "right booster", c, va="bottom", ha="center")
        ax.plot([-5.0, -0.6], [51.2, 40.0], color=c["muted"], linewidth=1, zorder=6)

    if step >= 2:
        ax.plot([-r, r], [JOINT_Y, JOINT_Y], color=ACCENT, linewidth=3, zorder=5)
        ax.add_patch(Circle((0, JOINT_Y), 3.0, facecolor="none", edgecolor=ACCENT, linewidth=2, zorder=5))
        label(ax, 3.6, JOINT_Y, "joint", c, color=ACCENT, va="center", ha="left", fontweight="bold")


def draw_section(ax, c, step):
    ax.set_xlim(-4.2, 6.2)
    ax.set_ylim(-3.4, 8.4)
    ax.set_aspect("equal")
    ax.axis("off")
    if step < 3:
        return
    ax.add_patch(FancyBboxPatch((-4.0, -3.25), 10.1, 11.5, boxstyle="round,pad=0,rounding_size=0.3",
                                facecolor="none", edgecolor=c["faint_edge"], linewidth=1, linestyle=(0, (4, 3))))
    steel = dict(facecolor=c["steel"], edgecolor="none")
    opened = step >= 4
    shift = -0.38 if opened else 0.0  # inner clevis leg pulled away from the tang (joint rotation, exaggerated)

    # Upper segment: wall ending in the tang, which slides into the clevis below.
    ax.add_patch(Rectangle((0.95, 0.35), 0.8, 7.8, **steel))
    # Lower segment: clevis (U shape) on top of the wall.
    ax.add_patch(Rectangle((0.95, -3.2), 0.8, 2.0, **steel))           # wall
    ax.add_patch(Polygon([(0, -1.2), (2.7, -1.2), (2.7, 0), (0, 0)], closed=True, **steel))  # base
    ax.add_patch(Rectangle((1.8, 0), 0.9, 5.6, **steel))               # outer leg
    inner = Polygon([(0, 0), (0.9, 0), (0.9 + shift, 5.6), (0 + shift, 5.6)], closed=True, **steel)
    ax.add_patch(inner)                                                 # inner leg (O-ring side)
    ax.add_patch(Rectangle((-0.1, 1.15), 2.9, 0.5, facecolor=c["faint_edge"], edgecolor="none"))  # pin

    # O-rings in grooves on the inner leg, against the tang: primary (upper), secondary (lower).
    for y in (4.4, 3.3):
        x = 0.9 + shift * y / 5.6 - 0.12
        ax.add_patch(Circle((x, y), 0.26, facecolor=ACCENT, edgecolor=c["bg"], linewidth=1.5, zorder=4))

    if FONT_SCALE == 1.0:  # too small to read in the square layout
        label(ax, -2.0, 7.6, "inside", c, color=c["muted"], ha="center", fontsize=12)
        label(ax, 4.4, 7.6, "outside", c, color=c["muted"], ha="center", fontsize=12)
    if FONT_SCALE == 1.0:  # wide: label on the outside
        label(ax, 3.05, 3.85, "O-rings", c, color=ACCENT, va="center", fontweight="bold")
        ax.add_patch(FancyArrowPatch((2.85, 3.85), (1.15, 3.9), arrowstyle="-", color=ACCENT, linewidth=1.2,
                                     connectionstyle="arc3,rad=0.0", zorder=5))
    else:  # square: no room on the right, label on the inside next to the rings
        label(ax, -0.35 + shift, 3.85, "O-rings", c, color=ACCENT, va="center", ha="right", fontweight="bold")

    # Hot gas from the burning propellant inside, down the gap towards the O-rings.
    gas_end = (0.93, 2.5) if opened else (0.93, 5.0)
    path = [(-2.8, 6.4), (0.93, 6.25), gas_end]
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        last = (x1, y1) == gas_end
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>" if last else "-",
                                     mutation_scale=16, color=c["ink"], linewidth=2, zorder=6,
                                     shrinkA=0, shrinkB=0))
    label(ax, -2.8, 6.75, "hot gas", c, ha="left", fontsize=13)
    if opened and FONT_SCALE == 1.0:  # square layout: the slide's bullet says it
        label(ax, -3.5, 2.4, "the joint\nopens", c, color=c["muted"], ha="left", fontsize=12, linespacing=1.15)


LAYOUTS = {  # name -> (figure size in inches, stack axes, section axes, file prefix)
    "wide": ((9.6, 5.4), [0.0, 0.02, 0.42, 0.96], [0.48, 0.04, 0.5, 0.92], "oring_location"),
    "square": ((4.2, 4.0), [-0.02, 0.01, 0.46, 0.98], [0.44, 0.06, 0.56, 0.88], "oring_location_square"),
}


def draw(theme, step, layout="wide"):
    c = THEMES[theme]
    plt.rcParams.update({"font.family": "Helvetica Neue"})
    global FONT_SCALE
    size, stack_box, sec_box, prefix = LAYOUTS[layout]
    FONT_SCALE = 1.0 if layout == "wide" else 1.1
    fig = plt.figure(figsize=size, dpi=200 if layout == "wide" else 300)
    fig.patch.set_facecolor(c["bg"])
    ax_stack = fig.add_axes(stack_box)
    ax_sec = fig.add_axes(sec_box)
    for ax in (ax_stack, ax_sec):
        ax.set_facecolor(c["bg"])
    draw_stack(ax_stack, c, step)
    draw_section(ax_sec, c, step)

    if step >= 3:  # zoom lines from the circled joint to the section
        for ys, yd in ((JOINT_Y + 3.0, 8.25), (JOINT_Y - 3.0, -3.25)):
            fig.add_artist(ConnectionPatch(xyA=(0.4, ys), coordsA=ax_stack.transData, xyB=(-4.0, yd),
                                           coordsB=ax_sec.transData, color=c["faint_edge"], linewidth=1,
                                           linestyle=(0, (4, 3))))

    crop = {}
    if layout == "square":  # trim margins, with the same crop for every frame so they stack exactly
        global SQUARE_BBOX
        if SQUARE_BBOX is None:  # first call must be frame 3 (largest content)
            SQUARE_BBOX = fig.get_tightbbox(fig.canvas.get_renderer()).padded(0.04)
        crop = {"bbox_inches": SQUARE_BBOX}
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{prefix}_{step}_{theme}.{ext}", facecolor=c["bg"], **crop)
    plt.close(fig)


if __name__ == "__main__":
    for theme in THEMES:
        for step in (1, 2, 3, 4):
            draw(theme, step)
        for step in (3, 2, 4):  # 3 first: it sets the shared crop
            draw(theme, step, layout="square")
