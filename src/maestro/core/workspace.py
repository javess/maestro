from __future__ import annotations

from pathlib import Path

from maestro.schemas.contracts import CodeChange, CodeResult, FileOperation


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
