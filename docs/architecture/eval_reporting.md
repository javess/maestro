# Eval Reporting

`STEP-017` turns the eval harness into a typed reporting pipeline.

## Report model

- `EvalScenarioResult`
- `EvalSummary`
- `EvalReport`

## Metrics

- scenario count
- passed / failed
- retries
- schema errors
- policy violations
- evidence bundle counts per scenario

## CLI behavior

- `maestro eval` prints a human-readable summary table plus per-scenario rows.
- `maestro eval --json-output` prints the full JSON report.
- `maestro eval --json-output-path <path>` writes the JSON report to disk while preserving the
  human-readable console output path.
