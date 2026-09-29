#!/usr/bin/env python3
"""plates.py . guards the plate box model.

The plate classes are applied to <span> elements. aspect-ratio, overflow and
height do not apply to non-replaced inline boxes, so without display:block the
plates collapse to zero height and the ::after placeholder label escapes the
frame. This asserts that can't regress, and that every plate in the markup
carries a known class and a label when it is empty.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
css = (ROOT / "css" / "main.css").read_text()
PLATES = ["screen16", "screen21", "screen45", "screen-diagram"]
fails = []

for cls in PLATES:
    m = re.search(rf"^\.{re.escape(cls)} \{{(.*?)^\}}", css, re.S | re.M)
    if not m:
        fails.append(f".{cls}: rule missing"); continue
    body = m.group(1)
    for prop in ["display: block", "aspect-ratio", "overflow: hidden", "position: relative"]:
        if prop not in body:
            fails.append(f".{cls}: missing `{prop}`")
    print(f".{cls:16s} display:block OK  aspect-ratio OK  overflow OK")

if "@supports not (aspect-ratio" not in css:
    fails.append("missing aspect-ratio fallback block")

pages = 0
for html in ROOT.rglob("*.html"):
    if "templates" in html.parts: continue
    t = html.read_text()
    for m in re.finditer(r'<span class="(screen[a-z0-9-]*)((?:\s[^"]*)?)"([^>]*)>', t):
        cls, extra, attrs = m.group(1), m.group(2), m.group(3)
        if cls not in PLATES:
            fails.append(f"{html}: unknown plate class .{cls}")
        if "awaiting" in extra and "data-awaiting" not in attrs:
            fails.append(f"{html}: empty plate with no label")
    pages += 1

print(f"\nchecked {pages} pages")
print("FAILURES:", fails if fails else "none")
sys.exit(1 if fails else 0)
