from __future__ import annotations

from pathlib import Path

from maestro.schemas.contracts import RepoDiscovery
from maestro.schemas.readiness import RepoReadiness, SupportTier


def assess_repo_readiness(root: Path, discovery: RepoDiscovery) -> RepoReadiness:
    signals = {
        "specialized_adapter": 25 if discovery.adapter_name != "generic" else 0,
        "git_repo": 15 if (root / ".git").exists() else 0,
        "build_commands": min(15, len(discovery.repo_info.build_commands) * 10),
        "test_commands": min(20, len(discovery.repo_info.test_commands) * 10),
        "lint_commands": min(15, len(discovery.repo_info.lint_commands) * 8),
        "guidance": min(10, len(discovery.repo_info.guidance) * 3),
    }
    score = sum(signals.values())
    blockers: list[str] = []
    recommendations: list[str] = []

    if discovery.adapter_name == "generic":
        blockers.append("No specialized repo adapter matched this repository.")
        recommendations.append("Add a supported build marker or extend repo adapter coverage.")
    if not (root / ".git").exists():
        blockers.append("Repository is not initialized as a git repo.")
        recommendations.append("Run git init so worktrees, branches, and commits can be used.")
    if not discovery.repo_info.test_commands:
        blockers.append("No test command was discovered.")
        recommendations.append(
            "Expose a deterministic test command for validation and repair loops."
        )
    if not discovery.repo_info.lint_commands:
        recommendations.append("Add a lint or type-check command to improve mutation safety.")

    if blockers and discovery.adapter_name == "generic":
        tier = SupportTier.planning_only
    elif blockers:
        tier = SupportTier.experimental
    elif score >= 60:
        tier = SupportTier.supported
    else:
        tier = SupportTier.experimental

    return RepoReadiness(
        tier=tier,
        score=score,
        blockers=blockers,
        recommendations=recommendations,
        signals=signals,
    )
