# Risk Scoring

## What Exists Today

The repository now computes a deterministic risk score for each ticket attempt and stores it in
the emitted evidence bundle.

## Where To Look

1. Run `uv run maestro plan --brief examples/brief.md` or `uv run maestro run-ticket TICKET-1`.
2. Open the saved run state in `runs/state/<RUN_ID>.json`.
3. Follow `artifacts.evidence_bundles` to the relevant bundle JSON.
4. Inspect `risk_score` for:
   - `score`
   - `level`
   - `factors`

## What Influences Risk

- Number of changed files
- Protected path changes from the active policy pack
- Repo adapter risky paths
- Dependency file changes
- Migration-related file changes
- Sensitive path patterns
- Sensitive ticket-domain keywords

## Policy Tuning

Risk behavior is controlled through policy YAML fields:

- `risk_weights`
- `risk_thresholds`
- `sensitive_path_patterns`

Changing these values changes the resulting score without changing the core engine code.

## Operational Notes

- The current score is deterministic and synchronous.
- The score is advisory only in this step; it does not yet block or pause execution.
- Approval gating based on this score is deferred to `STEP-006`.
