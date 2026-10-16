#!/usr/bin/env python3
"""diagrams.py . inline SVG case-study diagrams for rohanrelated.com.

Why SVG and not PNG: these are diagrams, so they should be code. A few KB
instead of a half-megabyte export, crisp at any size, and every colour comes
from the CSS custom properties, which means the diagrams re-theme themselves
if the palette ever moves. A PNG pair could do none of that.

Reflow: SVG cannot actually reflow, because a viewBox is fixed and CSS cannot
change it. So each diagram emits TWO layout groups inside one <svg> . a wide
16:9 arrangement and a tall 4:5 one . and CSS shows exactly one. Both are
generated from the single CONTENT dict below, so content is edited in one
place and coordinates are never hand-maintained.

Legibility, computed rather than guessed. Plate width is
  min(72rem, 100vw - 2*gutter) - 2*frame-padding
The wide layout is used from 760px up, where the plate is 674px and the scale
against a 1600-unit viewBox is 0.422, so the smallest label at 34 units
renders 14.3px. The tall layout serves 375px to 759px against a 1000-unit
box; at 375px the scale is 0.315, so 38 units renders 12.0px and 44 units
renders 13.9px. Nothing below 34u wide or 38u tall.

Confidentiality: no participant or department names, no per-segment numbers,
no internal metrics, nothing touching the security finding. The Egnyte bands
are equal width by design . real proportions would publish per-segment
findings about a named company, and invented ones would be a lie in a
diagram. The five roadmap bars are unlabelled: they show that a ranking
exists without publishing what was in it.
"""

# ----------------------------------------------------------------------
# CONTENT . the only place to edit. Coordinates are derived, never typed.
# ----------------------------------------------------------------------

EGNYTE = {
    "slug": "egnyte-segmentation",
    "title": "How the study was segmented",
    "desc": (
        "A research diagram in two stages. The sample is 23 participants drawn from "
        "8 departments and 3 seniority tiers. A study-design decision then groups them "
        "by adoption behaviour, producing three groups: sustained use, tried once, and "
        "never encountered. The third group is emphasised, because it is where the "
        "finding came from. Five unlabelled bars in descending length stand for the "
        "ranked set of priorities that followed."
    ),
    "sample_label": "Sample",
    "count": 23,
    "count_line": "23 participants",
    "meta_line": "8 departments · 3 seniority tiers",
    "pivot_label": "Study design",
    # Reads as a decision made, not a correction to something.
    "pivot_line": "Grouped by adoption behaviour",
    "groups_label": "Three groups",
    "groups": [
        ("Sustained use", False),
        ("Tried once", False),
        ("Never encountered", True),   # True = Safelight emphasis
    ],
    "outcome_label": ["Ranked", "priorities"],
    "bars": 5,
}

MERCOR = {
    "slug": "mercor-frameworks",
    "title": "Six evaluation frameworks, by the judgment each asks for",
    "desc": (
        "A diagram organised along a single axis running from judged by eye to judged "
        "against the brief. Six evaluation frameworks sit along it in three families. "
        "Visual quality covers aesthetic ranking and style matching. Content substance "
        "covers content grading and template reuse. Guideline adherence covers system "
        "following and written direction. The axis is the point: the frameworks sit at "
        "different places on it, so each asks for a different kind of judgment."
    ),
    # Both ends name a kind of judgment. Nothing here implies an absence of it.
    "axis_left": "Judged by eye",
    "axis_right": "Judged against the brief",
    "axis_note": "Every framework asks for judgment. They differ in which kind.",
    "families": [
        ("Visual quality", [
            ("Aesthetic ranking", "ranking outputs against each other"),
            ("Style matching", "taking on a target style without pastiche"),
        ]),
        ("Content substance", [
            ("Content grading", "judging whether the substance holds up"),
            ("Template reuse", "whether a generated template is truly reusable"),
        ]),
        ("Guideline adherence", [
            ("System following", "new content that respects an existing system"),
            ("Written direction", "conformance to written design direction"),
        ]),
    ],
}

# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

