# Run Graph Resume Runbook

## What Exists Today

Each `RunState` can now persist:

- the canonical run graph
- the current graph node id

This allows deterministic inspection of where a run currently is, even though the engine
still executes from explicit Python logic.

## Resume Semantics

- If a graph node is currently active, resume points there.
- If no node is active, the first pending node in topological order is used.
- If the state file predates run-graph persistence, resume falls back gracefully because the graph fields are optional.

## Operator Notes

- Use `maestro status` and `maestro resume <RUN_ID>` to inspect saved state.
- The persisted graph is currently an inspection and resume contract, not yet the direct execution driver.
- Multi-ticket continuation remains a graph handoff boundary rather than a cyclic edge in the graph itself.

