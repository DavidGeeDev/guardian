# Reproducible installs

This repo is **pyproject-first** (dependencies live in `pyproject.toml`).

Two supported lock strategies:

## Option A (recommended): uv
- Install: `pip install uv`
- Lock: `uv lock` (produces `uv.lock`)
- Sync: `uv sync --all-extras` (or `uv pip install -e ".[dev]"`)

## Option B: pip-tools
- Install: `pip install pip-tools`
- Lock: `make lock-piptools` (produces `requirements/base.lock`, `requirements/dev.lock`)
- Install from lock:
  - `pip install -r requirements/base.lock`
  - `pip install -r requirements/dev.lock`

In CI we install from the project metadata (`pip install -e ".[dev]"`) and run smoke tests.
