# Approval Gate Framework

## Purpose

`STEP-006` adds deterministic human-in-the-loop approval gates without turning the orchestrator
into an LLM-driven decision loop.

The approval gate consumes:

- the active `PolicyPack`
- the per-attempt `RiskScore`
- the already-computed automated validation and review outcome

## Contracts

The typed approval contracts live in
[contracts.py](/Users/javiersierra/dev/maestro/src/maestro/schemas/contracts.py):

- `ApprovalMode`
- `ApprovalRequest`

`RunState` now persists:

- `approval_request`
- `status="awaiting_approval"` when a gate is blocking automatic completion

Evidence bundles also persist the approval request that triggered the hold.

## Modes

Supported policy modes:

- `auto_go`: never require approval
- `review_go`: require one approval at or above the configured risk threshold
- `multi_go`: require `multi_approval_count` approvals at or above the configured risk threshold

## Transition Behavior

The gate is evaluated only after:

- checks pass
- review approves
- no revise or escalation violations remain

If approval is required:

- the run remains at `REVIEW`
- `RunState.status` becomes `awaiting_approval`
- an `ApprovalRequest` is persisted
- the run exits cleanly without completing the ticket

This keeps approval separate from ordinary failure and escalation handling.

## Follow-On Work

- A later step can add explicit approval-resolution commands and continuation flow.
- The current framework already exposes the deterministic request surface required for that work.
