from __future__ import annotations

from pathlib import Path

from maestro.schemas.contracts import RepoContextFile, RepoContextSnapshot
from maestro.schemas.impact import ImpactAnalysis

_MAX_SNAPSHOT_FILES = 8
_MAX_FILE_BYTES = 12_000


def build_repo_snapshot(
    repo_root: Path,
    impact_analysis: ImpactAnalysis | None,
) -> RepoContextSnapshot:
    if impact_analysis is None:
        return RepoContextSnapshot()
    files: list[RepoContextFile] = []
    truncated = False
    for relative in impact_analysis.context_slice[:_MAX_SNAPSHOT_FILES]:
        path = repo_root / relative
        if not path.exists() or not path.is_file():
            continue
        content = path.read_text(errors="ignore")
        if len(content.encode("utf-8")) > _MAX_FILE_BYTES:
            content = content.encode("utf-8")[:_MAX_FILE_BYTES].decode("utf-8", errors="ignore")
            truncated = True
        files.append(RepoContextFile(path=relative, content=content))
    if len(impact_analysis.context_slice) > _MAX_SNAPSHOT_FILES:
        truncated = True
    return RepoContextSnapshot(files=files, truncated=truncated)
