from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from maestro.agents.roles import (
    CeremonyMasterAgent,
    CoderAgent,
    ProductDesignerAgent,
    ReviewerAgent,
)
from maestro.config import load_config
from maestro.core.evidence import (
    build_evidence_bundle,
    collect_policy_findings,
    determine_approval_request,
)
from maestro.core.models import OrchestratorState
from maestro.core.policy import enforce_code_policy, enforce_review_policy
from maestro.core.product_brief import compile_product_brief
from maestro.core.run_graph_runtime import (
    advance_run_graph,
    determine_resume_node_id,
    initialize_run_graph,
)
from maestro.providers.base import LlmProvider
from maestro.providers.factory import build_provider
from maestro.providers.router import ProviderRouter
from maestro.repo.discovery import discover_repo
from maestro.schemas.contracts import (
    ApprovalRequest,
    CheckResult,
    CodeResult,
    MaestroConfig,
    PolicyPack,
    RepoInfo,
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
    providers: Mapping[str, LlmProvider]
    router: ProviderRouter
    prompt_root: Path


def build_engine_deps(project_root: Path, config_path: Path) -> EngineDeps:
    config = load_config(config_path)
    providers = {
        name: build_provider(provider_cfg["type"])
        for name, provider_cfg in config.providers.items()
    }
    router = ProviderRouter(config=config, providers=providers)
    policy = load_policy(config.policy, project_root / "policies")
    return EngineDeps(
        config=config,
        policy=policy,
        artifact_store=LocalArtifactStore(project_root / "runs"),
        state_store=LocalStateStore(project_root / "runs" / "state"),
        shell=LocalShellRunner(),
        providers=providers,
        router=router,
        prompt_root=project_root / "prompts",
    )


class OrchestratorEngine:
    def __init__(self, project_root: Path, deps: EngineDeps) -> None:
        self.project_root = project_root
        self.deps = deps

    def new_state(self, repo_path: Path, brief_path: Path | None) -> RunState:
        manifest = self.deps.artifact_store.create_run()
        run_graph, current_node_id = initialize_run_graph(self.deps.policy.max_review_cycles)
        state = RunState(
            run_id=manifest.run_id,
            current_state=OrchestratorState.DISCOVER_REPO.value,
            repo_path=repo_path,
            brief_path=brief_path,
            run_graph=run_graph,
            run_graph_current_node_id=current_node_id,
            artifacts=manifest,
        )
        self.deps.state_store.save(state)
        return state

    def _append_event(self, state: RunState, current: OrchestratorState, detail: str) -> None:
        state.current_state = current.value
        state.events.append(RunEvent(state=current.value, detail=detail))
        state.run_graph, state.run_graph_current_node_id = advance_run_graph(
            state.run_graph,
            orchestrator_state=current,
            current_node_id=state.run_graph_current_node_id,
        )
        self.deps.state_store.save(state)

    def _record_state_note(self, state: RunState, detail: str) -> None:
        state.events.append(RunEvent(state=state.current_state, detail=detail))
        self.deps.state_store.save(state)

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
        agent = ProductDesignerAgent(self.deps.router, self.deps.prompt_root, "product_designer")
        compiled_brief = compile_product_brief(brief_text)
        self.deps.artifact_store.write_json(
            state.artifacts,
            "product_brief_compiler",
            compiled_brief.model_dump(mode="json"),
        )
        spec = agent.run_spec({"brief": compiled_brief.model_dump(mode="json")})
        self.deps.artifact_store.write_json(
            state.artifacts,
            "product_designer",
            spec.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.DEFINE_PRODUCT, spec.title)
        return spec

    def plan_tickets(self, state: RunState, spec_payload: dict):
        agent = CeremonyMasterAgent(self.deps.router, self.deps.prompt_root, "ceremony_master")
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
        agent = CoderAgent(self.deps.router, self.deps.prompt_root, "coder")
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
        agent = ReviewerAgent(self.deps.router, self.deps.prompt_root, "reviewer")
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

    def write_evidence_bundle(
        self,
        state: RunState,
        ticket: Ticket,
        code_result: CodeResult,
        checks: list[CheckResult],
        review: ReviewResult,
        repo_info: RepoInfo,
    ) -> tuple[list[str], ApprovalRequest | None]:
        review_cycle = state.review_cycles + 1
        violations, policy_findings = collect_policy_findings(
            policy=self.deps.policy,
            review_cycles=state.review_cycles,
            code_result=code_result,
            checks=checks,
            review=review,
        )
        approval_request = determine_approval_request(
            policy=self.deps.policy,
            ticket=ticket,
            code_result=code_result,
            repo_info=repo_info,
            violations=violations,
        )
        bundle = build_evidence_bundle(
            run_id=state.run_id,
            ticket=ticket,
            review_cycle=review_cycle,
            code_result=code_result,
            checks=checks,
            review=review,
            repo_info=repo_info,
            violations=violations,
            policy_findings=policy_findings,
            policy=self.deps.policy,
            approval_request=approval_request,
        )
        self.deps.artifact_store.write_evidence_bundle(state.artifacts, bundle)
        state.approval_request = approval_request
        self.deps.state_store.save(state)
        return violations, approval_request

    def advance_ticket(
        self,
        state: RunState,
        ticket: Ticket,
        code_result: CodeResult,
        checks: list[CheckResult],
        review: ReviewResult,
        violations: list[str] | None = None,
        approval_request: ApprovalRequest | None = None,
    ) -> OrchestratorState:
        if violations is None:
            violations = enforce_code_policy(self.deps.policy, code_result)
            violations.extend(enforce_review_policy(self.deps.policy, state.review_cycles, review))
            failing_checks = [check.command for check in checks if not check.success]
            if not review.approved:
                violations.append("review_rejected")
            if failing_checks:
                violations.append("checks_failed")
        if not violations and approval_request is not None:
            state.status = "awaiting_approval"
            self._record_state_note(
                state,
                f"approval_required:{state.current_ticket_id}:{approval_request.required_approvals}",
            )
            return OrchestratorState.REVIEW
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
            violations, approval_request = self.write_evidence_bundle(
                state,
                ticket,
                code_result,
                checks,
                review,
                repo.repo_info,
            )
            result = self.advance_ticket(
                state,
                ticket,
                code_result,
                checks,
                review,
                violations=violations,
                approval_request=approval_request,
            )
            if result is OrchestratorState.ESCALATE:
                break
            if state.status == "awaiting_approval":
                break
            if result is OrchestratorState.COMPLETE_TICKET:
                self._append_event(state, OrchestratorState.NEXT_TICKET, ticket.id)
                ticket = self.pick_ticket(state)
                if ticket is None:
                    break
        state.current_state = (
            OrchestratorState.DONE.value if state.status == "done" else state.current_state
        )
        state.run_graph_current_node_id = determine_resume_node_id(
            state.run_graph,
            state.run_graph_current_node_id,
        )
        self.deps.state_store.save(state)
        return state
