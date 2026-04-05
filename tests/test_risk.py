from pathlib import Path

from maestro.core.risk import compute_risk_score
from maestro.schemas.contracts import CodeChange, CodeResult, PolicyPack, RepoInfo, Ticket


def _ticket() -> Ticket:
    return Ticket(
        id="T-1",
        title="Harden billing auth path",
        description="Touch auth and billing flow",
        acceptance_criteria=["update payment guardrails"],
    )


def _repo_info() -> RepoInfo:
    return RepoInfo(root=Path("."), repo_type="python", risky_paths=["migrations/", "infra/"])


def test_risk_score_is_deterministic_for_same_inputs() -> None:
    policy = PolicyPack(name="default")
    code_result = CodeResult(
        ticket_id="T-1",
        summary="Update service",
        changed_files=[CodeChange(path="src/auth/service.py", summary="auth change")],
        tests_added=["tests/test_auth.py"],
    )

    first = compute_risk_score(
        policy=policy, ticket=_ticket(), code_result=code_result, repo_info=_repo_info()
    )
    second = compute_risk_score(
        policy=policy, ticket=_ticket(), code_result=code_result, repo_info=_repo_info()
    )

    assert first == second


def test_risk_score_detects_migrations_and_protected_paths() -> None:
    policy = PolicyPack(
        name="strict",
        protected_paths=[".github/", "infra/"],
        dependency_change_rules={"allow_lockfile_updates": False},
    )
    code_result = CodeResult(
        ticket_id="T-1",
        summary="High risk change",
        changed_files=[
            CodeChange(path=".github/workflows/test.yml", summary="workflow"),
            CodeChange(path="migrations/001_add_user_table.sql", summary="migration"),
            CodeChange(path="pyproject.toml", summary="dependency change"),
        ],
        tests_added=["tests/test_policy.py"],
    )

    score = compute_risk_score(
        policy=policy, ticket=_ticket(), code_result=code_result, repo_info=_repo_info()
    )

    factor_names = {factor.name for factor in score.factors}
    assert {"protected_path", "migration_change", "dependency_change_restricted"} <= factor_names
    assert score.level.value in {"high", "critical"}


def test_policy_configuration_influences_risk_thresholds_and_weights() -> None:
    code_result = CodeResult(
        ticket_id="T-1",
        summary="Lockfile update",
        changed_files=[CodeChange(path="package-lock.json", summary="lockfile")],
        tests_added=["tests/test_lockfile.py"],
    )
    repo_info = RepoInfo(root=Path("."), repo_type="node", risky_paths=["package-lock.json"])
    default_policy = PolicyPack(name="default")
    prototype_policy = PolicyPack(
        name="prototype",
        risk_weights={
            "blast_radius_medium": 1,
            "blast_radius_large": 2,
            "protected_path": 2,
            "repo_risky_path": 1,
            "dependency_change": 0,
            "dependency_change_restricted": 1,
            "migration_change": 2,
            "sensitive_area": 1,
            "ticket_sensitive_domain": 0,
        },
        risk_thresholds={"medium": 4, "high": 7, "critical": 10},
        dependency_change_rules={"allow_lockfile_updates": True},
    )

    default_score = compute_risk_score(
        policy=default_policy, ticket=_ticket(), code_result=code_result, repo_info=repo_info
    )
    prototype_score = compute_risk_score(
        policy=prototype_policy, ticket=_ticket(), code_result=code_result, repo_info=repo_info
    )

    assert default_score.score > prototype_score.score
    assert default_score.level != prototype_score.level
