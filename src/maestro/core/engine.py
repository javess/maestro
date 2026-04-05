from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maestro.agents.roles import (
    CeremonyMasterAgent,
    CoderAgent,
    ProductDesignerAgent,
    ReviewerAgent,
)
from maestro.config import load_config
from maestro.core.models import OrchestratorState
from maestro.core.policy import enforce_code_policy, enforce_review_policy
from maestro.providers.base import LlmProvider
from maestro.providers.factory import build_provider
from maestro.repo.discovery import discover_repo
from maestro.schemas.contracts import (
    CheckResult,
    CodeResult,
    MaestroConfig,
    PolicyPack,
    ReviewResult,
    RunEvent,
    RunState,
    Ticket,
    TicketStatus,
)
from maestro.storage.local import LocalArtifactStore, LocalStateStore
from maestro.storage.policies import load_policy
from maestro.tools.shell import LocalShellRunner


@dataclass
class EngineDeps:
    config: MaestroConfig
    policy: PolicyPack
    artifact_store: LocalArtifactStore
    state_store: LocalStateStore
    shell: LocalShellRunner
    providers: dict[str, LlmProvider]
    prompt_root: Path


def build_engine_deps(project_root: Path, config_path: Path) -> EngineDeps:
    config = load_config(config_path)
    providers = {
        name: build_provider(provider_cfg["type"])
        for name, provider_cfg in config.providers.items()
    }
    policy = load_policy(config.policy, project_root / "policies")
    return EngineDeps(
        config=config,
        policy=policy,
        artifact_store=LocalArtifactStore(project_root / "runs"),
        state_store=LocalStateStore(project_root / "runs" / "state"),
        shell=LocalShellRunner(),
        providers=providers,
        prompt_root=project_root / "prompts",
    )


