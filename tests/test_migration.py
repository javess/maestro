from maestro.core.migration import build_migration_plan
from maestro.schemas.contracts import CodeChange, CodeResult, Ticket


def test_build_migration_plan_detects_migration_paths() -> None:
    ticket = Ticket(
        id="T-1",
        title="Add user table",
        description="Add the database migration",
        acceptance_criteria=["migration is documented"],
    )
    code_result = CodeResult(
        ticket_id="T-1",
        summary="Add migration",
        changed_files=[CodeChange(path="migrations/001_add_user.sql", summary="add migration")],
        commands=["uv run pytest"],
    )

    plan = build_migration_plan(ticket, code_result)

    assert plan is not None
    assert plan.changed_paths == ["migrations/001_add_user.sql"]
    assert plan.validation_hooks[0].command == "uv run pytest"


def test_build_migration_plan_returns_none_for_non_migration_change() -> None:
    ticket = Ticket(
        id="T-1",
        title="Update docs",
        description="Docs only",
        acceptance_criteria=["docs updated"],
    )
    code_result = CodeResult(
        ticket_id="T-1",
        summary="Docs",
        changed_files=[CodeChange(path="README.md", summary="docs")],
    )

    assert build_migration_plan(ticket, code_result) is None
