from __future__ import annotations

from types import MappingProxyType

import pytest
import numpy as np

from model_guardian.core.utils import deep_freeze
from model_guardian.schemas import Prediction


def test_deep_freeze_produces_read_only_recursive_structures():
    frozen = deep_freeze({"a": [1, 2], "b": {"c": {"d": {1, 2}}}})

    assert isinstance(frozen, MappingProxyType)
    assert frozen["a"] == (1, 2)  # list -> tuple

    inner = frozen["b"]["c"]["d"]
    assert isinstance(inner, frozenset)  # set -> frozenset
    assert set(inner) == {1, 2}

    # read-only mapping
    with pytest.raises(TypeError):
        frozen["x"] = 1  # type: ignore[misc]


def test_prediction_raw_serializes_to_json_friendly_containers():
    # Serializer must handle already-frozen data structures.
    p = Prediction(value=1, raw=deep_freeze({"t": (1, 2, 3), "s": {"x", "y"}, "nested": {"l": ["a", "b"]}}))

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
