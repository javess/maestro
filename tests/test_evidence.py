from maestro.core.evidence import build_evidence_bundle, collect_policy_findings
from maestro.schemas.contracts import (
    CheckResult,
    CodeChange,
    CodeResult,
    PolicyPack,
    ReviewResult,
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
        violations=["checks_failed", "review_rejected"],
        policy_findings=[],
    )

    assert bundle.bundle_id == "T-1_evidence_2"
    assert bundle.diff_summary.changed_files == ["src/app.py"]
    assert bundle.review_result is not None
    assert bundle.metadata["violations"] == ["checks_failed", "review_rejected"]
    assert bundle.rollback_notes[0].steps[0].startswith("Revert changed files:")
