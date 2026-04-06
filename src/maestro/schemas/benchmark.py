from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkScenarioResult(BaseModel):
    scenario: str
    repo_type: str
    provider: str
    status: str
    score: int
    retries: int
    notes: list[str] = Field(default_factory=list)


class BenchmarkReport(BaseModel):
    total_score: int
    scenario_count: int
    average_score: float
    scenarios: list[BenchmarkScenarioResult] = Field(default_factory=list)
