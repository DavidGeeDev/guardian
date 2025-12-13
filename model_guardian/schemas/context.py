from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


class RequestContext(BaseModel):
    """Per-request metadata for traceability and policy decisions."""

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional metadata to support future routing (tenanting, risk tier, etc.)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    tags: Mapping[str, Any] = Field(default_factory=dict)
