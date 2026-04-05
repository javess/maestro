from pathlib import Path

from maestro.core.engine import OrchestratorEngine, build_engine_deps


def test_run_plan_completes(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    deps = build_engine_deps(project_root, project_root / "examples" / "maestro.example.yaml")
    engine = OrchestratorEngine(project_root, deps)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")
    assert state.status in {"done", "escalated"}
