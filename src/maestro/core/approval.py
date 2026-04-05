from __future__ import annotations

from maestro.schemas.contracts import (
    ApprovalMode,
    ApprovalRequest,
    PolicyPack,
    RiskLevel,
    RiskScore,
)

RISK_ORDER = {
    RiskLevel.low: 0,
    RiskLevel.medium: 1,
    RiskLevel.high: 2,
    RiskLevel.critical: 3,
}


def requires_approval(policy: PolicyPack, risk_score: RiskScore) -> bool:
    if policy.approval_mode is ApprovalMode.auto_go:
        return False
    return RISK_ORDER[risk_score.level] >= RISK_ORDER[policy.approval_risk_level]


def build_approval_request(
    *,
    policy: PolicyPack,
    ticket_id: str,
    risk_score: RiskScore,
) -> ApprovalRequest | None:
    if not requires_approval(policy, risk_score):
        return None
    required_approvals = (
        1 if policy.approval_mode is ApprovalMode.review_go else policy.multi_approval_count
    )
    return ApprovalRequest(
        ticket_id=ticket_id,
        mode=policy.approval_mode,
        required_approvals=max(1, required_approvals),
        risk_level=risk_score.level,
        risk_score=risk_score.score,
        reason=(
            f"risk {risk_score.level.value} score={risk_score.score} "
            f"meets threshold {policy.approval_risk_level.value}"
        ),
    )
