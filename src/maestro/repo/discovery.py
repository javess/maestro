from __future__ import annotations

from pathlib import Path

from maestro.repo.adapters import RepoAdapter, default_adapters
from maestro.schemas.contracts import RepoDiscovery


def discover_repo(root: Path, adapters: list[RepoAdapter] | None = None) -> RepoDiscovery:
    for adapter in adapters or default_adapters():
        if adapter.matches(root):
            return adapter.discover(root)
    raise RuntimeError("No repo adapter available")
