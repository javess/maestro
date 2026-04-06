from __future__ import annotations

from maestro.core.approval import build_approval_request
from maestro.core.migration import build_migration_plan
from maestro.core.policy import enforce_code_policy, enforce_review_policy
from maestro.core.risk import compute_risk_score
from maestro.schemas.contracts import (
    ApprovalRequest,
    CheckResult,
    CodeResult,
    DiffSummary,
    EvidenceBundle,
    PolicyFinding,
    PolicyPack,
    RepoInfo,
    ReviewResult,
    RollbackNote,
    Ticket,
)


def collect_policy_findings(
    *,
    policy: PolicyPack,
    review_cycles: int,
    code_result: CodeResult,
    checks: list[CheckResult],
    review: ReviewResult,
) -> tuple[list[str], list[PolicyFinding]]:
    violations = enforce_code_policy(policy, code_result)
    violations.extend(enforce_review_policy(policy, review_cycles, review))
    failing_checks = [check.command for check in checks if not check.success]
    if not review.approved:
        violations.append("review_rejected")
    if failing_checks:
        violations.append("checks_failed")

    policy_findings = [
        PolicyFinding(
            rule="max_files_changed",
            outcome="fail" if "max_files_changed_exceeded" in violations else "pass",
            detail=(
                f"changed_files={len(code_result.changed_files)} "
                f"limit={policy.max_files_changed}"
            ),
        ),
        PolicyFinding(
            rule="require_tests",
            outcome=(
                "not_applicable"
                if not policy.require_tests
                else "fail" if "tests_required" in violations else "pass"
            ),
            detail=(
                "policy disabled"
                if not policy.require_tests
                else f"tests_added={len(code_result.tests_added)}"
            ),
        ),
        PolicyFinding(
            rule="protected_paths",
            outcome=(
                "fail"
                if any(item.startswith("protected_path:") for item in violations)
                else "pass"
            ),
            detail=", ".join(item for item in violations if item.startswith("protected_path:")),
        ),
        PolicyFinding(
            rule="checks",
            outcome="fail" if failing_checks else "pass",
            detail=", ".join(failing_checks),
        ),
        PolicyFinding(
            rule="review_approval",
            outcome="pass" if review.approved else "fail",
            detail=review.summary,
        ),
        PolicyFinding(
            rule="review_cycles",
            outcome="fail" if "review_cycles_exhausted" in violations else "pass",
            detail=f"review_cycles={review_cycles} limit={policy.max_review_cycles}",
        ),
    ]
    return violations, policy_findings


def build_evidence_bundle(
    *,
    run_id: str,
    ticket: Ticket,
    review_cycle: int,
    code_result: CodeResult,
    checks: list[CheckResult],
    review: ReviewResult,
    repo_info: RepoInfo,
    violations: list[str],
    policy_findings: list[PolicyFinding],
    policy: PolicyPack,
    approval_request: ApprovalRequest | None = None,
) -> EvidenceBundle:
    changed_files = [change.path for change in code_result.changed_files]
    migration_plan = code_result.migration_plan or build_migration_plan(ticket, code_result)
    rollback_steps: list[str] = []
    if changed_files:
        rollback_steps.append(f"Revert changed files: {', '.join(changed_files)}")
    failed_checks = [check.command for check in checks if not check.success]
    if failed_checks:
        rollback_steps.append(f"Re-run failed checks: {', '.join(failed_checks)}")
    if not review.approved:
        rollback_steps.append("Address reviewer issues before resubmitting the ticket")
    rollback_notes = (
        [RollbackNote(summary=f"Rollback guidance for {ticket.id}", steps=rollback_steps)]
        if rollback_steps
        else []
    )
    risk_score = compute_risk_score(
        policy=policy,
        ticket=ticket,
        code_result=code_result,
        repo_info=repo_info,
    )
    return EvidenceBundle(
        bundle_id=f"{ticket.id}_evidence_{review_cycle}",
        run_id=run_id,
        ticket_id=ticket.id,
        diff_summary=DiffSummary(
            changed_files=changed_files,
            file_count=len(changed_files),
            summary=code_result.summary,
        ),
        checks=checks,
        policy_findings=policy_findings,
        migration_plan=migration_plan,
        rollback_notes=rollback_notes,
        review_result=review,
        risk_score=risk_score,
        approval_request=approval_request,
        commit_metadata=code_result.commit_metadata,
        metadata={
            "review_cycle": review_cycle,
            "violations": violations,
            "code_commands": code_result.commands,
            "code_notes": code_result.notes,
        },
    )


def determine_approval_request(
    *,
    policy: PolicyPack,
    ticket: Ticket,
    code_result: CodeResult,
    repo_info: RepoInfo,
    violations: list[str],
) -> ApprovalRequest | None:
    if violations:
        return None
    risk_score = compute_risk_score(
        policy=policy,
        ticket=ticket,
        code_result=code_result,
        repo_info=repo_info,
    )
    return build_approval_request(
        policy=policy,
        ticket_id=ticket.id,
        risk_score=risk_score,
    )
