from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from pydantic import BaseModel

from maestro.providers.base import LlmProvider, SchemaT
from maestro.schemas.architecture import ArchitectureArtifacts
from maestro.schemas.backlog_graph import BacklogGraph
from maestro.schemas.contracts import (
    AssumptionKind,
    AssumptionRecord,
    Backlog,
    CodeResult,
    ProductSpec,
    ProviderCapability,
    ProviderError,
    ProviderModelInfo,
    ReviewIssue,
    ReviewResult,
    Severity,
    Ticket,
)


class FakeProvider(LlmProvider):
    def __init__(
        self,
        scenario: dict[str, Any] | None = None,
        resolver: Callable[[str, type[BaseModel]], BaseModel] | None = None,
    ) -> None:
        self.scenario = scenario or {}
        self.resolver = resolver
        self._capabilities = ProviderCapability(
            structured_outputs=True,
            tool_calling=False,
            streaming=False,
            vision=False,
            long_context=True,
            code_specialized=True,
            json_mode=True,
        )

    @property
    def capabilities(self) -> ProviderCapability:
        return self._capabilities

    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        return f"fake:{model}:{metadata or {}}:{prompt[:32]}"

    def generate_structured(
        self,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> SchemaT:
        if self.resolver is not None:
            return cast(SchemaT, self.resolver(prompt, schema))
        payload = self.scenario.get(schema.__name__)
        if payload is not None:
            if isinstance(payload, BaseModel):
                return cast(SchemaT, payload)
            return schema.model_validate(payload)
        if schema is ProductSpec:
            return cast(
                SchemaT,
                ProductSpec(
                    title="Maestro",
                    summary="Deterministic orchestration baseline",
                    problem="Software delivery work needs deterministic orchestration.",
                    target_users=["Platform engineers", "Software teams"],
                    outcomes=["Create baseline framework", "Validate via tests"],
                    scope=["CLI", "providers", "repo adapters", "evals"],
                    non_goals=["Full autonomous code editing"],
                    constraints=["Deterministic execution", "Schema-validated outputs"],
                    risks=["Provider variability"],
                    assumptions=["Repositories expose standard test commands"],
                    assumption_log=[
                        AssumptionRecord(
                            kind=AssumptionKind.stated_fact,
                            statement="Repositories expose standard test commands",
                            source="product_spec",
                        )
                    ],
                    unresolved_questions=["Which repo-local constraints are still unknown?"],
                    acceptance_criteria=["Structured output validation", "Deterministic evals"],
                ),
            )
        if schema is Backlog:
            product_spec = ((metadata or {}).get("product_spec")) or {}
            return cast(
                SchemaT,
                Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Bootstrap framework",
                            description="Create deterministic baseline",
                            acceptance_criteria=["Tests pass", "CLI runs"],
                        )
                    ],
                    assumption_log=[
                        AssumptionRecord.model_validate(item)
                        for item in product_spec.get("assumption_log", [])
                    ],
                    unresolved_questions=list(product_spec.get("unresolved_questions", [])),
                    architecture_artifacts=(
                        ArchitectureArtifacts.model_validate(item)
                        if (
                            item := (metadata or {}).get("architecture_artifacts")
                        )
                        else None
                    ),
                    execution_graph=(
                        BacklogGraph.model_validate(item)
                        if (item := (metadata or {}).get("execution_graph"))
                        else None
                    ),
                ),
            )
        if schema is CodeResult:
            ticket_id = (metadata or {}).get("ticket_id", "TICKET-1")
            return cast(
                SchemaT,
                CodeResult(
                    ticket_id=ticket_id,
                    summary="Fake implementation completed",
                    changed_files=[],
                    commands=["pytest"],
                    tests_added=["tests/test_fake_flow.py"],
                    notes=[],
                    success=True,
                ),
            )
        if schema is ReviewResult:
            ticket_id = (metadata or {}).get("ticket_id", "TICKET-1")
            if self.scenario.get("force_review_issue"):
                return cast(
                    SchemaT,
                    ReviewResult(
                        ticket_id=ticket_id,
                        approved=False,
                        summary="Found issues",
                        issues=[
                            ReviewIssue(
                                severity=Severity.medium,
                                path="src/maestro/core/engine.py",
                                message="Missing validation coverage",
                                recommendation="Add coverage before approval",
                            )
                        ],
                    ),
                )
            return cast(
                SchemaT,
                ReviewResult(
                    ticket_id=ticket_id,
                    approved=True,
                    summary="Approved",
                    issues=[],
                ),
            )
        raise ValueError(f"No fake payload configured for {schema.__name__}")

    def supports_structured_output(self) -> bool:
        return True

    def supports_tool_calling(self) -> bool:
        return False

    def model_info(self, model: str) -> ProviderModelInfo:
        return ProviderModelInfo(provider="fake", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        return ProviderError(provider="fake", retryable=False, message=str(error))
