# This file defines the ghcr.io/sfnw-dev-owner/renderer image used by
# ./{all,go} to render MarkDown manuals to PDF.
#
# When this Dockerfile changes on main,
# ../.github/workflows/build-renderer-container.yml will trigger a
# rebuild and push to ghcr.io/sfnw-dev-owner/renderer:
# https://github.com/sfnw-dev-owner/process-manuals/actions/workflows/build-renderer-container.yml
#
# To test local modifications: `docker build -t renderer .` and
# temporarily change ./.container's first line to just read
# "renderer".

FROM ghcr.io/pandoc/typst:3.8.3-debian

ENV QCAD_VERSION=3.32.9

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  libasound2 \
  libdbus-1-3 \
  libegl1 \
  libfontconfig1 \
  libgl1-mesa-dri \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libice6 \
  libsm6 \
  libx11-xcb1 \
  libxcb-cursor0 \
  libxcb-icccm4 \
  libxcb-image0 \
  libxcb-keysyms1 \
  libxcb-randr0 \
  libxcb-render-util0 \
  libxcb-shape0 \
  libxcb-xfixes0 \
  libxcb-xinerama0 \
  libxcb-xkb1 \
  libxext6 \
  libxi6 \
  libxkbcommon-x11-0 \
  libxrender1

# Download and extract the archive directly to /opt/qcad, then remove
# the Professional add-ons/plugins to revert to the Community Edition.
RUN set -x && \
  curl -L "https://www.qcad.org/archives/qcad/qcad-${QCAD_VERSION}-trial-linux-qt6-x86_64.tar.gz" | tar -xz -C /opt && \
  mv /opt/qcad-${QCAD_VERSION}-trial-linux-qt6-x86_64 /opt/qcad && \
  bash -c 'rm /opt/qcad/plugins/libqcad{pdf,polygon,proj,proscripts,proxies,shp,spatialindexpro,trace,dwg}.so'

ENV LC_ALL="C.utf8"
ENV PATH="/opt/qcad:${PATH}"
ENV QT_LOGGING_RULES="*.debug=false;qt.*.debug=false;*.warning=false;qt.*.warning=false"

LABEL org.opencontainers.image.source="https://github.com/sfnw-dev-owner/process-manuals"

WORKDIR /s
