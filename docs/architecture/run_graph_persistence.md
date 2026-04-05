# Run Graph Persistence And Resume

## Purpose

`STEP-002` persists the canonical run graph with `RunState` and adds deterministic helpers
 for resume and inspection.

This step remains intentionally narrow:

- the orchestrator still runs from explicit Python control flow
- the run graph is now persisted alongside state for replay and resume inspection
- resume helpers point to the current active or next pending graph node

## Data Model Changes

`RunState` now includes:

- `run_graph`: the persisted canonical `RunGraph`
- `run_graph_current_node_id`: the current active or most recent graph node id

These fields are optional so older state files still load cleanly.

## Runtime Helpers

The helper module [src/maestro/core/run_graph_runtime.py](/Users/javiersierra/dev/maestro/src/maestro/core/run_graph_runtime.py) provides:

- `initialize_run_graph(max_review_cycles)`
- `advance_run_graph(...)`
- `determine_resume_node_id(...)`
- `topological_node_ids(...)`

## Behavior

- New runs initialize with the canonical graph entry node active.
- Each orchestrator event advances the persisted graph to the next matching node.
- Resume logic prefers the current active node, then falls back to the first pending node in topological order.
- Legacy saved states without graph fields remain valid.

## Follow-On Work

- `STEP-003` can extend persisted graph-linked state with evidence artifacts.
- Later steps can use the persisted graph to drive deterministic replay and richer resume behavior rather than only inspection.

