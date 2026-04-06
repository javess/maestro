# Migration Planner

`STEP-014` introduces migration plans as first-class deterministic artifacts.

## Artifact model

- `MigrationPlan` captures:
  - changed migration paths
  - backward-compatibility notes
  - rollback notes
  - validation hooks
  - impacted surfaces

## Detection model

- Migration plans are inferred deterministically from:
  - changed paths containing migration-related tokens
  - `schema.sql`
  - ticket text that explicitly describes schema or migration work

## Runtime integration

- Evidence bundles now include an optional `migration_plan`.
- Migration-aware tickets also emit a dedicated persisted migration artifact:
  - `<ticket_id>_migration_plan_<review_cycle>.json`
- Existing risk scoring already treats migration-related paths as a first-class risk factor.

## Current limitation

- The planner is generic and heuristic-based, not framework-specific.
- It does not execute migrations; it produces reviewable migration planning artifacts.
