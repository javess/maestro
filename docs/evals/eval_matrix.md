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

## STEP-011 Note

- Added `backlog-graph-ordering` to validate deterministic multi-ticket ordering through the new
  planning graph.
- Existing scenarios continue to validate the current completion, escalation, approval-hold, and
  fallback behaviors alongside the graph-aware ticket selection path.

## STEP-012 Note

- No scenario set changes were required in STEP-012 because impact analysis enriches planning and
  execution context without changing the current orchestration state machine.
- Existing scenarios were rerun to confirm repo-aware context slicing preserves deterministic
  completion, escalation, approval-hold, and graph-ordering behavior.

## STEP-012A Note

- No eval scenario set changes were required in STEP-012A because OpenAI runtime wiring and `.env`
  loading do not change deterministic eval coverage, which continues to use `FakeProvider`.
- Existing scenarios were rerun to confirm the provider-layer changes do not alter current
  deterministic orchestration behavior.

## STEP-013 Note

- No eval scenario set changes were required in STEP-013 because preview generation is exposed
  through a separate CLI surface and does not yet alter the orchestrator state machine.
- Existing scenarios were rerun to confirm the preview abstraction does not change deterministic
  planning, approval, fallback, or backlog-ordering behavior.

## STEP-013D Note

- No scenario set changes were required in STEP-013D because logging and the OpenAI runtime
  fallback fix do not alter deterministic fake-provider eval behavior.
- Existing eval coverage remains valid because the orchestration state machine and fake-provider
  scenarios are unchanged.

## STEP-013E Note

- No eval scenario set changes were required in STEP-013E because the new `-vv` provider
  request/response logging changes observability only.

## STEP-013G Note

- No eval scenario set changes were required in STEP-013G because repo-local `.maestro/` storage
  changes runtime persistence location, not deterministic orchestration outcomes.
- Existing eval runs remain intentionally framework-local and isolated from target repos.

## STEP-013H Note

- No new eval scenario was required for STEP-013H because repo mutation is covered by integration
  tests with deterministic fake providers and does not alter the orchestrator state machine shape.
- Existing deterministic scenarios were preserved while the runtime execution path began applying
  file operations to target repos.

## STEP-013IA Note

- No eval scenario set changes were required in STEP-013IA because worktree isolation changes the
  execution filesystem boundary, not the orchestrator state machine.
- Existing deterministic scenarios were rerun to confirm isolated execution preserves current
  completion, escalation, approval-hold, and graph-ordering outcomes.

## STEP-013IB Note

- No eval scenario set changes were required in STEP-013IB because parallel ticket attempts still
  preserve deterministic ordered persistence and state transitions.
- Existing deterministic scenarios were preserved while integration tests validated actual
  concurrent execution behavior.

## STEP-013J Note

- No eval scenario set changes were required in STEP-013J because deterministic evals remain on
  `FakeProvider`.
- Existing deterministic coverage continues to validate provider routing and fallback behavior,
  while mocked adapter tests cover the new real-provider runtime paths.

## STEP-014 Note

- Added `migration-sensitive-flow` to keep migration planning visible in deterministic eval runs.
- Existing scenarios continue to validate completion, escalation, approval-hold, fallback, graph
  ordering, and now migration-sensitive artifact generation.
