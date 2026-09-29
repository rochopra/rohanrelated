# rohanrelated.com

Personal portfolio for Rohan Chopra. Static HTML/CSS/JS: no framework, no build step, no dependencies.

## Why no framework

Ten fixed pages, one stylesheet, one 30-line script. A static build deploys anywhere in seconds, cannot fail a build, ships zero JavaScript beyond a scroll-reveal enhancement, and makes Lighthouse 90+ the default rather than a target. Content additions are file copies, documented below. If the site ever grows past ~25 pages or needs real templating, migrate to Astro or Next.js then. the HTML here ports directly.

## Structure

```
/
├── index.html                      Home
├── work/egnyte/index.html          Case study. AI adoption research
├── work/mercor/index.html          Case study. AI design evaluation
├── film/index.html                 Film index (+ reel slot)
├── film/journey-to-mars/index.html Case study. NASA CineSpace
├── sound/index.html                Music & audio engineering
├── notes/index.html                Writing index
├── notes/wired-earphones/index.html  Essay: “Bring back the wire” (GENERATED)
├── about/index.html                Bio, résumé, contact
├── content/notes/*.md              Essay sources. markdown + front matter
├── templates/note.html             Page shell for generated essays
├── build.py                        Generates essay pages, notes index, sitemap
├── css/main.css                    All styles (tokens documented at top)
├── js/main.js                      Scroll reveals + ?draft toggle; site works without JS
├── assets/
│   ├── fonts/                      Self-hosted woff2 (Syne, Instrument Sans, IBM Plex Mono)
│   ├── favicon.svg                 Slate mark
│   ├── og.png                      Social preview (1200×630)
│   └── rohan-chopra-resume.pdf     Résumé download
├── sitemap.xml
└── robots.txt
```

## Run locally

Any static server from the site root, e.g.:

```
python3 -m http.server 8000
# → http://localhost:8000
```

(Open via a server, not `file://`, so the absolute paths `/css/…` resolve.)

## Deploy

**Netlify:** drag the folder onto app.netlify.com, or `netlify deploy --prod --dir .`
**Vercel:** `vercel --prod` from the site root (it auto-detects a static site).
Then point `rohanrelated.com` at the deployment in your registrar's DNS and enable HTTPS (both platforms do this automatically).

## Adding an essay

One step: drop a markdown file in `content/notes/` and run `python3 build.py` (stdlib only, no installs). The script generates the essay page, rebuilds the notes index, and regenerates `sitemap.xml`. Front matter fields are documented at the top of `build.py`; mark a piece `status: upcoming` to list it without a page. Never hand-edit generated essay pages or the region between `NOTES:BEGIN`/`NOTES:END` in `notes/index.html`. the build overwrites them.

## Adding a project or film

Copy the closest existing page (`work/mercor/` or the film card pattern in `film/index.html`), edit the content, add a card to the relevant index, and add the path to `STATIC_PAGES` in `build.py`, then run it to refresh the sitemap.

## Design system (summary): gallery wall

Pale, quiet ground. All darkness and drama comes from the imagery, which hangs in Ink letterbox frames like prints on a wall. The page is quiet so the work is loud.

**Palette (6 named values)**

| Token | Hex | Role | Contrast |
|---|---|---|---|
| Wall | `#EEEFF1` | page ground, the 18% gray card lifted | . |
| Mat | `#FAFAFB` | raised surfaces, mat board around a print | . |
| Ink | `#171B22` | text, and the letterbox ground of every frame | 15.0:1 on Wall |
| Ash | `#5A6270` | captions, gallery labels, secondary text | 5.3:1 on Wall |
| Safelight | `#9E3A16` | the accent, at every size | 5.94:1 on Wall, 6.56:1 on Mat |
| Amber | `#E3A339` | marks inside frames only | 8.67:1 on screen-ground |
| screen-ground | `#0D1016` | the letterbox inside every frame | . |
| Fog | `#9FA8B5` | placeholder labels, on screen-ground | 7.93:1 on screen-ground |

Every figure above is emitted by `python3 tools/contrast.py`, which parses the hexes straight out of `css/main.css`. Quote that output rather than retyping numbers, and always name the surface: Fog reads 7.93:1 on screen-ground `#0D1016` where it actually renders, and 7.19:1 against Ink `#171B22` where it does not. Both are correct arithmetic for different pairs, which is exactly how a wrong number gets repeated.

**On the accent.** The previous light-ground accent, Ochre `#8A5F00`, passed contrast but was a darkened yellow, which loses chroma and reads olive. Safelight is a burnt orange-red that keeps its hue when taken down, and clears AA at every size on both surfaces. Mission Amber is retired from the light ground entirely: it measures 1.91:1 on Wall, which fails not just text contrast but the 3:1 floor for graphic marks, so no size or role rescues it there. It survives in one place only, sitting on Ink inside a media frame, where it reads at 7.9:1 and still ties the frames to the original identity.

