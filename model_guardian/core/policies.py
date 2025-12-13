from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, TypeVar, Generic

from model_guardian.interfaces import AbstentionPolicy
from model_guardian.schemas import (
    GuardianAction,
    GuardianDecision,
    Prediction,
    RequestContext,
    Signal,
    UncertaintyScore,
)

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass(frozen=True)
class ThresholdPolicyConfig:
    """Simple tier-1 policy for Phase 0.

    Keep defaults conservative; thresholds are governance-controlled.
    """

    epistemic_abstain_at: float = 0.7
    aleatoric_degrade_at: float = 0.7


class ThresholdAbstentionPolicy(AbstentionPolicy[InputT, OutputT], Generic[InputT, OutputT]):
    def __init__(self, cfg: ThresholdPolicyConfig | None = None):
        self.cfg = cfg or ThresholdPolicyConfig()

    async def decide(
        self,
        *,
        x: InputT,
        prediction: Prediction[OutputT],
        uncertainty: UncertaintyScore,
        signals: Sequence[Signal],
        context: RequestContext,
    ) -> GuardianDecision:
        if uncertainty.epistemic >= self.cfg.epistemic_abstain_at:
            return GuardianDecision(
                action=GuardianAction.ABSTAIN,
                reason="High epistemic uncertainty (out-of-depth).",
                confidence=1.0 - uncertainty.epistemic,
                user_message="I’m not confident enough to answer safely for this input.",
            )

        if uncertainty.aleatoric >= self.cfg.aleatoric_degrade_at:
            return GuardianDecision(
                action=GuardianAction.DEGRADE,
                reason="High aleatoric uncertainty (ambiguous/noisy input).",
                confidence=1.0 - uncertainty.aleatoric,
                user_message="I can respond, but the input seems ambiguous—consider clarifying or providing more detail.",
            )

        return GuardianDecision(
            action=GuardianAction.ALLOW,
            reason="Signals within acceptable bounds.",
            confidence=min(1.0, 1.0 - max(uncertainty.aleatoric, uncertainty.epistemic)),
        )
