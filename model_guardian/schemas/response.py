from __future__ import annotations

from typing import Generic, Optional, TypeVar, List

from pydantic import BaseModel, ConfigDict, Field

from .decision import GuardianDecision
from .failure import FailureRecord
from .prediction import Prediction
from .signal import Signal
from .uncertainty import UncertaintyScore

T = TypeVar("T")


class GuardianResponse(BaseModel, Generic[T]):
    """Final output of the Guardian wrapper.

    Exactly one of (prediction, failure) should be populated.
    """

    model_config = ConfigDict(extra="forbid")

    prediction: Optional[Prediction[T]] = None
    failure: Optional[FailureRecord] = None

    uncertainty: Optional[UncertaintyScore] = None
    decision: GuardianDecision

    signals: List[Signal] = Field(default_factory=list)
