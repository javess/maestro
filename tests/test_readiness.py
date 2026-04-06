import subprocess
from pathlib import Path

from maestro.repo.discovery import discover_repo
from maestro.repo.readiness import assess_repo_readiness
from maestro.schemas.readiness import SupportTier


def test_specialized_git_repo_scores_supported(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    readiness = assess_repo_readiness(tmp_path, discover_repo(tmp_path))
    assert readiness.tier is SupportTier.supported
    assert readiness.score >= 60


def test_generic_repo_without_git_is_planning_only(tmp_path: Path) -> None:
    readiness = assess_repo_readiness(tmp_path, discover_repo(tmp_path))
    assert readiness.tier is SupportTier.planning_only
    assert readiness.blockers
