# Test Matrix

## Current Baseline

| Area | Command | Purpose | Latest Recorded Result |
| --- | --- | --- | --- |
| Lint | `uv run ruff check .` | Python lint validation | Passed in STEP-000 |
| Type checking | `uv run ty check` | Python type validation | Passed in STEP-000 |
| Unit and integration tests | `uv run pytest` | Backend regression suite | Passed in STEP-000 |
| Eval harness | `uv run maestro eval --json-output` | Deterministic scenario validation | Passed in STEP-000 |
| UI build | `cd ui && npm run build` | Frontend compile validation | Passed in STEP-000 |

## Step-Specific Guidance

- Documentation-only steps: run lightweight validation and record why feature tests were not required.
- Code steps: add or update focused unit tests first, then integration tests and eval scenarios when orchestration changes.
- If baseline failures appear, record them in the current step file and `docs/progress/status.md` before proceeding.

## STEP-000 Note

- No product-code changes were made in STEP-000, so no new tests were added.
- Existing repository validation was rerun to establish a durable baseline for future sessions.

## STEP-000A Note

- VS Code workspace changes are editor configuration only.
- Validate JSON structure and rerun lightweight relevant baseline commands before committing.

## STEP-001 Note

- Added `tests/test_run_graph.py` for run-graph validation, invariants, and serialization.
- Full backend test baseline and UI build were rerun after the contract layer was added.

## STEP-002 Note

- Added `tests/test_run_graph_runtime.py` for graph initialization, advancement, and resume-point helpers.
- Updated `tests/test_storage.py` for graph persistence round-trip and legacy state compatibility.
- Full backend test baseline and UI build were rerun after persistence changes.

## STEP-003 Note

- Updated `tests/test_schemas.py` for evidence bundle contracts and placeholders.
- Updated `tests/test_storage.py` for evidence bundle persistence and manifest references.
- Full backend test baseline and UI build were rerun after artifact contract changes.

## STEP-004 Note

- Added `tests/test_evidence.py` for policy-finding aggregation and bundle content generation.
- Updated `tests/test_engine.py` to assert evidence bundle emission in completed and escalated flows.
- Full backend test baseline and UI build were rerun after runtime artifact generation changes.

## STEP-005 Note

- Added `tests/test_risk.py` for deterministic scoring, migration/protected-path detection, and
  policy-driven score differences.
- Updated `tests/test_evidence.py` and `tests/test_engine.py` to assert persisted risk scores in
  generated evidence bundles.
- Full backend test baseline and UI build were rerun after policy and artifact changes.

## STEP-006 Note

- Updated `tests/test_engine.py` to assert the approval-required hold path and persisted approval
  request state.
- Updated `tests/test_storage.py` to round-trip persisted approval requests in saved run state.
- Updated `tests/test_evidence.py` with approval-request unit coverage.
- Full backend test baseline and UI build were rerun after approval-gate changes.

## STEP-007 Note

- Added `tests/test_product_brief.py` for deterministic markdown and plain-text brief compilation.
- Updated `tests/test_schemas.py` and `tests/test_fake_provider.py` for the richer product model.
- Updated `tests/test_engine.py` to keep the product-definition path covered after compiled-brief integration.
- Full backend test baseline and UI build were rerun after product-model changes.

## STEP-008 Note

- Added `tests/test_assumptions.py` for deterministic assumption classification and unresolved-question extraction.
- Updated `tests/test_product_brief.py`, `tests/test_schemas.py`, and `tests/test_fake_provider.py` for structured assumption and backlog propagation.
- Full backend test baseline and UI build were rerun after uncertainty-model changes.

## STEP-009 Note

- Added `tests/test_architecture_artifacts.py` for architecture artifact validation, reference
  integrity, and serialization round-trips.
- Full backend test baseline and UI build were rerun after introducing the schema-only
  architecture contracts.

## STEP-010 Note

- Added `tests/test_architecture_synthesizer.py` for deterministic synthesis across fixture repos
  and fake-provider planning propagation.
- Updated `tests/test_engine.py` and `tests/test_schemas.py` to cover persisted planning-time
  architecture artifacts.
- Full backend test baseline and UI build were rerun after synthesis integration.

## STEP-011 Note

- Added `tests/test_backlog_graph.py` for graph validation, ordering, and next-ticket selection.
- Updated `tests/test_engine.py` to cover graph-driven multi-ticket execution ordering.
- Full backend test baseline and UI build were rerun after backlog graph integration.

## STEP-012 Note

- Added `tests/test_impact_analysis.py` for deterministic fixture-based repo impact analysis across
  supported repo types.
- Updated `tests/test_engine.py` to assert ticket-specific impact analysis is persisted and passed
  into execution context.
- Full backend test baseline and UI build were rerun after impact-analysis integration.
