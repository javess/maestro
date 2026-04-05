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
