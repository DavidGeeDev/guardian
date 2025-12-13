from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GuardianAction(str, Enum):
    ALLOW = "allow"
    ABSTAIN = "abstain"
    DEGRADE = "degrade"
    BLOCK = "block"


class GuardianDecision(BaseModel):
    """Decision emitted by the policy engine."""

    model_config = ConfigDict(extra="forbid")

    action: GuardianAction
    reason: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    # human-readable guidance for downstream UX
    user_message: Optional[str] = None
