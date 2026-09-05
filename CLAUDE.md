# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Corporate website of SOLARMA S.n.c. — a static, bilingual (Italian / English) site with **no
build step, no framework, no runtime dependencies**. Every page is plain HTML that can be
edited directly. Primary deploy is GitHub Pages (custom domain via the root `CNAME` file);
an alternative Kubernetes deploy exists under `deploy/`.

## Structure

```
/                     Italian site (default): index, azienda, impianto, servizi,
                      contatti, note-legali
/en/                  English mirror of the same six pages
/assets/css/site.css  Single stylesheet — design tokens in the :root block at the top
/assets/js/site.js    Mobile nav + consent-gated analytics
/assets/img/          Favicons, hero illustration, Open Graph image
404.html              Bilingual not-found page
sitemap.xml           All 12 pages, with hreflang alternates
/deploy/              Kubernetes manifests (base + k3s-gmhome overlay) and a Dockerfile —
                      alternative to GitHub Pages, see deploy/k8s/README.md
/tools/               Python scripts to package the site for offline/email review
/history/2014/, /history/2023/  Archived prior versions of the site, kept for reference only
                      — not part of the live site, do not edit
```

## Editing conventions

- **Header and footer are duplicated in every page on purpose** so no build tool is needed.
  When changing a navigation link, update it in every page:
  `grep -rl 'azienda.html' *.html en/*.html`
- **Colours, spacing, typography** all come from the CSS custom properties in the `:root`
  block at the top of `assets/css/site.css`.
- **Placeholders**: search for `TODO SOLARMA` to find values still needing real data (plant
  capacity, annual output, avoided CO₂, photographs). Placeholder figures render as `n.d.` /
  `n/a` rather than false data: `grep -rn "TODO SOLARMA" *.html en/*.html`
- Internal links and assets use **relative paths** so the site works both via a web server
  and opened straight from disk — except **`404.html`, which deliberately keeps
  root-absolute paths** (GitHub Pages serves it at whatever URL was requested, so relative
  paths there would resolve against the wrong folder).
- GA4 analytics loads only after explicit cookie-banner consent (choice stored in
  `localStorage`); nothing third-party is fetched before that.

## Local preview

```sh
python3 -m http.server 8000        # serve over HTTP as it's actually served
```
Opening the HTML files directly from disk also works (relative paths), except `404.html`.

## Building review packages (for non-technical reviewers)

```sh
python3 tools/build-review-package.py   # -> build/SOLARMA-anteprima-sito.zip
python3 tools/build-review-pdf.py       # -> build/SOLARMA-anteprima-sito.pdf (needs playwright + pypdf)
```
The ZIP can't be emailed via Gmail (blocks `.html` inside archives) — use the PDF or Google
Drive instead. The PDF script renders with the *screen* stylesheet so reviewers see the real
design, one bookmarked PDF, and needs `pip install playwright pypdf && playwright install chromium`.

## Kubernetes deploy (optional, alongside/instead of GitHub Pages)

```sh
kubectl kustomize deploy/k8s/overlays/k3s-gmhome        # render and read before applying
kubectl apply -k deploy/k8s/overlays/k3s-gmhome
kubectl -n solarma rollout status deployment/solarma-site
kubectl -n solarma rollout restart deployment/solarma-site   # content is fetched at pod start
```
See `deploy/k8s/README.md` for full detail. Key points to remember:
- Content is pulled by an init container from a `.zip` (repo archive or the reviewer
  package) at pod start — nothing is baked into an image unless you switch to
  `deploy/docker/Dockerfile`. Prefer a **tag** archive over a branch (a branch can change
  under a running pod).
- Three cluster-specific values in `overlays/k3s-gmhome/patch-ingress.yaml`
  (`ingressClassName`, the cert-manager `ClusterIssuer`, and the `host`) are guesses and
  must be confirmed against the real cluster before applying.
- **Never serve `www.solarma.it` from both GitHub Pages and the cluster at once** — the
  domain's DNS/CNAME must point at exactly one.
- In the nginx ConfigMap, a `location` block that sets its own `add_header` discards every
  `add_header` inherited from the `server` block — caching in `location /assets/` therefore
  uses `expires`, not `add_header`, to avoid silently dropping the security headers.
- The CSP is strict on `script-src` (no inline scripts exist in the site); `style-src`
  allows `'unsafe-inline'` because pages use inline `style="..."` attributes.
