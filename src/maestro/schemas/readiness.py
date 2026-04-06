from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SupportTier(StrEnum):
    supported = "supported"
    experimental = "experimental"
    planning_only = "planning_only"


class RepoReadiness(BaseModel):
    tier: SupportTier
    score: int
    blockers: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    signals: dict[str, int] = Field(default_factory=dict)
