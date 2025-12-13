#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install it with: pip install uv" >&2
  exit 1
fi

mkdir -p requirements

echo "==> Generating requirements/base.lock from pyproject.toml"
uv pip compile pyproject.toml \
  --no-emit-project \
  --generate-hashes \
  -o requirements/base.lock

echo "==> Generating requirements/dev.lock (includes [project.optional-dependencies].dev)"
uv pip compile pyproject.toml \
  --extra dev \
  --no-emit-project \
  --generate-hashes \
  -o requirements/dev.lock

echo "==> Done. Commit requirements/base.lock and requirements/dev.lock"
