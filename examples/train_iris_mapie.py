from __future__ import annotations

import joblib

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from mapie.classification import MapieClassifier


def main() -> None:
    iris = load_iris()
    X, y = iris.data, iris.target

    base = LogisticRegression(max_iter=200).fit(X, y)
    mapie = MapieClassifier(estimator=base, method="score")
    mapie.fit(X, y)

    joblib.dump(mapie, "iris_mapie.joblib")
    print("Saved iris_mapie.joblib")


if __name__ == "__main__":
    main()
