from __future__ import annotations

from maestro.preview.base import PreviewAdapter
from maestro.schemas.preview import PreviewArtifact, PreviewRequest, PreviewStatus


class NoopPreviewAdapter(PreviewAdapter):
    name = "noop"

    def build_preview(self, request: PreviewRequest) -> PreviewArtifact:
        return PreviewArtifact(
            adapter=self.name,
            status=PreviewStatus.placeholder,
            repo_path=request.repo_path,
            command=request.command,
            placeholders=["No preview command was executed."],
            notes=["Use the local adapter with an explicit command for a runnable preview."],
        )
