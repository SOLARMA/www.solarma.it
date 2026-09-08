# Kubernetes deployment

Scaffolding to serve the SOLARMA website from a Kubernetes cluster instead of
(or alongside) GitHub Pages. Plain manifests plus a Kustomize overlay — no Helm,
no operator, no persistent storage.

```
deploy/k8s/
  base/                     portable manifests, no cluster-specific values
  overlays/k3s-gmhome/      everything specific to the k3s-gmhome cluster
deploy/docker/Dockerfile    alternative: bake the site into an image
```

## How the content gets in

By default an **init container downloads a .zip archive and unpacks it** into an
`emptyDir` that nginx then serves read-only. Nothing is baked into an image, so
no registry and no build pipeline are needed.

The unpack step strips a single wrapping directory, then copies only the files
that belong on a web server — `README.md`, `LICENSE`, `tools/`, `deploy/` and
`.github/` in a repository archive are skipped. If the archive turns out not to
contain the site, the init container exits non-zero and the pod never starts,
rather than serving an empty document root.

Two archive shapes are supported, set via `SITE_ARCHIVE_URL`:

| Archive | Contents |
|---|---|
| Repository tag/branch archive from `codeload.github.com` (default) | The complete site, including `404.html`, `robots.txt` and `sitemap.xml` |
| The reviewer package from `tools/build-review-package.py` | The pages only — no `404.html`, `robots.txt` or `sitemap.xml` |

Prefer a **tag** over a branch. A branch archive changes under you, so two pods
started at different times can end up serving different content.

Content is fetched at pod start, so refreshing it is a restart:

```sh
kubectl -n solarma rollout restart deployment/solarma-site
```

If the cluster has no egress to `codeload.github.com`, or you want the running
version pinned to an image digest, use `deploy/docker/Dockerfile` instead: build
and push the image, then drop the `initContainers` block and the `site`
emptyDir from the overlay and point the nginx container at your image.

## Check these against your cluster before applying

These manifests were written **without access to `gmacario/gmhome-infra`**, so
the three cluster-specific values are guesses based on k3s defaults. All three
live in `overlays/k3s-gmhome/patch-ingress.yaml`:

| Value | Default assumed | How to confirm |
|---|---|---|
| `ingressClassName` | `traefik` (k3s ships it, but many homelabs replace it with ingress-nginx) | `kubectl get ingressclass` |
| `cert-manager.io/cluster-issuer` | `letsencrypt-prod` | `kubectl get clusterissuer` |
| `host` | `solarma.gmhome.example` — a placeholder | your DNS |

Also worth confirming: whether the cluster is managed by a GitOps controller. If
Flux or Argo CD owns it, this directory should be referenced from there rather
than applied by hand.

## Applying

```sh
kubectl kustomize deploy/k8s/overlays/k3s-gmhome        # render and read it first
kubectl apply -k deploy/k8s/overlays/k3s-gmhome
kubectl -n solarma rollout status deployment/solarma-site
```

## What the manifests do

* **Namespace** labelled for the `restricted` Pod Security Standard.
* **Deployment** — one replica, `nginx-unprivileged` on port 8080, running as
  uid 101 with a read-only root filesystem, all capabilities dropped, no
  privilege escalation, `RuntimeDefault` seccomp and no service-account token
  mounted. Writable scratch space is provided by `emptyDir`s on `/tmp` and
  `/var/cache/nginx`, which is what a read-only root filesystem requires.
  Startup, readiness and liveness probes all hit `/healthz`.
* **Service** — ClusterIP on port 80.
* **Ingress** — TLS via cert-manager.
* **nginx ConfigMap** — gzip, cache headers (5 minutes for HTML, 30 days for
  `/assets/` and `/images/`), a real `/healthz`, `404.html` wired to the 404
  status, and security headers including a Content-Security-Policy.

The CSP is strict on scripts: the site has no inline `<script>`, so `script-src`
needs no `'unsafe-inline'`. It does allow `'unsafe-inline'` for `style-src`,
because the pages use inline `style="..."` attributes. The `googletagmanager`
and `google-analytics` origins are needed only once a visitor accepts analytics
— remove them from the policy if you drop GA.

One nginx subtlety worth knowing before editing that config: **a `location`
block that declares its own `add_header` discards every `add_header` inherited
from the server block.** That is why the caching rules use only `expires`, which
is a separate directive. Adding an `add_header` to `location /assets/` would
silently strip the security headers from every asset response.

## Caution: do not serve the same hostname from both places

`www.solarma.it` currently points at GitHub Pages, which is configured from the
`CNAME` file at the repository root. If you move that hostname to the cluster,
change the DNS record and remove or repoint the GitHub Pages custom domain —
do not leave both claiming it. For a staging hostname alongside the live site,
this is not a concern.

## What has been verified

* `kustomize build` of the overlay renders cleanly.
* The init container script was run verbatim against a real repository archive
  and a real reviewer package (correct file sets in both), against an archive
  that is not the site (exits 1) and against a URL that 404s (exits 8).
* The nginx server block passes `nginx -t`, and was served by a real nginx:
  security headers present on both HTML and asset responses, HTML cached for 5
  minutes and assets for 30 days, gzip active, `/healthz` returning `ok`,
  unknown paths returning the styled 404 page with a 404 status.
* The site was loaded through that nginx in a browser with the CSP active: no
  policy violations, stylesheet and logo and JavaScript all working, and the
  analytics request permitted after consent.

Not verified: applying to an actual cluster. That is the part that depends on
the three values in the table above.
