from pathlib import Path

from maestro.core.diffing import build_diff_artifact
from maestro.schemas.contracts import CodeResult, FileOperation


def test_build_diff_artifact_emits_unified_diff(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    work = tmp_path / "work"
    (repo / "src").mkdir(parents=True)
    (work / "src").mkdir(parents=True)
    (repo / "src" / "app.py").write_text("print('old')\n")
    (work / "src" / "app.py").write_text("print('new')\n")

    artifact = build_diff_artifact(
        run_id="RUN-1",
        ticket_id="T-1",
        review_cycle=1,
        code_result=CodeResult(
            ticket_id="T-1",
            summary="update",
            file_operations=[
                FileOperation(path="src/app.py", action="write", content="print('new')\n")
            ],
        ),
        repo_root=repo,
        execution_root=work,
    )

    assert artifact.artifact_id == "T-1_diff_1"
    assert artifact.files[0].change_type == "modified"
    assert "-print('old')" in artifact.files[0].unified_diff
    assert "+print('new')" in artifact.files[0].unified_diff
