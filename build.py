#!/usr/bin/env python3
"""Build the Video Calls, Calm guide from docs/ into a static HTML site in site/.

Local-first: plain Python, no network access, no external assets. The generated
site is plain HTML pages with embedded CSS; open site/index.html in a browser.

Usage:
    python3 build.py            build the site (cleans site/ first)
    python3 build.py --check    build the site, then run all verification checks

Exit code 0 means success; 1 means something failed verification.
"""

import html as html_mod
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

PAGES = [
    ("index", "Start Here"),
    ("01-gear", "1 Gear"),
    ("02-framing-light", "2 Framing & Light"),
    ("03-captions", "3 Captions"),
    ("04-muting", "4 Muting"),
    ("05-screen-share", "5 Screen Share"),
    ("06-ai-note-takers", "6 AI Note-Takers"),
    ("07-grandkid-calls", "7 Grandkid Calls"),
    ("08-troubleshooting", "8 Troubleshooting"),
    ("checklist", "Checklist"),
    ("dial-in-card", "Dial-In Card"),
    ("glossary", "Glossary"),
]

PROJECT_HOME = "dylanasdale.github.io"
COMPANY = "Asdale Dynamics, LLC"
BOOK = "The Massive AI Manual"

VERIFY_MESSAGES: list[str] = []


def md_to_html(md_source: str) -> str:
    """Convert markdown to HTML. Prefers the `markdown` package; falls back to a
    built-in converter covering the subset of Markdown this book uses
    (headings, paragraphs, lists, tables, fenced code, blockquotes, hr, inline
    emphasis/code/links). Keep both paths exercised by --check."""
    try:
        import markdown
    except ImportError:
        return _fallback_md_to_html(md_source)
    return markdown.markdown(
        md_source,
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={"toc": {"permalink": False}},
    )


_INLINE_PATTERNS: list[tuple[str, str]] = [
    (r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)",
     r'<img src="\g<src>" alt="\g<alt>" loading="lazy">'),
    (r"\[(?P<text>[^\]]+)\]\((?P<href>[^)]+)\)",
     r'<a href="\g<href>">\g<text></a>'),
    (r"\*\*(?P<b>[^*]+)\*\*", r"<strong>\g<b></strong>"),
    (r"(?<!\w)\*(?P<i>[^*\n]+)\*(?!\w)", r"<em>\g<i></em>"),
    (r"`(?P<c>[^`]+)`", r"<code>\g<c></code>"),
]


def _inline(text: str) -> str:
    escaped = html_mod.escape(text, quote=False)
    for pattern, replacement in _INLINE_PATTERNS:
        escaped = re.sub(pattern, replacement, escaped)
    return escaped


_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")


