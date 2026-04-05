# Status

| Step ID | Title | Status | Last Updated | Step File | Commit | Tests / Evals | Next Recommended Step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| STEP-000 | Workflow bootstrap and prompt capture | done | 2026-04-05 10:26 UTC | [STEP-000](steps/STEP-000.md) | `6e1fe7e` | `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-000A` |
| STEP-000A | VS Code workspace bootstrap | done | 2026-04-05 10:49 UTC | [STEP-000A](steps/STEP-000A.md) | `9cfd36b` | JSON validation pass; `pytest` pass; UI build pass | `STEP-001` |
| STEP-000B | Workflow batching policy update | done | 2026-04-05 20:17 UTC | [STEP-000B](steps/STEP-000B.md) | `bc0c49b` | `git diff --check` pass | Follow user-approved batch starting from `STEP-010` |
| STEP-001 | Canonical run graph contracts | done | 2026-04-05 11:02 UTC | [STEP-001](steps/STEP-001.md) | `e0bed4a` | `test_run_graph` pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-002` |
| STEP-002 | Run graph persistence, replay, and resume support | done | 2026-04-05 11:14 UTC | [STEP-002](steps/STEP-002.md) | `441523c` | targeted persistence pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-003` |
| STEP-003 | Evidence bundle contracts and artifact manifest extensions | done | 2026-04-05 11:35 UTC | [STEP-003](steps/STEP-003.md) | `ddcdd03` | targeted schema/storage pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-004` |
| STEP-004 | Evidence bundle generation in the existing flow | done | 2026-04-05 12:05 UTC | [STEP-004](steps/STEP-004.md) | `cae3de4` | targeted evidence pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-005` |
| STEP-005 | Risk scoring engine | done | 2026-04-05 12:31 UTC | [STEP-005](steps/STEP-005.md) | `476082f` | targeted risk pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-006` |
| STEP-006 | Approval gate framework | done | 2026-04-05 13:00 UTC | [STEP-006](steps/STEP-006.md) | `f69655a` | targeted approval pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-007` |
| STEP-007 | Product brief compiler | done | 2026-04-05 13:18 UTC | [STEP-007](steps/STEP-007.md) | `c711fd4` | targeted product-model pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-008` |
| STEP-008 | Assumption tracker | done | 2026-04-05 13:34 UTC | [STEP-008](steps/STEP-008.md) | `6794e5f` | targeted assumption pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-009` |
| STEP-009 | Architecture artifact model | done | 2026-04-05 20:14 UTC | [STEP-009](steps/STEP-009.md) | `82a72f3` | targeted architecture-artifact pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | `STEP-010` |
| STEP-010 | Architecture synthesizer | done | 2026-04-05 21:45 UTC | [STEP-010](steps/STEP-010.md) | pending post-commit recording | targeted synthesis pass; `ruff` pass; `ty` pass; `pytest` pass; `eval` pass; UI build pass | Continue approved batch with `STEP-011` |
| STEP-011 | Backlog graph | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-010 |
| STEP-012 | Repo-aware impact analysis | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-011 |
| STEP-013 | Preview environment abstraction | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-012 |
| STEP-014 | Migration planner | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-013 |
| STEP-015 | Observation-to-backlog loop | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-014 |
| STEP-016 | Archetype pack system | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-015 |
| STEP-017 | Scenario eval library expansion | planned | 2026-04-05 10:14 UTC | - | - | - | Wait for STEP-016 |
| STEP-018 | Local SQL persistence backend | planned | 2026-04-05 11:22 UTC | - | - | - | Wait for STEP-017 completion |

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
