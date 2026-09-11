# solarma.github.com

Corporate website of **SOLARMA S.n.c. di Gianpaolo Macario & C.** — <https://www.solarma.it/>

A static, bilingual (Italian / English) site served by GitHub Pages. No build step, no
framework, no runtime dependencies: every page is plain HTML that can be edited directly.

## Structure

```text
/                     Italian site (default)
  index.html          Home
  azienda.html        Company — history, partners, principles, company objects
  impianto.html       Plant — the Peveragno photovoltaic power plant
  servizi.html        Services — generation, design, construction, O&M
  contatti.html       Contact details and electronic invoicing data
  note-legali.html    Legal notice, GDPR privacy notice, cookie policy
/en/                  English site (same six pages: index, company, plant,
                      services, contact, legal)
/assets/
  css/site.css        Single stylesheet — design tokens at the top
  js/site.js          Mobile nav + consent-gated analytics
  img/                Favicons, hero illustration, Open Graph image
images/
  SOLARMA_logo.png    The company logo, used in the header and footer
404.html              Bilingual not-found page
sitemap.xml           All 12 pages, with hreflang alternates
```

## Editing

* **Text and structure** — edit the `.html` files directly. The header and footer are
  duplicated in every page on purpose, so that no build tool is needed; if you change a
  navigation link, change it in all pages (`grep -rl 'azienda.html' *.html en/*.html`).
* **Colours, spacing, typography** — the CSS custom properties in the `:root` block at the
  top of `assets/css/site.css` drive the whole design.
* **Placeholders** — search the repository for `TODO SOLARMA` to find every value that still
  needs real data (plant capacity, annual output, avoided CO₂, photographs). Placeholder
  figures are rendered as `n.d.` / `n/a` so nothing false is ever published.

```sh
grep -rn "TODO SOLARMA" *.html en/*.html
```

## Linting

`.github/workflows/super-linter.yml` runs [Super-linter](https://github.com/super-linter/super-linter)
on every push and pull request against `main`, checking only the files that changed. It
covers YAML, GitHub Actions workflows, the Dockerfile (hadolint), Python (flake8),
Markdown, HTML and JavaScript (ESLint) — CSS is off, since a generic stylelint config
reads this project's BEM class names and dense one-line utility rules as violations, and
`history/` is excluded outright, since it's old code kept for reference rather than a
target for today's conventions.

The five dotfiles at the repo root (`.flake8`, `.yaml-lint.yml`, `.markdown-lint.yml`,
`.hadolint.yaml`, `.htmlhintrc`) and `eslint.config.mjs` are pinned copies of Super-linter's
own bundled defaults, so a future change to those defaults can't silently start failing
this repo's existing style (long single-line values in the nginx ConfigMap and CSP header,
aligned YAML in `deployment.yaml`, long-line prose in these docs).

## Site version

Every page carries the released version twice: visibly, as the last entry of the footer
legal strip (*Versione v3.0.1* / *Version v3.0.1*), and machine readably, as
`<meta name="version">` in the `<head>`. Both are plain committed HTML — what is in the
repository is what the visitor sees, with no build step and no JavaScript involved.

`tools/set-site-version.py` keeps the two in sync across all 13 pages. It is idempotent,
so it can be re-run freely:

```sh
python3 tools/set-site-version.py                    # write `git describe --tags --always`
python3 tools/set-site-version.py -v v3.0.2          # write an explicit version
python3 tools/set-site-version.py --check            # verify the pages agree
python3 tools/set-site-version.py --check -v v3.0.2  # ...and carry this exact version
```

`--check` on its own only asks that every page carry a version and that they all agree
on it — it does **not** compare them against `git describe`. Between releases `main` sits
ahead of the last tag, so that comparison would fail on every commit and be useless as a
guard. The Pages deploy workflow runs exactly this form, so a half-applied stamp — some
pages naming one release, the rest another — fails the deploy instead of being published.

Releasing:

```sh
python3 tools/set-site-version.py -v v3.0.2
python3 tools/set-site-version.py --check -v v3.0.2
git commit -am "Release v3.0.2"
git tag -a v3.0.2 -m "v3.0.2" && git push --follow-tags
```

Stamp *before* tagging, so that the tagged commit is the one carrying its own version.
Between releases the committed version names the last release, not every intermediate
commit.

## Local preview

Internal links and assets use **relative** paths, so the site works both when served from
a web server and when opened straight from disk.

To send the site to a non-technical reviewer, build the review package:

```sh
python3 tools/build-review-package.py
# -> build/SOLARMA-anteprima-sito.zip
```

They extract the ZIP and double-click `index.html` — no server, no tooling and no
internet connection needed. The package bundles an Italian instruction sheet explaining
how to extract it, what to look at, and what the `n.d.` placeholders mean.

**The ZIP cannot be emailed from Gmail**, which blocks archives containing `.html`
files. Share it through Google Drive, or send the PDF version instead:

```sh
python3 tools/build-review-pdf.py
# -> build/SOLARMA-anteprima-sito.pdf
```

That renders every page with the on-screen stylesheet — real colours and layout, not a
stripped-down printout — into one bookmarked PDF that Gmail previews inline and that
opens on a phone. It needs `playwright` and `pypdf`; see the script header.

Optionally, to preview over HTTP as it will actually be served:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```

One exception: **`404.html` keeps root-absolute paths on purpose.** GitHub Pages serves it
at whatever URL was requested (say `/foo/bar`), so relative paths there would resolve
against the wrong folder and the page would lose its styling. It is therefore the one page
that does not render correctly from disk.

## Privacy and analytics

Google Analytics (GA4, `G-2ZJF0K1SZL`) is loaded **only after the visitor explicitly
accepts** through the cookie banner; the choice is stored in `localStorage`. No web fonts,
scripts or images are fetched from third-party servers before that point.

## Copyright and licensing

Copyright 2016–2026 by [SOLARMA snc di Gianpaolo Macario & C](https://www.solarma.it/).

<!-- EOF -->
