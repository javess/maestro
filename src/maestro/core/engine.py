"""Deterministic orchestrator engine for planning, execution, validation, and review."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from maestro.agents.roles import (
    CeremonyMasterAgent,
    CoderAgent,
    ProductDesignerAgent,
    ReviewerAgent,
)
from maestro.archetypes import load_archetype_pack
from maestro.config import load_config
from maestro.core.architecture_synthesizer import synthesize_architecture
from maestro.core.backlog_graph import build_backlog_graph, select_ready_tickets
from maestro.core.evidence import (
    build_evidence_bundle,
    collect_policy_findings,
    determine_approval_request,
)
from maestro.core.models import OrchestratorState
from maestro.core.observation import compile_observations
from maestro.core.policy import enforce_code_policy, enforce_review_policy
from maestro.core.product_brief import compile_product_brief
from maestro.core.run_graph_runtime import (
    advance_run_graph,
    determine_resume_node_id,
    initialize_run_graph,
)
from maestro.core.workspace import apply_code_result, sync_code_result
from maestro.providers.base import LlmProvider
from maestro.providers.factory import build_provider
from maestro.providers.router import ProviderRouter
from maestro.repo.context import build_repo_snapshot
from maestro.repo.discovery import discover_repo
from maestro.repo.impact import analyze_backlog_impact
from maestro.schemas.contracts import (
    ApprovalRequest,
    CheckResult,
    CodeResult,
    MaestroConfig,
    PolicyPack,
    ProductSpec,
    RepoInfo,
    ReviewResult,
    RunEvent,
    RunState,
    Ticket,
    TicketStatus,
)
from maestro.schemas.observation import Observation
from maestro.storage.local import LocalArtifactStore, LocalStateStore
from maestro.storage.policies import load_policy
from maestro.storage.sqlite import SqliteRunIndex
from maestro.tools.git import GitWorktreeManager
from maestro.tools.shell import LocalShellRunner

logger = logging.getLogger(__name__)


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


@dataclass
class TicketAttempt:
    code_result: CodeResult
    checks: list[CheckResult]
    review: ReviewResult


def build_engine_deps(
    project_root: Path,
    config_path: Path,
    *,
    workspace_root: Path | None = None,
) -> EngineDeps:
    config = load_config(config_path)
    providers = {
        name: build_provider(provider_cfg)
        for name, provider_cfg in config.providers.items()
    }
    router = ProviderRouter(config=config, providers=providers)
    policy = load_policy(config.policy, project_root / "policies")
    logger.info(
        "engine_deps_built config=%s policy=%s providers=%s",
        config_path,
        policy.name,
        ",".join(sorted(providers.keys())),
    )
    artifact_root = workspace_root / "runs" if workspace_root is not None else project_root / "runs"
    state_root = workspace_root / "state" if workspace_root is not None else artifact_root / "state"
    index_path = (
        workspace_root / "maestro.db"
        if workspace_root is not None
        else artifact_root / "maestro.db"
    )
    index = SqliteRunIndex(index_path)
    return EngineDeps(
        config=config,
        policy=policy,
        artifact_store=LocalArtifactStore(artifact_root, index=index),
        state_store=LocalStateStore(state_root, index=index),
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
        logger.info(
            "run_initialized run_id=%s repo=%s brief=%s",
            state.run_id,
            repo_path,
            brief_path,
        )
        return state

    def _ticket_execution_root(self, state: RunState, ticket_id: str) -> Path:
        workdir = state.ticket_workdirs.get(ticket_id)
        if workdir is not None:
            return Path(workdir)
        if not (state.repo_path / ".git").exists():
            return state.repo_path
        workspace = state.repo_path / ".maestro" / "worktrees" / state.run_id / ticket_id
        manager = GitWorktreeManager(state.repo_path)
        root, kind = manager.create_workspace(workspace)
        state.ticket_workdirs[ticket_id] = str(root)
        state.events.append(
            RunEvent(
                state=OrchestratorState.IMPLEMENT.value,
                detail=f"workspace:{ticket_id}:{kind}",
            )
        )
        self.deps.state_store.save(state)
        return root

    def _sync_ticket_result(self, state: RunState, ticket: Ticket, code_result: CodeResult) -> None:
        workdir = state.ticket_workdirs.get(ticket.id)
        if workdir is None:
            return
        sync_code_result(Path(workdir), state.repo_path, code_result)
        self.deps.state_store.save(state)

    def _parallel_ticket_limit(self) -> int:
        return max(1, self.deps.policy.max_parallel_tickets)

    def _append_event(self, state: RunState, current: OrchestratorState, detail: str) -> None:
        state.current_state = current.value
        state.events.append(RunEvent(state=current.value, detail=detail))
        logger.info(
            "state_transition run_id=%s state=%s detail=%s",
            state.run_id,
            current.value,
            detail,
        )
        state.run_graph, state.run_graph_current_node_id = advance_run_graph(
            state.run_graph,
            orchestrator_state=current,
            current_node_id=state.run_graph_current_node_id,
        )
        self.deps.state_store.save(state)

    def _record_state_note(self, state: RunState, detail: str) -> None:
        state.events.append(RunEvent(state=state.current_state, detail=detail))
        logger.info(
            "state_note run_id=%s state=%s detail=%s",
            state.run_id,
            state.current_state,
            detail,
        )
        self.deps.state_store.save(state)

    def discover(self, state: RunState):
        logger.debug("repo_discovery_start run_id=%s repo=%s", state.run_id, state.repo_path)
        repo = discover_repo(state.repo_path)
        self.deps.artifact_store.write_json(
            state.artifacts,
            "repo_discovery",
            repo.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.DISCOVER_REPO, repo.adapter_name)
        return repo

    def define_product(self, state: RunState, brief_text: str):
        logger.debug("define_product_start run_id=%s", state.run_id)
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
        logger.debug("plan_tickets_start run_id=%s", state.run_id)
        agent = CeremonyMasterAgent(self.deps.router, self.deps.prompt_root, "ceremony_master")
        repo = discover_repo(state.repo_path)
        spec = ProductSpec.model_validate(spec_payload)
        architecture = synthesize_architecture(spec, repo)
        archetype_pack = (
            load_archetype_pack(self.deps.config.archetype, self.project_root / "archetypes")
            if self.deps.config.archetype is not None
            else None
        )
        backlog = agent.run_backlog(
            {
                "product_spec": spec_payload,
                "architecture_artifacts": architecture.model_dump(mode="json"),
                "repo_context": repo.model_dump(mode="json"),
                "archetype_pack": (
                    archetype_pack.model_dump(mode="json") if archetype_pack is not None else None
                ),
            }
        )
        backlog.architecture_artifacts = backlog.architecture_artifacts or architecture
        backlog.execution_graph = backlog.execution_graph or build_backlog_graph(backlog)
        backlog.impact_analyses = analyze_backlog_impact(backlog, repo)
        self.deps.artifact_store.write_json(
            state.artifacts,
            "architecture_synthesizer",
            architecture.model_dump(mode="json"),
        )
        self.deps.artifact_store.write_json(
            state.artifacts,
            "impact_analysis",
            {
                ticket_id: analysis.model_dump(mode="json")
                for ticket_id, analysis in backlog.impact_analyses.items()
            },
        )
        if archetype_pack is not None:
            self.deps.artifact_store.write_json(
                state.artifacts,
                "archetype_pack",
                archetype_pack.model_dump(mode="json"),
            )
        state.backlog = backlog
        logger.info(
            "plan_tickets_complete run_id=%s tickets=%s",
            state.run_id,
            len(backlog.tickets),
        )
        self.deps.artifact_store.write_json(
            state.artifacts,
            "ceremony_master",
            backlog.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.PLAN_TICKETS, str(len(backlog.tickets)))
        return backlog

    def pick_tickets(self, state: RunState) -> list[Ticket]:
        logger.debug(
            "pick_tickets_start run_id=%s completed=%s",
            state.run_id,
            len(state.completed_tickets),
        )
        tickets = select_ready_tickets(
            state.backlog,
            state.completed_tickets,
            limit=self._parallel_ticket_limit(),
        )
        if tickets:
            for ticket in tickets:
                ticket.status = TicketStatus.in_progress
                self._append_event(state, OrchestratorState.PICK_TICKET, ticket.id)
            state.current_ticket_id = tickets[0].id
            return tickets
        self._append_event(state, OrchestratorState.DONE, "no pending tickets")
        state.status = "done"
        logger.info("run_complete_no_pending_tickets run_id=%s", state.run_id)
        return []

    def _generate_code_result(
        self,
        state: RunState,
        ticket: Ticket,
        repo_context: dict,
        execution_root: Path,
    ) -> CodeResult:
        impact_analysis = state.backlog.impact_analyses.get(ticket.id)
        repo_snapshot = build_repo_snapshot(execution_root, impact_analysis)
        agent = CoderAgent(self.deps.router, self.deps.prompt_root, "coder")
        result = agent.run_code(
            {
                "ticket_id": ticket.id,
                "ticket": ticket.model_dump(),
                "repo_context": {
                    **repo_context,
                    "impact_analysis": impact_analysis.model_dump(mode="json")
                    if impact_analysis is not None
                    else None,
                    "repo_snapshot": repo_snapshot.model_dump(mode="json"),
                },
            }
        )
        return apply_code_result(execution_root, result)

    def _run_checks(
        self,
        execution_root: Path,
        repo_commands: list[str],
        code_result: CodeResult,
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []
        for command in _unique_commands([*repo_commands, *code_result.commands]):
            result = self.deps.shell.run(command, execution_root)
            checks.append(
                CheckResult(
                    command=command,
                    success=result.ok,
                    output=(result.stdout + result.stderr).strip(),
                )
            )
        return checks

    def _generate_review(
        self,
        ticket: Ticket,
        code_result: CodeResult,
        checks: list[CheckResult],
    ) -> ReviewResult:
        agent = ReviewerAgent(self.deps.router, self.deps.prompt_root, "reviewer")
        return agent.run_review(
            {
                "ticket_id": ticket.id,
                "ticket": ticket.model_dump(),
                "code_result": code_result.model_dump(),
                "checks": [check.model_dump() for check in checks],
                "policy": self.deps.policy.model_dump(),
            }
        )

    def implement(self, state: RunState, ticket: Ticket, repo_context: dict) -> CodeResult:
        logger.debug("implement_start run_id=%s ticket=%s", state.run_id, ticket.id)
        execution_root = self._ticket_execution_root(state, ticket.id)
        result = self._generate_code_result(state, ticket, repo_context, execution_root)
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_coder_attempt_{state.review_cycles + 1}",
            result.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.IMPLEMENT, ticket.id)
        return result

    def validate(
        self,
        state: RunState,
        repo_commands: list[str],
        code_result: CodeResult,
    ) -> list[CheckResult]:
        logger.debug(
            "validate_start run_id=%s ticket=%s commands=%s",
            state.run_id,
            state.current_ticket_id,
            len(repo_commands),
        )
        execution_root = (
            self._ticket_execution_root(state, state.current_ticket_id)
            if state.current_ticket_id is not None
            else state.repo_path
        )
        checks = self._run_checks(execution_root, repo_commands, code_result)
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
        logger.debug("review_start run_id=%s ticket=%s", state.run_id, ticket.id)
        review = self._generate_review(ticket, code_result, checks)
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_reviewer_{state.review_cycles + 1}",
            review.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.REVIEW, ticket.id)
        return review

    def _persist_ticket_attempt(
        self,
        state: RunState,
        ticket: Ticket,
        attempt: TicketAttempt,
    ) -> None:
        review_cycle = state.review_cycles + 1
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_coder_attempt_{review_cycle}",
            attempt.code_result.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.IMPLEMENT, ticket.id)
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_checks_{review_cycle}",
            [check.model_dump(mode="json") for check in attempt.checks],
        )
        self._append_event(state, OrchestratorState.VALIDATE, ticket.id)
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_reviewer_{review_cycle}",
            attempt.review.model_dump(mode="json"),
        )
        self._append_event(state, OrchestratorState.REVIEW, ticket.id)

    def _execute_ticket_attempt(
        self,
        state: RunState,
        ticket: Ticket,
        repo_context: dict,
        repo_commands: list[str],
    ) -> TicketAttempt:
        logger.debug("ticket_attempt_start run_id=%s ticket=%s", state.run_id, ticket.id)
        execution_root = self._ticket_execution_root(state, ticket.id)
        code_result = self._generate_code_result(
            state,
            ticket,
            repo_context,
            execution_root,
        )
        checks = self._run_checks(execution_root, repo_commands, code_result)
        review = self._generate_review(ticket, code_result, checks)
        return TicketAttempt(code_result=code_result, checks=checks, review=review)

    def run_ticket_batch(
        self,
        state: RunState,
        tickets: list[Ticket],
        repo_context: dict,
        repo_commands: list[str],
    ) -> dict[str, TicketAttempt]:
        for ticket in tickets:
            self._ticket_execution_root(state, ticket.id)
        if len(tickets) == 1:
            ticket = tickets[0]
            return {
                ticket.id: self._execute_ticket_attempt(state, ticket, repo_context, repo_commands)
            }
        logger.info(
            "parallel_ticket_batch_start run_id=%s tickets=%s workers=%s",
            state.run_id,
            ",".join(ticket.id for ticket in tickets),
            len(tickets),
        )
        with ThreadPoolExecutor(max_workers=len(tickets)) as executor:
            futures = {
                ticket.id: executor.submit(
                    self._execute_ticket_attempt,
                    state,
                    ticket,
                    repo_context,
                    repo_commands,
                )
                for ticket in tickets
            }
        return {ticket.id: futures[ticket.id].result() for ticket in tickets}

    def write_evidence_bundle(
        self,
        state: RunState,
        ticket: Ticket,
        code_result: CodeResult,
        checks: list[CheckResult],
        review: ReviewResult,
        repo_info: RepoInfo,
    ) -> tuple[list[str], ApprovalRequest | None]:
        logger.debug("evidence_bundle_start run_id=%s ticket=%s", state.run_id, ticket.id)
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
        if bundle.migration_plan is not None:
            self.deps.artifact_store.write_json(
                state.artifacts,
                f"{ticket.id}_migration_plan_{review_cycle}",
                bundle.migration_plan.model_dump(mode="json"),
            )
        state.approval_request = approval_request
        self.deps.state_store.save(state)
        logger.info(
            "evidence_bundle_written run_id=%s ticket=%s violations=%s approval_required=%s",
            state.run_id,
            ticket.id,
            len(violations),
            approval_request is not None,
        )
        return violations, approval_request

    def write_observation_followups(
        self,
        state: RunState,
        ticket: Ticket,
        checks: list[CheckResult],
        review: ReviewResult,
    ) -> None:
        observations: list[Observation] = []
        for check in checks:
            if check.success:
                continue
            observations.append(
                Observation(
                    source="check",
                    category="error",
                    summary=f"Failed check: {check.command}",
                    detail=check.output,
                    severity="high",
                )
            )
        for issue in review.issues:
            observations.append(
                Observation(
                    source="review",
                    category="regression" if review.approved is False else "feedback",
                    summary=issue.message,
                    detail=issue.recommendation,
                    path=issue.path,
                    severity=issue.severity.value,
                )
            )
        if not observations:
            return
        compilation = compile_observations(observations)
        self.deps.artifact_store.write_json(
            state.artifacts,
            f"{ticket.id}_observation_followups_{state.review_cycles + 1}",
            compilation.model_dump(mode="json"),
        )

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
        logger.debug("advance_ticket_start run_id=%s ticket=%s", state.run_id, ticket.id)
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
            logger.warning(
                "ticket_policy_violations run_id=%s ticket=%s violations=%s",
                state.run_id,
                ticket.id,
                ",".join(violations),
            )
            if state.review_cycles >= self.deps.policy.max_review_cycles:
                ticket.status = TicketStatus.escalated
                state.status = "escalated"
                self._append_event(state, OrchestratorState.ESCALATE, ",".join(violations))
                return OrchestratorState.ESCALATE
            state.review_cycles += 1
            ticket.status = TicketStatus.pending
            self._append_event(state, OrchestratorState.REVISE, ",".join(violations))
            return OrchestratorState.REVISE
        ticket.status = TicketStatus.complete
        self._sync_ticket_result(state, ticket, code_result)
        state.completed_tickets.append(ticket.id)
        state.review_cycles = 0
        logger.info("ticket_completed run_id=%s ticket=%s", state.run_id, ticket.id)
        self._append_event(state, OrchestratorState.COMPLETE_TICKET, ticket.id)
        return OrchestratorState.COMPLETE_TICKET

    def run_plan(self, repo_path: Path, brief_path: Path) -> RunState:
        logger.info("run_plan_start repo=%s brief=%s", repo_path, brief_path)
        state = self.new_state(repo_path=repo_path, brief_path=brief_path)
        repo = self.discover(state)
        spec = self.define_product(state, brief_path.read_text())
        self.plan_tickets(state, spec.model_dump(mode="json"))
        tickets = self.pick_tickets(state)
        if not tickets:
            state.status = "done"
            return state
        repo_commands = repo.repo_info.lint_commands + repo.repo_info.test_commands
        while tickets:
            logger.debug(
                "run_plan_loop run_id=%s tickets=%s review_cycles=%s",
                state.run_id,
                ",".join(ticket.id for ticket in tickets),
                state.review_cycles,
            )
            attempts = self.run_ticket_batch(
                state,
                tickets,
                repo.model_dump(mode="json"),
                repo_commands,
            )
            should_stop = False
            for ticket in tickets:
                state.current_ticket_id = ticket.id
                attempt = attempts[ticket.id]
                self._persist_ticket_attempt(state, ticket, attempt)
                violations, approval_request = self.write_evidence_bundle(
                    state,
                    ticket,
                    attempt.code_result,
                    attempt.checks,
                    attempt.review,
                    repo.repo_info,
                )
                self.write_observation_followups(
                    state,
                    ticket,
                    attempt.checks,
                    attempt.review,
                )
                result = self.advance_ticket(
                    state,
                    ticket,
                    attempt.code_result,
                    attempt.checks,
                    attempt.review,
                    violations=violations,
                    approval_request=approval_request,
                )
                if result is OrchestratorState.ESCALATE or state.status == "awaiting_approval":
                    should_stop = True
                    break
            if should_stop:
                break
            self._append_event(
                state,
                OrchestratorState.NEXT_TICKET,
                ",".join(ticket.id for ticket in tickets),
            )
            tickets = self.pick_tickets(state)
            if not tickets:
                break
        state.current_state = (
            OrchestratorState.DONE.value if state.status == "done" else state.current_state
        )
        state.run_graph_current_node_id = determine_resume_node_id(
            state.run_graph,
            state.run_graph_current_node_id,
        )
        self.deps.state_store.save(state)
        logger.info(
            "run_plan_complete run_id=%s status=%s state=%s",
            state.run_id,
            state.status,
            state.current_state,
        )
        return state


def _unique_commands(commands: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for command in commands:
        if command not in seen:
            seen.add(command)
            ordered.append(command)
    return ordered
