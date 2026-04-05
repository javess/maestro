from maestro.core.policy import enforce_code_policy, enforce_review_policy
from maestro.schemas.contracts import CodeChange, CodeResult, PolicyPack, ReviewResult


def test_policy_requires_tests() -> None:
    policy = PolicyPack(name="default")
    result = CodeResult(
        ticket_id="T-1",
        summary="s",
        changed_files=[CodeChange(path="x.py", summary="x")],
    )
    assert "tests_required" in enforce_code_policy(policy, result)


def test_review_cycle_exhausted() -> None:
    policy = PolicyPack(name="default", max_review_cycles=1)
    review = ReviewResult(ticket_id="T-1", approved=False, summary="n")
    assert "review_cycles_exhausted" in enforce_review_policy(policy, 1, review)
