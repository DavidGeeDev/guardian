# Dependency compatibility notes

## MAPIE

Phase 0 targets the **MAPIE 0.x** API.

The Phase 0 adapters assume the 0.x-style objects and return shapes for conformal
prediction sets/intervals (as used by `MapieClassifier` / `MapieRegressor`).

For that reason, `pyproject.toml` pins:

```text
mapie>=0.7,<1.0
```

If you want to upgrade to MAPIE 1.x, plan for a small adapter update and add a
compatibility test that covers the exact MAPIE version you deploy.
