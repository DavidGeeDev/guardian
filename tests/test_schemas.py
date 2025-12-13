from __future__ import annotations

from model_guardian.schemas import GuardianAction, GuardianDecision, UncertaintyScore, FailureRecord, FailureType


def test_uncertainty_score_bounds():
    u = UncertaintyScore(aleatoric=0.2, epistemic=0.7, method="x")
    assert 0.0 <= u.aleatoric <= 1.0
    assert 0.0 <= u.epistemic <= 1.0


def test_decision():
    d = GuardianDecision(action=GuardianAction.ALLOW, reason="ok", confidence=0.9)
    assert d.action == GuardianAction.ALLOW


def test_failure_record():
    f = FailureRecord(failure_type=FailureType.EPISTEMIC_OOD, message="nope")
    assert f.failure_type == FailureType.EPISTEMIC_OOD
