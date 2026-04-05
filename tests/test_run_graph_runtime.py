from pathlib import Path

from maestro.core.models import OrchestratorState
from maestro.core.run_graph_runtime import (
    advance_run_graph,
    determine_resume_node_id,
    initialize_run_graph,
)
from maestro.schemas.contracts import ArtifactManifest, RunState
from maestro.schemas.run_graph import StageState


def test_initialize_run_graph_sets_entry_active() -> None:
    graph, current = initialize_run_graph(max_review_cycles=2)
    assert current == OrchestratorState.DISCOVER_REPO.value
    node = next(node for node in graph.nodes if node.id == current)
    assert node.stage_state == "active"


def test_advance_run_graph_moves_to_next_matching_node() -> None:
    graph, current = initialize_run_graph(max_review_cycles=1)
    graph_after_discover, current = advance_run_graph(
        graph,
        orchestrator_state=OrchestratorState.DISCOVER_REPO,
        current_node_id=current,
    )
    assert graph_after_discover is not None
    graph_after_define, current = advance_run_graph(
        graph_after_discover,
        orchestrator_state=OrchestratorState.DEFINE_PRODUCT,
        current_node_id=current,
    )
    assert graph_after_define is not None
    assert current == OrchestratorState.DEFINE_PRODUCT.value
    discover = next(
        node
        for node in graph_after_define.nodes
        if node.id == OrchestratorState.DISCOVER_REPO.value
    )
    define = next(
        node
        for node in graph_after_define.nodes
        if node.id == OrchestratorState.DEFINE_PRODUCT.value
    )
    assert discover.stage_state == StageState.complete
    assert define.stage_state == StageState.active


def test_determine_resume_node_id_prefers_current_active_node() -> None:
    graph, current = initialize_run_graph(max_review_cycles=1)
    assert determine_resume_node_id(graph, current) == OrchestratorState.DISCOVER_REPO.value


def test_determine_resume_node_id_handles_missing_graph() -> None:
    assert determine_resume_node_id(None, None) is None


def test_run_state_accepts_missing_run_graph_for_compatibility(tmp_path: Path) -> None:
    state = RunState(
        run_id="run-compat",
        current_state=OrchestratorState.DISCOVER_REPO.value,
        repo_path=tmp_path,
        artifacts=ArtifactManifest(run_id="run-compat"),
    )
    assert state.run_graph is None
    assert state.run_graph_current_node_id is None