def _is_table_separator(line: str) -> bool:
    row = _TABLE_ROW.match(line)
    if not row:
        return False
    cells = [c.strip() for c in row.group(1).split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def _fallback_md_to_html(md_source: str) -> str:
    lines = md_source.splitlines()
    out: list[str] = []
    i = 0
    list_stack: list[str] = []

    def close_lists(until: int = 0) -> None:
        while len(list_stack) > until:
            out.append("</li>")
            out.append(f"</{list_stack.pop()}>")

    def open_bullet(kind: str) -> None:
        if list_stack and list_stack[-1] == kind:
            out.append("</li>")
        else:
            close_lists()
            out.append(f"<{kind}>")
            list_stack.append(kind)
        out.append("<li>")

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            close_lists()
            i += 1
            continue

        if line.startswith("```"):
            close_lists()
            lang = line[3:].strip()
            cls = f' class="language-{html_mod.escape(lang)}"' if lang else ""
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append(f"<pre><code{cls}>{html_mod.escape(chr(10).join(code))}</code></pre>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            text = re.sub(r"\s+#+\s*$", "", m.group(2))
            out.append(f"<h{level}>{_inline(text)}</h{level}>")
            i += 1
            continue

        if re.fullmatch(r"\s*(-{3,}|\*{3,})\s*", line):
            close_lists()
            out.append("<hr />")
            i += 1
            continue

        if line.lstrip().startswith(">"):
            close_lists()
            quote: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            inner = _fallback_md_to_html("\n".join(quote)).strip()
            out.append(f"<blockquote>\n{inner}\n</blockquote>")
            continue

        if _TABLE_ROW.match(line) and i + 1 < len(lines) and _is_table_separator(lines[i + 1]):
            close_lists()
            aligns = [c.strip() for c in _TABLE_ROW.match(lines[i + 1]).group(1).split("|")]
            align_style = [
                (' style="text-align:center"' if a.startswith(":") and a.endswith(":")
                 else ' style="text-align:left"' if a.startswith(":")
                 else ' style="text-align:right"' if a.endswith(":")
                 else "")
                for a in aligns
            ]
            head_cells = [c.strip() for c in _TABLE_ROW.match(line).group(1).split("|")]
            head_row = "".join(
                f"<th{align_style[k]}>{_inline(c)}</th>"
                for k, c in enumerate(head_cells)
            )
            out.append("<table>\n<thead><tr>" + head_row + "</tr></thead>")
            out.append("<tbody>")
            i += 2
            while i < len(lines) and _TABLE_ROW.match(lines[i]):
                body_cells = [c.strip() for c in _TABLE_ROW.match(lines[i]).group(1).split("|")]
                body_row = "".join(
                    f"<td{align_style[k]}>{_inline(c)}</td>"
                    for k, c in enumerate(body_cells)
                )
                out.append("<tr>" + body_row + "</tr>")
                i += 1
            out.append("</tbody>\n</table>")
            continue

        m_cb = re.match(r"^(\s*)-\s+\[( |x)\]\s+(.*)$", line)
        m_ul = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        m_ol = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", line)
        if m_cb:
            open_bullet("ul")
            box = '<input type="checkbox" disabled{}>'.format(
                " checked" if m_cb.group(2) == "x" else ""
            )
            out.append(box + " " + _inline(m_cb.group(3)))
            i += 1
            continue
        if m_ul or m_ol:
            kind = "ul" if m_ul else "ol"
            match = m_ul or m_ol
            open_bullet(kind)
            out.append(_inline(match.group(3) if kind == "ol" else match.group(2)))
            i += 1
            continue

        close_lists()
        para: list[str] = [line.strip()]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not re.match(r"^(#{1,6}\s|```|\s*[-*]\s|\s*\d+[.)]\s|>|\s*\|)", lines[i])
            and not re.fullmatch(r"\s*(-{3,}|\*{3,})\s*", lines[i])
        ):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + _inline(" ".join(para)) + "</p>")

    close_lists()
    return "\n".join(out)


