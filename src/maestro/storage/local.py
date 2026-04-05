from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from maestro.schemas.contracts import ArtifactEntry, ArtifactManifest, EvidenceBundle, RunState

WORKSPACE_DIRNAME = ".maestro"


def workspace_root_for_repo(repo_path: Path) -> Path:
    return repo_path / WORKSPACE_DIRNAME


class MaestroWorkspace:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.runs_dir = root / "runs"
        self.state_dir = root / "state"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def for_repo(cls, repo_path: Path) -> MaestroWorkspace:
        return cls(workspace_root_for_repo(repo_path))


class LocalArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def create_run(self) -> ArtifactManifest:
        run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return ArtifactManifest(run_id=run_id, artifacts=[])

    def write_json(self, manifest: ArtifactManifest, name: str, payload: Any) -> Path:
        run_dir = self.root / manifest.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, default=str))
        manifest.artifacts.append(ArtifactEntry(name=name, path=str(path), kind="json"))
        return path

    def write_evidence_bundle(self, manifest: ArtifactManifest, bundle: EvidenceBundle) -> Path:
        run_dir = self.root / manifest.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{bundle.bundle_id}.json"
        path.write_text(bundle.model_dump_json(indent=2))
        manifest.evidence_bundles.append(
            ArtifactEntry(name=bundle.bundle_id, path=str(path), kind="evidence_bundle")
        )
        return path


class LocalStateStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, state: RunState) -> Path:
        path = self.root / f"{state.run_id}.json"
        path.write_text(state.model_dump_json(indent=2))
        return path

    def load(self, run_id: str) -> RunState:
        path = self.root / f"{run_id}.json"
        return RunState.model_validate_json(path.read_text())

    def list_run_ids(self) -> list[str]:
        return sorted(path.stem for path in self.root.glob("*.json"))

    def exists(self, run_id: str) -> bool:
        return (self.root / f"{run_id}.json").exists()
