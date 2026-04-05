import subprocess
from pathlib import Path

from maestro.tools.git import GitWorktreeManager


def test_create_workspace_copy_ignores_tool_caches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    (repo / "tracked.txt").write_text("tracked\n")
    subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    (repo / "dirty.txt").write_text("dirty\n")
    (repo / ".venv").mkdir()
    (repo / ".venv" / "python").write_text("binary\n")
    (repo / "node_modules").mkdir()
    (repo / "node_modules" / "pkg.js").write_text("pkg\n")

    manager = GitWorktreeManager(repo)
    workspace, kind = manager.create_workspace(tmp_path / "workspace")

    assert kind == "copy"
    assert (workspace / "tracked.txt").read_text() == "tracked\n"
    assert (workspace / "dirty.txt").read_text() == "dirty\n"
    assert not (workspace / ".venv").exists()
    assert not (workspace / "node_modules").exists()
