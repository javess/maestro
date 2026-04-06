from __future__ import annotations

from pydantic import BaseModel, Field


class EvalScenarioResult(BaseModel):
    scenario: str
    status: str
    current_state: str
    expected_state: str
    expected_status: str
    evidence_bundles: int
    retries: int
    schema_errors: int
    policy_violations: int
    passed: bool
    assertions: list[str] = Field(default_factory=list)


class EvalSummary(BaseModel):
    scenario_count: int
    passed: int
    failed: int
    total_retries: int
    total_schema_errors: int
    total_policy_violations: int


class EvalReport(BaseModel):
    summary: EvalSummary
    scenarios: list[EvalScenarioResult] = Field(default_factory=list)
