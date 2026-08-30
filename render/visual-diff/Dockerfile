# This file defines the ghcr.io/sfnw-dev-owner/visual-diff image used by
# .github/workflows/render-pdfs.yml to visually compare PDFs from a PR
# against the latest release.
#
# When anything in this directory changes on main,
# ../../.github/workflows/build-visual-diff-container.yml will trigger a
# rebuild and push to ghcr.io/sfnw-dev-owner/visual-diff.
#
# To test local modifications: `docker build -t visual-diff .`

FROM fedora:latest

RUN dnf install -y --setopt=install_weak_deps=False \
        diff-pdf \
        diffutils \
        unzip \
        xorg-x11-server-Xvfb

COPY compare-pdfs.sh /usr/local/bin/compare-pdfs.sh
RUN chmod +x /usr/local/bin/compare-pdfs.sh

WORKDIR /work

ENTRYPOINT ["/usr/local/bin/compare-pdfs.sh"]
