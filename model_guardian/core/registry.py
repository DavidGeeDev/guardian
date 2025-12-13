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
from importlib import import_module, metadata
import logging
from typing import Any, Dict, Mapping, Optional

logger = logging.getLogger(__name__)

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
    if ":" in path:
        mod, attr = path.split(":", 1)
    else:
        # allow "pkg.mod.Class" form
        mod, attr = path.rsplit(".", 1)
    module = import_module(mod)
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
            # But do log so misconfigurations don't fail silently.
            logger.warning(
                "Failed to load entry point '%s' from group '%s'", ep.name, group, exc_info=e
            )
            out[ep.name] = e
    return out


def resolve_plugin(spec: PluginSpec) -> Any:
    """Resolve a PluginSpec to a Python object (class/function).

    Raises ValueError if resolution fails.
    """
    if spec.entrypoint is not None:
        all_eps = load_entrypoints(spec.group)
        if spec.entrypoint not in all_eps:
            available = sorted(k for k, v in all_eps.items() if not isinstance(v, Exception))
            failed = sorted(k for k, v in all_eps.items() if isinstance(v, Exception))
            raise ValueError(
                f"No entry point named '{spec.entrypoint}' in group '{spec.group}'. "
                f"Available: {available}"
                + (f". Failed to load: {failed}" if failed else "")
            )
        obj = all_eps[spec.entrypoint]
        if isinstance(obj, Exception):  # pragma: no cover
            raise ValueError(
                f"Failed to load entry point '{spec.entrypoint}' in group '{spec.group}': {obj}"
            )
        return obj

    assert spec.dotted_path is not None
    return _load_from_dotted_path(spec.dotted_path)


def instantiate(spec: PluginSpec, **kwargs: Any) -> Any:
    """Instantiate a plugin class or call a factory."""
    obj = resolve_plugin(spec)
    if callable(obj):
        return obj(**kwargs)
    return obj
