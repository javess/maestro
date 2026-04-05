from __future__ import annotations

import subprocess
from pathlib import Path


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
