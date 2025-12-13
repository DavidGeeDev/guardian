from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from model_guardian.core.utils import run_sync
from model_guardian.interfaces import DriftAdapter
from model_guardian.schemas import Prediction, RequestContext, Signal, SignalSeverity, SignalType

try:
    from alibi_detect.cd import KSDrift
except Exception:  # pragma: no cover
    KSDrift = None


@dataclass(frozen=True)
class AlibiDriftConfig:
    p_val: float = 0.05
    # For Phase 0, a simple KSDrift on tabular features is enough to demonstrate flow.
    # More advanced detectors (MMD, learned, embeddings) can be slotted later.
    name: str = "alibi_ks"
    blocking: bool = False  # drift should not block inference by default


class AlibiDriftAdapter(DriftAdapter[Sequence[float], Any]):
    """Non-blocking drift signal provider.

    Pattern:
    - Drift computation can be expensive; we run it in an executor via `run_sync`
      so it doesn't block the async event loop.
    - The Guardian wrapper treats drift as non-critical-path by default.
    """

    def __init__(self, detector: Any, cfg: AlibiDriftConfig | None = None):
        if detector is None:
            raise ValueError("detector must be an Alibi-Detect detector instance")
        self._detector = detector
        self.cfg = cfg or AlibiDriftConfig()
        self.name = self.cfg.name
        self.blocking = self.cfg.blocking

    async def compute(
        self,
        *,
        x: Sequence[float],
        prediction: Prediction[Any],
        context: RequestContext,
    ):
        X = np.asarray([list(x)], dtype=float)

        def _predict():
            return self._detector.predict(X)

        out = await run_sync(_predict)
        # Alibi-Detect returns dict with keys like 'data' containing p_val, is_drift, etc.
        data = out.get("data", {}) if isinstance(out, dict) else {}
        is_drift = bool(data.get("is_drift", False))
        p_val = data.get("p_val", None)

        severity = SignalSeverity.INFO
        if is_drift:
            severity = SignalSeverity.WARNING

        return [
            Signal(
                name="drift.ks",
                type=SignalType.DRIFT,
                severity=severity,
                value={"is_drift": is_drift, "p_val": p_val},
                details=data if isinstance(data, dict) else None,
                blocking=False,
            )
        ]


def build_ks_drift_reference(
    *,
    X_ref: np.ndarray,
    p_val: float = 0.05,
) -> Any:
    if KSDrift is None:  # pragma: no cover
        raise RuntimeError("alibi-detect KSDrift is not available")
    return KSDrift(X_ref, p_val=p_val)
