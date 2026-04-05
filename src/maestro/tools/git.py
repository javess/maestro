from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

IGNORED_WORKSPACE_PATTERNS = (
    ".git",
    ".maestro",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "dist",
    "build",
)


class GitWorktreeManager:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def is_dirty(self) -> bool:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        return bool(completed.stdout.strip())

    def current_branch(self) -> str:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed.stdout.strip()

    def create_workspace(self, target: Path) -> tuple[Path, str]:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not self.is_dirty():
            subprocess.run(
                ["git", "worktree", "add", "--detach", str(target), "HEAD"],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=True,
            )
            return target, "git_worktree"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            self.repo_root,
            target,
            ignore=shutil.ignore_patterns(*IGNORED_WORKSPACE_PATTERNS),
            dirs_exist_ok=True,
        )
        return target, "copy"

    def remove_workspace(self, target: Path, kind: str) -> None:
        if not target.exists():
            return
        if kind == "git_worktree":
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(target)],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
            subprocess.run(
                ["git", "worktree", "prune"],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
            return
        shutil.rmtree(target, ignore_errors=True)
