from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ArchitectureDecisionStatus(StrEnum):
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"
    deferred = "deferred"


class ApiProtocol(StrEnum):
    http = "http"
    grpc = "grpc"
    cli = "cli"
    event = "event"
    internal = "internal"
    other = "other"


class ModuleBoundary(BaseModel):
    module_id: str
    name: str
    responsibility: str
    paths: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    exposed_interfaces: list[str] = Field(default_factory=list)
    risky: bool = False


class DomainEntity(BaseModel):
    entity_id: str
    name: str
    description: str
    owner_module_id: str | None = None
    fields: list[str] = Field(default_factory=list)


class DataFlow(BaseModel):
    flow_id: str
    name: str
    source_module_id: str
    target_module_id: str
    description: str
    payloads: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)


class ApiContract(BaseModel):
    contract_id: str
    name: str
    protocol: ApiProtocol
    producer_module_id: str
    consumer_module_id: str
    request_shape: list[str] = Field(default_factory=list)
    response_shape: list[str] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)


class StateTransition(BaseModel):
    transition_id: str
    state_machine: str
    from_state: str
    to_state: str
    trigger: str
    notes: list[str] = Field(default_factory=list)


class ArchitectureDecision(BaseModel):
    decision_id: str
    title: str
    status: ArchitectureDecisionStatus
    context: str
    decision: str
    consequences: list[str] = Field(default_factory=list)


class SystemContext(BaseModel):
    system_name: str
    summary: str
    primary_user_types: list[str] = Field(default_factory=list)
    external_dependencies: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class ArchitectureArtifacts(BaseModel):
    system_context: SystemContext
    module_boundaries: list[ModuleBoundary] = Field(default_factory=list)
    domain_entities: list[DomainEntity] = Field(default_factory=list)
    data_flows: list[DataFlow] = Field(default_factory=list)
    api_contracts: list[ApiContract] = Field(default_factory=list)
    state_transitions: list[StateTransition] = Field(default_factory=list)
    decisions: list[ArchitectureDecision] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> ArchitectureArtifacts:
        module_ids = {module.module_id for module in self.module_boundaries}
        if len(module_ids) != len(self.module_boundaries):
            raise ValueError("module ids must be unique")

        entity_ids = {entity.entity_id for entity in self.domain_entities}
        if len(entity_ids) != len(self.domain_entities):
            raise ValueError("domain entity ids must be unique")

        contract_ids = {contract.contract_id for contract in self.api_contracts}
        if len(contract_ids) != len(self.api_contracts):
            raise ValueError("api contract ids must be unique")

        transition_ids = {transition.transition_id for transition in self.state_transitions}
        if len(transition_ids) != len(self.state_transitions):
            raise ValueError("state transition ids must be unique")

        flow_ids = {flow.flow_id for flow in self.data_flows}
        if len(flow_ids) != len(self.data_flows):
            raise ValueError("data flow ids must be unique")

        decision_ids = {decision.decision_id for decision in self.decisions}
        if len(decision_ids) != len(self.decisions):
            raise ValueError("architecture decision ids must be unique")

        for module in self.module_boundaries:
            missing_dependencies = sorted(set(module.depends_on) - module_ids)
            if missing_dependencies:
                raise ValueError(
                    f"module '{module.module_id}' depends on unknown modules: "
                    f"{missing_dependencies}"
                )

        for entity in self.domain_entities:
            if entity.owner_module_id and entity.owner_module_id not in module_ids:
                raise ValueError(
                    f"domain entity '{entity.entity_id}' references unknown owner module "
                    f"'{entity.owner_module_id}'"
                )

        for flow in self.data_flows:
            if flow.source_module_id not in module_ids:
                raise ValueError(
                    f"data flow '{flow.flow_id}' references unknown source module "
                    f"'{flow.source_module_id}'"
                )
            if flow.target_module_id not in module_ids:
                raise ValueError(
                    f"data flow '{flow.flow_id}' references unknown target module "
                    f"'{flow.target_module_id}'"
                )

        for contract in self.api_contracts:
            if contract.producer_module_id not in module_ids:
                raise ValueError(
                    f"api contract '{contract.contract_id}' references unknown producer module "
                    f"'{contract.producer_module_id}'"
                )
            if contract.consumer_module_id not in module_ids:
                raise ValueError(
                    f"api contract '{contract.contract_id}' references unknown consumer module "
                    f"'{contract.consumer_module_id}'"
                )

        return self
