from pathlib import Path

from maestro.repo.discovery import discover_repo


def test_python_repo_detection(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    discovery = discover_repo(tmp_path)
    assert discovery.adapter_name == "python"


def test_generic_repo_detection(tmp_path: Path) -> None:
    discovery = discover_repo(tmp_path)
    assert discovery.adapter_name == "generic"
