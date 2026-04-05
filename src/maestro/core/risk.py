from __future__ import annotations

from math import ceil
from pathlib import PurePath

from maestro.schemas.contracts import (
    CodeResult,
    PolicyPack,
    RepoInfo,
    RiskFactor,
    RiskLevel,
    RiskScore,
    Ticket,
)

DEPENDENCY_FILES = {
    "pyproject.toml",
    "requirements.txt",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
}
LOCKFILE_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "Cargo.lock"}
MIGRATION_TOKENS = {"migration", "migrations", "alembic", "db", "migrate"}
SENSITIVE_KEYWORDS = {"auth", "billing", "payment", "payments", "infra", "deploy", "security"}


def compute_risk_score(
    *,
    policy: PolicyPack,
    ticket: Ticket,
    code_result: CodeResult,
    repo_info: RepoInfo,
) -> RiskScore:
    changed_paths = [change.path for change in code_result.changed_files]
    changed_parts = [tuple(PurePath(path).parts) for path in changed_paths]
    weights = policy.risk_weights
    factors: list[RiskFactor] = []

    file_count = len(changed_paths)
    medium_cutoff = max(2, ceil(policy.max_files_changed * 0.2))
    large_cutoff = max(4, ceil(policy.max_files_changed * 0.5))
    if file_count >= large_cutoff:
        factors.append(
            RiskFactor(
                name="blast_radius_large",
                triggered=True,
                weight=weights.get("blast_radius_large", 0),
                detail=f"changed_files={file_count} cutoff={large_cutoff}",
            )
        )
    elif file_count >= medium_cutoff:
        factors.append(
            RiskFactor(
                name="blast_radius_medium",
                triggered=True,
                weight=weights.get("blast_radius_medium", 0),
                detail=f"changed_files={file_count} cutoff={medium_cutoff}",
            )
        )

    protected = [
        path
        for path in changed_paths
        if any(path.startswith(prefix) for prefix in policy.protected_paths)
    ]
    if protected:
        factors.append(
            RiskFactor(
                name="protected_path",
                triggered=True,
                weight=weights.get("protected_path", 0),
                detail=", ".join(protected),
            )
        )

    repo_risky = [
        path
        for path in changed_paths
        if any(path.startswith(prefix) for prefix in repo_info.risky_paths)
    ]
    if repo_risky:
        factors.append(
            RiskFactor(
                name="repo_risky_path",
                triggered=True,
                weight=weights.get("repo_risky_path", 0),
                detail=", ".join(repo_risky),
            )
        )

    dependency_changes = [path for path in changed_paths if PurePath(path).name in DEPENDENCY_FILES]
    if dependency_changes:
        only_lockfiles = all(PurePath(path).name in LOCKFILE_NAMES for path in dependency_changes)
        restricted = not policy.dependency_change_rules.get("allow_lockfile_updates", True)
        factor_name = (
            "dependency_change_restricted"
            if restricted or not only_lockfiles
            else "dependency_change"
        )
        factors.append(
            RiskFactor(
                name=factor_name,
                triggered=True,
                weight=weights.get(factor_name, 0),
                detail=", ".join(dependency_changes),
            )
        )

    migrations = [
        path
        for path, parts in zip(changed_paths, changed_parts, strict=False)
        if MIGRATION_TOKENS.intersection(part.lower() for part in parts)
        or PurePath(path).name.lower() == "schema.sql"
    ]
    if migrations:
        factors.append(
            RiskFactor(
                name="migration_change",
                triggered=True,
                weight=weights.get("migration_change", 0),
                detail=", ".join(migrations),
            )
        )

    sensitive_patterns = tuple(
        pattern.lower().strip("/") for pattern in policy.sensitive_path_patterns
    )
    sensitive_paths = [
        path
        for path, parts in zip(changed_paths, changed_parts, strict=False)
        if any(
            pattern in "/".join(part.lower() for part in parts)
            for pattern in sensitive_patterns
        )
    ]
    if sensitive_paths:
        factors.append(
            RiskFactor(
                name="sensitive_area",
                triggered=True,
                weight=weights.get("sensitive_area", 0),
                detail=", ".join(sensitive_paths),
            )
        )

    ticket_text = " ".join([ticket.title, ticket.description, *ticket.acceptance_criteria]).lower()
    ticket_keywords = sorted(keyword for keyword in SENSITIVE_KEYWORDS if keyword in ticket_text)
    if ticket_keywords:
        factors.append(
            RiskFactor(
                name="ticket_sensitive_domain",
                triggered=True,
                weight=weights.get("ticket_sensitive_domain", 0),
                detail=", ".join(ticket_keywords),
            )
        )

    score = sum(factor.weight for factor in factors if factor.triggered)
    thresholds = policy.risk_thresholds
    if score >= thresholds.get("critical", 10):
        level = RiskLevel.critical
    elif score >= thresholds.get("high", 6):
        level = RiskLevel.high
    elif score >= thresholds.get("medium", 3):
        level = RiskLevel.medium
    else:
        level = RiskLevel.low
    return RiskScore(score=score, level=level, factors=factors)
