from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Observation(BaseModel):
    source: Literal["check", "review", "user_feedback", "runtime"]
    category: Literal["error", "latency", "feedback", "regression", "operational"]
    summary: str
    detail: str = ""
    path: str | None = None
    severity: Literal["low", "medium", "high", "critical"] = "medium"


class ObservationFollowUp(BaseModel):
    id: str
    title: str
    description: str
    priority: int = 1
    acceptance_criteria: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)


class ObservationCompilation(BaseModel):
    observations: list[Observation] = Field(default_factory=list)
    follow_ups: list[ObservationFollowUp] = Field(default_factory=list)
