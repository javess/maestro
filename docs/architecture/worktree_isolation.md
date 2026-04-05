# Worktree Isolation

`STEP-013IA` moves ticket execution for git-backed repos into isolated per-ticket workspaces.

## Runtime model

- Non-git repos still execute directly in the target repo root.
- Clean git repos use `git worktree add --detach` to create a ticket workspace under
  `<repo>/.maestro/worktrees/<run_id>/<ticket_id>/`.
- Dirty git repos fall back to a filesystem copy of the repo into that same workspace layout.
- Dirty-copy workspaces skip bulky local caches and tooling directories such as `.venv`,
  `node_modules`, `.maestro`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `dist`, and `build`.

## Synchronization model

- The coder stage writes files into the isolated workspace.
- Validation commands run inside the isolated workspace.
- When a ticket is approved and passes policy gates, changed files from the structured
  `file_operations` payload are copied back into the target repo.
- Rejected or escalated attempts do not sync intermediate files back to the target repo.

## Persistence

- `RunState.ticket_workdirs` records the active per-ticket workspace paths.
- Workspace creation is also recorded as a run event so debugging traces show whether a ticket
  ran in a git worktree or a dirty-copy workspace.

## Current limitation

- Workspace cleanup is not yet automatic. `STEP-013IB` focuses on parallel execution, and later
  cleanup policy can be layered on without changing the execution contract introduced here.
