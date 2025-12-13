#!/usr/bin/env bash
set -euo pipefail

if ! command -v pip-compile >/dev/null 2>&1; then
  echo "pip-compile not found. Install with: pip install pip-tools" >&2
  exit 1
fi

mkdir -p requirements

# pip-tools supports pyproject.toml inputs in recent versions.
# We generate hash-locked, fully pinned lockfiles.

echo "==> Generating requirements/base.lock from pyproject.toml"
pip-compile pyproject.toml \
  --no-emit-index-url \
  --generate-hashes \
  --output-file requirements/base.lock

echo "==> Generating requirements/dev.lock (extras: dev)"
pip-compile pyproject.toml \
  --extra dev \
  --no-emit-index-url \
  --generate-hashes \
  --output-file requirements/dev.lock

echo "==> Done. Commit requirements/base.lock and requirements/dev.lock"
