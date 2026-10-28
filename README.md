Video Calls, Calm
=================

A calm, beginner-friendly manual for feeling un-awkward on video calls — camera and mic
picks on any budget, framing and light tricks, captions, muting manners, screen sharing
without leaking your tabs, AI note-taker bots (with consent etiquette and no-thanks
wording), grandkid call setups, and kind troubleshooting for echo and frozen squares.

Written the way everything from ASDALE DYNAMICS, LLC is written: plain English, step by
step, never condescending. It complements the Family Tech Support Guide; that one is for
the family repair dispatcher, this one is for the person in front of the camera.

What's inside
-------------

- `docs/` — the manual in Markdown, one chapter per file:
  1. Gear: camera and mic picks on any budget (including the $0 tier)
  2. Framing and light tricks — the free polish
  3. Captions: why they help everyone and how to turn them on
  4. Muting manners
  5. Screen sharing without leaking your tabs
  6. AI note-taker bots: consent, asking, and how to say no thanks
  7. Grandkid call setups (ages 2 through 12)
  8. Troubleshooting echo and frozen squares, kindly
- `docs/checklist.md` — the 2-minute pre-call checklist (printable)
- `docs/dial-in-card.md` — the family dial-in card (printable)
- `docs/glossary.md` — plain-English glossary
- `site/` — the built static website (plain HTML, open `site/index.html` in a browser)
- `build.py` / `build.sh` — the build and verification script

Quick start
-----------

Requirements: Python 3.10+ (no third-party packages needed; the `markdown` library is
used when installed and a built-in fallback converter takes over when it isn't).

```sh
./build.sh            # build site/ from docs/
./build.sh --check    # build, then run all verification checks
```

Then open `site/index.html` in any browser. The site is fully local: no network
requests, no external assets, no cookies, no analytics. Print any page
(Ctrl/Cmd + P) and the navigation hides itself for clean printouts.

How the build works
-------------------

`build.py` converts each Markdown file in `docs/` to HTML, wraps it in a warm,
print-friendly template with chapter navigation and prev/next paging, and writes the
result to `site/`. `build.sh --check` (or `python3 build.py --check`) additionally
verifies:

- all 12 source chapters exist and produce pages
- internal links across the whole book resolve
- the LICENSE carries the required copyright line
- required project files are present
- the fallback markdown converter handles the constructs the book uses
  (`python3 build.py --check-fallback` runs that test alone)

License and credit
------------------

MIT License — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
Built by Asdale Dynamics, LLC as part of Dylan Asdale's plain-English AI library, home
of *The Massive AI Manual* and dylanasdale.github.io.

Privacy by design
-----------------

No secrets, API keys, or personal data live in this repository. The guide is education
only — nothing in it is legal, medical, or insurance advice.
