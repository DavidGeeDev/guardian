#!/usr/bin/env bash
set -euo pipefail

# Smoke test used locally and in CI.
# Assumes dependencies already installed (e.g., pip install -e ".[dev]").

echo "==> compileall"
python -m compileall -q model_guardian

echo "==> pytest"
pytest -q

echo "==> run example"
python examples/sklearn_mapie_hello_world.py

