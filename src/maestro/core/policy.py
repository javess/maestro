from __future__ import annotations

from maestro.schemas.contracts import CodeResult, PolicyPack, ReviewResult


def enforce_code_policy(policy: PolicyPack, result: CodeResult) -> list[str]:
    violations: list[str] = []
    if len(result.changed_files) > policy.max_files_changed:
        violations.append("max_files_changed_exceeded")
    for change in result.changed_files:
        if any(change.path.startswith(prefix) for prefix in policy.protected_paths):
            violations.append(f"protected_path:{change.path}")
    if policy.require_tests and not result.tests_added:
        violations.append("tests_required")
    return violations


def enforce_review_policy(
    policy: PolicyPack,
    review_cycles: int,
    review: ReviewResult,
) -> list[str]:
    violations: list[str] = []
    if not review.approved and review_cycles >= policy.max_review_cycles:
        violations.append("review_cycles_exhausted")
    return violations