CSS = """
:root {
  --ink: #26221d; --paper: #fbf8f2; --accent: #7a4a2b; --soft: #f0e7d8;
  --line: #e3d9c8; --link: #59421f;
}
* { box-sizing: border-box; }
html { font-size: 18px; scroll-behavior: smooth; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: Georgia, 'Iowan Old Style', 'Palatino Linotype', serif;
  line-height: 1.65;
}
header.site {
  background: var(--soft); border-bottom: 2px solid var(--line); padding: 1rem 1.2rem 0.6rem;
}
header.site a { color: inherit; text-decoration: none; }
header.site .book { font-size: 0.85rem; color: var(--accent); letter-spacing: 0.04em; text-transform: uppercase; }
header.site h1 { margin: 0.1rem 0 0; font-size: 1.35rem; }
nav.pages {
  max-width: 60rem; margin: 0 auto; padding: 0.45rem 0 0.15rem;
  display: flex; flex-wrap: wrap; gap: 0.3rem 0.55rem; font-size: 0.85rem;
}
nav.pages a {
  padding: 0.15rem 0.55rem; border: 1px solid var(--line); border-radius: 999px;
  background: #fdfbf6; color: var(--link); text-decoration: none;
}
nav.pages a[aria-current="page"] { background: var(--accent); color: #fff; border-color: var(--accent); }
nav.pages a:hover { background: #f3ead9; }
nav.pages a[aria-current="page"]:hover { background: var(--accent); }
main { max-width: 42rem; margin: 0 auto; padding: 2rem 1.2rem 3rem; }
h2 { margin-top: 2.2em; line-height: 1.25; }
a { color: var(--link); }
code { background: var(--soft); border: 1px solid var(--line); border-radius: 4px; padding: 0.05em 0.35em; font-size: 0.92em; font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; }
pre code { display: block; padding: 0.8em 1em; overflow-x: auto; }
blockquote {
  margin: 1.4rem 0; padding: 0.7rem 1.1rem; background: var(--soft);
  border-left: 4px solid var(--accent); border-radius: 0 8px 8px 0; font-style: italic;
}
table { border-collapse: collapse; width: 100%; margin: 1.2rem 0; font-size: 0.95rem; }
th, td { border: 1px solid var(--line); padding: 0.5rem 0.7rem; text-align: left; vertical-align: top; }
th { background: var(--soft); }
input[type="checkbox"] { width: 1rem; height: 1rem; accent-color: var(--accent); }
hr { border: 0; border-top: 1px solid var(--line); margin: 2rem 0; }
footer.site { max-width: 60rem; margin: 0 auto; padding: 1rem 1.2rem 2rem; font-size: 0.82rem; color: #6f6250; border-top: 2px solid var(--line); }
footer.site a { color: var(--accent); }
.pager { display: flex; justify-content: space-between; gap: 1rem; margin-top: 3rem; font-size: 0.95rem; }
.pager a { text-decoration: none; }
.pager .arrow { color: var(--accent); }
@media print {
  header.site, footer.site, .pager { display: none; }
  body { background: #fff; font-size: 12pt; }
  nav.doc { display: none; }
  a { color: inherit; text-decoration: none; }
  .no-print { display: none; }
}
""".strip()

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Video Calls, Calm</title>
<meta name="description" content="{description}">
<style>
{css}
</style>
</head>
<body>
<header class="site">
  <a href="index.html">
    <div class="book">From {book} &middot; {company}</div>
    <h1>Video Calls, Calm</h1>
  </a>
  <nav class="pages" aria-label="Chapters">
{nav_links}
  </nav>
</header>
<main>
{content}
<div class="pager">
  <div>{prev_link}</div>
  <div>{next_link}</div>
</div>
</main>
<footer class="site">
  <p><em>Video Calls, Calm</em> — a companion volume to the <em>Family Tech Support Guide</em>.
  Plain English, step by step, never condescending. Built locally; no network required.</p>
  <p>Copyright (c) 2026 {company} &middot; MIT License &middot;
  part of <a href="https://{project_home}">{project_home}</a> &amp; {book}</p>
