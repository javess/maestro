import pytest
from pydantic import ValidationError

from maestro.core.models import OrchestratorState
from maestro.schemas.run_graph import (
    RunGraph,
    RunGraphEdge,
    RunGraphMetadata,
    RunGraphNode,
    RunGraphNodeKind,
    StageState,
    build_canonical_run_graph,
)


def test_canonical_run_graph_serializes_and_round_trips() -> None:
    graph = build_canonical_run_graph()
    payload = graph.model_dump_json()
    restored = RunGraph.model_validate_json(payload)
    assert restored.metadata.graph_id == "canonical-orchestrator-run-graph"
    assert restored.metadata.entry_node_id == OrchestratorState.DISCOVER_REPO.value
    states = {node.orchestrator_state for node in restored.nodes}
    assert set(OrchestratorState).issubset(states)


def test_canonical_run_graph_unrolls_retry_budget() -> None:
    graph = build_canonical_run_graph(max_review_cycles=2)
    ids = {node.id for node in graph.nodes}
    assert "IMPLEMENT__attempt_1" in ids
    assert "IMPLEMENT__attempt_3" in ids
    assert "REVISE__attempt_2" in ids


def test_canonical_run_graph_rejects_negative_retry_budget() -> None:
    with pytest.raises(ValueError):
        build_canonical_run_graph(max_review_cycles=-1)


def test_stage_node_requires_orchestrator_state() -> None:
    with pytest.raises(ValidationError):
        RunGraphNode(id="x", label="X", kind=RunGraphNodeKind.stage)


def test_run_graph_rejects_missing_edge_target() -> None:
    with pytest.raises(ValidationError):
        RunGraph(
            metadata=RunGraphMetadata(
                graph_id="bad-target",
                entry_node_id="start",
                terminal_node_ids=["done"],
            ),
            nodes=[
                RunGraphNode(
                    id="start",
                    label="Start",
                    orchestrator_state=OrchestratorState.DISCOVER_REPO,
                ),
                RunGraphNode(
                    id="done",
                    label="Done",
                    orchestrator_state=OrchestratorState.DONE,
                    stage_state=StageState.complete,
                ),
            ],
            edges=[RunGraphEdge(source="start", target="missing")],
        )


def test_run_graph_rejects_cycle() -> None:
    with pytest.raises(ValidationError):
        RunGraph(
            metadata=RunGraphMetadata(
                graph_id="cycle",
                entry_node_id="a",
                terminal_node_ids=["c"],
            ),
            nodes=[
                RunGraphNode(
                    id="a",
                    label="A",
                    orchestrator_state=OrchestratorState.DISCOVER_REPO,
                ),
                RunGraphNode(
                    id="b",
                    label="B",
                    orchestrator_state=OrchestratorState.DEFINE_PRODUCT,
                ),
                RunGraphNode(
                    id="c",
                    label="C",
                    orchestrator_state=OrchestratorState.DONE,
                    stage_state=StageState.complete,
                ),
            ],
            edges=[
                RunGraphEdge(source="a", target="b"),
                RunGraphEdge(source="b", target="a"),
                RunGraphEdge(source="b", target="c"),
            ],
        )


def test_run_graph_rejects_unreachable_node() -> None:
    with pytest.raises(ValidationError):
        RunGraph(
            metadata=RunGraphMetadata(
                graph_id="unreachable",
                entry_node_id="a",
                terminal_node_ids=["c"],
            ),
            nodes=[
                RunGraphNode(
                    id="a",
                    label="A",
                    orchestrator_state=OrchestratorState.DISCOVER_REPO,
                ),
                RunGraphNode(
                    id="b",
                    label="B",
                    orchestrator_state=OrchestratorState.DEFINE_PRODUCT,
                ),
                RunGraphNode(
                    id="c",
                    label="C",
                    orchestrator_state=OrchestratorState.DONE,
                    stage_state=StageState.complete,
                ),
            ],
            edges=[RunGraphEdge(source="a", target="c")],
        )


def test_run_graph_rejects_terminal_with_outgoing_edges() -> None:
    with pytest.raises(ValidationError):
        RunGraph(
            metadata=RunGraphMetadata(
                graph_id="bad-terminal",
                entry_node_id="a",
                terminal_node_ids=["c"],
            ),
            nodes=[
                RunGraphNode(
                    id="a",
                    label="A",
                    orchestrator_state=OrchestratorState.DISCOVER_REPO,
                ),
                RunGraphNode(
                    id="b",
                    label="B",
                    orchestrator_state=OrchestratorState.DEFINE_PRODUCT,
                ),
                RunGraphNode(
                    id="c",
                    label="C",
                    orchestrator_state=OrchestratorState.DONE,
                    stage_state=StageState.complete,
                ),
            ],
            edges=[
                RunGraphEdge(source="a", target="b"),
                RunGraphEdge(source="b", target="c"),
                RunGraphEdge(source="c", target="b"),
            ],
        )
