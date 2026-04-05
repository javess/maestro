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
- determine whether the user has explicitly authorized a bounded multi-step batch, such as the next
  `N` steps or progress through a named target step
- if needed, split it and document the split
- implement only the approved step range
- add/update tests and evals
- update docs and progress files
- create one atomic commit per completed step if the work is complete and green
- stop
- output a concise report and request explicit user confirmation before continuing past the
  approved batch boundary

Never continue beyond the explicit user-approved batch boundary in the same session.
Never rely on memory outside the repository.
