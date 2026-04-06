from __future__ import annotations

from pathlib import PurePath

from maestro.core.risk import MIGRATION_TOKENS
from maestro.schemas.contracts import CodeResult, Ticket
from maestro.schemas.migration import MigrationPlan, ValidationHook


def build_migration_plan(ticket: Ticket, code_result: CodeResult) -> MigrationPlan | None:
    changed_paths = [change.path for change in code_result.changed_files]
    migration_paths = [
        path
        for path in changed_paths
        if MIGRATION_TOKENS.intersection(part.lower() for part in PurePath(path).parts)
        or PurePath(path).name.lower() == "schema.sql"
    ]
    ticket_text = " ".join([ticket.title, ticket.description, *ticket.acceptance_criteria]).lower()
    is_migration_ticket = any(token in ticket_text for token in (*MIGRATION_TOKENS, "schema"))
    if not migration_paths and not is_migration_ticket:
        return None
    validation_hooks = [
        ValidationHook(name=f"check_{index + 1}", command=command)
        for index, command in enumerate(code_result.commands)
    ]
    if not validation_hooks:
        validation_hooks.append(
            ValidationHook(
                name="manual_validation",
                command="Run repo test and rollout validation commands before deploy",
                required=True,
            )
        )
    impacted_surfaces = ["database schema", "application compatibility", "rollback path"]
    return MigrationPlan(
        summary=code_result.summary or f"Migration plan for {ticket.id}",
        changed_paths=migration_paths or changed_paths,
        backward_compatibility_notes=[
            "Maintain backward-compatible reads and writes during rollout.",
            "Gate destructive schema cleanup until the new path is validated.",
        ],
        rollback_notes=[
            "Revert migration files and application changes together.",
            "Validate rollback on a staging-like environment before production execution.",
        ],
        validation_hooks=validation_hooks,
        impacted_surfaces=impacted_surfaces,
    )
