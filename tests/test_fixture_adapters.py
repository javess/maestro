from pathlib import Path

import pytest

from maestro.repo.discovery import discover_repo


@pytest.mark.parametrize(
    ("fixture", "adapter"),
    [
        ("python_repo", "python"),
        ("node_repo", "node"),
        ("go_repo", "go"),
        ("rust_repo", "rust"),
        ("java_repo", "java"),
        ("monorepo", "monorepo"),
        ("broken_repo", "generic"),
    ],
)
def test_fixture_adapter_selection(fixture: str, adapter: str) -> None:
    root = Path(__file__).parent / "fixtures" / fixture
    discovery = discover_repo(root)
    assert discovery.adapter_name == adapter
