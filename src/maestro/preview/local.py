from __future__ import annotations

import logging

from maestro.preview.base import PreviewAdapter
from maestro.schemas.contracts import CheckResult
from maestro.schemas.preview import PreviewArtifact, PreviewRequest, PreviewStatus
from maestro.tools.shell import LocalShellRunner

logger = logging.getLogger(__name__)


class LocalPreviewAdapter(PreviewAdapter):
    name = "local"

    def __init__(self, shell: LocalShellRunner | None = None) -> None:
        self.shell = shell or LocalShellRunner()

    def build_preview(self, request: PreviewRequest) -> PreviewArtifact:
        if not request.command:
            raise ValueError("local preview adapter requires a command")
        logger.info("preview_local_start repo=%s command=%s", request.repo_path, request.command)
        result = self.shell.run(request.command, request.repo_path)
        check = CheckResult(
            command=request.command,
            success=result.ok,
            output=(result.stdout + result.stderr).strip(),
        )
        return PreviewArtifact(
            adapter=self.name,
            status=PreviewStatus.ready if result.ok else PreviewStatus.failed,
            repo_path=request.repo_path,
            command=request.command,
            smoke_results=[check],
            notes=["Local preview executed as a smoke command against the target repo."],
        )
