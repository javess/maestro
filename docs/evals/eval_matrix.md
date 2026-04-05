# Eval Matrix

## Current Deterministic Scenarios

| Scenario | Purpose | Expected Result | Latest Recorded Result |
| --- | --- | --- | --- |
| `planning-flow` | Happy-path orchestration baseline | `DONE` | Passed in STEP-000 |
| `review-loop-escalation` | Reviewer rejection escalates deterministically | `ESCALATE` | Passed in STEP-000 |
| `test-failure-blocks-approval` | Failed checks block completion | `ESCALATE` | Passed in STEP-000 |
| `fallback-provider-behavior` | Provider fallback path succeeds deterministically | `DONE` | Passed in STEP-000 |

## Update Rules

- Add or update eval scenarios whenever workflow behavior, orchestration, approval logic,
  persistence, or provider routing changes.
- Record human-readable and JSON eval results in the current step file and session log.

## STEP-001 Note

- No eval scenarios changed in STEP-001 because the new run-graph layer is contract-only and does not yet alter orchestrator execution.

## STEP-002 Note

- No eval scenarios changed in STEP-002 because persisted run-graph state and resume helpers do not yet change orchestration outcomes.
