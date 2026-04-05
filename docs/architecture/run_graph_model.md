# Canonical Run Graph Model

## Purpose

`STEP-001` introduces a typed run-graph contract that describes the orchestrator flow as
an explicit DAG instead of leaving the graph shape implicit in control flow code.

This step is intentionally narrow:

- it defines contracts and validation only
- it does not yet change persistence or orchestrator execution
- it provides a canonical graph for the current deterministic state machine

## Contracts

The run-graph schema lives in [src/maestro/schemas/run_graph.py](/Users/javiersierra/dev/maestro/src/maestro/schemas/run_graph.py).

Key types:

- `RunGraphNodeKind`
- `StageState`
- `RunGraphNode`
- `RunGraphEdge`
- `RunGraphMetadata`
- `RunGraph`

## Validation Invariants

The graph validator enforces:

- at least one node
- unique node ids
- valid entry node
- valid terminal nodes
- all edges reference existing nodes
- no self-referential edges
- entry node has no incoming edges
- every node is reachable from the entry node
- terminal nodes have no outgoing edges
- non-terminal dead ends are rejected
- the graph is acyclic

## Canonical Graph

The helper `build_canonical_run_graph()` expresses the current orchestrator path using
the existing `OrchestratorState` enum. To preserve the DAG invariant:

- review retries are unrolled by `max_review_cycles`
- `NEXT_TICKET` is modeled as a graph handoff checkpoint instead of a back-edge to `PICK_TICKET`

This provides a stable contract for later steps:

- `STEP-002` can persist and reload the graph
- later steps can attach artifacts, approvals, and execution state to explicit nodes/edges

## Follow-On Work

- Persist run graphs with run state in `STEP-002`
- Attach artifact and evidence models to graph execution in later steps
- Use the graph to drive deterministic replay and resume rather than only implicit engine flow
