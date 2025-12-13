from __future__ import annotations

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from model_guardian import DefaultGuardian
from model_guardian.core.telemetry import TelemetryFanout
from model_guardian.implementations.alibi_detect.adapter import AlibiDriftAdapter, build_ks_drift_reference
from model_guardian.implementations.mapie.adapter import MapieModelAdapter, MapieUncertaintyAdapter
from model_guardian.implementations.telemetry.jsonl import JsonlFileSink

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from mapie.classification import MapieClassifier

router = APIRouter()


class PredictRequest(BaseModel):
    features: List[float]


_guardian: DefaultGuardian | None = None


def get_demo_guardian() -> DefaultGuardian:
    global _guardian
    if _guardian is not None:
        return _guardian

    iris = load_iris()
    X, y = iris.data, iris.target

    clf = LogisticRegression(max_iter=200).fit(X, y)
    mapie = MapieClassifier(estimator=clf, method="score")
    mapie.fit(X, y)

    # Drift baseline (demo-only): KS drift on raw features vs training reference.
    ks = build_ks_drift_reference(X_ref=X.astype(float), p_val=0.05)
    drift = AlibiDriftAdapter(ks)

    model_adapter = MapieModelAdapter(mapie, model_id="iris_logreg", model_version="demo", alpha=0.1)
    uq = MapieUncertaintyAdapter()

    telemetry = TelemetryFanout([JsonlFileSink("telemetry/model_guardian.jsonl")])

    _guardian = DefaultGuardian(model=model_adapter, uncertainty=uq, drift=drift, telemetry=telemetry)
    return _guardian


@router.post("/predict")
async def predict(req: PredictRequest):
    g = get_demo_guardian()
    return (await g(req.features)).model_dump()
