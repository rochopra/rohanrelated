#!/usr/bin/env python3
"""build.py — rohanrelated.com content build. Python 3 stdlib only.

Reads content/notes/*.md (front matter + markdown) and generates:
  1. notes/<slug>/index.html          one page per published essay
  2. notes/index.html                 the list between NOTES:BEGIN / NOTES:END markers
  3. sitemap.xml                      static pages + published essay URLs

Run from the site root:  python3 build.py

To add an essay: drop a .md file in content/notes/ and run this script.
Front matter fields:
  title (required)      slug (required)        date YYYY-MM-DD (required, sorts)
  status               published | upcoming (default published)
  display_date         e.g. "July 2026"       read: e.g. "5 min"
  description          meta/OG description    standfirst: intro under the title
  index_blurb          one-liner on the notes index (falls back to description)

Markdown supported (deliberately small): paragraphs, *italic*, **bold**,
[link](url), and ## subheads. That is all an essay here needs.
"""

import html
import re

import diagrams
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content" / "notes"
TEMPLATE = (ROOT / "templates" / "note.html").read_text()

STATIC_PAGES = [
    "", "work/egnyte/", "work/mercor/",
    "film/", "film/journey-to-mars/", "sound/", "notes/", "about/",
]

# ---------- parsing ----------

def parse_front_matter(text, path):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        sys.exit(f"error: {path} has no front matter block")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for req in ("title", "slug", "date"):
        if req not in meta:
            sys.exit(f"error: {path} missing required field '{req}'")
    meta.setdefault("status", "published")
    return meta, m.group(2).strip()


def md_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def md_to_html(body):
    out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        if block.startswith("## "):
            out.append(f"        <h2>{md_inline(block[3:])}</h2>")
        else:
            text = md_inline(" ".join(line.strip() for line in block.splitlines()))
            out.append(f"        <p>{text}</p>")
    return "\n\n".join(out)


# ---------- generation ----------

def render_note(meta, body_html, number, source_name):
    page = TEMPLATE
    for k, v in {
        "SOURCE": source_name,
        "TITLE": html.escape(meta["title"], quote=False),
        "DESCRIPTION": html.escape(meta.get("description", meta["title"])),
        "SLUG": meta["slug"],
        "NUMBER": f"{number:02d}",
        "DISPLAY_DATE": meta.get("display_date", meta["date"]),
        "READ": meta.get("read", ""),
        "STANDFIRST": html.escape(meta.get("standfirst", ""), quote=False),
        "BODY": body_html,
    }.items():
        page = page.replace("{{" + k + "}}", v)
    return page


def index_entry(meta, published):
    if published:
        blurb = html.escape(meta.get("index_blurb", meta.get("description", "")), quote=False)
        meta_line = " · ".join(x for x in ["Essay", meta.get("display_date", ""), f"{meta.get('read','')} read" if meta.get("read") else ""] if x)
        return (
            f'          <li class="reveal">\n'
            f'            <h3><a href="/notes/{meta["slug"]}/">{html.escape(meta["title"], quote=False)}</a></h3>\n'
            f'            <p>{blurb}</p>\n'
            f'            <span class="meta">{meta_line}</span>\n'
            f'          </li>'
        )
    return (
        f'          <li class="upcoming reveal">\n'
        f'            <h3>{html.escape(meta["title"], quote=False)}</h3>\n'
        f'            <p>In progress.</p>\n'
        f'            <span class="meta">Upcoming</span>\n'
        f'          </li>'
    )


def main():
    posts = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(), path)
        posts.append((meta, body, path.name))

    published = [p for p in posts if p[0]["status"] == "published"]
    upcoming = [p for p in posts if p[0]["status"] != "published"]
    published.sort(key=lambda p: p[0]["date"])          # oldest first → Note 01, 02…
    upcoming.sort(key=lambda p: p[0]["date"])

    # 1. essay pages
    for n, (meta, body, name) in enumerate(published, start=1):
        out_dir = ROOT / "notes" / meta["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(render_note(meta, md_to_html(body), n, name))
        print(f"  built notes/{meta['slug']}/index.html  (Note {n:02d})")

    # 2. notes index — replace the marked region, newest published first
    entries = [index_entry(m, True) for m, _, _ in reversed(published)]
    entries += [index_entry(m, False) for m, _, _ in upcoming]
    index_path = ROOT / "notes" / "index.html"
    src = index_path.read_text()
    begin, end = "<!-- NOTES:BEGIN -->", "<!-- NOTES:END -->"
    if begin not in src or end not in src:
        sys.exit("error: notes/index.html is missing NOTES:BEGIN / NOTES:END markers")
    head, rest = src.split(begin, 1)
    _, tail = rest.split(end, 1)
    index_path.write_text(head + begin + "\n" + "\n".join(entries) + "\n          " + end + tail)
    print("  built notes/index.html")

    # 3. case-study diagrams, generated from diagrams.py
    svgs = diagrams.build()
    targets = {"egnyte-segmentation": ROOT / "work" / "egnyte" / "index.html",
               "mercor-frameworks": ROOT / "work" / "mercor" / "index.html"}
    for slug, svg in svgs.items():
        path = targets[slug]
        src = path.read_text()
        b0, b1 = f"<!-- DIAGRAM:{slug}:BEGIN -->", f"<!-- DIAGRAM:{slug}:END -->"
        if b0 not in src or b1 not in src:
            sys.exit(f"error: {path} is missing the {slug} diagram markers")
        head, rest = src.split(b0, 1)
        _, tail = rest.split(b1, 1)
        path.write_text(head + b0 + svg + b1 + tail)
        print(f"  built {slug} diagram ({len(svg)} bytes) into {path.relative_to(ROOT)}")

    # 3b. the same two diagrams, reused on the home page. One artwork, two
    #     placements. The home copies are decorative: the entry title and
    #     sentence beside them already carry the meaning, so announcing the
    #     full <desc> again would just be noise in a screen reader.
    home = ROOT / "index.html"
    src = home.read_text()
    for slug, svg in svgs.items():
        deco = re.sub(r'role="img" aria-labelledby="[^"]*"', 'aria-hidden="true" focusable="false"', svg)
        deco = re.sub(r'<title id="[^"]*">.*?</title>', '', deco)
        deco = re.sub(r'<desc id="[^"]*">.*?</desc>', '', deco)
        b0, b1 = f"<!-- HOMEDIAGRAM:{slug}:BEGIN -->", f"<!-- HOMEDIAGRAM:{slug}:END -->"
        if b0 not in src or b1 not in src:
            sys.exit(f"error: index.html is missing the {slug} home markers")
        head, rest = src.split(b0, 1)
        _, tail = rest.split(b1, 1)
        src = head + b0 + deco + b1 + tail
    home.write_text(src)
    print(f"  built {len(svgs)} diagrams into index.html (decorative copies)")

    # 4. sitemap
    urls = [f"https://rohanrelated.com/{p}" for p in STATIC_PAGES]
    urls += [f"https://rohanrelated.com/notes/{m['slug']}/" for m, _, _ in published]
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap)
    print("  built sitemap.xml")
    print(f"done — {len(published)} published, {len(upcoming)} upcoming")


if __name__ == "__main__":
    main()
