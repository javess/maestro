from pathlib import Path

from maestro.schemas.contracts import ArtifactManifest, RunState
from maestro.storage.local import LocalArtifactStore, LocalStateStore


def test_artifact_store_writes_json(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path)
    manifest = store.create_run()
    path = store.write_json(manifest, "payload", {"ok": True})
    assert path.exists()
    assert manifest.artifacts[0].name == "payload"


def test_state_store_round_trip(tmp_path: Path) -> None:
    store = LocalStateStore(tmp_path)
    state = RunState(
        run_id="run-1",
        current_state="DISCOVER_REPO",
        repo_path=tmp_path,
        artifacts=ArtifactManifest(run_id="run-1"),
    )
    store.save(state)
    loaded = store.load("run-1")
    assert loaded.run_id == "run-1"
