from __future__ import annotations

from collections import Counter, deque
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from maestro.core.models import OrchestratorState


class RunGraphNodeKind(StrEnum):
    stage = "stage"
    decision = "decision"
    artifact = "artifact"


class StageState(StrEnum):
    pending = "pending"
    active = "active"
    complete = "complete"
    blocked = "blocked"
    failed = "failed"
    skipped = "skipped"


class RunGraphNode(BaseModel):
    id: str
    kind: RunGraphNodeKind = RunGraphNodeKind.stage
    label: str
    orchestrator_state: OrchestratorState | None = None
    stage_state: StageState = StageState.pending
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_node(self) -> RunGraphNode:
        if self.kind is RunGraphNodeKind.stage and self.orchestrator_state is None:
            raise ValueError("stage nodes must declare an orchestrator_state")
        return self


class RunGraphEdge(BaseModel):
    source: str
    target: str
    condition: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunGraphMetadata(BaseModel):
    graph_id: str
    version: str = "1"
    entry_node_id: str
    terminal_node_ids: list[str]
    description: str = ""


class RunGraph(BaseModel):
    metadata: RunGraphMetadata
    nodes: list[RunGraphNode]
    edges: list[RunGraphEdge]

    @model_validator(mode="after")
    def validate_graph(self) -> RunGraph:
        if not self.nodes:
            raise ValueError("run graph must contain at least one node")

        node_ids = [node.id for node in self.nodes]
        duplicates = [node_id for node_id, count in Counter(node_ids).items() if count > 1]
        if duplicates:
            raise ValueError(f"run graph node ids must be unique: {duplicates}")

        nodes_by_id = {node.id: node for node in self.nodes}
        if self.metadata.entry_node_id not in nodes_by_id:
            raise ValueError("entry_node_id must reference an existing node")

        missing_terminals = [
            node_id for node_id in self.metadata.terminal_node_ids if node_id not in nodes_by_id
        ]
        if missing_terminals:
            raise ValueError(f"terminal_node_ids must exist in nodes: {missing_terminals}")

        incoming: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
        outgoing: dict[str, set[str]] = {node_id: set() for node_id in node_ids}

        for edge in self.edges:
            if edge.source not in nodes_by_id or edge.target not in nodes_by_id:
                raise ValueError("all edges must reference existing nodes")
            if edge.source == edge.target:
                raise ValueError("self-referential edges are not allowed")
            incoming[edge.target].add(edge.source)
            outgoing[edge.source].add(edge.target)

        if incoming[self.metadata.entry_node_id]:
            raise ValueError("entry node must not have incoming edges")

        unreachable = self._unreachable_nodes(
            entry_node_id=self.metadata.entry_node_id,
            outgoing=outgoing,
            node_ids=node_ids,
        )
        if unreachable:
            raise ValueError(f"all nodes must be reachable from entry: {sorted(unreachable)}")

        non_terminal_dead_ends = [
            node_id
            for node_id, targets in outgoing.items()
            if not targets and node_id not in self.metadata.terminal_node_ids
        ]
        if non_terminal_dead_ends:
            raise ValueError(f"dead-end nodes must be declared terminal: {non_terminal_dead_ends}")

        terminal_with_outgoing = [
            node_id
            for node_id in self.metadata.terminal_node_ids
            if outgoing[node_id]
        ]
        if terminal_with_outgoing:
            raise ValueError(
                f"terminal nodes must not have outgoing edges: {terminal_with_outgoing}"
            )

        if self._has_cycle(node_ids=node_ids, incoming=incoming, outgoing=outgoing):
            raise ValueError("run graph must be acyclic")

        return self

    @staticmethod
    def _unreachable_nodes(
        *,
        entry_node_id: str,
        outgoing: dict[str, set[str]],
        node_ids: list[str],
    ) -> set[str]:
        seen = {entry_node_id}
        queue = deque([entry_node_id])
        while queue:
            current = queue.popleft()
            for target in outgoing[current]:
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return set(node_ids) - seen

    @staticmethod
    def _has_cycle(
        *,
        node_ids: list[str],
        incoming: dict[str, set[str]],
        outgoing: dict[str, set[str]],
    ) -> bool:
        in_degree = {node_id: len(incoming[node_id]) for node_id in node_ids}
        queue = deque(node_id for node_id, degree in in_degree.items() if degree == 0)
        visited = 0
        while queue:
            current = queue.popleft()
            visited += 1
            for target in outgoing[current]:
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)
        return visited != len(node_ids)


