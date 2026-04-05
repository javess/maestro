# Impact Analysis Runbook

Use this when you need to inspect or debug repo-aware planning and execution context.

## Where To Look

- run artifact: `runs/<RUN_ID>/impact_analysis.json`
- planning payload: `Backlog.impact_analyses`
- execution payload: coder `repo_context.impact_analysis`

## What To Check

- `likely_touched_modules` should reflect the highest-scoring repo areas for the ticket
- `nearby_tests` should point to test files close to those modules
- `hotspots` should surface risky adapter paths when relevant
- `context_slice` should stay small and deterministic

## Fixture Expectations

- Python repos should typically surface `src/...`, `tests/...`, and migration risks when present
- Monorepos should bias toward workspace-level modules like `packages/<name>`
- Build config files such as `pyproject.toml` or `package.json` may appear in `context_slice` or
  `coupled_interfaces`

## Troubleshooting

- If no module match is found, expect a repo-level fallback such as `.`
- If analysis is too broad, inspect the ticket wording and the actual repo file names
- If analysis is too slow, check for ignored directories that should be pruned from the walk
