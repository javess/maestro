# Risk Model

## Purpose

`STEP-005` adds a deterministic risk scoring engine that converts ticket and change-set inputs into
a reproducible risk score.

The goal of this layer is to give later approval and orchestration steps a stable policy-driven
signal without introducing provider-specific logic or free-form judgment.

## Contracts

The typed contracts live in [contracts.py](/Users/javiersierra/dev/maestro/src/maestro/schemas/contracts.py):

- `RiskLevel`
- `RiskFactor`
- `RiskScore`

`PolicyPack` now also includes:

- `risk_weights`
- `risk_thresholds`
- `sensitive_path_patterns`

## Inputs

The scoring engine in [risk.py](/Users/javiersierra/dev/maestro/src/maestro/core/risk.py)
computes risk from deterministic inputs only:

- blast radius from changed file count
- policy protected paths
- repo adapter risky paths
- dependency-related files
- migration-related files
- sensitive path patterns
- ticket text that references sensitive domains such as auth or billing

## Scoring Rules

Each triggered factor contributes a configured integer weight. The total score is mapped to a
level using policy thresholds:

- `low`
- `medium`
- `high`
- `critical`

The result is deterministic for identical policy, ticket, repo, and code-result inputs.

## Current Integration

Evidence bundles now persist the computed `risk_score` for each ticket attempt. This keeps the
scoring surface attached to real execution artifacts without introducing approval branching yet.

## Follow-On Work

- `STEP-006` can consume the risk score for deterministic approval gates.
- Later migration and architecture steps can add richer inputs without changing the core scoring
  contract shape.
