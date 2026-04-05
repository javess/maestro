from __future__ import annotations

from maestro.preview.base import PreviewAdapter
from maestro.preview.local import LocalPreviewAdapter
from maestro.preview.noop import NoopPreviewAdapter
from maestro.tools.shell import LocalShellRunner


def build_preview_adapter(name: str, shell: LocalShellRunner | None = None) -> PreviewAdapter:
    mapping = {
        "local": lambda: LocalPreviewAdapter(shell=shell),
        "noop": NoopPreviewAdapter,
    }
    builder = mapping.get(name)
    if builder is None:
        raise ValueError(f"Unsupported preview adapter: {name}")
    return builder()
