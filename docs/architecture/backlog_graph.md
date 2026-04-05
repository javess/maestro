# Backlog Graph

`STEP-011` replaces the implicit flat-ticket execution order with a typed `BacklogGraph`.

## Contract Surface

The graph contracts live in `src/maestro/schemas/backlog_graph.py`.

The persisted planning surface now includes:

- `Backlog.execution_graph`
- graph nodes with ticket dependencies, priority, parallelizable flags, and critical-path rank
- graph edges representing dependency links
- deterministic ordered ticket ids
- critical path ticket ids

## Deterministic Graph Builder

The current builder lives in `src/maestro/core/backlog_graph.py`.

It derives graph structure from the planned tickets by:

- preserving declared ticket dependencies
- computing a depth-based critical-path rank
- sorting tickets deterministically by dependency depth, descending priority, then id
- marking dependency-free tickets as parallelizable in the baseline model

## Execution Impact

`OrchestratorEngine.pick_ticket()` now uses the backlog graph instead of scanning tickets in list
order. A ticket is eligible only when:

- its status is `pending`
- all dependency tickets are in the completed set

This keeps execution deterministic while making ticket-ordering decisions explicit and inspectable.

## Current Limitations

- The builder infers graph structure from ticket dependencies only.
- Parallelizable flags are heuristic and do not yet drive concurrent execution.
- Critical path metadata is shallow and based on dependency depth rather than duration estimates.
