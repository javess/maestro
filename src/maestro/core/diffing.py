from __future__ import annotations

from difflib import unified_diff
from pathlib import Path

from maestro.schemas.contracts import CodeResult, DiffArtifact, DiffFilePatch, FileOperation


def build_diff_artifact(
    *,
    run_id: str,
    ticket_id: str,
    review_cycle: int,
    code_result: CodeResult,
    repo_root: Path,
    execution_root: Path,
) -> DiffArtifact:
    files: list[DiffFilePatch] = []
    for operation in code_result.file_operations:
        patch = _build_file_patch(operation, repo_root=repo_root, execution_root=execution_root)
        if patch is not None:
            files.append(patch)
    return DiffArtifact(
        artifact_id=f"{ticket_id}_diff_{review_cycle}",
        run_id=run_id,
        ticket_id=ticket_id,
        review_cycle=review_cycle,
        summary=code_result.summary,
        files=files,
    )


def _build_file_patch(
    operation: FileOperation,
    *,
    repo_root: Path,
    execution_root: Path,
) -> DiffFilePatch | None:
    before_path = repo_root / operation.path
    after_path = execution_root / operation.path
    before = before_path.read_text().splitlines(keepends=True) if before_path.exists() else []
    after = after_path.read_text().splitlines(keepends=True) if after_path.exists() else []
    if before == after:
        return None
    change_type: str
    if not before and after:
        change_type = "added"
    elif before and not after:
        change_type = "deleted"
    else:
        change_type = "modified"
    diff_text = "".join(
        unified_diff(
            before,
            after,
            fromfile=f"a/{operation.path}",
            tofile=f"b/{operation.path}",
            lineterm="",
        )
    )
    return DiffFilePatch(
        path=operation.path,
        change_type=change_type,
        unified_diff=diff_text,
    )
