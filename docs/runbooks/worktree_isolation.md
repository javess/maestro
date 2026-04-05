# Worktree Isolation Runbook

## Where ticket workspaces live

For a target repo at `/path/to/repo`, isolated ticket execution now uses:

- `/path/to/repo/.maestro/worktrees/<run_id>/<ticket_id>/`

## How to inspect an isolated run

1. Run `maestro plan ... --repo /path/to/repo`.
2. Open `/path/to/repo/.maestro/state/<run_id>.json`.
3. Look at `ticket_workdirs` to find the workspace for each in-progress or completed ticket.
4. Inspect `/path/to/repo/.maestro/runs/<run_id>/` for the persisted coder, check, reviewer, and
   evidence artifacts.

## Expected behavior

- Approved changes sync back into the target repo root.
- Validation runs inside the isolated workspace instead of the target repo root.
- Dirty repos use a filtered copy fallback so local caches and dependency directories are not
  duplicated into `.maestro/worktrees`.

## When debugging mismatches

- Check the coder artifact first:
  `/path/to/repo/.maestro/runs/<run_id>/<ticket_id>_coder_attempt_<n>.json`
- Confirm the `file_operations` payload contains the files you expected to change.
- Confirm the review artifact approved the ticket.
- Confirm the ticket reached `COMPLETE_TICKET`; rejected or escalated tickets do not sync their
  workspace contents back to the main repo.
