from __future__ import annotations

from pydantic import BaseModel, Field


class SharedRunHistoryConfig(BaseModel):
    enabled: bool = False
    retention_days: int = 30
    mode: str = "local_only"


class OrgPolicyPackRef(BaseModel):
    name: str
    source: str = "local"
    path: str | None = None


class ManagedSecretBackend(BaseModel):
    name: str
    kind: str
    scope: str
    hosted: bool = False


class AnalyticsSurface(BaseModel):
    run_metrics: bool = True
    provider_usage: bool = False
    benchmark_tracking: bool = True


class GovernanceSurface(BaseModel):
    audit_log: bool = True
    approval_policies: bool = True
    spend_controls: bool = False


class ProviderCredentialSurface(BaseModel):
    provider: str
    resolved_source: str
    env_present: bool
    keyring_present: bool


class ControlPlaneBoundary(BaseModel):
    oss_capabilities: list[str] = Field(default_factory=list)
    hosted_extension_points: list[str] = Field(default_factory=list)


class ControlPlaneConfig(BaseModel):
    organization: str = "local"
    project: str = "default"
    shared_run_history: SharedRunHistoryConfig = Field(default_factory=SharedRunHistoryConfig)
    org_policy_packs: list[OrgPolicyPackRef] = Field(default_factory=list)
    managed_secret_backends: list[ManagedSecretBackend] = Field(default_factory=list)
    analytics: AnalyticsSurface = Field(default_factory=AnalyticsSurface)
    governance: GovernanceSurface = Field(default_factory=GovernanceSurface)


class ControlPlaneSnapshot(BaseModel):
    repo_path: str
    config_path: str
    config: ControlPlaneConfig
    recent_runs: list[str] = Field(default_factory=list)
    credential_surfaces: list[ProviderCredentialSurface] = Field(default_factory=list)
    boundary: ControlPlaneBoundary
