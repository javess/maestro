# Run Scheduler Runbook

The UI and local API now expose scheduler state.

## API surfaces

- `GET /api/scheduler`
  - list queued, running, and completed runs
- `POST /api/runs/{run_id}/cancel`
  - cancel queued work if it has not started yet

## Current behavior

- queued runs wait for a free worker
- running runs occupy one worker slot
- queued cancellation is supported
- running cancellation is best-effort through `Future.cancel()`

This is a local scheduling layer, not yet a durable distributed queue.
