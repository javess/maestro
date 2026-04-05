from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any, cast

from pydantic import BaseModel

from maestro.logging import log_provider_request, log_provider_response
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

logger = logging.getLogger(__name__)


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
        log_provider_request(
            logger,
            provider="fake",
            action="generate_text",
            model=model,
            prompt=prompt,
            metadata=metadata,
        )
        text = f"fake:{model}:{metadata or {}}:{prompt[:32]}"
        log_provider_response(
            logger,
            provider="fake",
            action="generate_text",
            model=model,
            payload=text,
        )
        return text

    def generate_structured(
        self,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> SchemaT:
        log_provider_request(
            logger,
            provider="fake",
            action="generate_structured",
            model=model,
            prompt=prompt,
            metadata=metadata,
            schema_name=schema.__name__,
        )
        if self.resolver is not None:
            result = cast(SchemaT, self.resolver(prompt, schema))
            log_provider_response(
                logger,
                provider="fake",
                action="generate_structured",
                model=model,
                payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                schema_name=schema.__name__,
            )
            return result
        payload = self.scenario.get(schema.__name__)
        if payload is not None:
            if isinstance(payload, BaseModel):
                result = cast(SchemaT, payload)
            else:
                result = schema.model_validate(payload)
            log_provider_response(
                logger,
                provider="fake",
                action="generate_structured",
                model=model,
                payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                schema_name=schema.__name__,
            )
            return result
        if schema is ProductSpec:
            result = cast(
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
            log_provider_response(
                logger,
                provider="fake",
                action="generate_structured",
                model=model,
                payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                schema_name=schema.__name__,
            )
            return result
        if schema is Backlog:
            product_spec = ((metadata or {}).get("product_spec")) or {}
            result = cast(
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
            log_provider_response(
                logger,
                provider="fake",
                action="generate_structured",
                model=model,
                payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                schema_name=schema.__name__,
            )
            return result
        if schema is CodeResult:
            ticket_id = (metadata or {}).get("ticket_id", "TICKET-1")
            result = cast(
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
            log_provider_response(
                logger,
                provider="fake",
                action="generate_structured",
                model=model,
                payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                schema_name=schema.__name__,
            )
            return result
        if schema is ReviewResult:
            ticket_id = (metadata or {}).get("ticket_id", "TICKET-1")
            if self.scenario.get("force_review_issue"):
                result = cast(
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
                log_provider_response(
                    logger,
                    provider="fake",
                    action="generate_structured",
                    model=model,
                    payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                    schema_name=schema.__name__,
                )
                return result
            result = cast(
                SchemaT,
                ReviewResult(
                    ticket_id=ticket_id,
                    approved=True,
                    summary="Approved",
                    issues=[],
                ),
            )
            log_provider_response(
                logger,
                provider="fake",
                action="generate_structured",
                model=model,
                payload=json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
                schema_name=schema.__name__,
            )
            return result
        raise ValueError(f"No fake payload configured for {schema.__name__}")

    def supports_structured_output(self) -> bool:
        return True

    def supports_tool_calling(self) -> bool:
        return False

    def model_info(self, model: str) -> ProviderModelInfo:
        return ProviderModelInfo(provider="fake", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        return ProviderError(provider="fake", retryable=False, message=str(error))