**Type**: Syne (display, variable 400-800), Instrument Sans (body), IBM Plex Mono (utility). Self-hosted latin subsets, 104KB total.

Syne replaced Fraunces. Because Syne's x-height/em is 0.500 against Fraunces' 0.482, the same nominal size reads about 3.7% larger, so the whole display scale came down 3.6% rather than being left to grow. Weights: hero thesis 500, all titles 560, wordmark 620 to compensate at small size. Tracking is slightly negative throughout, tightest on the hero at -0.022em, because geometric faces open up at display size. Syne ships no italic, so the two places that leaned on display italic were rewritten: the hero accent is carried by colour alone, and the pull quote by weight and measure. Synthetic oblique on a geometric sans is not an acceptable fallback. Body-face italic (`.em`, `<em>`) is unaffected, since Instrument Sans has a real italic.

**Signature**: the slate, quieted. A small mono gallery label with a Safelight tick, set under or beside imagery the way a wall label or contact-sheet annotation works.

**Frames**: media is a framed object with deliberate margin, never camouflage. `figure.hung` wraps a frame plus its label. Add all imagery this way.

**Audio visualizer** (`/sound/`): `js/visualizer.js` analyses a real MP3 through an `AnalyserNode` and draws a mirrored spectrum contour inside a normal `.screen21` plate. No autoplay, and the `AudioContext` is only constructed on the first click, which is both good manners and what autoplay policy requires. Under `prefers-reduced-motion` the animation loop never starts and the plate shows a static horizon; the audio still plays. Without JS or Web Audio it falls back to the native `<audio>` element, and a failed `play()` or a missing file switches to the same fallback rather than leaving a dead button. The canvas is `aria-hidden` with state exposed in a text status line, since a canvas is opaque to a screen reader. To fill it: drop the MP3 at `assets/audio/excerpt.mp3`, set the track title in the slate, and delete the `.vis-empty` span.

**Placeholder plates**: every image slot ships as a real Ink screen carrying its own label, so an unfilled page reads as a prepared mount rather than a broken image. Markup is `<span class="screen21 awaiting" data-awaiting="Key still · 21:9">`. Ratios available: `.screen21` (21:9 heroes), `.screen16` (16:9 default), `.screen45` (4:5 portrait). To fill one: drop an `<img>` inside, remove `class="awaiting"` and the `data-awaiting` attribute, and write real alt text.

**Direction applied to**: home, `/work/`, both case studies, `/film/`, `/film/journey-to-mars/`, `/sound/`, `/notes/`, `/about/`. Nothing is left on the old dark direction.

**Motion** (retuned for the light ground): the load sequence runs slate, thesis, subline at 420ms each with 90/190ms offsets, then the hero frame wipes up over 640ms at a 260ms delay. Text reveals travel 16px with a 220ms fade and a 380ms transform; frames reveal by `clip-path` wipe rather than fade so the drop shadow never ghosts. Fully disabled under `prefers-reduced-motion`, and all content is visible with JS off.


## Navigation and IA

There is no `/work/` index. Nav stays at five items and "Work" points straight at `/work/egnyte/`, the lead case study. Both case studies end with a case pager that links to the other one, which is how a visitor moves between them. On the Egnyte page the nav link carries `aria-current="page"`; on Mercor it carries `aria-current="true"`, because claiming `page` on a link that goes somewhere else would be a lie to a screen reader. `_redirects` and `vercel.json` both 301 `/work/` to `/work/egnyte/` so any existing link survives.

## Case-study diagrams

The two case-study diagrams are inline SVG, generated by `diagrams.py` and injected at build time. No image files, no exports to keep in sync.

**One data definition, two layouts.** SVG cannot reflow, because a viewBox is fixed and CSS cannot change it. So each diagram emits two layout groups from the same `CONTENT` dict: a wide 16:9 arrangement and a tall 4:5 one, with CSS showing exactly one. Content is edited in `diagrams.py`; coordinates are never hand-maintained. Weight is about 7KB inline, 1.5KB gzipped, against roughly 500KB for a PNG pair.

**Reuse.** Each artwork appears twice. Egnyte and Mercor each render on their own case study (as `role="img"` with a `<title>` and `<desc>`) and again on the home page as decorative copies with `aria-hidden`, since the entry title and sentence beside them already carry the meaning. The home Egnyte slot is 21:9 and the diagram is 16:9; `preserveAspectRatio="xMidYMid meet"` centres it, and because the plate ground and the diagram ground are the same value, the extra width simply reads as more letterbox.

