# Prompt Changelog

## 2026-04-05

- Version: v1
- Action: initialized prompt persistence
- Notes:
  - Added the master implementation prompt verbatim to `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`.
  - Added the companion resume prompt to `docs/codex/RESUME_PROMPT.md`.
  - Future prompt revisions must append new entries instead of replacing history.

- Version: v2
- Action: updated repo-local execution policy
- Notes:
  - Kept the original master prompt intact as the historical source prompt.
  - Updated `AGENTS.md` and `docs/codex/RESUME_PROMPT.md` so future sessions may execute a
    user-authorized bounded batch, such as the next `N` roadmap steps or progress through a named
    target step.
  - Preserved the requirement to stop at the explicit batch boundary.
