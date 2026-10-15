"""Build docs/manual/index.html from docs/manual/manual.md.

Layout and styling mirror the GRC Readiness Manual (same stylesheet: docs/manual/manual.css).
Markdown conventions used in manual.md:
  <!-- part:intro -->                 starts the "About this manual" section
  <!-- part:N Title -->               starts Part N
  :::plain / :::practice / :::tech / :::shot  ...  :::   three-layer callouts (may be indented in lists)
  ![caption](images/x.png){.wide}     a figure; the alt text becomes the caption
Run:  python tools/build_manual.py      (needs: pip install markdown)
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "manual" / "manual.md"
CSS = ROOT / "docs" / "manual" / "manual.css"
OUT = ROOT / "docs" / "manual" / "index.html"

ENGINE_VERSION = "1.0.0"
INSTRUMENT_VERSION = "1.0.0"

LABELS = {"plain": "In plain terms", "practice": "For A.R.C. practitioners",
          "tech": "Under the hood", "shot": "Screenshot to add"}
EXTS = ["tables", "attr_list", "md_in_html", "fenced_code", "toc", "sane_lists"]


def md(text: str) -> str:
    return markdown.markdown(text, extensions=EXTS, extension_configs={"toc": {"permalink": False}})


def render_layers(text: str) -> tuple[str, dict[str, str]]:
    """Replace ::: blocks with placeholder lines; return text and placeholder -> HTML."""
    out, blocks, lines, i = [], {}, text.split("\n"), 0
    while i < len(lines):
        m = re.match(r"^(\s*):::(plain|practice|tech|shot)\s*$", lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        indent, kind = m.group(1), m.group(2)
        body, i = [], i + 1
        while i < len(lines) and not re.match(r"^\s*:::\s*$", lines[i]):
            body.append(lines[i][len(indent):] if lines[i].startswith(indent) else lines[i].lstrip())
            i += 1
        i += 1
        key = f"LAYERBLOCK{len(blocks)}X"
        inner = md("\n".join(body))
        blocks[key] = (f'<aside class="layer {kind}"><span class="layer-label">{LABELS[kind]}</span>'
                       f"{inner}</aside>")
        out.append(f"{indent}{key}")
    return "\n".join(out), blocks


def figures(h: str) -> str:
    def rep(m):
        attrs = m.group(1)
        alt = re.search(r'alt="([^"]*)"', attrs).group(1)
        src = re.search(r'src="([^"]*)"', attrs).group(1)
        wide = " wide" if re.search(r'class="[^"]*wide', attrs) else ""
        return (f'<figure class="fig{wide}"><img src="{src}" alt="{alt}" loading="lazy">'
                f"<figcaption>{alt}</figcaption></figure>")
    return re.sub(r"<p>\s*<img([^>]*)/?>\s*</p>", rep, h)


def tables(h: str) -> str:
    return re.sub(r"<table>(.*?)</table>", r'<div class="tbl"><table>\1</table></div>', h, flags=re.S)


def build() -> str:
    raw = SRC.read_text()
    parts = re.split(r"<!-- part:(\S+)(?: ([^>]*?))? -->", raw)
    sections, nav = [], []
    # parts = ['', key, title, body, key, title, body, ...]
    for k in range(1, len(parts), 3):
        key, title, body = parts[k], parts[k + 1], parts[k + 2]
        text, blocks = render_layers(body)
        h = md(text)
        for ph, block in blocks.items():
            h = re.sub(rf"<p>\s*{ph}\s*</p>", block, h)
            h = h.replace(ph, block)
        h = tables(figures(h))
        h2s = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', h)
        skip = {"contents", "modules", "index"}
        sub = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in h2s if i not in skip)
        if key == "intro":
            sections.append(f'<section class="part" id="intro">\n{h}\n</section>')
            nav.append(f'<li><a href="#intro"><b>About this manual</b></a><ol>{sub}</ol></li>')
        else:
            pid = f"part-{key}"
            slug = re.sub(r"[^a-z0-9]+", "-", f"part {key} {title}".lower()).strip("-")
            sections.append(f'<section class="part" id="{pid}"><h1 id="{slug}" data-part="{pid}">'
                            f"Part {key}: {html.escape(title)}</h1>\n{h}\n</section>")
            nav.append(f'<li><a href="#{pid}"><b>{html.escape(title)}</b></a><ol>{sub}</ol></li>')

    css = CSS.read_text()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aderhold A.R.C. Manual</title>
<meta name="description" content="User manual for Aderhold A.R.C.: product guide, training guide and troubleshooting.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=Source+Serif+4:opsz,wght@8..60,600&display=swap">
<style>
{css}
/* ONI brand mark on the cover: light artwork by default, dark artwork in dark theme */
.brand{{margin:0 0 18px}}
.brand .logo{{display:block;width:clamp(200px,40vw,310px);height:auto;border-radius:8px}}
.brand .logo-dark{{display:none}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) .brand .logo-light{{display:none}} :root:not([data-theme="light"]) .brand .logo-dark{{display:block}}}}
:root[data-theme="dark"] .brand .logo-light{{display:none}} :root[data-theme="dark"] .brand .logo-dark{{display:block}}
:root[data-theme="light"] .brand .logo-dark{{display:none}} :root[data-theme="light"] .brand .logo-light{{display:block}}
</style></head><body>
<div class="wrap">
<nav class="toc" aria-label="Contents"><p>Contents</p><ol>{''.join(nav)}</ol></nav>
<main>
<header class="cover"><div class="brand"><img class="logo logo-light" src="images/oni-logo-light.png" alt="ONI: The Human Element in AI" width="310" height="146"><img class="logo logo-dark" src="images/oni-logo-dark.png" alt="ONI: The Human Element in AI" width="310" height="146"></div><p class="kicker">Aderhold A.R.C. · an ONI framework · Acceptance · Reliance · Collaboration</p><h1>User manual</h1>
<p class="meta">Engine version {ENGINE_VERSION} · Instrument version {INSTRUMENT_VERSION} · Product guide, training guide and troubleshooting guide</p></header>
{''.join(sections)}
</main></div>
</body></html>
"""


def artifact_fragment(full: str) -> str:
    """The Artifact service adds its own doctype/html/head/body skeleton, so publish the inner content."""
    inner = re.sub(r"(?s)^<!doctype html>\s*<html[^>]*><head>", "", full)
    inner = inner.replace("</head><body>", "", 1)
    return re.sub(r"</body></html>\s*$", "", inner)


def main() -> None:
    full = build()
    OUT.write_text(full)
    (OUT.parent / "artifact.html").write_text(artifact_fragment(full))
    print(f"Wrote {OUT.relative_to(ROOT)} and docs/manual/artifact.html")


if __name__ == "__main__":
    main()
