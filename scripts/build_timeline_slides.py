"""Generate the horizontal-timeline slides and splice them into index.html between
<!-- timeline:start --> and <!-- timeline:end -->.

Every slide carries the same strip of events (same data-id on every dot, date and the track),
so reveal.js auto-animate slides the strip sideways from one event to the next; the last slide
spaces the whole strip out across the slide ("zoom out") under "What went wrong?".
The strip sits at the bottom of every slide; the first dot (general context) joins it with a dotted line.
Positions are absolute pixel values (no CSS transforms: auto-animate uses transforms itself).

Sources for each event are in its notes (EVENTS below).
Run:  .venv/bin/python scripts/build_timeline_slides.py
"""
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "index.html"

# (date label, short label for the overview, slide title, bullets, notes facts with sources).
# Index 0 is the general context: its dot sits before the timeline and joins it with a dotted line.
# Bullets give the gist of the chronology, not the full story: short, few numbers, no judgement.
# Page numbers: printed pages of Rogers Commission Report Vol. 1; "Vaughan" = The Challenger Launch Decision.
EVENTS = [
    ("Context", "", "A cheap, reusable shuttle.", [
        "1972: NASA picks the cheapest design to develop",
        "Solid-fuel boosters, never used before to fly people",
        "Their joints: copied from a proven rocket, then changed",
     ], ["Design chosen Mar 1972; solid boosters chosen mainly for lower development cost (Rogers pp. 2–4).",
         "Thiokol design based on the Titan III, with two O-rings, a longer tang, reusable segments (pp. 120–122)."]),
    ("1977", "Joint opens", "The joint opens at ignition.", [
        "A pressure test: the joint opens instead of closing",
        "The O-rings now have a gap to seal",
     ], ["Sep 1977 hydroburst test, gap up to 0.052 in. at the primary O-ring (Rogers pp. 122–123)."]),
    ("1981", "First erosion", "First O-ring erosion in flight.", [
        "Second flight: hot gas burns into an O-ring",
        "Not reported at the next flight review",
     ], ["STS-2, Nov 1981, 0.053 in. erosion; not reported at the Level I review for STS-3 (Rogers p. 125)."]),
    ("1982", "No backup", "The second ring is not a backup.", [
        "Tests: the second O-ring may not seal",
        "The joint is rated a single point of failure",
        "The rating is waived before the next flight",
     ], ["Criticality 1 in Dec 1982, waived Mar 1983 days before STS-6 (Rogers pp. 125–128)."]),
    ("1984", "Erosion", "Erosion on two joints.", [
        "A calculated “safety margin” makes it acceptable",
        "Erosion becomes a regular finding",
     ], ["41-B, Feb 1984; margin 0.090 vs 0.095 in., “not a constraint” (Rogers pp. 128–129).",
         "After the leak-check change, anomalies on more than half of flights (pp. 133–134)."]),
    ("27 Jan 1986", "Night before", "The night before.", [
        "Forecast: below freezing",
        "Engineers: no launch below 12 °C",
        "After a break, their managers say go",
     ], ["Teleconferences 5:45 and 8:45 p.m.; 30-min Thiokol caucus from ~10:30 p.m. (Rogers pp. 85–97)."]),
    ("28 Jan 1986", "Launch", "Launch at 2 °C.", [
        "0.7 s: black smoke at the joint",
        "59 s: a flame at the joint",
        "73 s: breakup",
     ], ["36 °F at launch; smoke at 0.678 s, flame at 58.788 s, breakup at 73.124 s (Rogers pp. 19–21, 70)."]),
]
# Optional picture on the left of an event slide; its bullets then start at the event's dot (x = 480 px).
# index -> (src, source page, alt text, object-position)
# AFTER_IMAGES: more pictures in the same spot, revealed one per click after the last bullet.
IMAGES = {
    0: ("media/shuttle-sts6-launch-2.jpg",
        "https://commons.wikimedia.org/wiki/File:Space_Shuttle_Challenger_(04-04-1983).JPEG",
        "Challenger lifting off on its first flight, STS-6, April 1983: orbiter, orange tank and two white boosters",
        "72% 40%"),
}
AFTER_IMAGES = {  # index -> pictures shown one per click after the last bullet, each covering the previous
    0: [("figures/oring_location_square_2_dark.png",
         "Side view of the Shuttle with the right booster's lowest joint circled"),
        ("figures/oring_location_square_3_dark.png",
         "Same view with a zoomed cut through that joint: the two O-rings between the steel walls, hot gas inside")],
    1: [("figures/oring_location_square_4_dark.png",
         "The same cut with the joint opened (gap exaggerated): the O-rings no longer touch the metal and hot gas "
         "gets past them")],
    5: [("figures/oring_temperature_field_incomplete_nochallenger_square_dark.png",
         "Scatter of damaged field joints against joint temperature, only the 7 flights with damage: no clear trend"),
        ("figures/oring_temperature_field_incomplete_square_dark.png",
         "The same scatter with Challenger's joint temperature, -0.6 °C, marked far to the left"),
        ("figures/oring_temperature_field_square_dark.png",
         "Same scatter with all 23 flights: every flight below 18 °C had damage, few warmer ones did; "
         "Challenger's line at -0.6 °C far to the left")],
}
LAST = len(EVENTS) - 1
OVERVIEW_DATE = {}  # shorter overview dates where neighbours would touch, e.g. {5: "27 Jan"}
WIDTH = 960          # slide width (reveal default)
STEP = 250           # distance between events while walking through
DATE_W = 140         # width of a date label (centred on its dot)
SHORT_W = 92         # width of an overview label
OV_LEFT, OV_RIGHT = 50, 910  # overview: first and last dot