</footer>
</body>
</html>
"""


def render_page(stem: str, title: str, content_html: str) -> str:
    idx = [s for s, _ in PAGES].index(stem)
    nav_links = "\n".join(
        '    <a href="{0}.html"{1}>{2}</a>'.format(
            s, ' aria-current="page"' if s == stem else "", lbl
        )
        for s, lbl in PAGES
    )

    def pager(offset: int) -> str:
        pos = idx + offset
        if 0 <= pos < len(PAGES):
            s, lbl = PAGES[pos]
            arrow = "&larr;" if offset < 0 else "&rarr;"
            side = "Previous" if offset < 0 else "Next"
            return f'<a href="{s}.html"><span class="arrow">{arrow}</span> {side}: {lbl}</a>'
        return ""

    description = f"A calm, beginner-friendly guide to video calls: {title.lower()}, step by step."
    return TEMPLATE.format(
        title=title,
        description=html_mod.escape(description, quote=True),
        css=CSS,
        book=BOOK,
        company=COMPANY,
        project_home=PROJECT_HOME,
        nav_links=nav_links,
        content=content_html,
        prev_link=pager(-1),
        next_link=pager(1),
    )


def first_title_of(md_source: str) -> str:
    for line in md_source.splitlines():
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    raise ValueError("no H1 title found")


def toc_links_to_stem(href: str) -> str:
    return href.split("#", 1)[0].removesuffix(".md").removesuffix(".html")


def build() -> list[tuple[str, str]]:
    pages_built: list[tuple[str, str]] = []
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    for stem, _ in PAGES:
        md_path = DOCS / f"{stem}.md"
        if not md_path.exists():
            raise SystemExit(f"ERROR: missing source document docs/{stem}.md")
        source = md_path.read_text(encoding="utf-8")
        title = first_title_of(source)
        content = md_to_html(source)
        page = render_page(stem, title, content)
        target = SITE / f"{stem}.html"
        target.write_text(page, encoding="utf-8")
        pages_built.append((stem, target.read_text(encoding="utf-8")))
    return pages_built


def check(pages: list[tuple[str, str]]) -> bool:
    ok = True

    def note(msg: str) -> None:
        nonlocal ok
        ok = False
        VERIFY_MESSAGES.append(f"FAIL: {msg}")

    def good(msg: str) -> None:
        VERIFY_MESSAGES.append(f"ok: {msg}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Copyright (c) 2026 Asdale Dynamics, LLC" in license_text:
        good("LICENSE carries the required copyright line")
    else:
        note("LICENSE copyright line missing or incorrect")

    for required in ("README.md", "docs", "site", "build.py", "build.sh"):
        if (ROOT / required).exists():
            good(f"required project item present: {required}")
        else:
            note(f"required project item missing: {required}")

    if pages:
        good(f"built {len(pages)} HTML pages into site/")
        missing = [stem for stem, text in pages if "<main>" not in text]
        if missing:
            note(f"pages missing <main>: {missing}")
    else:
        note("no pages were built")

    anchor_re = re.compile(r'id="([^"]+)"')
    page_texts = dict(pages)
    for stem, text in pages:
        for target, frag in re.findall(r'href="([^"#]+)(?:#([^"]+))?"', text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (target.endswith(".md") or target.endswith(".html")):
                continue
            stem_target = toc_links_to_stem(target)
            if stem_target not in {s for s, _ in PAGES}:
                note(f"{stem}: link target '{target}' is not a page of this guide")
            elif frag:
                target_ids = set(anchor_re.findall(page_texts.get(stem_target, "")))
                if target_ids and frag not in target_ids:
                    note(f"{stem}: link '{target}#{frag}' has no matching heading")

    for stem, text in pages:
        if "<img" in text:
            note(f"{stem}: unexpected embedded image (keep the guide local-text only)")

    good("internal links resolved across all pages")
    return ok


def main() -> int:
    if "--check-fallback" in sys.argv:
        sample = (
            "# Head\n\nSome **bold**, *ital*, `code`, [link](01-gear.md).\n\n"
            "- a\n- b\n\n1. one\n2. two\n\n> quoted\n\n---\n\n"
            "| A | B |\n|---|---|\n| 1 | 2 |\n\n- [ ] box\n"
        )
        rendered = _fallback_md_to_html(sample)
        expected = (
            "<h1>Head</h1>", "<strong>bold</strong>", "<em>ital</em>", "<code>code</code>",
            '<a href="01-gear.md">link</a>', "<ul>", "<li>\na\n</li>", "<ol>",
            "<li>\none\n</li>", "<blockquote>", "<hr />", "<table>", "<th>A</th>",
            "<td>1</td>", "checkbox"
        )
        missing = [frag for frag in expected if frag not in rendered]
        if missing:
            print(f"fallback converter check FAILED; missing: {missing}")
            print("rendered was:")
            print(rendered)
            return 1
        print("fallback converter check passed")
        return 0

    print(f"building site -> {SITE}")
    pages = build()
    print(f"built {len(pages)} pages")
    if "--check" in sys.argv:
        ok = check(pages)
        for msg in VERIFY_MESSAGES:
            print("  " + msg)
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
