from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from maestro.schemas.contracts import ArtifactEntry, ArtifactManifest, EvidenceBundle, RunState
from maestro.schemas.storage import IndexedRunRecord
from maestro.storage.sqlite import SqliteRunIndex

WORKSPACE_DIRNAME = ".maestro"


def workspace_root_for_repo(repo_path: Path) -> Path:
    return repo_path / WORKSPACE_DIRNAME


class MaestroWorkspace:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.runs_dir = root / "runs"
        self.state_dir = root / "state"
        self.index_path = root / "maestro.db"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def for_repo(cls, repo_path: Path) -> MaestroWorkspace:
        return cls(workspace_root_for_repo(repo_path))


class LocalArtifactStore:
    def __init__(self, root: Path, index: SqliteRunIndex | None = None) -> None:
        self.root = root
        self.index = index
        self.root.mkdir(parents=True, exist_ok=True)

    def create_run(self) -> ArtifactManifest:
        run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            self.index.record_manifest(run_id, run_dir)
        return ArtifactManifest(run_id=run_id, artifacts=[])

    def write_json(self, manifest: ArtifactManifest, name: str, payload: Any) -> Path:
        run_dir = self.root / manifest.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, default=str))
        entry = ArtifactEntry(name=name, path=str(path), kind="json")
        manifest.artifacts.append(entry)
        if self.index is not None:
            self.index.record_artifact(manifest.run_id, entry)
        return path

    def write_evidence_bundle(self, manifest: ArtifactManifest, bundle: EvidenceBundle) -> Path:
        run_dir = self.root / manifest.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{bundle.bundle_id}.json"
        path.write_text(bundle.model_dump_json(indent=2))
        entry = ArtifactEntry(name=bundle.bundle_id, path=str(path), kind="evidence_bundle")
        manifest.evidence_bundles.append(entry)
        if self.index is not None:
            self.index.record_artifact(manifest.run_id, entry)
        return path


class LocalStateStore:
    def __init__(self, root: Path, index: SqliteRunIndex | None = None) -> None:
        self.root = root
        self.index = index
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, state: RunState) -> Path:
        path = self.root / f"{state.run_id}.json"
        path.write_text(state.model_dump_json(indent=2))
        if self.index is not None:
            self.index.record_state(state, path)
        return path

    def load(self, run_id: str) -> RunState:
        path = self.root / f"{run_id}.json"
        return RunState.model_validate_json(path.read_text())

    def list_run_ids(self) -> list[str]:
        if self.index is not None and self.index.path.exists():
            return [record.run_id for record in self.index.list_runs()]
        return sorted(path.stem for path in self.root.glob("*.json"))

    def list_runs(self) -> list[IndexedRunRecord]:
        if self.index is not None and self.index.path.exists():
            return self.index.list_runs()
        records: list[IndexedRunRecord] = []
        for run_id in self.list_run_ids():
            state = self.load(run_id)
            path = self.root / f"{run_id}.json"
            timestamp = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()
            records.append(
                IndexedRunRecord(
                    run_id=run_id,
                    repo_path=str(state.repo_path),
                    brief_path=str(state.brief_path) if state.brief_path is not None else None,
                    status=state.status,
                    current_state=state.current_state,
                    current_ticket_id=state.current_ticket_id,
                    state_path=str(path),
                    run_dir=str(path.parent.parent / run_id),
                    created_at=timestamp,
                    updated_at=timestamp,
                )
            )
        return sorted(records, key=lambda record: (record.updated_at, record.run_id), reverse=True)

    def exists(self, run_id: str) -> bool:
        return (self.root / f"{run_id}.json").exists()
