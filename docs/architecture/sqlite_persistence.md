# SQLite Persistence

`STEP-018` adds a SQLite-backed run index without replacing JSON state or artifact files.

## Canonical storage model

- JSON run state remains the source of truth.
- JSON artifacts remain the source of truth.
- SQLite stores indexed metadata for faster listing, resume lookup, and artifact discovery.

## Database location

- Repo-local runs: `<target-repo>/.maestro/maestro.db`
- Framework-local eval runs: `<project-root>/runs/maestro.db`

## Indexed tables

- `runs`
  - `run_id`
  - `repo_path`
  - `brief_path`
  - `status`
  - `current_state`
  - `current_ticket_id`
  - `state_path`
  - `run_dir`
  - `created_at`
  - `updated_at`
- `artifacts`
  - `run_id`
  - `name`
  - `kind`
  - `path`
  - `created_at`

## Compatibility model

- Saving run state still writes the full JSON file first.
- Artifact creation still writes JSON files first.
- SQLite updates shadow the JSON writes and are safe to rebuild from canonical files later.
- If the SQLite database is missing, `maestro` can still load individual runs from JSON.

## Why SQLite first

- zero extra service dependency
- deterministic local behavior
- simple file-level backup and inspection
- enough query power for repo-local status and resume workflows

PostgreSQL remains a possible later step only if shared multi-user storage or remote coordination
becomes necessary.
