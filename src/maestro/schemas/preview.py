from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from maestro.schemas.contracts import CheckResult, RepoInfo


class PreviewStatus(StrEnum):
    ready = "ready"
    failed = "failed"
    placeholder = "placeholder"


class PreviewRequest(BaseModel):
    repo_path: Path
    repo_info: RepoInfo
    command: str | None = None


class PreviewArtifact(BaseModel):
    adapter: str
    status: PreviewStatus
    repo_path: Path
    command: str | None = None
    url: str | None = None
    smoke_results: list[CheckResult] = Field(default_factory=list)
    screenshots: list[str] = Field(default_factory=list)
    placeholders: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
