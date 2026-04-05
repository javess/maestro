from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from maestro.schemas.architecture import ArchitectureArtifacts
from maestro.schemas.backlog_graph import BacklogGraph
from maestro.schemas.impact import ImpactAnalysis
from maestro.schemas.run_graph import RunGraph


class Severity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ApprovalMode(StrEnum):
    auto_go = "auto_go"
    review_go = "review_go"
    multi_go = "multi_go"


class AssumptionKind(StrEnum):
    stated_fact = "stated_fact"
    inferred_fact = "inferred_fact"
    guess = "guess"
    unresolved_question = "unresolved_question"


class TicketStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    escalated = "escalated"


class ProductSpec(BaseModel):
    title: str
    summary: str
    problem: str
    target_users: list[str] = Field(default_factory=list)
    outcomes: list[str]
    scope: list[str]
    non_goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    assumption_log: list[AssumptionRecord] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str]


class CompiledBrief(BaseModel):
    raw_text: str
    title_hint: str = ""
    summary_hint: str = ""
    problem_points: list[str] = Field(default_factory=list)
    target_users: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    scope: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    assumption_log: list[AssumptionRecord] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)


class AssumptionRecord(BaseModel):
    kind: AssumptionKind
    statement: str
    source: Literal["brief", "product_spec", "planning"] = "brief"


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    acceptance_criteria: list[str]
    dependencies: list[str] = Field(default_factory=list)
    priority: int = 1
    parallelizable: bool = False
    status: TicketStatus = TicketStatus.pending


class Backlog(BaseModel):
    tickets: list[Ticket]
    assumption_log: list[AssumptionRecord] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    architecture_artifacts: ArchitectureArtifacts | None = None
    execution_graph: BacklogGraph | None = None
    impact_analyses: dict[str, ImpactAnalysis] = Field(default_factory=dict)


class CodeChange(BaseModel):
    path: str
    summary: str


class FileOperation(BaseModel):
    path: str
    action: Literal["write", "delete"]
    content: str | None = None
    executable: bool = False


class RepoContextFile(BaseModel):
    path: str
    content: str


class RepoContextSnapshot(BaseModel):
    files: list[RepoContextFile] = Field(default_factory=list)
    truncated: bool = False


class CodeResult(BaseModel):
    ticket_id: str
    summary: str
    changed_files: list[CodeChange] = Field(default_factory=list)
    file_operations: list[FileOperation] = Field(default_factory=list)
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
    max_parallel_tickets: int = 1
    require_tests: bool = True
    require_lint: bool = True
    require_format: bool = True
    max_files_changed: int = 20
    protected_paths: list[str] = Field(default_factory=list)
    dependency_change_rules: dict[str, Any] = Field(default_factory=dict)
    escalation_rules: dict[str, Any] = Field(default_factory=dict)
    approval_mode: ApprovalMode = ApprovalMode.auto_go
    approval_risk_level: RiskLevel = RiskLevel.high
    multi_approval_count: int = 2
    risk_weights: dict[str, int] = Field(
        default_factory=lambda: {
            "blast_radius_medium": 2,
            "blast_radius_large": 4,
            "protected_path": 4,
            "repo_risky_path": 3,
            "dependency_change": 2,
            "dependency_change_restricted": 4,
            "migration_change": 4,
            "sensitive_area": 3,
            "ticket_sensitive_domain": 2,
        }
    )
    risk_thresholds: dict[str, int] = Field(
        default_factory=lambda: {"medium": 3, "high": 6, "critical": 10}
    )
    sensitive_path_patterns: list[str] = Field(
        default_factory=lambda: ["auth/", "billing/", "payments/", "infra/", "deploy/", "k8s/"]
    )


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


class RiskFactor(BaseModel):
    name: str
    triggered: bool
    weight: int
    detail: str = ""


class RiskScore(BaseModel):
    score: int
    level: RiskLevel
    factors: list[RiskFactor] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    ticket_id: str
    mode: ApprovalMode
    required_approvals: int
    granted_approvals: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    risk_score: int
    reason: str
    status: Literal["pending", "approved"] = "pending"


class EvidenceBundle(BaseModel):
    bundle_id: str
    run_id: str
    ticket_id: str | None = None
    diff_summary: DiffSummary = Field(default_factory=DiffSummary)
    checks: list[CheckResult] = Field(default_factory=list)
    policy_findings: list[PolicyFinding] = Field(default_factory=list)
    rollback_notes: list[RollbackNote] = Field(default_factory=list)
    review_result: ReviewResult | None = None
    risk_score: RiskScore | None = None
    approval_request: ApprovalRequest | None = None
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
    ticket_workdirs: dict[str, str] = Field(default_factory=dict)
    completed_tickets: list[str] = Field(default_factory=list)
    review_cycles: int = 0
    approval_request: ApprovalRequest | None = None
    artifacts: ArtifactManifest
    events: list[RunEvent] = Field(default_factory=list)
    status: Literal["running", "done", "escalated", "awaiting_approval"] = "running"
