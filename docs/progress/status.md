# Status

| Step ID | Title | Status | Last Updated | Step File | Commit | Tests / Evals | Next Recommended Step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| STEP-000 | Workflow bootstrap and prompt capture | done | 2026-04-05 10:26 UTC | [STEP-000](steps/STEP-000.md) | `6e1fe7e` | `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-000A` |
| STEP-000A | VS Code workspace bootstrap | done | 2026-04-05 10:49 UTC | [STEP-000A](steps/STEP-000A.md) | pending post-commit recording | JSON validation pass; `pytest` pass; UI build pass | Request confirmation before `STEP-001` |
| STEP-001 | Canonical run graph contracts | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-000A completion |
| STEP-002 | Run graph persistence, replay, and resume support | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-001 |
| STEP-003 | Evidence bundle contracts and artifact manifest extensions | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-002 |
| STEP-004 | Evidence bundle generation in the existing flow | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-003 |
| STEP-005 | Risk scoring engine | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-004 |
| STEP-006 | Approval gate framework | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-005 |
| STEP-007 | Product brief compiler | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-006 |
| STEP-008 | Assumption tracker | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-007 |
| STEP-009 | Architecture artifact model | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-008 |
| STEP-010 | Architecture synthesizer | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-009 |
| STEP-011 | Backlog graph | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-010 |
| STEP-012 | Repo-aware impact analysis | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-011 |
| STEP-013 | Preview environment abstraction | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-012 |
| STEP-014 | Migration planner | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-013 |
| STEP-015 | Observation-to-backlog loop | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-014 |
| STEP-016 | Archetype pack system | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-015 |
| STEP-017 | Scenario eval library expansion | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-016 |

## Baseline

- Repository state at session start: clean `main`
- Validation baseline recorded during STEP-000:
  - `uv run ruff check .` passed
  - `uv run ty check` passed
  - `uv run pytest` passed
  - `uv run maestro eval --json-output` passed
  - `cd ui && npm run build` passed

## Notes

- Exact commit hash back-reference cannot be embedded into the same atomic step commit
  without a follow-up amend. The created commit hash is reported in session output and can
  be synchronized in a future metadata-only update if needed.
