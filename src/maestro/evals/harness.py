from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from maestro.core.engine import EngineDeps, OrchestratorEngine
from maestro.core.models import OrchestratorState
from maestro.providers.fake import FakeProvider
from maestro.providers.router import ProviderRouter
from maestro.schemas.contracts import (
    ApprovalMode,
    Backlog,
    FallbackConfig,
    MaestroConfig,
    PolicyPack,
    RiskLevel,
    RoleConfig,
    Ticket,
)
from maestro.schemas.eval import EvalReport, EvalScenarioResult, EvalSummary
from maestro.storage.local import LocalArtifactStore, LocalStateStore
from maestro.storage.sqlite import SqliteRunIndex
from maestro.tools.shell import LocalShellRunner


class PassingShellRunner(LocalShellRunner):
    def __init__(self, failures: set[str] | None = None) -> None:
        self.failures = failures or set()

    def run(self, command: str, cwd: Path):  # type: ignore[override]
        from maestro.tools.shell import ShellResult

        if command in self.failures:
            return ShellResult(command=command, returncode=1, stdout="", stderr="forced failure")
        return ShellResult(command=command, returncode=0, stdout="ok", stderr="")


def _reviewer_failure_provider() -> FakeProvider:
    delegate = FakeProvider()

    def resolver(prompt: str, schema: type[BaseModel]) -> BaseModel:
        if schema.__name__ == "ReviewResult":
            raise ValueError("primary failed")
        return delegate.generate_structured(prompt=prompt, model="delegate", schema=schema)

    return FakeProvider(resolver=resolver)


@dataclass
class EvalScenario:
    name: str
    provider: FakeProvider
    expected_final_state: OrchestratorState
    expected_status: str
    fallback_provider: FakeProvider | None = None
    shell_failures: set[str] | None = None
    policy: PolicyPack | None = None


def build_eval_engine(project_root: Path, scenario: EvalScenario) -> OrchestratorEngine:
    config = MaestroConfig(
        providers={"fake": {"type": "fake"}},
        llm={
            "product_designer": RoleConfig(provider="fake", model="fake-product"),
            "ceremony_master": RoleConfig(provider="fake", model="fake-ceremony"),
            "coder": RoleConfig(provider="fake", model="fake-coder"),
            "reviewer": RoleConfig(provider="fake", model="fake-reviewer"),
        },
        fallbacks={},
        policy="default",
    )
    providers = {"fake": scenario.provider}
    if scenario.fallback_provider is not None:
        config.providers["fallback"] = {"type": "fake"}
        config.fallbacks["reviewer"] = [
            FallbackConfig(provider="fallback", model="fake-fallback-reviewer")
        ]
        providers["fallback"] = scenario.fallback_provider
    deps = EngineDeps(
        config=config,
        policy=scenario.policy or PolicyPack(name="default"),
        artifact_store=LocalArtifactStore(
            project_root / "runs",
            index=SqliteRunIndex(project_root / "runs" / "maestro.db"),
        ),
        state_store=LocalStateStore(
            project_root / "runs" / "state",
            index=SqliteRunIndex(project_root / "runs" / "maestro.db"),
        ),
        shell=PassingShellRunner(scenario.shell_failures),
        providers=providers,
        router=ProviderRouter(config=config, providers=providers),
        prompt_root=project_root / "prompts",
    )
    return OrchestratorEngine(project_root, deps)


