# -*- coding: utf-8 -*-
"""Build the reviewer-preview copy of the site into build/preview/.

The preview is published to a throwaway repository (SOLARMA/sito-anteprima) so
that it can be read online before the real site changes. It differs from the
published site in exactly three ways, all of them deliberate:

  * a staging banner at the top of every page, so nobody mistakes it for live;
  * noindex/nofollow plus a blanket robots.txt, so it is never indexed;
  * no CNAME file, so it cannot interfere with the www.solarma.it domain.

Usage:  python3 tools/build-preview.py
"""
import os, re, shutil, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent
OUT = SRC / "build" / "preview"

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

PAGES = ["index.html", "azienda.html", "impianto.html", "servizi.html",
         "contatti.html", "note-legali.html"]
EN = ["index.html", "company.html", "plant.html", "services.html",
      "contact.html", "legal.html"]

# assets and the logo travel as-is
shutil.copytree(SRC / "assets", OUT / "assets")
(OUT / "images").mkdir()
shutil.copy(SRC / "images" / "SOLARMA_logo.png", OUT / "images" / "SOLARMA_logo.png")

BANNER = {
    "it": ('<div class="preview-flag" role="note">'
           '<strong>Anteprima riservata</strong> &mdash; bozza del nuovo sito, non ancora pubblicata. '
           'Il sito ufficiale resta <a href="https://www.solarma.it/">www.solarma.it</a>. '
           'Vi chiediamo di non diffondere questo indirizzo.</div>'),
    "en": ('<div class="preview-flag" role="note">'
           '<strong>Private preview</strong> &mdash; draft of the new website, not yet published. '
           'The live site remains <a href="https://www.solarma.it/">www.solarma.it</a>. '
           'Please do not share this address.</div>'),
}

def transform(html, lang):
    # never let a search engine index the preview
    html = html.replace('<meta name="robots" content="index, follow">',
                        '<meta name="robots" content="noindex, nofollow">')
    # the canonical tag already points at the real domain, which is what we want
    html = html.replace('<a class="skip-link"', BANNER[lang] + '\n<a class="skip-link"', 1)
    return html

for name in PAGES:
    (OUT / name).write_text(transform((SRC / name).read_text(encoding="utf-8"), "it"), encoding="utf-8")
(OUT / "en").mkdir()
for name in EN:
    (OUT / "en" / name).write_text(
        transform((SRC / "en" / name).read_text(encoding="utf-8"), "en"), encoding="utf-8")

# banner styling, appended only to the preview copy of the stylesheet
css = (OUT / "assets" / "css" / "site.css")
css.write_text(css.read_text(encoding="utf-8") + """

/* ---------- Preview-only staging banner (not part of the published site) ---------- */
.preview-flag {
  background: #7a2e00; color: #ffe4c4; text-align: center;
  padding: .6rem 1rem; font-size: .85rem; line-height: 1.45;
  border-bottom: 2px solid var(--solar);
}
.preview-flag strong { color: #fff; }
.preview-flag a { color: #ffd79a; }
@media print { .preview-flag { display: none; } }
""", encoding="utf-8")

(OUT / "robots.txt").write_text("# Preview copy - must never be indexed.\nUser-agent: *\nDisallow: /\n",
                                encoding="utf-8")
(OUT / ".nojekyll").write_text("", encoding="utf-8")

(OUT / "README.md").write_text("""# sito-anteprima

Anteprima del **nuovo sito di SOLARMA S.n.c.**, pubblicata qui per essere
riletta prima della messa online.

**Questo non e' il sito ufficiale.** Il sito pubblicato resta
<https://www.solarma.it/>.

Anteprima: <https://solarma.github.io/sito-anteprima/>

Questa copia:

* riporta un avviso in cima a ogni pagina, assente nella versione definitiva;
* e' esclusa dai motori di ricerca (`robots.txt` e `noindex` su ogni pagina);
* non contiene il file `CNAME`, quindi non puo' in alcun modo interferire con
  il dominio www.solarma.it.

Il contenuto vero e proprio vive nel repository
[solarma.github.com](https://github.com/SOLARMA/solarma.github.com), sul ramo
`claude/solarma-website-revamp-tcb3z1`. Questo repository e' una copia
temporanea e puo' essere cancellato a revisione conclusa.
""", encoding="utf-8")

wf = OUT / ".github" / "workflows"
wf.mkdir(parents=True)
(wf / "pages.yml").write_text("""name: Deploy preview to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure Pages
        uses: actions/configure-pages@v5
        with:
          # turns Pages on for this repository if it is not enabled yet
          enablement: true
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deployment
        uses: actions/deploy-pages@v4
""", encoding="utf-8")

n = sum(1 for _ in OUT.rglob("*") if _.is_file())
print(f"preview built at {OUT}  ({n} files)")
for p in sorted(OUT.rglob("*")):
    if p.is_file() and p.suffix in (".html", ".txt", ".md", ".yml"):
        print("  ", p.relative_to(OUT))
