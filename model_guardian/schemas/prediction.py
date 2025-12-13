from __future__ import annotations

from datetime import datetime
from collections.abc import Mapping
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer

T = TypeVar("T")


class Prediction(BaseModel, Generic[T]):
    """A model prediction plus optional raw artifacts.

    `raw` is designed to carry framework-specific artifacts without breaking the typed envelope:
    - MAPIE: prediction set / interval
    - TorchCP (future): tensors on GPU
    - LLMs (future): logits, token-level stats, etc.
    """

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        frozen=True,
        # Allow fields like model_id/model_version without pydantic warnings.
        protected_namespaces=(),
    )

    value: T
    proba: Optional[Any] = None  # allow np.ndarray/list for classification; kept flexible
    raw: Optional[Mapping[str, Any]] = None

    model_id: Optional[str] = None
    model_version: Optional[str] = None

    created_at: Optional[datetime] = None
    latency_ms: Optional[float] = Field(default=None, ge=0.0)

    @field_serializer("raw")
    def _serialize_raw(self, v: Optional[Mapping[str, Any]]) -> Optional[Any]:
        """Serialize read-only/raw artifacts to JSON-friendly plain containers."""
        if v is None:
            return None

        def to_plain(obj: Any) -> Any:
            if isinstance(obj, Mapping):
                return {k: to_plain(val) for k, val in obj.items()}
            if isinstance(obj, tuple):
                return [to_plain(x) for x in obj]
            if isinstance(obj, frozenset):
                return [to_plain(x) for x in obj]
            # numpy arrays are common artifacts; ensure they serialize cleanly
            try:
                import numpy as np  # type: ignore
            except ImportError:
                np = None  # type: ignore

            if np is not None and isinstance(obj, np.ndarray):  # type: ignore[attr-defined]
                # If numpy is present, do not swallow errors from tolist(); those indicate real bugs.
                return obj.tolist()
            return obj

        return to_plain(v)
