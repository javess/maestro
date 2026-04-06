# Repair Loop

`STEP-025` formalizes the existing revise path into a deterministic repair loop with explicit
failure context.

## Model

When validation or review fails but retries remain, `maestro` now creates a typed `RepairContext`
containing:

- failing checks and their outputs
- reviewer issues
- prior attempt summary and notes
- the violation list that caused the retry
- the 1-based review cycle

The orchestrator persists that context and passes it back into the next coder invocation through
the structured payload.

## Why

Before this step, retries happened implicitly because the state machine moved from `REVIEW` to
`REVISE`, but the next attempt received no canonical explanation of why the prior attempt failed.

That made retries less reliable and harder to audit.

## Runtime flow

1. coder attempt runs
2. checks and review are persisted
3. policy violations are computed
4. if retries remain, a `RepairContext` artifact is written
5. the next coder invocation receives `repair_context`
6. on success, the repair context is cleared for that ticket

The existing `max_review_cycles` policy remains the retry bound.
