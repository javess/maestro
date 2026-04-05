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
