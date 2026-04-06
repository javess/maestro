from pathlib import Path

from maestro.core.approval import build_approval_request
from maestro.core.evidence import build_evidence_bundle, collect_policy_findings
from maestro.schemas.contracts import (
    ApprovalMode,
    CheckResult,
    CodeChange,
    CodeResult,
    PolicyPack,
    RepoInfo,
    ReviewResult,
    RiskLevel,
    RiskScore,
    Ticket,
)


def test_collect_policy_findings_captures_failures() -> None:
    policy = PolicyPack(name="default", protected_paths=[".github/"])
    code_result = CodeResult(
        ticket_id="T-1",
        summary="Implemented change",
        changed_files=[CodeChange(path=".github/workflows/test.yml", summary="workflow change")],
        tests_added=[],
    )
    checks = [CheckResult(command="pytest", success=False, output="failed")]
    review = ReviewResult(ticket_id="T-1", approved=False, summary="Needs changes")

    violations, findings = collect_policy_findings(
        policy=policy,
        review_cycles=policy.max_review_cycles,
        code_result=code_result,
        checks=checks,
        review=review,
    )

    assert "tests_required" in violations
    assert "checks_failed" in violations
    assert any(item.startswith("protected_path:") for item in violations)
    assert {finding.rule for finding in findings} >= {
        "max_files_changed",
        "require_tests",
        "protected_paths",
        "checks",
        "review_approval",
        "review_cycles",
    }
    assert next(item for item in findings if item.rule == "checks").outcome == "fail"


def test_build_approval_request_respects_policy_thresholds() -> None:
    policy = PolicyPack(
        name="strict",
        approval_mode=ApprovalMode.review_go,
        approval_risk_level=RiskLevel.high,
    )
    request = build_approval_request(
        policy=policy,
        ticket_id="T-1",
        risk_score=RiskScore(score=6, level=RiskLevel.high),
    )

    assert request is not None
    assert request.mode is ApprovalMode.review_go
    assert request.required_approvals == 1


def test_build_evidence_bundle_includes_review_and_rollback_guidance() -> None:
    ticket = Ticket(
        id="T-1",
        title="Ticket",
        description="Description",
        acceptance_criteria=["one"],
    )
    code_result = CodeResult(
        ticket_id="T-1",
        summary="Implemented change",
        changed_files=[CodeChange(path="src/app.py", summary="app update")],
        commands=["pytest"],
        tests_added=["tests/test_app.py"],
    )
    checks = [CheckResult(command="pytest", success=False, output="failed")]
    review = ReviewResult(ticket_id="T-1", approved=False, summary="Needs changes")

    bundle = build_evidence_bundle(
        run_id="run-1",
        ticket=ticket,
        review_cycle=2,
        code_result=code_result,
        checks=checks,
        review=review,
        repo_info=RepoInfo(root=Path("."), repo_type="python", risky_paths=["src/"]),
        violations=["checks_failed", "review_rejected"],
        policy_findings=[],
        policy=PolicyPack(name="default"),
    )

    assert bundle.bundle_id == "T-1_evidence_2"
    assert bundle.diff_summary.changed_files == ["src/app.py"]
    assert bundle.review_result is not None
    assert bundle.risk_score is not None
    assert bundle.approval_request is None
    assert bundle.migration_plan is None
    assert bundle.metadata["violations"] == ["checks_failed", "review_rejected"]
    assert bundle.rollback_notes[0].steps[0].startswith("Revert changed files:")


def test_build_evidence_bundle_includes_migration_plan_when_paths_require_it() -> None:
    ticket = Ticket(
        id="T-2",
        title="Add migration",
        description="Update schema",
        acceptance_criteria=["schema updated"],
    )
    code_result = CodeResult(
        ticket_id="T-2",
        summary="Add migration",
        changed_files=[CodeChange(path="migrations/001_add_table.sql", summary="migration")],
        commands=["uv run pytest"],
    )
    review = ReviewResult(ticket_id="T-2", approved=True, summary="Approved")

    bundle = build_evidence_bundle(
        run_id="run-2",
        ticket=ticket,
        review_cycle=1,
        code_result=code_result,
        checks=[],
        review=review,
        repo_info=RepoInfo(root=Path("."), repo_type="python", risky_paths=["migrations/"]),
        violations=[],
        policy_findings=[],
        policy=PolicyPack(name="default"),
    )

    assert bundle.migration_plan is not None
    assert bundle.migration_plan.changed_paths == ["migrations/001_add_table.sql"]
