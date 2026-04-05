from pathlib import Path

from maestro.core.run_graph_runtime import determine_resume_node_id, initialize_run_graph
from maestro.schemas.contracts import (
    ApprovalMode,
    ApprovalRequest,
    ArtifactManifest,
    EvidenceBundle,
    RiskLevel,
    RunState,
)
from maestro.storage.local import LocalArtifactStore, LocalStateStore


def test_artifact_store_writes_json(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path)
    manifest = store.create_run()
    path = store.write_json(manifest, "payload", {"ok": True})
    assert path.exists()
    assert manifest.artifacts[0].name == "payload"


def test_artifact_store_writes_evidence_bundle(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path)
    manifest = store.create_run()
    bundle = EvidenceBundle(bundle_id="bundle-1", run_id=manifest.run_id, ticket_id="T-1")
    path = store.write_evidence_bundle(manifest, bundle)
    assert path.exists()
    assert manifest.evidence_bundles[0].name == "bundle-1"
    assert manifest.evidence_bundles[0].kind == "evidence_bundle"


def test_state_store_round_trip(tmp_path: Path) -> None:
    store = LocalStateStore(tmp_path)
    graph, current = initialize_run_graph(max_review_cycles=1)
    state = RunState(
        run_id="run-1",
        current_state="DISCOVER_REPO",
        repo_path=tmp_path,
        run_graph=graph,
        run_graph_current_node_id=current,
        approval_request=ApprovalRequest(
            ticket_id="T-1",
            mode=ApprovalMode.review_go,
            required_approvals=1,
            risk_level=RiskLevel.high,
            risk_score=6,
            reason="risk high",
        ),
        artifacts=ArtifactManifest(run_id="run-1"),
    )
    store.save(state)
    loaded = store.load("run-1")
    assert loaded.run_id == "run-1"
    assert loaded.run_graph is not None
    assert loaded.approval_request is not None
    assert determine_resume_node_id(loaded.run_graph, loaded.run_graph_current_node_id) == current


def test_state_store_loads_legacy_partial_state_without_run_graph(tmp_path: Path) -> None:
    store = LocalStateStore(tmp_path)
    legacy = {
        "run_id": "legacy-1",
        "current_state": "DISCOVER_REPO",
        "repo_path": str(tmp_path),
        "artifacts": {"run_id": "legacy-1", "artifacts": []},
        "events": [],
        "status": "running",
        "backlog": {"tickets": []},
        "completed_tickets": [],
        "review_cycles": 0,
    }
    (tmp_path / "legacy-1.json").write_text(__import__("json").dumps(legacy))
    loaded = store.load("legacy-1")
    assert loaded.run_graph is None
    assert loaded.run_graph_current_node_id is None
