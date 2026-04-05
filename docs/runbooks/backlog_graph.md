# Backlog Graph Runbook

Use this when you need to inspect or debug how `maestro` ordered planned tickets.

## Where To Look

- planning artifact: `runs/<RUN_ID>/ceremony_master.json`
- in-memory contract: `Backlog.execution_graph`
- eval scenario: `backlog-graph-ordering`

## What To Check

- `ordered_ticket_ids` should reflect the deterministic ticket execution order
- `critical_path_ticket_ids` should highlight the deepest dependency chain
- node `dependencies` should match ticket-level dependencies
- `parallelizable` should be `true` only for dependency-free tickets in the current baseline

## Troubleshooting

- If a dependent ticket runs too early, inspect whether the dependency ids were declared on the
  ticket and whether they appear in the graph node.
- If ordering looks unstable, compare dependency depth, ticket priority, and ticket id.
- If a planner payload omits `execution_graph`, the engine will rebuild it deterministically from
  the ticket list.
