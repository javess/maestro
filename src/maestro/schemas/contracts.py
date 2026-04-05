from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from maestro.schemas.run_graph import RunGraph


class Severity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TicketStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    escalated = "escalated"


class ProductSpec(BaseModel):
    title: str
    summary: str
    outcomes: list[str]
    scope: list[str]
    non_goals: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str]


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    acceptance_criteria: list[str]
    dependencies: list[str] = Field(default_factory=list)
    priority: int = 1
    status: TicketStatus = TicketStatus.pending


class Backlog(BaseModel):
    tickets: list[Ticket]


class CodeChange(BaseModel):
    path: str
    summary: str


class CodeResult(BaseModel):
    ticket_id: str
    summary: str
    changed_files: list[CodeChange] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    tests_added: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    success: bool = True


class CheckResult(BaseModel):
    command: str
    success: bool
    output: str = ""


class ReviewIssue(BaseModel):
    severity: Severity
    path: str | None = None
    message: str
    recommendation: str


class ReviewResult(BaseModel):
    ticket_id: str
    approved: bool
    summary: str
    issues: list[ReviewIssue] = Field(default_factory=list)


class RepoInfo(BaseModel):
    root: Path
    repo_type: str
    build_commands: list[str] = Field(default_factory=list)
    test_commands: list[str] = Field(default_factory=list)
    lint_commands: list[str] = Field(default_factory=list)
    risky_paths: list[str] = Field(default_factory=list)
    guidance: list[str] = Field(default_factory=list)


class RepoDiscovery(BaseModel):
    repo_info: RepoInfo
    adapter_name: str
    reasons: list[str] = Field(default_factory=list)


class PolicyPack(BaseModel):
    name: str
    max_review_cycles: int = 2
    require_tests: bool = True
    require_lint: bool = True
    require_format: bool = True
    max_files_changed: int = 20
    protected_paths: list[str] = Field(default_factory=list)
    dependency_change_rules: dict[str, Any] = Field(default_factory=dict)
    escalation_rules: dict[str, Any] = Field(default_factory=dict)


class ArtifactEntry(BaseModel):
    name: str
    path: str
    kind: str


class DiffSummary(BaseModel):
    changed_files: list[str] = Field(default_factory=list)
    file_count: int = 0
    summary: str = ""


class RollbackNote(BaseModel):
    summary: str
    steps: list[str] = Field(default_factory=list)


class PolicyFinding(BaseModel):
    rule: str
    outcome: Literal["pass", "fail", "warn", "not_applicable"]
    detail: str = ""


class EvidenceBundle(BaseModel):
    bundle_id: str
    run_id: str
    ticket_id: str | None = None
    diff_summary: DiffSummary = Field(default_factory=DiffSummary)
    checks: list[CheckResult] = Field(default_factory=list)
    policy_findings: list[PolicyFinding] = Field(default_factory=list)
    rollback_notes: list[RollbackNote] = Field(default_factory=list)
    review_result: ReviewResult | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactManifest(BaseModel):
    run_id: str
    artifacts: list[ArtifactEntry] = Field(default_factory=list)
    evidence_bundles: list[ArtifactEntry] = Field(default_factory=list)


class ProviderCapability(BaseModel):
    structured_outputs: bool = False
    tool_calling: bool = False
    streaming: bool = False
    vision: bool = False
    long_context: bool = False
    code_specialized: bool = False
    json_mode: bool = False


class ProviderModelInfo(BaseModel):
    provider: str
    model: str
    capabilities: ProviderCapability


class ProviderError(BaseModel):
    provider: str
    retryable: bool
    message: str


class RoleConfig(BaseModel):
    provider: str
    model: str


class FallbackConfig(BaseModel):
    provider: str
    model: str


class MaestroConfig(BaseModel):
    providers: dict[str, dict[str, Any]]
    llm: dict[str, RoleConfig]
    fallbacks: dict[str, list[FallbackConfig]] = Field(default_factory=dict)
    policy: str = "default"


class RunEvent(BaseModel):
    state: str
    detail: str


class RunState(BaseModel):
    run_id: str
    current_state: str
    repo_path: Path
    brief_path: Path | None = None
    run_graph: RunGraph | None = None
    run_graph_current_node_id: str | None = None
    backlog: Backlog = Field(default_factory=lambda: Backlog(tickets=[]))
    current_ticket_id: str | None = None
    completed_tickets: list[str] = Field(default_factory=list)
    review_cycles: int = 0
    artifacts: ArtifactManifest
    events: list[RunEvent] = Field(default_factory=list)
    status: Literal["running", "done", "escalated"] = "running"
