from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ShellResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class LocalShellRunner:
    def run(self, command: str, cwd: Path) -> ShellResult:
        logger.info("shell_run_start cwd=%s command=%s", cwd, command)
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )
        level = logging.INFO if completed.returncode == 0 else logging.WARNING
        logger.log(
            level,
            "shell_run_complete cwd=%s command=%s returncode=%s",
            cwd,
            command,
            completed.returncode,
        )
        return ShellResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
