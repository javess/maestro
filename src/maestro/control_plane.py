from __future__ import annotations

from pathlib import Path

import yaml

from maestro.config import load_config
from maestro.credentials import credential_status
from maestro.schemas.control_plane import (
    ControlPlaneBoundary,
    ControlPlaneConfig,
    ControlPlaneSnapshot,
    ManagedSecretBackend,
    OrgPolicyPackRef,
    ProviderCredentialSurface,
)
from maestro.storage.local import LocalStateStore, MaestroWorkspace
from maestro.storage.sqlite import SqliteRunIndex


def control_plane_config_path(repo_path: Path) -> Path:
    return MaestroWorkspace.for_repo(repo_path).root / "control_plane.yaml"


def default_control_plane_config() -> ControlPlaneConfig:
    return ControlPlaneConfig(
        org_policy_packs=[
            OrgPolicyPackRef(name="default", source="local", path="policies/default.yaml"),
        ],
        managed_secret_backends=[
            ManagedSecretBackend(name="env", kind="environment", scope="user", hosted=False),
            ManagedSecretBackend(name="keyring", kind="os_keychain", scope="user", hosted=False),
            ManagedSecretBackend(
                name="managed-secrets",
                kind="hosted_placeholder",
                scope="org",
                hosted=True,
            ),
        ],
    )


def load_control_plane_config(repo_path: Path) -> tuple[Path, ControlPlaneConfig]:
    path = control_plane_config_path(repo_path)
    if not path.exists():
        return path, default_control_plane_config()
    data = yaml.safe_load(path.read_text()) or {}
    return path, ControlPlaneConfig.model_validate(data)


def write_default_control_plane_config(repo_path: Path) -> Path:
    path = control_plane_config_path(repo_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(
                default_control_plane_config().model_dump(mode="json"),
                sort_keys=False,
            )
        )
    return path


def build_control_plane_snapshot(
    repo_path: Path,
    maestro_config_path: Path,
) -> ControlPlaneSnapshot:
    resolved_repo = repo_path.resolve()
    config_path, control_plane = load_control_plane_config(resolved_repo)
    maestro_config = load_config(maestro_config_path)
    workspace = MaestroWorkspace.for_repo(resolved_repo)
    state_store = LocalStateStore(workspace.state_dir, index=SqliteRunIndex(workspace.index_path))
    recent_runs = [row.run_id for row in state_store.list_runs()[:10]]
    credential_surfaces = []
    for name in sorted(maestro_config.providers.keys()):
        try:
            credential_info = credential_status(provider=name)
        except ValueError:
            credential_info = {
                "provider": name,
                "resolved_source": "unsupported",
                "env_present": False,
                "keyring_present": False,
            }
        credential_surfaces.append(ProviderCredentialSurface.model_validate(credential_info))
    return ControlPlaneSnapshot(
        repo_path=str(resolved_repo),
        config_path=str(config_path),
        config=control_plane,
        recent_runs=recent_runs,
        credential_surfaces=credential_surfaces,
        boundary=ControlPlaneBoundary(
            oss_capabilities=[
                "local deterministic orchestration",
                "repo-local state and artifacts",
                "local keyring or env credentials",
                "local UI and scheduler",
            ],
            hosted_extension_points=[
                "shared run history",
                "org policy registry",
                "managed secrets service",
                "cross-repo analytics",
                "team governance and approval workflows",
            ],
        ),
    )
