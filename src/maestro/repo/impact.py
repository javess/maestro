from __future__ import annotations

import os
from pathlib import Path

from maestro.schemas.contracts import Backlog, RepoDiscovery, Ticket
from maestro.schemas.impact import ImpactAnalysis

_IGNORED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "runs",
}


def analyze_backlog_impact(backlog: Backlog, repo: RepoDiscovery) -> dict[str, ImpactAnalysis]:
    return {ticket.id: analyze_ticket_impact(ticket, repo) for ticket in backlog.tickets}


def analyze_ticket_impact(ticket: Ticket, repo: RepoDiscovery) -> ImpactAnalysis:
    files = _repo_files(repo.repo_info.root)
    ticket_terms = _ticket_terms(ticket)

    scored_paths = [
        (path, _score_path(path, ticket_terms))
        for path in files
        if _score_path(path, ticket_terms) > 0
    ]
    scored_paths.sort(key=lambda item: (-item[1], item[0]))

    likely_touched_modules = _likely_modules(scored_paths, repo)
    nearby_tests = _nearby_tests(files, likely_touched_modules)
    hotspots = _hotspots(repo, likely_touched_modules)
    coupled_interfaces = _coupled_interfaces(repo, files)
    context_slice = _context_slice(scored_paths, nearby_tests, files)
    notes = _notes(repo, likely_touched_modules)

    return ImpactAnalysis(
        ticket_id=ticket.id,
        likely_touched_modules=likely_touched_modules,
        nearby_tests=nearby_tests,
        hotspots=hotspots,
        coupled_interfaces=coupled_interfaces,
        context_slice=context_slice,
        notes=notes,
    )


def _repo_files(root: Path) -> list[str]:
    files: list[str] = []
    for current_root, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = sorted(name for name in dirnames if name not in _IGNORED_PARTS)
        current_path = Path(current_root)
        for filename in sorted(filenames):
            relative = (current_path / filename).relative_to(root)
            files.append(relative.as_posix())
    return files


def _ticket_terms(ticket: Ticket) -> set[str]:
    text = " ".join([ticket.title, ticket.description, *ticket.acceptance_criteria]).lower()
    tokens = {
        token.strip(".,:_-/()")
        for token in text.split()
        if len(token.strip(".,:_-/()")) >= 3
    }
    return {token for token in tokens if token}


def _score_path(path: str, ticket_terms: set[str]) -> int:
    parts = {
        part.lower().replace(".", "_")
        for segment in path.split("/")
        for part in segment.replace(".", "_").split("_")
        if len(part) >= 3
    }
    return len(parts & ticket_terms)


def _likely_modules(scored_paths: list[tuple[str, int]], repo: RepoDiscovery) -> list[str]:
    ranked: list[str] = []
    for path, _score in scored_paths:
        module = _module_for_path(path)
        if module not in ranked:
            ranked.append(module)
        if len(ranked) == 3:
            break
    if ranked:
        return ranked

    repo_type_defaults = {
        "python": ["src", "tests"],
        "node": ["src", "test"],
        "go": ["internal", "pkg"],
        "rust": ["src", "tests"],
        "java": ["src/main", "src/test"],
        "monorepo": ["packages", "apps"],
    }
    return repo_type_defaults.get(repo.repo_info.repo_type, ["."])


def _module_for_path(path: str) -> str:
    parts = path.split("/")
    if len(parts) == 1:
        return "."
    if parts[0] == "src" and len(parts) > 1:
        return "/".join(parts[:2])
    if parts[0] in {"tests", "test"} and len(parts) > 1:
        return parts[0]
    if parts[0] in {"packages", "apps", "services"} and len(parts) > 1:
        return "/".join(parts[:2])
    if parts[0] == "internal" and len(parts) > 1:
        return "/".join(parts[:2])
    if parts[0] == "src" and len(parts) > 2 and parts[1] in {"main", "test"}:
        return "/".join(parts[:3])
    return parts[0]


def _nearby_tests(files: list[str], likely_modules: list[str]) -> list[str]:
    tests = [
        path
        for path in files
        if (
            "/tests/" in f"/{path}"
            or "/test/" in f"/{path}"
            or path.endswith("_test.py")
            or path.endswith("_test.go")
            or path.endswith(".test.ts")
            or path.endswith("Test.java")
        )
    ]
    selected = [
        path
        for path in tests
        if any(module != "." and module.split("/")[-1] in path for module in likely_modules)
    ]
    return sorted(selected or tests)[:5]


def _hotspots(repo: RepoDiscovery, likely_modules: list[str]) -> list[str]:
    hotspots = [
        risky
        for risky in repo.repo_info.risky_paths
        if any(
            module == "." or risky.startswith(module) or module.startswith(risky)
            for module in likely_modules
        )
    ]
    return hotspots or repo.repo_info.risky_paths[:3]


def _coupled_interfaces(repo: RepoDiscovery, files: list[str]) -> list[str]:
    config_files = [
        path
        for path in files
        if path
        in {"pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml", "build.gradle"}
    ]
    interfaces = (
        repo.repo_info.build_commands + repo.repo_info.test_commands + repo.repo_info.lint_commands
    )
    return (interfaces + config_files)[:6]


def _context_slice(
    scored_paths: list[tuple[str, int]],
    nearby_tests: list[str],
    files: list[str],
) -> list[str]:
    slice_paths = [path for path, _score in scored_paths[:4]]
    for path in nearby_tests[:2]:
        if path not in slice_paths:
            slice_paths.append(path)
    for config in [
        "pyproject.toml",
        "package.json",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
    ]:
        if config in files and config not in slice_paths:
            slice_paths.append(config)
            break
    return slice_paths[:8]


def _notes(repo: RepoDiscovery, likely_modules: list[str]) -> list[str]:
    notes = list(repo.repo_info.guidance[:2])
    if repo.repo_info.repo_type == "monorepo":
        notes.append("Keep context sliced to the affected workspace or package.")
    if likely_modules == ["."]:
        notes.append("No strong module match found; fall back to repo-level context.")
    return notes
