# STATUS

**Repo:** video-calls-comfort-guide
**Date:** 2026-10-28
**Commit:** 69e45a3 (root commit, main branch)
**Author of work:** Asdale Dynamics, LLC — clean, Git-identity-only commit; no
co-authored-by trailers; never pushed; no remote; nothing published.

## What was built

A calm, beginner-friendly manual for feeling un-awkward on video calls — markdown
sources in `docs/`, rendered into a fully static, local-first HTML site in `site/`.

- **Chapters (`docs/`, 12 files):**
  - `index.md` — warm introduction, table of contents, the guide's promise
  - `01-gear.md` — camera and mic picks by budget tier, phone-as-webcam, microphone privacy
  - `02-framing-light.md` — eye-level rule, headroom rule, look-around test, wave test
  - `03-captions.md` — how captions work and how to turn them on in Zoom / Meet / Teams / FaceTime
  - `04-muting.md` — mute etiquette, when to mute, push to talk, group-call volley
  - `05-screen-share.md` — share the one window, never the whole screen; the 10-second sweep
  - `06-ai-note-takers.md` — what the bots do, consent habit, how hosts turn them off,
    kind "no-thanks" wording for both sides
  - `07-grandkid-calls.md` — setups by kid age band, reading together over video, parent kindnesses
  - `08-troubleshooting.md` — echo and frozen squares with kind language for both
  - `checklist.md` — the 2-minute printable pre-call checklist
  - `dial-in-card.md` — the printable family dial-in card (apps, IDs, plan B, house rules)
  - `glossary.md` — plain-English glossary of video-call jargon
- **Static site (`site/`, 12 HTML pages):** warm print-friendly template, chapter nav
  with current-page highlight, prev/next paging, embedded CSS (no external assets,
  no network requests, no analytics, no cookies). Print CSS hides chrome for clean printouts.
- **Build system:** `build.py` (Python 3.10+, stdlib-first) converts Markdown to HTML;
  uses the `markdown` library when present and falls back to a built-in converter that
  covers every construct the guide uses (headings, lists, checkboxes, tables, fenced
  code, blockquotes, hr, inline emphasis/code/links). `build.sh` wraps it.
- **Legal/identity:** MIT `LICENSE` with the exact line
  `Copyright (c) 2026 Asdale Dynamics, LLC`; `README.md` credits Asdale Dynamics, LLC.
  No secrets, API keys, or personal data anywhere in the repository.

## How to run it

```sh
./build.sh                 # rebuild site/ from docs/
./build.sh --check         # rebuild + run all verification checks
python3 build.py --check-fallback   # test only the fallback markdown converter
```

Then open `site/index.html` in any browser — fully offline-capable, or serve it with
anything like `python3 -m http.server --directory site`.

## Verification results (all passing, exit code 0)

- `./build.sh --check`
  - LICENSE copyright line: ok
  - required project files present (README.md, docs, site, build.py, build.sh): ok
  - 12/12 chapters found and 12/12 HTML pages built: ok
  - all internal links across all pages resolve: ok
  - no embedded images or external asset references (keeps the site local-only): ok
- `python3 build.py --check-fallback` — fallback converter handles every markdown
  construct used by the book: ok
- `python3 -m py_compile build.py` — no syntax errors: ok
- Manual spot checks: titles and current-page nav render correctly in all pages;
  footer license line present; site served successfully via a local `http.server`.
- Clean-room check: `docs/index.md` also renders correctly through the fallback
  converter path (as it would if the `markdown` package were unavailable).

## Known gaps / possible next steps

- Chapter navigation is a flat chip list; chapter counts fine at 12 pages but a
  sidebar or search would help if the book grows past ~20 pages.
- Zoom/Meet/Teams menu locations drift with app updates; the guide describes the
  menu paths as of writing — worth a yearly re-check against current UIs.
- The dial-in card is a fill-by-hand template; a small local companion web form that
  generates a filled card (still offline) could be a nice follow-up.
- Companion repo (family-tech-support-guide) is referenced by name in the intro
  and README but not hyperlinked, since no URL was provided here.
- No automated visual regression or browser snapshot tests; verification is build +
  link + content checks plus manual inspection.
