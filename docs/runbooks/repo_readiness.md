# Repo Readiness Runbook

Use `maestro doctor` before running feature delivery on a new repo.

## Command

```bash
maestro doctor --repo .
```

The output now includes:

- `support_tier`
- `readiness_score`
- `blockers`
- `recommendations`

## Interpretation

- `supported`
  - strong baseline for repo mutation and validation
- `experimental`
  - some parts are present, but missing signals or blockers still reduce confidence
- `planning_only`
  - `maestro` can still inspect and plan, but autonomous execution is not yet a safe default

The first version is heuristic and deterministic. It is meant to set expectations and guide setup,
not to replace human judgment.
