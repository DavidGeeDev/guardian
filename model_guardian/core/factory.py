from __future__ import annotations

from typing import Any, Optional

from model_guardian.core.middleware import DefaultGuardian
from model_guardian.core.registry import PluginSpec, instantiate
from model_guardian.schemas import GuardianConfig


def build_guardian(
    *,
    model: PluginSpec,
    uncertainty: PluginSpec,
    drift: Optional[PluginSpec] = None,
    policy: Optional[PluginSpec] = None,
    telemetry: Optional[PluginSpec] = None,
    config: Optional[GuardianConfig] = None,
    model_kwargs: Optional[dict[str, Any]] = None,
    uncertainty_kwargs: Optional[dict[str, Any]] = None,
    drift_kwargs: Optional[dict[str, Any]] = None,
    policy_kwargs: Optional[dict[str, Any]] = None,
    telemetry_kwargs: Optional[dict[str, Any]] = None,
) -> DefaultGuardian[Any, Any]:
    """Build a DefaultGuardian from plugin specs.

    This is intentionally minimal: it resolves entry points (or dotted paths)
    and instantiates components with provided kwargs.
    """
    model_obj = instantiate(model, **(model_kwargs or {}))
    uncertainty_obj = instantiate(uncertainty, **(uncertainty_kwargs or {}))

    drift_obj = instantiate(drift, **(drift_kwargs or {})) if drift else None
    policy_obj = instantiate(policy, **(policy_kwargs or {})) if policy else None
    telemetry_obj = instantiate(telemetry, **(telemetry_kwargs or {})) if telemetry else None

    return DefaultGuardian(
        model=model_obj,
        uncertainty=uncertainty_obj,
        drift=drift_obj,
        policy=policy_obj,
        telemetry=telemetry_obj,
        config=config,
    )
