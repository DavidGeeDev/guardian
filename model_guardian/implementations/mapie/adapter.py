from __future__ import annotations

import time
from typing import Any, Optional, Sequence, TypeVar, Generic

import numpy as np

try:
    from mapie.classification import MapieClassifier
    from mapie.regression import MapieRegressor
except ImportError:  # pragma: no cover
    MapieClassifier = None  # type: ignore[assignment]
    MapieRegressor = None  # type: ignore[assignment]

from model_guardian.core.utils import run_sync
from model_guardian.interfaces import ModelAdapter, UncertaintyAdapter
from model_guardian.schemas import Prediction, RequestContext, UncertaintyScore

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class MapieModelAdapter(ModelAdapter[Sequence[float], Any]):
    """ModelAdapter that runs MAPIE inference and stores conformal artifacts in Prediction.raw."""

    def __init__(
        self,
        mapie: Any,
        *,
        model_id: str | None = None,
        model_version: str | None = None,
        alpha: float = 0.1,
    ):
        self._mapie = mapie
        self._model_id = model_id
        self._model_version = model_version
        self._alpha = alpha

    @property
    def model_id(self) -> str | None:
        return self._model_id

    @property
    def model_version(self) -> str | None:
        return self._model_version

    async def predict(self, x: Sequence[float], *, context: RequestContext) -> Prediction[Any]:
        if MapieClassifier is None or MapieRegressor is None:
            raise RuntimeError(
                "MAPIE is not installed. Install dependencies with `pip install model-guardian[dev]` "
                "or `pip install mapie` (Phase 0 pins mapie<1.0)."
            )
        X = np.asarray([list(x)], dtype=float)

        def _predict_sync():
            if MapieClassifier is not None and isinstance(self._mapie, MapieClassifier):
                y_pred, y_ps = self._mapie.predict(X, alpha=self._alpha)
                proba = None
                if hasattr(self._mapie, "predict_proba"):
                    try:
                        proba = self._mapie.predict_proba(X)
                    except Exception:
                        proba = None
                return dict(kind="classification", y_pred=y_pred, y_ps=y_ps, proba=proba)
            # regression
            y_pred, y_pis = self._mapie.predict(X, alpha=self._alpha)
            return dict(kind="regression", y_pred=y_pred, y_pis=y_pis)

        t0 = time.perf_counter()
        out = await run_sync(_predict_sync)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        if out["kind"] == "classification":
            label = out["y_pred"][0]
            raw = {"prediction_set": out["y_ps"], "alpha": self._alpha, "classes": getattr(self._mapie, "classes_", None)}
            return Prediction(
                value=int(label) if np.issubdtype(type(label), np.integer) or isinstance(label, (np.integer,)) else label,
                proba=out["proba"],
                raw=raw,
                model_id=self.model_id,
                model_version=self.model_version,
                latency_ms=latency_ms,
            )

        # regression
        yhat = float(out["y_pred"][0])
        raw = {"prediction_interval": out["y_pis"], "alpha": self._alpha}
        return Prediction(
            value=yhat,
            raw=raw,
            model_id=self.model_id,
            model_version=self.model_version,
            latency_ms=latency_ms,
        )


class MapieUncertaintyAdapter(UncertaintyAdapter[Sequence[float], Any]):
    """Derive UncertaintyScore from MAPIE prediction sets/intervals.

    Signal extraction logic aligns with the research brief:
    - prediction set size of 1 => high confidence
    - larger set size => higher *aleatoric* uncertainty (ambiguity)
    - empty set => higher *epistemic* uncertainty (no class plausible / OOD proxy)
    """

    def __init__(self, *, method: str = "mapie", max_classes_hint: Optional[int] = None):
        self._method = method
        self._max_classes_hint = max_classes_hint

    async def quantify(
        self,
        *,
        x: Sequence[float],
        prediction: Prediction[Any],
        context: RequestContext,
    ) -> UncertaintyScore:
        raw = prediction.raw or {}

        if "prediction_set" in raw:
            y_ps = raw["prediction_set"]
            # MAPIE can return shape (n, n_classes) or (n, n_classes, n_alpha)
            arr = np.asarray(y_ps)
            if arr.ndim == 3:
                arr = arr[:, :, 0]
            if arr.ndim != 2:
                raise ValueError(f"Unexpected MAPIE prediction_set shape: {arr.shape}")

            set_size = int(arr[0].sum())
            classes = raw.get("classes")
            max_classes = self._max_classes_hint
            if max_classes is None:
                try:
                    max_classes = len(classes) if classes is not None else arr.shape[1]
                except Exception:
                    max_classes = arr.shape[1]

            # Map to normalized scores.
            # Epistemic: empty set -> 1.0, else 0.0 (Phase 0 heuristic).
            epistemic = 1.0 if set_size == 0 else 0.0

            # Aleatoric: grows with set size > 1.
            if max_classes <= 1:
                aleatoric = 0.0
            else:
                aleatoric = float(max(0, set_size - 1) / (max_classes - 1))
                aleatoric = min(1.0, max(0.0, aleatoric))

            return UncertaintyScore(
                aleatoric=aleatoric,
                epistemic=epistemic,
                prediction_set_size=set_size,
                coverage=1.0 - float(raw.get("alpha", 0.1)),
                method=self._method,
            )

        if "prediction_interval" in raw:
            y_pis = np.asarray(raw["prediction_interval"])
            # Expect shape (n, 2, n_alpha) or (n, 2)
            if y_pis.ndim == 3:
                lo, hi = float(y_pis[0, 0, 0]), float(y_pis[0, 1, 0])
            elif y_pis.ndim == 2:
                lo, hi = float(y_pis[0, 0]), float(y_pis[0, 1])
            else:
                raise ValueError(f"Unexpected MAPIE prediction_interval shape: {y_pis.shape}")

            width = max(0.0, hi - lo)
            # Phase 0: interpret width as aleatoric-like uncertainty proxy; epistemic left as 0.
            # (Future phases can use separate decomposition methods.)
            aleatoric = float(min(1.0, width / (abs(prediction.value) + 1e-6 + width)))
            return UncertaintyScore(
                aleatoric=aleatoric,
                epistemic=0.0,
                prediction_set_size=None,
                coverage=1.0 - float(raw.get("alpha", 0.1)),
                method=self._method,
            )

        # If no artifacts, return "unknown"
        return UncertaintyScore(aleatoric=0.0, epistemic=0.0, method="mapie:missing_artifacts")
