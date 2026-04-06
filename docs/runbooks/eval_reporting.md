# Eval Reporting Runbook

## Human-readable output

```bash
uv run maestro eval
```

This prints:

- a summary table
- per-scenario result rows

## JSON output to terminal

```bash
uv run maestro eval --json-output
```

## JSON output to file

```bash
uv run maestro eval --json-output-path eval-report.json
```

## What to inspect

- `summary.failed` should be `0`
- `summary.total_retries` indicates review-loop churn
- `summary.total_policy_violations` shows how often policies blocked progress
- per-scenario `assertions` explain any mismatches
