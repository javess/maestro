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
from maestro.storage.local import (
    LocalArtifactStore,
    LocalStateStore,
    MaestroWorkspace,
    workspace_root_for_repo,
)
from maestro.storage.sqlite import SqliteRunIndex


def test_artifact_store_writes_json(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path, index=SqliteRunIndex(tmp_path / "maestro.db"))
    manifest = store.create_run()
    path = store.write_json(manifest, "payload", {"ok": True})
    assert path.exists()
    assert manifest.artifacts[0].name == "payload"
    index = SqliteRunIndex(tmp_path / "maestro.db")
    artifacts = index.list_artifacts(manifest.run_id)
    assert artifacts[0].name == "payload"


def test_artifact_store_writes_evidence_bundle(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path, index=SqliteRunIndex(tmp_path / "maestro.db"))
    manifest = store.create_run()
    bundle = EvidenceBundle(bundle_id="bundle-1", run_id=manifest.run_id, ticket_id="T-1")
    path = store.write_evidence_bundle(manifest, bundle)
    assert path.exists()
    assert manifest.evidence_bundles[0].name == "bundle-1"
    assert manifest.evidence_bundles[0].kind == "evidence_bundle"


def test_state_store_round_trip(tmp_path: Path) -> None:
    index = SqliteRunIndex(tmp_path / "maestro.db")
    store = LocalStateStore(tmp_path, index=index)
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
    indexed = index.load_run("run-1")
    assert indexed is not None
    assert indexed.status == "running"
    assert indexed.current_state == "DISCOVER_REPO"


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


def test_state_store_lists_runs_from_sqlite_index(tmp_path: Path) -> None:
    index = SqliteRunIndex(tmp_path / "maestro.db")
    store = LocalStateStore(tmp_path, index=index)
    graph, current = initialize_run_graph(max_review_cycles=1)
    for run_id in ("run-1", "run-2"):
        store.save(
            RunState(
                run_id=run_id,
                current_state="DONE",
                repo_path=tmp_path / run_id,
                run_graph=graph,
                run_graph_current_node_id=current,
                artifacts=ArtifactManifest(run_id=run_id),
                status="done",
            )
        )

    records = store.list_runs()

    assert [record.run_id for record in records] == ["run-2", "run-1"]
    assert all(record.status == "done" for record in records)


def test_workspace_for_repo_creates_repo_local_maestro_directories(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = MaestroWorkspace.for_repo(repo)
    assert workspace.root == repo / ".maestro"
    assert workspace.runs_dir == repo / ".maestro" / "runs"
    assert workspace.state_dir == repo / ".maestro" / "state"
    assert workspace.index_path == repo / ".maestro" / "maestro.db"
    assert workspace.runs_dir.exists()
    assert workspace.state_dir.exists()
    assert workspace_root_for_repo(repo) == repo / ".maestro"
