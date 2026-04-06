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


def test_create_workspace_replaces_existing_nested_copy_workspace(tmp_path: Path) -> None:
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

    manager = GitWorktreeManager(repo)
    target = tmp_path / "workspace"
    existing = target / "docs" / "runbooks"
    existing.mkdir(parents=True)
    (existing / "stale.md").write_text("stale\n")

    workspace, kind = manager.create_workspace(target)

    assert kind == "copy"
    assert workspace == target
    assert (workspace / "tracked.txt").read_text() == "tracked\n"
    assert not (workspace / "docs" / "runbooks" / "stale.md").exists()


def test_checkout_branch_and_commit_paths(tmp_path: Path) -> None:
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

    manager = GitWorktreeManager(repo)
    manager.checkout_branch("maestro/test-run")

    (repo / "tracked.txt").write_text("updated\n")
    commit_hash = manager.commit_paths(paths=["tracked.txt"], message="update tracked")

    assert commit_hash is not None
    assert manager.current_branch() == "maestro/test-run"
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "update tracked" in log.stdout