class OrchestratorEngine:
    def __init__(self, project_root: Path, deps: EngineDeps) -> None:
        self.project_root = project_root
        self.deps = deps

    def new_state(self, repo_path: Path, brief_path: Path | None) -> RunState:
        manifest = self.deps.artifact_store.create_run()
        state = RunState(
            run_id=manifest.run_id,
            current_state=OrchestratorState.DISCOVER_REPO.value,
            repo_path=repo_path,
            brief_path=brief_path,
            artifacts=manifest,
        )
        self.deps.state_store.save(state)
        return state

    def _append_event(self, state: RunState, current: OrchestratorState, detail: str) -> None:
        state.current_state = current.value
        state.events.append(RunEvent(state=current.value, detail=detail))
        self.deps.state_store.save(state)

    def _role_provider(self, role: str) -> tuple[LlmProvider, str]:
        role_cfg = self.deps.config.llm[role]
        return self.deps.providers[role_cfg.provider], role_cfg.model

    def discover(self, state: RunState):
        repo = discover_repo(state.repo_path)
        self.deps.artifact_store.write_json(
            state.artifacts,
            "repo_discovery",
            repo.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.DISCOVER_REPO, repo.adapter_name)
        return repo

    def define_product(self, state: RunState, brief_text: str):
        provider, model = self._role_provider("product_designer")
        agent = ProductDesignerAgent(provider, model, self.deps.prompt_root, "product_designer")
        spec = agent.run_spec({"brief": brief_text})
        self.deps.artifact_store.write_json(
            state.artifacts,
            "product_designer",
            spec.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.DEFINE_PRODUCT, spec.title)
        return spec

    def plan_tickets(self, state: RunState, spec_payload: dict):
        provider, model = self._role_provider("ceremony_master")
        agent = CeremonyMasterAgent(provider, model, self.deps.prompt_root, "ceremony_master")
        backlog = agent.run_backlog({"product_spec": spec_payload})
        state.backlog = backlog
        self.deps.artifact_store.write_json(
            state.artifacts,
            "ceremony_master",
            backlog.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.PLAN_TICKETS, str(len(backlog.tickets)))
        return backlog

    def pick_ticket(self, state: RunState) -> Ticket | None:
        for ticket in state.backlog.tickets:
            if ticket.status is TicketStatus.pending:
                ticket.status = TicketStatus.in_progress
                state.current_ticket_id = ticket.id
                self._append_event(state, OrchestratorState.PICK_TICKET, ticket.id)
                return ticket
        self._append_event(state, OrchestratorState.DONE, "no pending tickets")
        state.status = "done"
        return None

    def implement(self, state: RunState, ticket: Ticket, repo_context: dict) -> CodeResult:
        provider, model = self._role_provider("coder")
        agent = CoderAgent(provider, model, self.deps.prompt_root, "coder")
        result = agent.run_code(
            {
                "ticket_id": ticket.id,
                "ticket": ticket.model_dump(),
                "repo_context": repo_context,
            }
        )
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_coder_attempt_{state.review_cycles + 1}",
            result.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.IMPLEMENT, ticket.id)
        return result

    def validate(self, state: RunState, repo_commands: list[str]) -> list[CheckResult]:
        checks: list[CheckResult] = []
        for command in repo_commands:
            result = self.deps.shell.run(command, state.repo_path)
            checks.append(
                CheckResult(
                    command=command,
                    success=result.ok,
                    output=(result.stdout + result.stderr).strip(),
                )
            )
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{state.current_ticket_id}_checks_{state.review_cycles + 1}",
            [check.model_dump(mode="json") for check in checks],
        )
        self._append_event(state, OrchestratorState.VALIDATE, state.current_ticket_id or "unknown")
        return checks

    def review(
        self,
        state: RunState,
        ticket: Ticket,
        code_result: CodeResult,
        checks: list[CheckResult],
    ) -> ReviewResult:
        provider, model = self._role_provider("reviewer")
        agent = ReviewerAgent(provider, model, self.deps.prompt_root, "reviewer")
        review = agent.run_review(
            {
                "ticket_id": ticket.id,
                "ticket": ticket.model_dump(),
                "code_result": code_result.model_dump(),
                "checks": [check.model_dump() for check in checks],
                "policy": self.deps.policy.model_dump(),
            }
        )
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_reviewer_{state.review_cycles + 1}",
            review.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.REVIEW, ticket.id)
        return review

    def advance_ticket(
        self,
        state: RunState,
        ticket: Ticket,
        code_result: CodeResult,
        checks: list[CheckResult],
        review: ReviewResult,
    ) -> OrchestratorState:
        violations = enforce_code_policy(self.deps.policy, code_result)
        violations.extend(enforce_review_policy(self.deps.policy, state.review_cycles, review))
        failing_checks = [check.command for check in checks if not check.success]
        if not review.approved:
            violations.append("review_rejected")
        if failing_checks:
            violations.append("checks_failed")
        if violations:
            if state.review_cycles >= self.deps.policy.max_review_cycles:
                ticket.status = TicketStatus.escalated
                state.status = "escalated"
                self._append_event(state, OrchestratorState.ESCALATE, ",".join(violations))
                return OrchestratorState.ESCALATE
            state.review_cycles += 1
            self._append_event(state, OrchestratorState.REVISE, ",".join(violations))
            return OrchestratorState.REVISE
        ticket.status = TicketStatus.complete
        state.completed_tickets.append(ticket.id)
        state.review_cycles = 0
        self._append_event(state, OrchestratorState.COMPLETE_TICKET, ticket.id)
        return OrchestratorState.COMPLETE_TICKET

    def run_plan(self, repo_path: Path, brief_path: Path) -> RunState:
        state = self.new_state(repo_path=repo_path, brief_path=brief_path)
        repo = self.discover(state)
        spec = self.define_product(state, brief_path.read_text())
        self.plan_tickets(state, spec.model_dump(mode="json"))
        ticket = self.pick_ticket(state)
        if ticket is None:
            state.status = "done"
            return state
        while ticket.status is TicketStatus.in_progress:
            code_result = self.implement(state, ticket, repo.model_dump(mode="json"))
            commands = repo.repo_info.lint_commands + repo.repo_info.test_commands
            checks = self.validate(state, commands)
            review = self.review(state, ticket, code_result, checks)
            result = self.advance_ticket(state, ticket, code_result, checks, review)
            if result is OrchestratorState.ESCALATE:
                break
            if result is OrchestratorState.COMPLETE_TICKET:
                self._append_event(state, OrchestratorState.NEXT_TICKET, ticket.id)
                ticket = self.pick_ticket(state)
                if ticket is None:
                    break
        state.current_state = (
            OrchestratorState.DONE.value if state.status == "done" else state.current_state
        )
        self.deps.state_store.save(state)
        return state
