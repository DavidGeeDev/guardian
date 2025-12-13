# Reproducible installs

This repo is **pyproject-first** (dependencies live in `pyproject.toml`).

Two supported lock strategies:

## Option A (recommended): uv
- Install: `pip install uv`
- Lock: `make lock-uv` (wraps `scripts/lock_uv.sh`)
  - Uses `uv pip compile` to generate:
    - `requirements/base.lock`
    - `requirements/dev.lock`
- Install from lock (hash-verified):
  - `pip install --require-hashes -r requirements/dev.lock`

> Note: `uv lock` is a different workflow that produces `uv.lock`. This repo
> intentionally uses `uv pip compile` to generate pip-compatible lockfiles.

## Option B: pip-tools
- Install: `pip install pip-tools`
- Lock: `make lock-piptools` (produces `requirements/base.lock`, `requirements/dev.lock`)
- Install from lock:
  - `pip install -r requirements/base.lock`
  - `pip install -r requirements/dev.lock`

In CI we install from the project metadata (`pip install -e ".[dev]"`) and run smoke tests.
