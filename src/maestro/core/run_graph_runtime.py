from __future__ import annotations

from collections import deque

from maestro.core.models import OrchestratorState
from maestro.schemas.run_graph import RunGraph, RunGraphNode, StageState, build_canonical_run_graph


def initialize_run_graph(max_review_cycles: int) -> tuple[RunGraph, str]:
    graph = build_canonical_run_graph(max_review_cycles=max_review_cycles)
    entry_id = graph.metadata.entry_node_id
    for node in graph.nodes:
        if node.id == entry_id:
            node.stage_state = StageState.active
            break
    return graph, entry_id


def advance_run_graph(
    graph: RunGraph | None,
    *,
    orchestrator_state: OrchestratorState,
    current_node_id: str | None,
) -> tuple[RunGraph | None, str | None]:
    if graph is None:
        return None, None

    target = _find_target_node(graph, orchestrator_state, current_node_id)
    if target is None:
        return graph, current_node_id

    if current_node_id is not None and current_node_id != target.id:
        current = _node_by_id(graph, current_node_id)
        if current is not None and current.stage_state is StageState.active:
            current.stage_state = StageState.complete

    if target.stage_state is StageState.pending:
        target.stage_state = StageState.active
    return graph, target.id


def determine_resume_node_id(graph: RunGraph | None, current_node_id: str | None) -> str | None:
    if graph is None:
        return None
    if current_node_id is not None:
        current = _node_by_id(graph, current_node_id)
        if current is not None and current.stage_state in {StageState.active, StageState.pending}:
            return current.id
    for node_id in topological_node_ids(graph):
        node = _node_by_id(graph, node_id)
        if node is not None and node.stage_state in {StageState.active, StageState.pending}:
            return node.id
    return None


def topological_node_ids(graph: RunGraph) -> list[str]:
    node_ids = [node.id for node in graph.nodes]
    outgoing: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    in_degree: dict[str, int] = {node_id: 0 for node_id in node_ids}
    for edge in graph.edges:
        if edge.target not in outgoing[edge.source]:
            outgoing[edge.source].add(edge.target)
            in_degree[edge.target] += 1
    queue = deque(node_id for node_id, degree in in_degree.items() if degree == 0)
    ordered: list[str] = []
    while queue:
        node_id = queue.popleft()
        ordered.append(node_id)
        for target in outgoing[node_id]:
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)
    return ordered


def _find_target_node(
    graph: RunGraph,
    orchestrator_state: OrchestratorState,
    current_node_id: str | None,
) -> RunGraphNode | None:
    if current_node_id is not None:
        current = _node_by_id(graph, current_node_id)
        if current is not None and current.orchestrator_state is orchestrator_state:
            return current
    for node_id in topological_node_ids(graph):
        node = _node_by_id(graph, node_id)
        if node is None:
            continue
        if node.orchestrator_state is orchestrator_state and node.stage_state in {
            StageState.pending,
            StageState.active,
        }:
            return node
    return None


def _node_by_id(graph: RunGraph, node_id: str) -> RunGraphNode | None:
    for node in graph.nodes:
        if node.id == node_id:
            return node
    return None

