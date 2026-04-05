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
| STEP-000A | VS Code workspace bootstrap | in_progress | User-requested prerequisite developer workflow setup before STEP-001 |
| STEP-001 | Canonical run graph contracts | planned | Typed DAG contracts and validation |
| STEP-002 | Run graph persistence, replay, and resume support | planned | Persist and resume canonical run graphs |
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

## Step Sequencing

1. Complete `STEP-000`, stop, and request confirmation.
2. Complete `STEP-000A`, stop, and request confirmation.
3. Complete `STEP-001`, stop, and request confirmation.
4. Continue one bounded step at a time in roadmap order.
