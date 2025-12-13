from __future__ import annotations

"""Plugin registry + entry-point loading.

Phase 0 ships with in-tree implementations (MAPIE, Alibi-Detect, JSONL sink), but
production deployments often want to supply their own adapters without forking.

We support this via Python packaging entry points:

  - model_guardian.models
  - model_guardian.uncertainty_adapters
  - model_guardian.drift_adapters
  - model_guardian.policies
  - model_guardian.telemetry_sinks

Each entry point should resolve to a class (or callable factory) that can be
instantiated by the host application.
"""

from dataclasses import dataclass
from importlib import metadata
from typing import Any, Callable, Dict, Mapping, Optional, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class PluginSpec:
    """Reference to a plugin.

    Use either:
      - entrypoint: name within a group
      - dotted_path: "pkg.module:ClassName" or "pkg.module.ClassName"
    """

    group: str
    entrypoint: Optional[str] = None
    dotted_path: Optional[str] = None

    def __post_init__(self) -> None:
        if (self.entrypoint is None) == (self.dotted_path is None):
            raise ValueError("Exactly one of entrypoint or dotted_path must be provided")


def _load_from_dotted_path(path: str) -> Any:
    import importlib

    if ":" in path:
        mod, attr = path.split(":", 1)
    else:
        # allow "pkg.mod.Class" form
        mod, attr = path.rsplit(".", 1)
    module = importlib.import_module(mod)
    return getattr(module, attr)


def load_entrypoints(group: str) -> Mapping[str, Any]:
    """Load all entry points for a group, returning {name: loaded_object}."""
    eps = metadata.entry_points()
    selected = eps.select(group=group) if hasattr(eps, "select") else eps.get(group, [])
    out: Dict[str, Any] = {}
    for ep in selected:
        try:
            out[ep.name] = ep.load()
        except Exception as e:  # pragma: no cover
            # Don't explode at import time; surface failures to caller.
            out[ep.name] = e
    return out


def resolve_plugin(spec: PluginSpec) -> Any:
    """Resolve a PluginSpec to a Python object (class/function).

    Raises ValueError if resolution fails.
    """
    if spec.entrypoint is not None:
        all_eps = load_entrypoints(spec.group)
        if spec.entrypoint not in all_eps:
            raise ValueError(
                f"No entry point named '{spec.entrypoint}' in group '{spec.group}'. "
                f"Available: {sorted(all_eps.keys())}"
            )
        obj = all_eps[spec.entrypoint]
        if isinstance(obj, Exception):  # pragma: no cover
            raise ValueError(f"Failed to load entry point '{spec.entrypoint}': {obj}")
        return obj

    assert spec.dotted_path is not None
    return _load_from_dotted_path(spec.dotted_path)


def instantiate(spec: PluginSpec, **kwargs: Any) -> Any:
    """Instantiate a plugin class or call a factory."""
    obj = resolve_plugin(spec)
    if callable(obj):
        return obj(**kwargs)
    return obj
