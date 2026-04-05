from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maestro.core.engine import EngineDeps, OrchestratorEngine
from maestro.core.models import OrchestratorState
from maestro.providers.fake import FakeProvider
from maestro.schemas.contracts import MaestroConfig, PolicyPack, RoleConfig
from maestro.storage.local import LocalArtifactStore, LocalStateStore
from maestro.tools.shell import LocalShellRunner


class PassingShellRunner(LocalShellRunner):
    def run(self, command: str, cwd: Path):  # type: ignore[override]
        from maestro.tools.shell import ShellResult

        return ShellResult(command=command, returncode=0, stdout="ok", stderr="")


@dataclass
class EvalScenario:
    name: str
    provider: FakeProvider
    expected_final_state: OrchestratorState
    expected_status: str


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
    deps = EngineDeps(
        config=config,
        policy=PolicyPack(name="default"),
        artifact_store=LocalArtifactStore(project_root / "runs"),
        state_store=LocalStateStore(project_root / "runs" / "state"),
        shell=PassingShellRunner(),
        providers={"fake": scenario.provider},
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
    ]
