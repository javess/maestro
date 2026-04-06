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
IGNORED_STATUS_PREFIXES = (".maestro/",)


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
        for line in completed.stdout.splitlines():
            path = line[3:]
            if any(
                path == prefix.rstrip("/") or path.startswith(prefix)
                for prefix in IGNORED_STATUS_PREFIXES
            ):
                continue
            return True
        return False

    def current_branch(self) -> str:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed.stdout.strip()

    def checkout_branch(self, branch: str) -> None:
        subprocess.run(
            ["git", "checkout", "-B", branch],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=True,
        )

    def commit_paths(self, *, paths: list[str], message: str) -> str | None:
        subprocess.run(
            ["git", "add", "--", *paths],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if status.returncode == 0:
            return None
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=True,
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
            self._remove_tree(target)
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
        self._remove_tree(target)

    def _remove_tree(self, target: Path) -> None:
        try:
            shutil.rmtree(target)
        except OSError:
            subprocess.run(
                ["rm", "-rf", str(target)],
                text=True,
                capture_output=True,
                check=True,
            )
