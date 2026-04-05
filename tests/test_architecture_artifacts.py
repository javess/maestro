import pytest
from pydantic import ValidationError

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


def build_artifacts() -> ArchitectureArtifacts:
    return ArchitectureArtifacts(
        system_context=SystemContext(
            system_name="maestro",
            summary="Deterministic design-to-execution orchestration",
            primary_user_types=["platform engineers", "software teams"],
            external_dependencies=["llm providers", "local repos"],
            constraints=["deterministic orchestration", "schema validation"],
        ),
        module_boundaries=[
            ModuleBoundary(
                module_id="core",
                name="Core engine",
                responsibility="Own orchestration state transitions",
                paths=["src/maestro/core"],
                exposed_interfaces=["Orchestrator.run_plan"],
            ),
            ModuleBoundary(
                module_id="providers",
                name="Provider layer",
                responsibility="Normalize provider capabilities and routing",
                paths=["src/maestro/providers"],
                depends_on=["core"],
                exposed_interfaces=["ProviderRouter.generate_structured"],
            ),
        ],
        domain_entities=[
            DomainEntity(
                entity_id="run-state",
                name="RunState",
                description="Persisted orchestration state",
                owner_module_id="core",
                fields=["run_id", "current_state", "status"],
            )
        ],
        data_flows=[
            DataFlow(
                flow_id="flow-1",
                name="planner request",
                source_module_id="core",
                target_module_id="providers",
                description="Core requests structured planner output through routed provider calls",
                payloads=["CompiledBrief", "ProductSpec"],
                triggers=["DEFINE_PRODUCT", "PLAN_TICKETS"],
            )
        ],
        api_contracts=[
            ApiContract(
                contract_id="contract-1",
                name="structured generation",
                protocol=ApiProtocol.internal,
                producer_module_id="providers",
                consumer_module_id="core",
                request_shape=["role", "prompt", "schema", "metadata"],
                response_shape=["validated schema instance", "route metadata"],
                invariants=[
                    "schema validation must succeed",
                    "provider routing remains deterministic",
                ],
            )
        ],
        state_transitions=[
            StateTransition(
                transition_id="transition-1",
                state_machine="orchestrator",
                from_state="DEFINE_PRODUCT",
                to_state="PLAN_TICKETS",
                trigger="product spec validated",
                notes=["run graph remains canonical state model"],
            )
        ],
        decisions=[
            ArchitectureDecision(
                decision_id="adr-1",
                title="Deterministic controller",
                status=ArchitectureDecisionStatus.accepted,
                context="Agent execution must remain resumable and auditable",
                decision=(
                    "Keep the orchestrator deterministic and push model logic to typed role "
                    "boundaries"
                ),
                consequences=[
                    "State transitions stay explicit",
                    "Provider-specific logic stays outside the core engine",
                ],
            )
        ],
    )


def test_architecture_artifacts_round_trip() -> None:
    artifacts = build_artifacts()
    restored = ArchitectureArtifacts.model_validate_json(artifacts.model_dump_json())
    assert restored.system_context.system_name == "maestro"
    assert restored.module_boundaries[1].depends_on == ["core"]
    assert restored.api_contracts[0].protocol is ApiProtocol.internal


def test_architecture_artifacts_reject_unknown_module_references() -> None:
    with pytest.raises(ValidationError):
        ArchitectureArtifacts(
            system_context=SystemContext(system_name="maestro", summary="x"),
            module_boundaries=[
                ModuleBoundary(
                    module_id="core",
                    name="Core engine",
                    responsibility="Own orchestration",
                )
            ],
            api_contracts=[
                ApiContract(
                    contract_id="contract-1",
                    name="broken contract",
                    protocol=ApiProtocol.internal,
                    producer_module_id="missing",
                    consumer_module_id="core",
                )
            ],
        )


def test_architecture_artifacts_reject_duplicate_ids() -> None:
    with pytest.raises(ValidationError):
        ArchitectureArtifacts(
            system_context=SystemContext(system_name="maestro", summary="x"),
            module_boundaries=[
                ModuleBoundary(module_id="core", name="Core", responsibility="Own orchestration"),
                ModuleBoundary(module_id="core", name="Duplicate", responsibility="Duplicate id"),
            ],
        )