# Text is measured against the real font metrics, not a per-character
# constant. An estimated average advance is what let two labels overflow
# their containers in the first build: Syne runs 0.503em on lowercase but
# 0.648em on caps, so any single constant is wrong for one of them.
from pathlib import Path as _Path

_FONTS = {
    "syne": _Path(__file__).parent / "assets/fonts/syne-latin-wght-normal.woff2",
    "mono": _Path(__file__).parent / "assets/fonts/ibm-plex-mono-latin-500-normal.woff2",
}
_METRICS = {}


def _load(key):
    if key in _METRICS:
        return _METRICS[key]
    table = None
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(_FONTS[key])
        upm = f["head"].unitsPerEm
        hmtx, cmap = f["hmtx"], f.getBestCmap()
        table = {ch: hmtx[g][0] / upm for ch, g in cmap.items()}
    except Exception:
        table = None      # fall back to constants below
    _METRICS[key] = table
    return table


# Fallbacks only used if fontTools is unavailable at build time.
_FALLBACK = {"syne": 0.53, "mono": 0.60}


def measure(s, size, font="syne"):
    """Width of a string in viewBox units, from real advance widths."""
    t = _load(font)
    if not t:
        return len(s) * size * _FALLBACK[font]
    default = _FALLBACK[font]
    return size * sum(t.get(ord(c), default) for c in s)


# Kept for callers that still pass an adv argument; ignored in favour of
# real measurement.
MONO_ADV = 0.60
SYNE_ADV = 0.53


class DiagramOverflow(Exception):
    pass


def check_bounds(used, limit, where, margin=12):
    """Fail the build rather than silently clipping. Content edits change
    wrap counts, which changes total height; without this the overflow only
    shows up in a browser."""
    if used > limit - margin:
        raise DiagramOverflow(
            f"{where}: content reaches {used:.0f} of {limit} units "
            f"(margin {margin}). Shorten the copy or reduce spacing.")
    return used


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def fits(s, size, max_units, font="syne"):
    return measure(s, size, font) <= max_units


def shrink_to_fit(s, size, max_units, font="syne", floor=None):
    """Step a size down until the string fits, never below the legibility
    floor. Returns the size actually usable."""
    while size > (floor or 0) and not fits(s, size, max_units, font):
        size -= 1
    return size


