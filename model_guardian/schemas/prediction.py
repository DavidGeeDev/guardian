from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Prediction(BaseModel, Generic[T]):
    """A model prediction plus optional raw artifacts.

    `raw` is designed to carry framework-specific artifacts without breaking the typed envelope:
    - MAPIE: prediction set / interval
    - TorchCP (future): tensors on GPU
    - LLMs (future): logits, token-level stats, etc.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    value: T
    proba: Optional[Any] = None  # allow np.ndarray/list for classification; kept flexible
    raw: Optional[Dict[str, Any]] = None

    model_id: Optional[str] = None
    model_version: Optional[str] = None

    created_at: Optional[datetime] = None
    latency_ms: Optional[float] = Field(default=None, ge=0.0)