def default_scenarios() -> list[EvalScenario]:
    return [
        EvalScenario(
            name="planning-flow",
            provider=FakeProvider(),
            expected_final_state=OrchestratorState.DONE,
            expected_status="done",
        ),
        EvalScenario(
            name="review-loop-escalation",
            provider=FakeProvider({"force_review_issue": True}),
            expected_final_state=OrchestratorState.ESCALATE,
            expected_status="escalated",
        ),
        EvalScenario(
            name="test-failure-blocks-approval",
            provider=FakeProvider(),
            expected_final_state=OrchestratorState.ESCALATE,
            expected_status="escalated",
            shell_failures={"uv run pytest"},
        ),
        EvalScenario(
            name="fallback-provider-behavior",
            provider=_reviewer_failure_provider(),
            fallback_provider=FakeProvider(),
            expected_final_state=OrchestratorState.DONE,
            expected_status="done",
        ),
        EvalScenario(
            name="approval-required-flow",
            provider=FakeProvider(),
            expected_final_state=OrchestratorState.REVIEW,
            expected_status="awaiting_approval",
            policy=PolicyPack(
                name="strict",
                approval_mode=ApprovalMode.review_go,
                approval_risk_level=RiskLevel.low,
            ),
        ),
        EvalScenario(
            name="backlog-graph-ordering",
            provider=FakeProvider(
                {
                    "Backlog": Backlog(
                        tickets=[
                            Ticket(
                                id="TICKET-1",
                                title="Foundations",
                                description="Set up shared contracts",
                                acceptance_criteria=["shared contracts exist"],
                                priority=3,
                            ),
                            Ticket(
                                id="TICKET-2",
                                title="Dependent flow",
                                description="Build on the shared contracts",
                                acceptance_criteria=["flow exists"],
                                dependencies=["TICKET-1"],
                                priority=2,
                            ),
                        ]
                    )
                }
            ),
            expected_final_state=OrchestratorState.DONE,
            expected_status="done",
        ),
        EvalScenario(
            name="migration-sensitive-flow",
            provider=FakeProvider(
                {
                    "CodeResult": {
                        "ticket_id": "TICKET-1",
                        "summary": "Add migration",
                        "changed_files": [
                            {
                                "path": "migrations/001_add_table.sql",
                                "summary": "migration",
                            }
                        ],
                        "commands": ["uv run pytest"],
                        "tests_added": ["tests/test_migration_flow.py"],
                    }
                }
            ),
            expected_final_state=OrchestratorState.DONE,
            expected_status="done",
        ),
        EvalScenario(
            name="observation-driven-followup",
            provider=FakeProvider({"force_review_issue": True}),
            expected_final_state=OrchestratorState.ESCALATE,
            expected_status="escalated",
        ),
    ]


def run_eval_report(project_root: Path, scenarios: list[EvalScenario] | None = None) -> EvalReport:
    scenario_list = scenarios or default_scenarios()
    results: list[EvalScenarioResult] = []
    for scenario in scenario_list:
        engine = build_eval_engine(project_root, scenario)
        state = engine.run_plan(project_root, project_root / "examples" / "brief.md")
        assertions: list[str] = []
        passed = True
        if state.current_state != scenario.expected_final_state.value:
            passed = False
            assertions.append(
                f"expected_state={scenario.expected_final_state.value} actual={state.current_state}"
            )
        if state.status != scenario.expected_status:
            passed = False
            assertions.append(f"expected_status={scenario.expected_status} actual={state.status}")
        retry_count = sum(
            1 for event in state.events if event.state == OrchestratorState.REVISE.value
        )
        schema_errors = sum(
            1
            for event in state.events
            if "schema" in event.detail.lower() and "error" in event.detail.lower()
        )
        policy_violations = sum(
            1 for event in state.events if event.state == OrchestratorState.ESCALATE.value
        )
        results.append(
            EvalScenarioResult(
                scenario=scenario.name,
                status=state.status,
                current_state=state.current_state,
                expected_state=scenario.expected_final_state.value,
                expected_status=scenario.expected_status,
                evidence_bundles=len(state.artifacts.evidence_bundles),
                retries=retry_count,
                schema_errors=schema_errors,
                policy_violations=policy_violations,
                passed=passed,
                assertions=assertions,
            )
        )
    return EvalReport(
        summary=EvalSummary(
            scenario_count=len(results),
            passed=sum(1 for result in results if result.passed),
            failed=sum(1 for result in results if not result.passed),
            total_retries=sum(result.retries for result in results),
            total_schema_errors=sum(result.schema_errors for result in results),
            total_policy_violations=sum(result.policy_violations for result in results),
        ),
        scenarios=results,
    )