def wrap(text, size, max_units, adv=None, font="syne"):
    """Greedy wrap using measured widths."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if measure(trial, size, font) <= max_units or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def text(x, y, s, cls, size, anchor="start", extra=""):
    return (f'<text x="{x:g}" y="{y:g}" class="{cls}" font-size="{size:g}" '
            f'text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def block(x, y, s, cls, size, max_units, adv=None, lead=1.25, anchor="start", font="syne"):
    lines = wrap(s, size, max_units, font=font)
    return "".join(text(x, y + i * size * lead, ln, cls, size, anchor)
                   for i, ln in enumerate(lines)), len(lines)


# ----------------------------------------------------------------------
# EGNYTE
# ----------------------------------------------------------------------

def egnyte_wide(d):
    """1600 x 900. Left: the sample and the design decision. Middle: the three
    groups. Right: the ranked outcome. The wide layout is used from 760px up,
    where the scale is 0.422, so the smallest type at 34u renders 14.3px.
    Every label is measured and shrunk to fit rather than trusted."""
    o = []
    PAD = 80
    colA, colA_w = PAD, 560
    colB, colB_w = 740, 470
    colC, colC_w = 1290, 230

    o.append(text(colA, 112, d["sample_label"].upper(), "d-label", 34))

    # 23 literal ticks. Not an 8x3 grid, which would imply 24.
    gap = colA_w / (d["count"] - 1)
    for i in range(d["count"]):
        x = colA + i * gap
        o.append(f'<line x1="{x:g}" y1="152" x2="{x:g}" y2="216" class="d-tick"/>')

    size = shrink_to_fit(d["count_line"], 68, colA_w, floor=44)
    o.append(text(colA, 316, d["count_line"], "d-display", size))
    # The meta line is 673u at 34, wider than this column. Shrinking it to
    # fit would land at 28u, which renders 11.8px at the 760px breakpoint and
    # falls under the 12px floor. Splitting on the separator keeps full size.
    for i, part in enumerate(d["meta_line"].split(" · ")):
        o.append(text(colA, 372 + i * 44, part, "d-meta", 34))

    # the design decision, given the accent
    o.append(f'<line x1="{colA}" y1="482" x2="{colA + colA_w}" y2="482" class="d-rule-accent"/>')
    o.append(text(colA, 546, d["pivot_label"].upper(), "d-label-accent", 34))
    body, n = block(colA, 610, d["pivot_line"], "d-display", 50, colA_w)
    o.append(body)
    fan_y = 610 + (n - 1) * 50 * 1.25

    # three groups, equal bands
    o.append(text(colB, 112, d["groups_label"].upper(), "d-label", 34))
    band_h, band_gap, top = 128, 116, 164
    centres = [top + i * (band_h + band_gap) + band_h / 2 for i in range(len(d["groups"]))]

    # A bus connector, not a fan. Three curves sharing one origin produced a
    # visible cusp where they overlapped; a spine with short spurs reads as a
    # diagram and stays clean at any size.
    bus = colB - 66
    o.append(f'<path d="M {colA + colA_w + 26} {fan_y} H {bus}" class="d-link"/>')
    o.append(f'<path d="M {bus} {centres[0]} V {centres[-1]}" class="d-link"/>')
    for cy in centres:
        o.append(f'<path d="M {bus} {cy} H {colB - 16}" class="d-link"/>')
        o.append(f'<circle cx="{bus}" cy="{cy}" r="4" class="d-node"/>')

    for i, (name, hot) in enumerate(d["groups"]):
        y = top + i * (band_h + band_gap)
        o.append(f'<rect x="{colB}" y="{y}" width="{colB_w}" height="{band_h}" rx="8" '
                 f'class="{"d-band-hot" if hot else "d-band"}"/>')
        ns = shrink_to_fit(name, 44, colB_w - 60, floor=34)
        o.append(text(colB + 30, centres[i] + ns * 0.35, name,
                      "d-name-hot" if hot else "d-name", ns))

    # ranked outcome: five unlabelled bars, descending
    for i, ln in enumerate(d["outcome_label"]):
        o.append(text(colC, 112 + i * 44, ln.upper(), "d-label", 34))
    bh, bgap = 40, 92
    for i in range(d["bars"]):
        y = 240 + i * (bh + bgap)
        o.append(f'<rect x="{colC}" y="{y}" width="{colC_w * (1 - i * 0.15):g}" '
                 f'height="{bh}" rx="4" class="{"d-bar-hot" if i == 0 else "d-bar"}"/>')
    check_bounds(240 + (d["bars"] - 1) * (bh + bgap) + bh, 900, "egnyte wide")
    check_bounds(top + len(d["groups"]) * (band_h + band_gap) - band_gap, 900, "egnyte wide bands")
    return "".join(o)


def egnyte_tall(d):
    """1000 x 1250, serving 375px to 759px. At 375px the scale is 0.315, so
    38u renders 12.0px and nothing is set below that."""
    o = []
    PAD = 60
    W = 1000 - 2 * PAD

    o.append(text(PAD, 80, d["sample_label"].upper(), "d-label", 38))
    gap = W / (d["count"] - 1)
    for i in range(d["count"]):
        x = PAD + i * gap
        o.append(f'<line x1="{x:g}" y1="112" x2="{x:g}" y2="172" class="d-tick"/>')

    size = shrink_to_fit(d["count_line"], 70, W, floor=48)
    o.append(text(PAD, 262, d["count_line"], "d-display", size))
    o.append(text(PAD, 316, d["meta_line"], "d-meta", 38))

    o.append(f'<line x1="{PAD}" y1="374" x2="{1000 - PAD}" y2="374" class="d-rule-accent"/>')
    o.append(text(PAD, 430, d["pivot_label"].upper(), "d-label-accent", 38))
    body, n = block(PAD, 490, d["pivot_line"], "d-display", 54, W)
    o.append(body)

    y = 490 + n * 54 * 1.25 + 44
    o.append(text(PAD, y, d["groups_label"].upper(), "d-label", 38))
    y += 34
    band_h, band_gap = 88, 20
    for name, hot in d["groups"]:
        o.append(f'<rect x="{PAD}" y="{y}" width="{W}" height="{band_h}" rx="8" '
                 f'class="{"d-band-hot" if hot else "d-band"}"/>')
        ns = shrink_to_fit(name, 48, W - 56, floor=38)
        o.append(text(PAD + 28, y + band_h / 2 + ns * 0.35, name,
                      "d-name-hot" if hot else "d-name", ns))
        y += band_h + band_gap

    y += 36
    o.append(text(PAD, y, " ".join(d["outcome_label"]).upper(), "d-label", 38))
    y += 34
    bh, bgap = 24, 16
    for i in range(d["bars"]):
        o.append(f'<rect x="{PAD}" y="{y}" width="{W * (1 - i * 0.15):g}" height="{bh}" '
                 f'rx="4" class="{"d-bar-hot" if i == 0 else "d-bar"}"/>')
        y += bh + bgap
    check_bounds(y, 1250, "egnyte tall")
    return "".join(o)


def mercor_wide(d):
    """1600 x 900. The axis is the diagram; the families hang from it.
    Wide carries the PHRASE for each framework."""
    o = []
    PAD = 80
    W = 1600 - 2 * PAD
    ax = 232

    o.append(text(800, 108, d["axis_note"], "d-meta", 34, anchor="middle"))
    o.append(f'<line x1="{PAD}" y1="{ax}" x2="{1600 - PAD}" y2="{ax}" class="d-axis"/>')
    for x, dx in ((PAD, 1), (1600 - PAD, -1)):
        o.append(f'<path d="M {x} {ax} L {x + dx * 24} {ax - 14} L {x + dx * 24} {ax + 14} Z" '
                 f'class="d-axis-cap"/>')
    o.append(text(PAD, ax - 38, d["axis_left"].upper(), "d-label-accent", 34))
    o.append(text(1600 - PAD, ax - 38, d["axis_right"].upper(), "d-label-accent", 34, anchor="end"))

    n = len(d["families"])
    gap = 46
    col_w = (W - gap * (n - 1)) / n
    box_top, box_h = 302, 536
    for i, (family, items) in enumerate(d["families"]):
        x = PAD + i * (col_w + gap)
        o.append(f'<line x1="{x + col_w / 2:g}" y1="{ax}" x2="{x + col_w / 2:g}" '
                 f'y2="{box_top}" class="d-drop"/>')
        o.append(f'<rect x="{x:g}" y="{box_top}" width="{col_w:g}" height="{box_h}" rx="10" '
                 f'class="d-family"/>')
        fs = shrink_to_fit(family, 44, col_w - 60, floor=34)
        o.append(text(x + 30, box_top + 66, family, "d-name", fs))
        o.append(f'<line x1="{x + 30:g}" y1="{box_top + 96}" x2="{x + col_w - 30:g}" '
                 f'y2="{box_top + 96}" class="d-rule"/>')
        y = box_top + 168
        for short, phrase in items:
            o.append(f'<rect x="{x + 30:g}" y="{y - 27}" width="10" height="10" class="d-dot"/>')
            body, lines = block(x + 60, y, phrase, "d-body", 36, col_w - 112)
            o.append(body)
            y += lines * 36 * 1.32 + 46
        check_bounds(y - 52, box_top + box_h, "mercor wide column", margin=8)
    check_bounds(box_top + box_h, 900, "mercor wide")
    return "".join(o)


def mercor_tall(d):
    """1000 x 1250. The axis runs down the left edge, so it stays the spine
    in both orientations. Tall carries the SHORT LABEL, to keep the phone
    uncrowded."""
    o = []
    PAD = 60
    ax = 132
    top, bottom = 214, 1128

    o.append(text(PAD, 92, d["axis_left"].upper(), "d-label-accent", 38))
    o.append(f'<line x1="{ax}" y1="{top}" x2="{ax}" y2="{bottom}" class="d-axis"/>')
    for y, dy in ((top, 1), (bottom, -1)):
        o.append(f'<path d="M {ax} {y} L {ax - 14} {y + dy * 24} L {ax + 14} {y + dy * 24} Z" '
                 f'class="d-axis-cap"/>')
    o.append(text(PAD, bottom + 76, d["axis_right"].upper(), "d-label-accent", 38))

    x = ax + 60
    w = 1000 - PAD - x
    y = top + 6
    for family, items in d["families"]:
        h = 76 + len(items) * 84
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="d-family"/>')
        o.append(f'<line x1="{ax}" y1="{y + 52}" x2="{x}" y2="{y + 52}" class="d-drop"/>')
        fs = shrink_to_fit(family, 46, w - 52, floor=38)
        o.append(text(x + 26, y + 64, family, "d-name", fs))
        yy = y + 134
        for short, phrase in items:
            o.append(f'<rect x="{x + 26}" y="{yy - 29}" width="11" height="11" class="d-dot"/>')
            ss = shrink_to_fit(short, 42, w - 90, floor=38)
            o.append(text(x + 56, yy, short, "d-body", ss))
            yy += 84
        y += h + 38
    check_bounds(y - 38, 1250, "mercor tall")
    return "".join(o)


# ----------------------------------------------------------------------
# assembly
# ----------------------------------------------------------------------

def render(d, wide_fn, tall_fn):
    tid, did = f"{d['slug']}-t", f"{d['slug']}-d"
    return (
        f'<svg class="diagram" viewBox="0 0 1600 900" role="img" '
        f'aria-labelledby="{tid} {did}" preserveAspectRatio="xMidYMid meet">'
        f'<title id="{tid}">{esc(d["title"])}</title>'
        f'<desc id="{did}">{esc(d["desc"])}</desc>'
        f'<g class="d-wide">{wide_fn(d)}</g>'
        f'<g class="d-tall">{tall_fn(d)}</g>'
        f'</svg>'
    )


def build():
    """Returns {slug: svg}. The wide group keeps the 1600x900 viewBox; the
    tall group is emitted against 1000x1250 and swapped in by CSS, which also
    rewrites the viewBox via the sibling <svg class="diagram--tall">."""
    return {
        EGNYTE["slug"]: (
            f'<svg class="diagram diagram--wide" viewBox="0 0 1600 900" role="img" '
            f'aria-labelledby="{EGNYTE["slug"]}-t {EGNYTE["slug"]}-d" '
            f'preserveAspectRatio="xMidYMid meet">'
            f'<title id="{EGNYTE["slug"]}-t">{esc(EGNYTE["title"])}</title>'
            f'<desc id="{EGNYTE["slug"]}-d">{esc(EGNYTE["desc"])}</desc>'
            f'{egnyte_wide(EGNYTE)}</svg>'
            f'<svg class="diagram diagram--tall" viewBox="0 0 1000 1250" '
            f'aria-hidden="true" focusable="false" preserveAspectRatio="xMidYMid meet">'
            f'{egnyte_tall(EGNYTE)}</svg>'
        ),
        MERCOR["slug"]: (
            f'<svg class="diagram diagram--wide" viewBox="0 0 1600 900" role="img" '
            f'aria-labelledby="{MERCOR["slug"]}-t {MERCOR["slug"]}-d" '
            f'preserveAspectRatio="xMidYMid meet">'
            f'<title id="{MERCOR["slug"]}-t">{esc(MERCOR["title"])}</title>'
            f'<desc id="{MERCOR["slug"]}-d">{esc(MERCOR["desc"])}</desc>'
            f'{mercor_wide(MERCOR)}</svg>'
            f'<svg class="diagram diagram--tall" viewBox="0 0 1000 1250" '
            f'aria-hidden="true" focusable="false" preserveAspectRatio="xMidYMid meet">'
            f'{mercor_tall(MERCOR)}</svg>'
        ),
    }


if __name__ == "__main__":
    for slug, svg in build().items():
        print(f"{slug}: {len(svg)} bytes")
