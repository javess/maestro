from __future__ import annotations

from abc import ABC, abstractmethod

from maestro.schemas.preview import PreviewArtifact, PreviewRequest


class PreviewAdapter(ABC):
    name = "preview"

    @abstractmethod
    def build_preview(self, request: PreviewRequest) -> PreviewArtifact:
        raise NotImplementedError
