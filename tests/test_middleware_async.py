from __future__ import annotations

import pytest

pytest.importorskip("mapie")
from mapie.classification import MapieClassifier

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

from model_guardian import DefaultGuardian
from model_guardian.implementations.mapie.adapter import MapieModelAdapter, MapieUncertaintyAdapter


async def test_guardian_returns_response():
    iris = load_iris()
    X, y = iris.data, iris.target

    base = LogisticRegression(max_iter=200).fit(X, y)
    mapie = MapieClassifier(estimator=base, method="score")
    mapie.fit(X, y)

    g = DefaultGuardian(model=MapieModelAdapter(mapie), uncertainty=MapieUncertaintyAdapter())

    resp = await g(X[0].tolist())
    assert resp.decision is not None
    assert resp.uncertainty is not None
    # prediction may be None if abstained; default policy should allow for in-distribution iris
    assert resp.prediction is not None
