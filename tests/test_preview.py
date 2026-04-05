from pathlib import Path

from typer.testing import CliRunner

from maestro.cli.main import app
from maestro.preview.factory import build_preview_adapter
from maestro.schemas.contracts import RepoInfo
from maestro.schemas.preview import PreviewRequest, PreviewStatus


def test_noop_preview_adapter_returns_placeholder(tmp_path: Path) -> None:
    adapter = build_preview_adapter("noop")
    artifact = adapter.build_preview(
        PreviewRequest(
            repo_path=tmp_path,
            repo_info=RepoInfo(root=tmp_path, repo_type="generic"),
        )
    )
    assert artifact.status is PreviewStatus.placeholder
    assert artifact.placeholders


def test_local_preview_adapter_runs_command(tmp_path: Path) -> None:
    runner = build_preview_adapter("local")
    script = tmp_path / "main.py"
    script.write_text("print('preview ok')\n")
    artifact = runner.build_preview(
        PreviewRequest(
            repo_path=tmp_path,
            repo_info=RepoInfo(root=tmp_path, repo_type="python"),
            command="python main.py",
        )
    )
    assert artifact.status is PreviewStatus.ready
    assert "preview ok" in artifact.smoke_results[0].output


def test_preview_cli_persists_local_preview(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='preview-fixture'\n")
    (repo / "main.py").write_text("print('preview cli ok')\n")

    result = CliRunner().invoke(
        app,
        [
            "preview",
            "--repo",
            str(repo),
            "--adapter",
            "local",
            "--command",
            "python main.py",
        ],
    )

    assert result.exit_code == 0
    assert "preview cli ok" in result.output
