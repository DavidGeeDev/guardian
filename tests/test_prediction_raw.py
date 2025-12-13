from __future__ import annotations

from types import MappingProxyType

import numpy as np

from model_guardian.schemas import Prediction


def test_prediction_raw_is_deep_frozen_and_read_only():
    p = Prediction(
        value=123,
        raw={
            "a": [1, 2],
            "b": {"c": {"d": {1, 2}}},
        },
    )

    assert isinstance(p.raw, MappingProxyType)

    # list -> tuple
    assert p.raw["a"] == (1, 2)

    # set -> frozenset (deep)
    inner = p.raw["b"]["c"]["d"]
    assert isinstance(inner, frozenset)
    assert set(inner) == {1, 2}


def test_prediction_raw_serializes_to_json_friendly_containers():
    p = Prediction(
        value=1,
        raw={
            "t": (1, 2, 3),
            "s": frozenset({"x", "y"}),
            "nested": {"l": ["a", "b"]},
        },
    )

    dumped = p.model_dump()
    assert dumped["raw"]["t"] == [1, 2, 3]
    assert sorted(dumped["raw"]["s"]) == ["x", "y"]
    assert dumped["raw"]["nested"]["l"] == ["a", "b"]


def test_prediction_raw_numpy_arrays_are_serialized():
    p = Prediction(value=0, raw={"arr": np.asarray([1, 2, 3])})
    dumped = p.model_dump()
    assert dumped["raw"]["arr"] == [1, 2, 3]


def test_prediction_raw_none_round_trips():
    p = Prediction(value=0, raw=None)
    assert p.model_dump()["raw"] is None
