from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from typing import Any, Sequence

import pytest

from model_guardian.core.factory import build_guardian
from model_guardian.core.registry import PluginSpec, instantiate, load_entrypoints, resolve_plugin
from model_guardian.interfaces import AbstentionPolicy, DriftAdapter, ModelAdapter, TelemetrySink, UncertaintyAdapter
from model_guardian.schemas import (
    FailureRecord,
    GuardianAction,
    GuardianDecision,
    Prediction,
    RequestContext,
    Signal,
    UncertaintyScore,
)


@dataclass
class DummyModel(ModelAdapter[list[float], int]):
    bias: int = 0

    async def predict(self, x: list[float], *, context: RequestContext) -> Prediction[int]:
        return Prediction(value=int(sum(x)) + self.bias, raw={"x": x})


@dataclass
class DummyUQ(UncertaintyAdapter[list[float], int]):
    fixed_aleatoric: float = 0.1
    fixed_epistemic: float = 0.1

    async def quantify(
        self, *, x: list[float], prediction: Prediction[int], context: RequestContext
    ) -> UncertaintyScore:
        return UncertaintyScore(
            aleatoric=self.fixed_aleatoric,
            epistemic=self.fixed_epistemic,
            method="dummy",
        )


@dataclass
class DummyDrift(DriftAdapter[list[float], int]):
    async def compute(
        self, *, x: list[float], prediction: Prediction[int], context: RequestContext
    ) -> Sequence[Signal]:
        return [Signal.info(name="drift.ok", provider="dummy", message="ok")]


@dataclass
class DummyPolicy(AbstentionPolicy[list[float], int]):
    called_with: dict[str, Any] | None = None

    async def decide(
        self,
        *,
        x: list[float],
        prediction: Prediction[int],
        uncertainty: UncertaintyScore,
        signals: Sequence[Signal],
        context: RequestContext,
    ) -> GuardianDecision:
        self.called_with = {
            "x": x,
            "prediction": prediction.value,
            "uncertainty": uncertainty.model_dump(),
            "signals": [s.name for s in signals],
        }
        return GuardianDecision(action=GuardianAction.ALLOW, reason="ok", confidence=0.9)


@dataclass
class DummyTelemetry(TelemetrySink):
    events: int = 0
    failures: int = 0

    async def emit_event(
        self,
        *,
        context: RequestContext,
        prediction: Prediction,
        uncertainty: UncertaintyScore,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        self.events += 1

    async def emit_failure(
        self,
        *,
        context: RequestContext,
        failure: FailureRecord,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        self.failures += 1


def _install_test_module() -> str:
    """Inject a temporary module into sys.modules so dotted-path loading can be tested."""
    module_name = "mg_test_plugins"
    m = types.ModuleType(module_name)
    m.DummyModel = DummyModel
    m.DummyUQ = DummyUQ
    m.DummyDrift = DummyDrift
    m.DummyPolicy = DummyPolicy
    m.DummyTelemetry = DummyTelemetry
    sys.modules[module_name] = m
    return module_name


def test_instantiate_from_dotted_path():
    mod = _install_test_module()
    spec = PluginSpec(group="model_guardian.models", dotted_path=f"{mod}:DummyModel")
    inst = instantiate(spec, bias=5)
    assert isinstance(inst, DummyModel)
    assert inst.bias == 5


def test_resolve_plugin_from_entrypoint(monkeypatch: pytest.MonkeyPatch):
    _install_test_module()

    class FakeEntryPoint:
        def __init__(self, name: str, obj: Any):
            self.name = name
            self._obj = obj

        def load(self) -> Any:
            return self._obj

    class FakeEntryPoints:
        def __init__(self):
            self._by_group = {
                "model_guardian.models": [FakeEntryPoint("dummy", DummyModel)],
            }

        def select(self, *, group: str):
            return self._by_group.get(group, [])

    monkeypatch.setattr(
        "model_guardian.core.registry.metadata.entry_points",
        lambda: FakeEntryPoints(),
    )

    eps = load_entrypoints("model_guardian.models")
    assert "dummy" in eps

    spec = PluginSpec(group="model_guardian.models", entrypoint="dummy")
    obj = resolve_plugin(spec)
    assert obj is DummyModel


def test_load_entrypoints_and_missing_entrypoint(monkeypatch: pytest.MonkeyPatch):
    _install_test_module()

    class FakeEntryPoint:
        def __init__(self, name: str, obj: Any):
            self.name = name
            self._obj = obj

        def load(self) -> Any:
            return self._obj

    class FakeEntryPoints:
        def __init__(self):
            self._by_group = {
                "model_guardian.models": [FakeEntryPoint("dummy", DummyModel)],
            }

        def select(self, *, group: str):
            return self._by_group.get(group, [])

    monkeypatch.setattr(
        "model_guardian.core.registry.metadata.entry_points",
        lambda: FakeEntryPoints(),
    )

    eps = load_entrypoints("model_guardian.models")
    assert "dummy" in eps
    assert eps["dummy"] is DummyModel

    with pytest.raises(ValueError):
        resolve_plugin(PluginSpec(group="model_guardian.models", entrypoint="missing"))


def test_resolve_plugin_missing_entrypoint_raises(monkeypatch: pytest.MonkeyPatch):
    class FakeEntryPoints:
        def select(self, *, group: str):
            return []

    monkeypatch.setattr(
        "model_guardian.core.registry.metadata.entry_points",
        lambda: FakeEntryPoints(),
    )

    spec = PluginSpec(group="model_guardian.models", entrypoint="does_not_exist")
    with pytest.raises(ValueError):
        resolve_plugin(spec)


@pytest.mark.asyncio
async def test_build_guardian_wires_components_and_runs():
    mod = _install_test_module()

    guardian = build_guardian(
        model=PluginSpec(group="model_guardian.models", dotted_path=f"{mod}:DummyModel"),
        uncertainty=PluginSpec(
            group="model_guardian.uncertainty_adapters", dotted_path=f"{mod}:DummyUQ"
        ),
        drift=PluginSpec(group="model_guardian.drift_adapters", dotted_path=f"{mod}:DummyDrift"),
        policy=PluginSpec(group="model_guardian.policies", dotted_path=f"{mod}:DummyPolicy"),
        telemetry=PluginSpec(
            group="model_guardian.telemetry_sinks", dotted_path=f"{mod}:DummyTelemetry"
        ),
        model_kwargs={"bias": 2},
        uncertainty_kwargs={"fixed_aleatoric": 0.2, "fixed_epistemic": 0.3},
    )

    resp = await guardian([1.0, 2.0, 3.0])
    assert resp.prediction is not None
    assert resp.prediction.value == 8  # sum + bias
    assert resp.uncertainty is not None
    assert resp.uncertainty.aleatoric == 0.2
    assert resp.uncertainty.epistemic == 0.3