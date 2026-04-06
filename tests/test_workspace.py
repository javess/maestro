from pathlib import Path

import pytest

from maestro.core.workspace import WorkspaceEditError, apply_code_result
from maestro.repo.context import build_repo_snapshot
from maestro.schemas.contracts import CodeResult, FileOperation, PatchHunk
from maestro.schemas.impact import ImpactAnalysis


def test_apply_code_result_writes_and_deletes_files(tmp_path: Path) -> None:
    target = tmp_path / "hello.py"
    target.write_text("print('old')\n")
    result = CodeResult(
        ticket_id="T-1",
        summary="update hello",
        file_operations=[
            FileOperation(path="hello.py", action="write", content="print('new')\n"),
            FileOperation(path="unused.txt", action="write", content="temp\n"),
            FileOperation(path="unused.txt", action="delete"),
        ],
    )

    applied = apply_code_result(tmp_path, result)

    assert target.read_text() == "print('new')\n"
    assert not (tmp_path / "unused.txt").exists()
    assert [change.path for change in applied.changed_files] == [
        "hello.py",
        "unused.txt",
        "unused.txt",
    ]


def test_build_repo_snapshot_uses_context_slice_files(tmp_path: Path) -> None:
    package = tmp_path / "src"
    package.mkdir()
    (package / "app.py").write_text("print('snapshot')\n")
    (tmp_path / "README.md").write_text("# hello\n")

    snapshot = build_repo_snapshot(
        tmp_path,
        ImpactAnalysis(
            ticket_id="T-1",
            context_slice=["src/app.py", "README.md", "missing.py"],
        ),
    )

    assert [item.path for item in snapshot.files] == ["src/app.py", "README.md"]
    assert "snapshot" in snapshot.files[0].content


def test_apply_code_result_supports_patch_hunks(tmp_path: Path) -> None:
    target = tmp_path / "hello.py"
    target.write_text("def greet() -> str:\n    return 'old'\n")
    result = CodeResult(
        ticket_id="T-2",
        summary="patch hello",
        file_operations=[
            FileOperation(
                path="hello.py",
                action="patch",
                hunks=[
                    PatchHunk(kind="replace", match="return 'old'", content="return 'new'"),
                    PatchHunk(
                        kind="insert_after",
                        match="def greet() -> str:\n",
                        content="    message = 'new'\n",
                    ),
                ],
            )
        ],
    )

    applied = apply_code_result(tmp_path, result)

    assert "message = 'new'" in target.read_text()
    assert "return 'new'" in target.read_text()
    assert [change.path for change in applied.changed_files] == ["hello.py"]


def test_apply_code_result_raises_when_patch_anchor_is_missing(tmp_path: Path) -> None:
    target = tmp_path / "hello.py"
    target.write_text("print('old')\n")
    result = CodeResult(
        ticket_id="T-3",
        summary="broken patch",
        file_operations=[
            FileOperation(
                path="hello.py",
                action="patch",
                hunks=[PatchHunk(kind="replace", match="missing", content="found")],
            )
        ],
    )

    with pytest.raises(WorkspaceEditError, match="Patch anchor not found"):
        apply_code_result(tmp_path, result)
