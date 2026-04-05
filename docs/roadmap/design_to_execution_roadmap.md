# Design To Execution Roadmap

## Principles

- Implement one bounded step per session.
- Preserve deterministic orchestration, provider neutrality, repo neutrality, policy-driven behavior, schema validation, evalability, and resumability.
- Split oversized steps before implementation and record the split in `docs/progress/decision_ledger.md`.
- Do not start the next step without explicit user confirmation.

## Planned Steps

| Step ID | Title | Status | Notes |
| --- | --- | --- | --- |
| STEP-000 | Workflow bootstrap and prompt capture | done | Durable control-plane bootstrap |
| STEP-000A | VS Code workspace bootstrap | done | User-requested prerequisite developer workflow setup before STEP-001 |
| STEP-001 | Canonical run graph contracts | done | Typed DAG contracts and validation |
| STEP-002 | Run graph persistence, replay, and resume support | done | Persist and resume canonical run graphs |
| STEP-003 | Evidence bundle contracts and artifact manifest extensions | planned | Approval and audit evidence contracts |
| STEP-004 | Evidence bundle generation in the existing flow | planned | Generate evidence bundles from the current run path |
| STEP-005 | Risk scoring engine | planned | Deterministic policy-driven risk scoring |
| STEP-006 | Approval gate framework | planned | Deterministic approval policy modes |
| STEP-007 | Product brief compiler | planned | Normalized product model from brief input |
| STEP-008 | Assumption tracker | planned | Persisted assumptions and unresolved questions |
| STEP-009 | Architecture artifact model | planned | Typed architecture contracts |
| STEP-010 | Architecture synthesizer | planned | Artifact synthesis from product model and repo discovery |
| STEP-011 | Backlog graph | planned | Dependency-aware execution graph |
| STEP-012 | Repo-aware impact analysis | planned | Deterministic repo-local context slicing |
| STEP-013 | Preview environment abstraction | planned | Generic preview surface with local/noop adapter |
| STEP-014 | Migration planner | planned | Migration artifacts and sensitivity handling |
| STEP-015 | Observation-to-backlog loop | planned | Convert observations into follow-up work |
| STEP-016 | Archetype pack system | planned | Configurable application archetypes |
| STEP-017 | Scenario eval library expansion | planned | Expand eval matrix for new roadmap coverage |
| STEP-018 | Local SQL persistence backend | planned | Add SQLite-first persistence backend with JSON compatibility; consider PostgreSQL later if justified |

## Step Sequencing

1. Complete `STEP-000`, stop, and request confirmation.
2. Complete `STEP-000A`, stop, and request confirmation.
3. Complete `STEP-001`, stop, and request confirmation.
4. Continue one bounded step at a time in roadmap order.
5. Reserve `STEP-018` for the end of the roadmap because the storage model is still evolving and JSON should remain the simpler source of truth until the contracts stabilize.

## Added Future Step

### STEP-018 — Local SQL persistence backend

Objective:
Add a local SQL-backed persistence layer after the core model stabilizes.

Minimum scope:

- add a SQLite-backed persistence implementation first
- preserve compatibility with the existing JSON state and artifact model
- keep JSON as a migration and recovery-friendly format during rollout
- introduce an indexing/query layer for runs, statuses, and resume metadata
- document why PostgreSQL would or would not be introduced later

Acceptance:

- a local SQL backend can persist and query run metadata deterministically
- JSON compatibility and migration behavior are documented and tested
- the storage abstraction remains provider-agnostic and resumable

Tests:

- persistence backend tests
- migration and compatibility tests
- resume and query tests

Docs:

- storage architecture note
- migration runbook
