# Resume Workflow Runbook

Use this runbook at the start of every Codex session:

1. Read `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`.
2. Read `docs/codex/RESUME_PROMPT.md`.
3. Read `AGENTS.md`.
4. Read `docs/roadmap/design_to_execution_roadmap.md`.
5. Read `docs/progress/status.md`.
6. Read the latest session entry in `docs/progress/session_log.md`.
7. Read the most recent unfinished step file in `docs/progress/steps/`, or the latest completed step if none are unfinished.
8. Read `docs/progress/decision_ledger.md`.
9. Inspect `git status --short --branch`.
10. Inspect the most recent test and eval results in repository docs.
11. Determine the next incomplete bounded roadmap step.
12. If the next step is too large, split it first, record the split, and implement only the first substep.
13. Complete one bounded step, update tests/evals/docs/progress, create one atomic commit if green, then stop and request user confirmation.

