# Alternative to the init-container approach: bake the site into an image.
#
# Prefer this if the cluster has no egress to codeload.github.com, or if you
# want the running version pinned to an image digest rather than to whatever a
# branch archive happens to contain at pod start.
#
# Build from the repository root:
#   docker build -f deploy/docker/Dockerfile -t ghcr.io/gmacario/solarma-site:1.0.0 .
#
# Then in the overlay, drop the initContainers block and the `site` emptyDir,
# and point the nginx container at this image instead.

FROM docker.io/nginxinc/nginx-unprivileged:1.27-alpine

COPY --chown=101:101 index.html 404.html azienda.html impianto.html \
     servizi.html contatti.html note-legali.html robots.txt sitemap.xml \
     /usr/share/nginx/html/
COPY --chown=101:101 en/     /usr/share/nginx/html/en/
COPY --chown=101:101 assets/ /usr/share/nginx/html/assets/
COPY --chown=101:101 images/SOLARMA_logo.png /usr/share/nginx/html/images/

# The nginx server block still comes from the solarma-site-nginx ConfigMap at
# runtime, so the same configuration applies to both deployment styles.

EXPOSE 8080
USER 101