def x_walk(i, cur):
    return WIDTH / 2 + (i - cur) * STEP


def x_overview(i):
    return OV_LEFT + i * (OV_RIGHT - OV_LEFT) / LAST


def strip(xs, cur, overview):
    """The timeline strip: track, then one dot + date per event (+ short label in the overview)."""
    out = [f'<div class="tl-link" data-id="tl-link" style="left:{xs[0]:.0f}px; width:{xs[1] - xs[0]:.0f}px"></div>',
           f'<div class="tl-track" data-id="tl-track" style="left:{xs[1]:.0f}px; width:{xs[-1] - xs[1]:.0f}px"></div>']
    for i, (date, short, *_rest) in enumerate(EVENTS):
        state = "now" if i == cur else ("past" if i < cur else "future")
        if i == 0:
            state += " context"
        if overview:
            state = "final" if i == LAST else ("past context" if i == 0 else "past")
        size = 18 if state.split()[0] in ("now", "final") else 12
        out.append(f'<span class="tl-dot {state}" data-id="tl-dot-{i}" '
                   f'style="left:{xs[i] - size / 2:.0f}px; width:{size}px; height:{size}px; top:{40 - size / 2:.0f}px"></span>')
        label = OVERVIEW_DATE.get(i, date) if overview else date
        out.append(f'<span class="tl-date {state}" data-id="tl-date-{i}" style="left:{xs[i] - DATE_W / 2:.0f}px">{label}</span>')
        if overview and short:
            out.append(f'<span class="tl-short" data-id="tl-short-{i}" style="left:{xs[i] - SHORT_W / 2:.0f}px">{short}</span>')
    return "\n          ".join(out)


def event_slide(cur):
    date, _short, title, bullets, facts = EVENTS[cur]
    xs = [x_walk(i, cur) for i in range(len(EVENTS))]
    items = "\n        ".join(f'<li class="fragment">{b}</li>' for b in bullets)
    notes = "\n        ".join(f'<p class="fact">{f}</p>' for f in facts)
    picture, split = "", ""
    if cur in IMAGES:
        src, href, alt, pos = IMAGES[cur]
        picture = (f'<a class="tl-picture fragment" href="{href}" target="_blank" rel="noopener">'
                   f'<img src="{src}" alt="{alt}" style="object-position: {pos}"></a>\n      ')
        split = " split"
    if cur in AFTER_IMAGES:
        split = " split"
    after = ""
    for src, alt in AFTER_IMAGES.get(cur, []):
        after += f'\n      <div class="tl-picture tl-after fragment"><img src="{src}" alt="{alt}"></div>'
    return f'''    <!-- Timeline {cur + 1}/{len(EVENTS)}: {date} (generated by scripts/build_timeline_slides.py) -->
    <section data-auto-animate class="tl-slide">
      <h3>{title}</h3>
      {picture}<ul class="tl-points{split}">
        {items}
      </ul>{after}
      <div class="tl-window" data-id="tl-window">
          {strip(xs, cur, overview=False)}
      </div>
      <aside class="notes">
        {notes}
        <p>[...]</p>
      </aside>
    </section>
'''


def overview_slide():
    xs = [x_overview(i) for i in range(len(EVENTS))]
    return f'''    <!-- Timeline overview: the whole strip at once (generated by scripts/build_timeline_slides.py) -->
    <section data-auto-animate class="tl-slide tl-overview">
      <h2 class="tl-question">What went wrong?</h2>
      <div class="tl-window" data-id="tl-window">
          {strip(xs, LAST, overview=True)}
      </div>
      <aside class="notes">
        <p>[...]</p>
      </aside>
    </section>
'''


def main():
    html = INDEX.read_text()
    start, end = "<!-- timeline:start -->", "<!-- timeline:end -->"
    i, j = html.index(start) + len(start), html.index(end)
    slides = "\n" + "\n".join(event_slide(k) for k in range(len(EVENTS))) + "\n" + overview_slide() + "    "
    INDEX.write_text(html[:i] + slides + html[j:])
    print(f"wrote {len(EVENTS) + 1} timeline slides")


if __name__ == "__main__":
    main()
