# solarma.github.com

Corporate website of **SOLARMA S.n.c. di Gianpaolo Macario & C.** — <https://www.solarma.it/>

A static, bilingual (Italian / English) site served by GitHub Pages. No build step, no
framework, no runtime dependencies: every page is plain HTML that can be edited directly.

## Structure

```
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
/old/                 Archive of the pre-2016 website, kept for reference
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

## Local preview

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```

Paths are root-absolute (`/assets/...`), so preview through a web server rather than by
opening the files directly from disk.

## Privacy and analytics

Google Analytics (GA4, `G-2ZJF0K1SZL`) is loaded **only after the visitor explicitly
accepts** through the cookie banner; the choice is stored in `localStorage`. No web fonts,
scripts or images are fetched from third-party servers before that point.

## Copyright and licensing

Copyright 2016–2026 by [SOLARMA snc di Gianpaolo Macario & C](https://www.solarma.it/).

<!-- EOF -->
