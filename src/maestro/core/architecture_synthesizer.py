from __future__ import annotations

from maestro.schemas.architecture import (
    ApiContract,
    ApiProtocol,
    ArchitectureArtifacts,
    ArchitectureDecision,
    ArchitectureDecisionStatus,
    DataFlow,
    DomainEntity,
    ModuleBoundary,
    StateTransition,
    SystemContext,
)
from maestro.schemas.contracts import ProductSpec, RepoDiscovery


def synthesize_architecture(spec: ProductSpec, repo: RepoDiscovery) -> ArchitectureArtifacts:
    repo_module_id = f"{repo.adapter_name}_repo"
    modules = [
        ModuleBoundary(
            module_id=repo_module_id,
            name=f"{repo.repo_info.repo_type.title()} repository surface",
            responsibility="Own repo-local build, test, and layout conventions",
            paths=["."],
            exposed_interfaces=repo.repo_info.build_commands + repo.repo_info.test_commands,
            risky=bool(repo.repo_info.risky_paths),
        ),
        ModuleBoundary(
            module_id="delivery_orchestrator",
            name="Delivery orchestrator",
            responsibility="Plan, execute, validate, and review ticket work deterministically",
            paths=["src/maestro/core", "src/maestro/agents", "src/maestro/providers"],
            depends_on=[repo_module_id],
            exposed_interfaces=["run_graph", "policy_enforcement", "structured_agent_roles"],
            risky=True,
        ),
        ModuleBoundary(
            module_id="quality_gate",
            name="Quality gate",
            responsibility="Run checks, enforce policies, and package evidence for approval",
            paths=["src/maestro/core", "src/maestro/storage", "runs/"],
            depends_on=["delivery_orchestrator", repo_module_id],
            exposed_interfaces=repo.repo_info.lint_commands + repo.repo_info.test_commands,
            risky=True,
        ),
    ]

    if repo.repo_info.repo_type == "monorepo":
        modules.append(
            ModuleBoundary(
                module_id="workspace_slice",
                name="Workspace slice",
                responsibility="Constrain planning and execution to affected package paths",
                paths=["packages/", "apps/", "services/"],
                depends_on=[repo_module_id],
                exposed_interfaces=["context_slice", "workspace_filters"],
            )
        )

    entities = [
        DomainEntity(
            entity_id="product_spec",
            name="ProductSpec",
            description="Normalized design brief used to drive planning",
            owner_module_id="delivery_orchestrator",
            fields=["problem", "outcomes", "constraints", "assumption_log"],
        ),
        DomainEntity(
            entity_id="ticket_backlog",
            name="Backlog",
            description="Structured implementation tickets derived from the product model",
            owner_module_id="delivery_orchestrator",
            fields=["tickets", "unresolved_questions", "architecture_artifacts"],
        ),
        DomainEntity(
            entity_id="repo_context",
            name="RepoContext",
            description="Repo discovery and adapter guidance used during execution",
            owner_module_id=repo_module_id,
            fields=["repo_type", "build_commands", "test_commands", "risky_paths"],
        ),
    ]

    data_flows = [
        DataFlow(
            flow_id="brief_to_architecture",
            name="Brief to architecture synthesis",
            source_module_id="delivery_orchestrator",
            target_module_id=repo_module_id,
            description="The orchestrator combines normalized product intent with repo discovery.",
            payloads=["ProductSpec", "RepoDiscovery", "ArchitectureArtifacts"],
            triggers=["DEFINE_PRODUCT", "PLAN_TICKETS"],
        ),
        DataFlow(
            flow_id="architecture_to_planning",
            name="Architecture to planning",
            source_module_id="delivery_orchestrator",
            target_module_id="quality_gate",
            description="Synthesized architecture shapes ticket planning and quality expectations.",
            payloads=["ArchitectureArtifacts", "Backlog"],
            triggers=["PLAN_TICKETS"],
        ),
    ]

    api_contracts = [
        ApiContract(
            contract_id="architecture_planning_payload",
            name="planning payload",
            protocol=ApiProtocol.internal,
            producer_module_id="delivery_orchestrator",
            consumer_module_id="quality_gate",
            request_shape=["product_spec", "architecture_artifacts", "repo_context"],
            response_shape=["backlog", "evidence expectations"],
            invariants=[
                "architecture artifacts must validate before planning continues",
                "repo adapter guidance remains visible to later execution steps",
            ],
        )
    ]

    state_transitions = [
        StateTransition(
            transition_id="define_to_plan",
            state_machine="orchestrator",
            from_state="DEFINE_PRODUCT",
            to_state="PLAN_TICKETS",
            trigger="product spec and synthesized architecture are both available",
            notes=["planning consumes both product intent and repo-aware architecture context"],
        )
    ]

    decisions = [
            ArchitectureDecision(
                decision_id="adr-architecture-synthesis-baseline",
                title="Deterministic architecture synthesis baseline",
                status=ArchitectureDecisionStatus.accepted,
                context="Architecture synthesis must be stable under fake-provider tests.",
                decision=(
                    "Start with deterministic repo-aware synthesis rules instead of another "
                    "model-driven design loop."
                ),
            consequences=[
                "Architecture artifacts remain reproducible across fixture repos",
                "Later LLM-assisted synthesis can layer on top of the typed contract if needed",
            ],
        )
    ]

    return ArchitectureArtifacts(
        system_context=SystemContext(
            system_name=spec.title,
            summary=spec.summary,
            primary_user_types=spec.target_users,
            external_dependencies=[repo.repo_info.repo_type, *repo.reasons],
            constraints=spec.constraints,
        ),
        module_boundaries=modules,
        domain_entities=entities,
        data_flows=data_flows,
        api_contracts=api_contracts,
        state_transitions=state_transitions,
        decisions=decisions,
    )
