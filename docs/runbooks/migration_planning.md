# Migration Planning Runbook

## When a migration plan appears

`maestro` emits a migration plan when a ticket changes migration-like paths or clearly describes a
schema/data migration task.

## Where to find it

- `<target-repo>/.maestro/runs/<RUN_ID>/<ticket_id>_migration_plan_<n>.json`
- inside the matching evidence bundle under `migration_plan`

## How to read it

Look for:

- `changed_paths`
- `backward_compatibility_notes`
- `rollback_notes`
- `validation_hooks`
- `impacted_surfaces`

## Operational guidance

- Treat the generated plan as a deterministic checklist, not as an executed migration.
- Verify the listed validation hooks in staging-like environments before production rollout.
- Pair application changes and migration changes in rollback planning; do not revert one without
  considering the other.
