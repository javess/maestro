from pathlib import Path

from maestro.control_plane import (
    build_control_plane_snapshot,
    control_plane_config_path,
    write_default_control_plane_config,
)
from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.storage.local import MaestroWorkspace


def test_write_default_control_plane_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    path = write_default_control_plane_config(repo)

    assert path == control_plane_config_path(repo)
    assert path.exists()
    assert "organization" in path.read_text()


def test_build_control_plane_snapshot_includes_recent_runs(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    write_default_control_plane_config(repo)
    workspace = MaestroWorkspace.for_repo(repo)
    deps = build_engine_deps(
        project_root,
        project_root / "examples" / "maestro.example.yaml",
        workspace_root=workspace.root,
    )
    engine = OrchestratorEngine(project_root, deps)
    run_state = engine.new_state(repo, project_root / "examples" / "brief.md")
    deps.state_store.save(run_state)

    snapshot = build_control_plane_snapshot(
        repo,
        project_root / "examples" / "maestro.example.yaml",
    )

    assert snapshot.repo_path == str(repo.resolve())
    assert snapshot.recent_runs == [run_state.run_id]
    assert snapshot.credential_surfaces
    assert any(item.provider == "fake" for item in snapshot.credential_surfaces)
    assert any(item.resolved_source == "unsupported" for item in snapshot.credential_surfaces)
    assert "shared run history" in snapshot.boundary.hosted_extension_points
