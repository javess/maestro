You are Codex resuming work in this repository.

Before changing anything:
1. Read `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`.
2. Read `docs/codex/RESUME_PROMPT.md`.
3. Read `AGENTS.md`.
4. Read `docs/roadmap/design_to_execution_roadmap.md`.
5. Read `docs/progress/status.md`.
6. Read the latest session entry in `docs/progress/session_log.md`.
7. Read the most recent unfinished step file, or the latest completed step file if all current steps are marked done.
8. Read `docs/progress/decision_ledger.md`.
9. Inspect git status.
10. Inspect the most recent test/eval results recorded in docs.

Then:
- determine the next bounded incomplete roadmap step
- if needed, split it and document the split
- implement only that one step
- add/update tests and evals
- update docs and progress files
- create one atomic commit if the step is complete and green
- stop
- output a concise report and request explicit user confirmation before continuing

Never continue to a second roadmap step in the same session.
Never rely on memory outside the repository.

