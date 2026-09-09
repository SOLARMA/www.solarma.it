#!/usr/bin/env python3
"""Stamp the site version into every page of the SOLARMA site.

The site has no build step on purpose: what is committed is what is served.
So the version is written *into* the HTML and committed, rather than being
substituted at deploy time or fetched at runtime by JavaScript. Each page
gets the version twice:

  * <meta name="version" content="v3.0.1">      -- machine readable
  * a "Versione v3.0.1" / "Version v3.0.1" entry in the footer legal strip

Both are kept in sync by this script, which is idempotent: run it again and
it rewrites the values in place instead of adding a second copy.

Usage
-----
    python3 tools/set-site-version.py                 # use `git describe`
    python3 tools/set-site-version.py -v v3.0.2       # use an explicit string
    python3 tools/set-site-version.py --check         # verify, change nothing

Release procedure
-----------------
    python3 tools/set-site-version.py -v v3.0.2
    git commit -am "Release v3.0.2"
    git tag -a v3.0.2 -m "v3.0.2" && git push --follow-tags

`--check` exits non-zero when a page carries no version, when the pages
disagree with each other, or when they disagree with the working tree
(`git describe --tags --always`). Useful before tagging a release.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Every page of the live site. 404.html is included -- it is served by
# GitHub Pages like any other page. /history/ is not part of the live site.
PAGES_IT = ["index.html", "azienda.html", "impianto.html", "servizi.html",
            "contatti.html", "note-legali.html", "404.html"]
PAGES_EN = ["en/index.html", "en/company.html", "en/plant.html",
            "en/services.html", "en/contact.html", "en/legal.html"]

LABEL = {"it": "Versione", "en": "Version"}

# Anchors: both are present, once, in all 13 pages. Keep the inserted markup
# on the same shape as what is already there so a hand edit stays natural.
META_ANCHOR = re.compile(r'^(<meta name="author" content="[^"]*">)$', re.M)
META_VERSION = re.compile(r'^<meta name="version" content="([^"]*)">$', re.M)
FOOTER_ANCHOR = re.compile(r'^(\s*)(<li>(?:Sito ospitato su|Hosted on) GitHub Pages</li>)$', re.M)
FOOTER_VERSION = re.compile(r'<span data-site-version>([^<]*)</span>')


def git_describe():
    """`git describe --tags --always` for HEAD, or None outside a checkout.

    Deliberately without --dirty: the value ends up committed, so it
    describes a commit and never a working tree. Stamping the pages is
    itself a modification, so a --dirty value could never validate -- it
    would be stale the instant it was written.
    """
    try:
        out = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            cwd=ROOT, capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.stdout.strip() or None


def pages():
    for name in PAGES_IT:
        yield ROOT / name, "it"
    for name in PAGES_EN:
        yield ROOT / name, "en"


def stamp(text, lang, version):
    """Return (new_text, notes) with the version written into `text`."""
    notes = []

    if META_VERSION.search(text):
        text = META_VERSION.sub(
            '<meta name="version" content="%s">' % version, text, count=1)
    else:
        text, n = META_ANCHOR.subn(
            r'\1' + '\n<meta name="version" content="%s">' % version,
            text, count=1)
        if not n:
            notes.append('no <meta name="author"> anchor -- meta not added')

    if FOOTER_VERSION.search(text):
        text = FOOTER_VERSION.sub(
            '<span data-site-version>%s</span>' % version, text, count=1)
    else:
        entry = '<li>%s <span data-site-version>%s</span></li>' % (
            LABEL[lang], version)
        text, n = FOOTER_ANCHOR.subn(
            lambda m: "%s%s\n%s%s" % (m.group(1), m.group(2), m.group(1), entry),
            text, count=1)
        if not n:
            notes.append("no GitHub Pages footer anchor -- footer entry not added")

    return text, notes


def read_versions(text):
    """The versions currently recorded in a page: (meta, footer)."""
    meta = META_VERSION.search(text)
    footer = FOOTER_VERSION.search(text)
    return (meta.group(1) if meta else None,
            footer.group(1) if footer else None)


def check(expected):
    problems = []
    for path, _lang in pages():
        rel = path.relative_to(ROOT)
        if not path.is_file():
            problems.append("%s: missing" % rel)
            continue
        meta, footer = read_versions(path.read_text(encoding="utf-8"))
        if meta is None:
            problems.append('%s: no <meta name="version">' % rel)
        if footer is None:
            problems.append("%s: no footer version entry" % rel)
        if meta and footer and meta != footer:
            problems.append("%s: meta %s but footer %s" % (rel, meta, footer))
        for found in (meta, footer):
            if found and expected and found != expected:
                problems.append("%s: %s, expected %s" % (rel, found, expected))
    return problems


def main():
    ap = argparse.ArgumentParser(
        description="Stamp the site version into every page.")
    ap.add_argument("-v", "--version", metavar="STRING",
                    help="version to write (default: git describe)")
    ap.add_argument("--check", action="store_true",
                    help="verify the pages, write nothing, exit 1 on drift")
    args = ap.parse_args()

    version = args.version or git_describe()
    if not version:
        sys.exit("cannot determine a version: not a git checkout, "
                 "pass one with --version")

    if args.check:
        problems = check(version)
        if problems:
            print("version check failed against %s:" % version)
            for p in problems:
                print("  %s" % p)
            sys.exit(1)
        print("version check passed: all %d pages report %s"
              % (len(PAGES_IT) + len(PAGES_EN), version))
        return

    changed = 0
    for path, lang in pages():
        if not path.is_file():
            print("  skipped %s (missing)" % path.relative_to(ROOT))
            continue
        before = path.read_text(encoding="utf-8")
        after, notes = stamp(before, lang, version)
        for note in notes:
            print("  %s: %s" % (path.relative_to(ROOT), note))
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
    print("version %s written; %d of %d pages changed"
          % (version, changed, len(PAGES_IT) + len(PAGES_EN)))


if __name__ == "__main__":
    main()
