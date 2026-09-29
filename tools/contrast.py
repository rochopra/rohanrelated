#!/usr/bin/env python3
"""contrast.py . authoritative WCAG audit for rohanrelated.com.

Hex values are parsed out of css/main.css, never retyped, so the numbers in
the README and in any write-up cannot drift from what actually ships.
Each row names the surface the colour actually renders on. Run:  python3 tools/contrast.py
"""
import re, sys
from pathlib import Path

CSS = Path(__file__).parent.parent / "css" / "main.css"
tok = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", CSS.read_text()))

def lum(h):
    h = h.lstrip("#"); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

T = lambda k: tok[k]
# (description, fg token, bg token, px, bold, kind)
ROWS = [
    ("body text",                      "ink",       "wall",          17, False, "text"),
    ("body text on a Mat surface",      "ink",       "mat",           17, False, "text"),
    ("Ash secondary prose",             "ash",       "wall",          17, False, "text"),
    ("Ash secondary on Mat",            "ash",       "mat",           17, False, "text"),
    ("Ash slate / caption",             "ash",       "wall",          12, False, "text"),
    ("Ash slate on Mat",                "ash",       "mat",           12, False, "text"),
    ("Ash sheet label (smallest text)", "ash",       "wall",          11, False, "text"),
    ("Ash nav",                         "ash",       "wall",          13, False, "text"),
    ("Safelight kicker",                "safelight", "wall",          11, True,  "text"),
    ("Safelight link in prose",         "safelight", "wall",          17, False, "text"),
    ("Safelight on Mat callout",        "safelight", "mat",           11, True,  "text"),
    ("Fog placeholder label",           "fog",       "screen-ground", 12, False, "text"),
    ("Safelight tick, smallest (10x2)", "safelight", "wall",           0, False, "graphic"),
    ("Safelight tick on Mat",           "safelight", "mat",            0, False, "graphic"),
    ("Amber mark inside a frame",       "amber",     "screen-ground",  0, False, "graphic"),
    ("Seam hairline",                   "seam",      "wall",           0, False, "decorative"),
    # diagram inks, all rendered on the letterbox ground inside a frame
    ("Diagram display type",            "wall",      "screen-ground", 26, False, "text"),
    ("Diagram labels and body",         "fog",       "screen-ground", 14, False, "text"),
    ("Diagram emphasis type",           "amber",     "screen-ground", 14, False, "text"),
    ("Diagram axis and rules",          "amber",     "screen-ground",  0, False, "graphic"),
    ("Diagram ticks and links",         "fog",       "screen-ground",  0, False, "graphic"),
]

def need(px, bold, kind):
    if kind == "decorative": return 0.0
    if kind == "graphic": return 3.0
    return 3.0 if (px >= 24 or (bold and px >= 19)) else 4.5

fails = []
print(f"{'pair':34s} {'on':15s} {'ratio':>7s} {'need':>5s}  verdict")
print("-" * 76)
for desc, fg, bg, px, bold, kind in ROWS:
    r, n = ratio(T(fg), T(bg)), need(px, bold, kind)
    ok = r >= n
    if not ok: fails.append((desc, round(r, 2), n))
    print(f"{desc:34s} {T(bg).upper():15s} {r:7.2f} {n if n else '-':>5}  {'PASS' if ok else 'FAIL'}")

print("\nRetired values, kept here so the reasoning stays visible:")
for desc, fg, bg in [("Mission Amber as a light-ground accent", "amber", "wall"),
                     ("Amber if it sat on Ink frame padding",    "amber", "ink"),
                     ("Fog if it sat on Ink frame padding",      "fog",   "ink"),
                     ("Safelight if used inside a frame",        "safelight", "screen-ground")]:
    print(f"  {desc:40s} {ratio(T(fg), T(bg)):.2f}:1 on {T(bg).upper()}")
print(f"  {'Ochre #8A5F00, the previous accent':40s} {ratio('#8a5f00', T('wall')):.2f}:1 on {T('wall').upper()}")

print("\nFAILURES:", fails if fails else "none")
sys.exit(1 if fails else 0)
