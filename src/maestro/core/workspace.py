from __future__ import annotations

import shutil
from pathlib import Path

from maestro.schemas.contracts import CodeChange, CodeResult, FileOperation, PatchHunk


class WorkspaceEditError(RuntimeError):
    """Raised when a structured repo mutation cannot be applied safely."""


def apply_code_result(repo_root: Path, result: CodeResult) -> CodeResult:
    changed_paths: list[str] = []
    for operation in result.file_operations:
        changed_paths.append(_apply_file_operation(repo_root, operation))
    if changed_paths and not result.changed_files:
        result.changed_files = [
            CodeChange(path=path, summary=f"{_summary_for_path(path)} via generated file operation")
            for path in changed_paths
        ]
    return result


def _apply_file_operation(repo_root: Path, operation: FileOperation) -> str:
    path = repo_root / operation.path
    if operation.action == "delete":
        if path.exists():
            path.unlink()
        return operation.path
    if operation.action == "patch":
        if not path.exists():
            raise WorkspaceEditError(f"Patch target does not exist: {operation.path}")
        patched = path.read_text()
        for hunk in operation.hunks:
            patched = _apply_patch_hunk(operation.path, patched, hunk)
        path.write_text(patched)
        if operation.executable:
            path.chmod(path.stat().st_mode | 0o111)
        return operation.path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(operation.content or "")
    if operation.executable:
        path.chmod(path.stat().st_mode | 0o111)
    return operation.path


def _summary_for_path(path: str) -> str:
    suffix = Path(path).suffix
    if suffix:
        return f"write {suffix.lstrip('.')} file"
    return "write file"


def sync_code_result(source_root: Path, target_root: Path, result: CodeResult) -> None:
    for operation in result.file_operations:
        source = source_root / operation.path
        target = target_root / operation.path
        if operation.action == "delete":
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.exists():
            shutil.copy2(source, target)


def _apply_patch_hunk(path: str, source: str, hunk: PatchHunk) -> str:
    start, end = _locate_occurrence(path, source, hunk.match, hunk.occurrence)
    if hunk.kind == "replace":
        return source[:start] + hunk.content + source[end:]
    if hunk.kind == "insert_before":
        return source[:start] + hunk.content + source[start:]
    return source[:end] + hunk.content + source[end:]


def _locate_occurrence(path: str, source: str, match: str, occurrence: int) -> tuple[int, int]:
    if occurrence < 1:
        raise WorkspaceEditError(f"Patch occurrence must be >= 1 for {path}")
    index = -1
    start = 0
    for _ in range(occurrence):
        index = source.find(match, start)
        if index == -1:
            raise WorkspaceEditError(
                f"Patch anchor not found for {path}: occurrence={occurrence} match={match!r}"
            )
        start = index + len(match)
    return index, index + len(match)
