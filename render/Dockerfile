# This file defines the ghcr.io/sfnw-dev-owner/renderer image used by
# ./{all,go} to render MarkDown manuals to PDF, and ./model2svg.py to
# render their figures from the model (common/model).
#
# When this Dockerfile changes on main,
# ../.github/workflows/build-renderer-container.yml will trigger a
# rebuild and push to ghcr.io/sfnw-dev-owner/renderer:
# https://github.com/sfnw-dev-owner/process-manuals/actions/workflows/build-renderer-container.yml
#
# To test local modifications, from the repo's root: `docker build -f
# render/Dockerfile -t renderer .` and temporarily change
# render/.container's first line to just read "renderer".

FROM ghcr.io/pandoc/typst:3.8.3-debian

ENV DEBIAN_FRONTEND=noninteractive
# OpenCASCADE (build123d's kernel) links against libGL and libX11 even
# though it never opens a window. git fetches build123d (pinned to a commit
# in requirements.txt).
RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  libexpat1 \
  libgl1 \
  libx11-6 \
  zlib1g \
  && rm -rf /var/lib/apt/lists/*

# Python for render/model2svg.py, installed and managed by uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY render/requirements.txt /tmp/requirements.txt
RUN uv venv /opt/venv --python 3.12 \
  && uv pip install --no-cache -r /tmp/requirements.txt \
  && rm /tmp/requirements.txt

ENV LC_ALL="C.utf8"

LABEL org.opencontainers.image.source="https://github.com/sfnw-dev-owner/process-manuals"

WORKDIR /s