**The 760px breakpoint is computed, not chosen.** Plate width is `min(72rem, 100vw - 2*gutter) - 2*frame-padding`. At 640px the plate is 568px and the smallest 34-unit label renders 12.1px, on the floor. At 760px the plate is 674px and the same label renders 14.3px. Below the breakpoint the tall layout is capped at 34rem, or on a small tablet it becomes an enormous portrait slab.

**Text is measured, not estimated.** Wrapping and fitting use real advance widths read from the shipped woff2 files via fontTools. A single per-character constant is wrong for at least one case: Syne runs 0.503em on lowercase and 0.648em on caps, and an estimated average is what let two labels overflow their containers in the first build.

**Overflow fails the build.** `check_bounds()` raises `DiagramOverflow` if any layout runs past its viewBox or a column past its box. It caught a real 5-unit overflow in the Mercor third column on its first run. Editing copy changes wrap counts, which changes total height, so without this the overflow would only appear in a browser.

**Emphasis is Amber, not Safelight.** Safelight `#9E3A16` is the light-ground accent and measures 2.78:1 on the letterbox ground, failing both the 4.5:1 text threshold and the 3:1 graphic floor. Inside a frame is exactly where Amber is sanctioned, at 8.67:1. Same rule as the visualizer play icon. All diagram inks are covered by `tools/contrast.py`.

**Confidentiality.** No participant or department names, no per-segment numbers, no internal metrics, nothing touching the security finding. The three Egnyte bands are equal width by design: real proportions would publish per-segment findings about a named company, and invented ones would be a lie in a diagram. The five roadmap bars are unlabelled, showing that a ranking exists without publishing its contents. Mercor's frameworks are described in original language.

## Copy constraints

House style for this site, applied to the home thesis, both case studies, and About:

* Em dashes: zero in site copy. The only remaining ones are the 8 in the wired-earphones essay, which Rohan is rewriting.
* The "not X, but Y" negation-reframe appears exactly once sitewide, in the Egnyte finding callout, where two competing hypotheses make the contrast do real work.
* Sections end on plain statements. No closing epigrams.
* Vary sentence length deliberately. Short fragments are welcome next to long sentences.
* Not every sentence needs a turn. Plain is fine.

## Accessibility & performance notes

Semantic landmarks, skip link, visible focus states, `aria-current` nav, alt text required on all images (none ship yet. see TODOs), AA contrast throughout (Graphite `#8B93A0` on Void ≈ 5.5:1; Amber is used at large/mono sizes only). Fonts are preloaded on the home page; the YouTube embed is lazy-loaded; no layout shift (embeds sit in fixed-ratio frames).

## TODO placeholders and draft mode

`[TODO]` blocks are **hidden from visitors by default**. they render only in draft mode. Append `?draft` to any URL (e.g. `rohanrelated.com/film/?draft`) to see them while editing. Nothing needs to be removed before deploy.

## Outstanding TODOs

Assets Rohan is supplying. Every slot renders as a labeled placeholder, so the site is shippable and legible before any of them land. Eleven plates total, down from sixteen.

1. **Résumé PDF** . the file supplied to the project was a ZIP-of-images container, not a PDF. `assets/rohan-chopra-resume.pdf` is now a valid single-page PDF rebuilt from the page image inside it, verified downloading as `application/pdf` from the header, footer, and About links. The source image is 952x1260 px, readable on screen and soft in print. Replace with a direct PDF export when available, same filename.
2. ~~Diagram artwork~~ . done. Both diagrams are inline SVG generated from `diagrams.py`; nothing to supply. Previously specified as:

   | Artwork | Export | Used on |
   |---|---|---|
   | `egnyte-segmentation.png` | 2400x1350 (16:9) | `/work/egnyte/` |
   | `egnyte-segmentation-portrait.png` | 2000x2500 (4:5) | `/work/egnyte/` below 640px |
   | `egnyte-segmentation-wide.png` | 2400x1029 (21:9) | home, lead entry |
   | `mercor-frameworks.png` | 2400x1350 (16:9) | `/work/mercor/` **and** home |
   | `mercor-frameworks-portrait.png` | 2000x2500 (4:5) | `/work/mercor/` below 640px |

3. **Audio excerpt** . 30-45s MP3 at `assets/audio/excerpt.mp3`, plus the track title for the slate.
4. **Stills** . home hero 21:9, Journey to Mars key frame 21:9, and the four contact-sheet frames.
5. **Portrait** . 4:5, minimum 1200px short edge, for `/about/`.
6. **Featured tracks** . name 2-3 releases with links on `/sound/`.
7. **Captions** . verify captions are enabled on the Journey to Mars YouTube upload; the embed inherits them.

Find every placeholder: `grep -rn "TODO" --include="*.html" .`