def build_canonical_run_graph(max_review_cycles: int = 2) -> RunGraph:
    if max_review_cycles < 0:
        raise ValueError("max_review_cycles must be >= 0")

    nodes = [
        RunGraphNode(
            id=OrchestratorState.DISCOVER_REPO.value,
            label="Discover Repo",
            orchestrator_state=OrchestratorState.DISCOVER_REPO,
        ),
        RunGraphNode(
            id=OrchestratorState.DEFINE_PRODUCT.value,
            label="Define Product",
            orchestrator_state=OrchestratorState.DEFINE_PRODUCT,
        ),
        RunGraphNode(
            id=OrchestratorState.PLAN_TICKETS.value,
            label="Plan Tickets",
            orchestrator_state=OrchestratorState.PLAN_TICKETS,
        ),
        RunGraphNode(
            id=OrchestratorState.PICK_TICKET.value,
            label="Pick Ticket",
            orchestrator_state=OrchestratorState.PICK_TICKET,
        ),
        RunGraphNode(
            id=OrchestratorState.COMPLETE_TICKET.value,
            label="Complete Ticket",
            orchestrator_state=OrchestratorState.COMPLETE_TICKET,
        ),
        RunGraphNode(
            id=OrchestratorState.NEXT_TICKET.value,
            label="Next Ticket",
            orchestrator_state=OrchestratorState.NEXT_TICKET,
        ),
        RunGraphNode(
            id=OrchestratorState.DONE.value,
            label="Done",
            orchestrator_state=OrchestratorState.DONE,
            stage_state=StageState.complete,
        ),
        RunGraphNode(
            id=OrchestratorState.ESCALATE.value,
            label="Escalate",
            orchestrator_state=OrchestratorState.ESCALATE,
            stage_state=StageState.blocked,
        ),
    ]

    edges = [
        RunGraphEdge(
            source=OrchestratorState.DISCOVER_REPO.value,
            target=OrchestratorState.DEFINE_PRODUCT.value,
        ),
        RunGraphEdge(
            source=OrchestratorState.DEFINE_PRODUCT.value,
            target=OrchestratorState.PLAN_TICKETS.value,
        ),
        RunGraphEdge(
            source=OrchestratorState.PLAN_TICKETS.value,
            target=OrchestratorState.PICK_TICKET.value,
        ),
        RunGraphEdge(
            source=OrchestratorState.PICK_TICKET.value,
            target=OrchestratorState.DONE.value,
            condition="no_pending_ticket",
        ),
        RunGraphEdge(
            source=OrchestratorState.COMPLETE_TICKET.value,
            target=OrchestratorState.NEXT_TICKET.value,
        ),
        RunGraphEdge(
            source=OrchestratorState.NEXT_TICKET.value,
            target=OrchestratorState.DONE.value,
            condition="graph_instance_complete_or_handoff",
        ),
    ]

    attempt_count = max_review_cycles + 1
    for attempt in range(1, attempt_count + 1):
        implement_id = f"{OrchestratorState.IMPLEMENT.value}__attempt_{attempt}"
        validate_id = f"{OrchestratorState.VALIDATE.value}__attempt_{attempt}"
        review_id = f"{OrchestratorState.REVIEW.value}__attempt_{attempt}"

        nodes.extend(
            [
                RunGraphNode(
                    id=implement_id,
                    label=f"Implement (Attempt {attempt})",
                    orchestrator_state=OrchestratorState.IMPLEMENT,
                ),
                RunGraphNode(
                    id=validate_id,
                    label=f"Validate (Attempt {attempt})",
                    orchestrator_state=OrchestratorState.VALIDATE,
                ),
                RunGraphNode(
                    id=review_id,
                    label=f"Review (Attempt {attempt})",
                    orchestrator_state=OrchestratorState.REVIEW,
                ),
            ]
        )

        if attempt == 1:
            edges.append(
                RunGraphEdge(
                    source=OrchestratorState.PICK_TICKET.value,
                    target=implement_id,
                    condition="ticket_available",
                )
            )

        edges.extend(
            [
                RunGraphEdge(source=implement_id, target=validate_id),
                RunGraphEdge(source=validate_id, target=review_id),
                RunGraphEdge(
                    source=review_id,
                    target=OrchestratorState.COMPLETE_TICKET.value,
                    condition="approved",
                ),
            ]
        )

        if attempt <= max_review_cycles:
            revise_id = f"{OrchestratorState.REVISE.value}__attempt_{attempt}"
            next_implement_id = f"{OrchestratorState.IMPLEMENT.value}__attempt_{attempt + 1}"
            nodes.append(
                RunGraphNode(
                    id=revise_id,
                    label=f"Revise (Attempt {attempt})",
                    orchestrator_state=OrchestratorState.REVISE,
                )
            )
            edges.extend(
                [
                    RunGraphEdge(
                        source=review_id,
                        target=revise_id,
                        condition="review_rejected_with_retry_available",
                    ),
                    RunGraphEdge(source=revise_id, target=next_implement_id),
                ]
            )
        else:
            edges.append(
                RunGraphEdge(
                    source=review_id,
                    target=OrchestratorState.ESCALATE.value,
                    condition="review_rejected_retry_exhausted",
                )
            )

    return RunGraph(
        metadata=RunGraphMetadata(
            graph_id="canonical-orchestrator-run-graph",
            entry_node_id=OrchestratorState.DISCOVER_REPO.value,
            terminal_node_ids=[
                OrchestratorState.DONE.value,
                OrchestratorState.ESCALATE.value,
            ],
            description=(
                "Canonical bounded DAG contract for the current deterministic orchestrator "
                "flow, with retry paths unrolled by max_review_cycles and next-ticket "
                "iteration treated as a later graph handoff."
            ),
        ),
        nodes=nodes,
        edges=edges,
    )
