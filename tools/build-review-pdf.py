# -*- coding: utf-8 -*-
"""Render the whole site to a single PDF for review by email.

Gmail (and Google Workspace in particular) blocks ZIP attachments that contain
.html files, so the review package cannot simply be attached to a message. A
PDF can: it previews inline in Gmail, opens on a phone, and can be annotated.

The pages are rendered with the *screen* stylesheet rather than the print one,
so reviewers see the real design, colours included, not a stripped-down
printout. Each page becomes a bookmark in the PDF outline.

Requires playwright (with a Chromium build) and pypdf:

    pip install playwright pypdf && playwright install chromium

Set CHROME_EXECUTABLE to reuse a Chromium you already have.

Usage:  python3 tools/build-review-pdf.py
"""
import contextlib
import functools
import http.server
import os
import pathlib
import socket
import threading

from playwright.sync_api import sync_playwright
from pypdf import PdfWriter

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUTPUT = BUILD / "SOLARMA-anteprima-sito.pdf"

PAGES = [
    ("/index.html",       "Home"),
    ("/azienda.html",     "Azienda"),
    ("/impianto.html",    "Impianto"),
    ("/servizi.html",     "Servizi"),
    ("/contatti.html",    "Contatti"),
    ("/note-legali.html", "Note legali e privacy"),
    ("/en/index.html",    "Home (English)"),
    ("/en/company.html",  "Company (English)"),
    ("/en/plant.html",    "Plant (English)"),
    ("/en/services.html", "Services (English)"),
    ("/en/contact.html",  "Contact (English)"),
    ("/en/legal.html",    "Legal notice (English)"),
]

# Sections are too tall to keep whole without leaving large gaps, so only the
# smaller components are protected from being split across a page break.
PAGE_BREAK_CSS = """
  .card, .stat, .timeline li, .contact-item, .table-card, .note,
  .media-placeholder, .cta-band, .person { break-inside: avoid; }
  h1, h2, h3, h4 { break-after: avoid; }
"""


@contextlib.contextmanager
def local_server(directory):
    """Serve `directory` on a free port for the lifetime of the block."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(directory))
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield "http://127.0.0.1:%d" % port
    finally:
        httpd.shutdown()


def main():
    BUILD.mkdir(exist_ok=True)
    parts = []

    with local_server(ROOT) as base, sync_playwright() as p:
        # CHROME_EXECUTABLE lets you point at an existing Chromium build
        # instead of the one `playwright install` downloads.
        chrome = os.environ.get("CHROME_EXECUTABLE")
        browser = p.chromium.launch(executable_path=chrome) if chrome \
            else p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        # Pre-set the cookie choice so the banner does not sit over the content
        # of every single page.
        context.add_init_script(
            "try{localStorage.setItem('solarma.consent.v1','denied')}catch(e){}")
        page = context.new_page()

        for index, (path, label) in enumerate(PAGES):
            page.goto(base + path, wait_until="networkidle")
            page.wait_for_timeout(250)
            page.emulate_media(media="screen")
            page.add_style_tag(content=PAGE_BREAK_CSS)

            # Gallery images carry loading="lazy", so in a headless render
            # everything below the fold stays unloaded and would be printed as
            # empty boxes. Force them to load and wait for every one.
            page.evaluate("""async () => {
                document.querySelectorAll('img[loading="lazy"]')
                        .forEach(img => { img.loading = 'eager'; });
                await Promise.all([...document.images].map(img =>
                    img.complete ? Promise.resolve()
                                 : new Promise(done => { img.onload = img.onerror = done; })));
            }""")
            missing = page.evaluate(
                "[...document.images].filter(i => !i.complete || i.naturalWidth === 0).length")
            if missing:
                raise SystemExit(
                    "%s: %d image(s) failed to load; refusing to write a PDF with blank figures"
                    % (path, missing))
            part = BUILD / ("_part-%02d.pdf" % index)
            page.pdf(path=str(part), width="1280px", print_background=True,
                     margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            parts.append((part, label))
            print("rendered", path)

        browser.close()

    writer = PdfWriter()
    for part, label in parts:
        # append first: an outline item pointing at a page that does not exist
        # yet resolves to a dangling destination
        start = len(writer.pages)
        writer.append(str(part))
        writer.add_outline_item(label, start)
    writer.add_metadata({
        "/Title": "SOLARMA S.n.c. - Anteprima del nuovo sito",
        "/Author": "SOLARMA S.n.c.",
        "/Subject": "Bozza del nuovo sito www.solarma.it - non ancora pubblicata",
    })
    with open(OUTPUT, "wb") as fh:
        writer.write(fh)
    for part, _ in parts:
        part.unlink()

    print("\nbuilt %s (%d pages, %.0f KB)"
          % (OUTPUT, len(writer.pages), OUTPUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
