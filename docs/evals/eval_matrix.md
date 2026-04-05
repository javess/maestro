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

## STEP-003 Note

- No eval scenarios changed in STEP-003 because evidence bundle work is contract/storage-only and does not yet change runtime behavior.

## STEP-004 Note

- The deterministic scenario set is unchanged, but eval reporting now includes emitted evidence bundle counts for each scenario.
- Existing scenarios continue to validate both happy-path and escalation flows while making evidence generation visible.

## STEP-005 Note

- No scenario set changes were required in STEP-005 because risk scoring does not yet alter
  orchestration transitions.
- Existing scenarios were rerun to confirm that risk scoring is persisted without changing the
  current happy-path and escalation outcomes.

## STEP-006 Note

- Added `approval-required-flow` to prove deterministic blocking when policy and risk require
  human approval.
- Existing scenarios continue to validate happy-path, escalation, failed-check, fallback, and now
  approval-hold behavior.

## STEP-007 Note

- No scenario set changes were required in STEP-007 because the brief compiler and richer product
  schema do not change current orchestration transitions.
- Existing scenarios were rerun to confirm product-definition normalization preserves current
  deterministic outcomes.

## STEP-008 Note

- No scenario set changes were required in STEP-008 because assumption tracking does not yet alter
  orchestration transitions.
- Existing scenarios were rerun to confirm structured uncertainty persistence preserves current
  deterministic outcomes.

## STEP-009 Note

- No scenario set changes were required in STEP-009 because architecture artifact contracts are
  schema-only and are not consumed by orchestration yet.
- Existing scenarios were rerun to confirm the new contract module does not alter current
  deterministic outcomes.

## STEP-010 Note

- No scenario set changes were required in STEP-010 because architecture synthesis enriches
  planning artifacts without changing the current orchestration state flow.
- Existing scenarios were rerun to confirm synthesized architecture remains attached without
  changing deterministic completion, escalation, or approval-hold outcomes.
