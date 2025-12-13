from __future__ import annotations

import asyncio

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from mapie.classification import MapieClassifier

from model_guardian import DefaultGuardian
from model_guardian.implementations.mapie.adapter import MapieModelAdapter, MapieUncertaintyAdapter
from model_guardian.core.telemetry import TelemetryFanout
from model_guardian.implementations.telemetry.jsonl import JsonlFileSink


async def main() -> None:
    iris = load_iris()
    X, y = iris.data, iris.target

    base = LogisticRegression(max_iter=200).fit(X, y)

    mapie = MapieClassifier(estimator=base, method="score")
    mapie.fit(X, y)

    model = MapieModelAdapter(mapie, model_id="iris_logreg", model_version="hello", alpha=0.1)
    uq = MapieUncertaintyAdapter()

    telemetry = TelemetryFanout([JsonlFileSink("telemetry/hello_world.jsonl")])

    guardian = DefaultGuardian(model=model, uncertainty=uq, telemetry=telemetry)

    x = X[0].tolist()
    resp = await guardian(x)
    print(resp.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
