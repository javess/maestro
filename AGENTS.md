# AGENTS

## Repository Purpose

`maestro` is a deterministic, provider-agnostic, repo-agnostic design-to-execution
automation framework. The repository must remain resumable from in-repo state alone.

## Read This Before Working

On every session, read these files in order before making changes:

1. `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`
2. `docs/codex/RESUME_PROMPT.md`
3. `AGENTS.md`
4. `docs/roadmap/design_to_execution_roadmap.md`
5. `docs/progress/status.md`
6. The latest session entry in `docs/progress/session_log.md`
7. The most recent unfinished step file in `docs/progress/steps/`, or the latest completed step if none are unfinished
8. `docs/progress/decision_ledger.md`
9. `git status --short --branch`
10. The most recent test and eval baseline recorded in docs

## Workflow Rules

- Default to one bounded roadmap step per session.
- If the user explicitly requests a bounded multi-step run, execute only the requested range, such
  as the next `N` steps or advancing through a named target step.
- Do not continue past the user-approved batch boundary without explicit confirmation.
- If a roadmap step is too large, split it into smaller substeps, update the roadmap,
  and record the split in the decision ledger before implementing only the first substep.
- Keep the system deterministic, provider-neutral, repo-agnostic, policy-driven,
  schema-validated, evaluable, and resumable.
- Do not silently skip failures. Record them in the step file, session log, and status docs.
- Do not silently rewrite roadmap scope. Any roadmap change must be documented.
- Stop immediately if the repository is unsafe, the step is complete, unexpected tests fail,
  a dependency blocks work, or the next step needs clarification.

## Commit Rules

- One atomic commit per completed step.
- Use a conventional-style commit message that includes the step id.
- Do not commit broken work unless the user explicitly allows it.
- If blocked before completion, update docs and stop without committing unless there is a
  clean, user-approved partial artifact worth preserving.

## Testing Rules

- Every code change requires tests or an explicit documented reason why tests are not applicable.
- For workflow or orchestration changes, update eval coverage when appropriate.
- Record all commands and results in the current step file and `docs/progress/session_log.md`.
- If the baseline is failing, document that before changing code and avoid regressions in touched areas.

## Documentation Rules

- Update repository docs for every completed step so the next session can resume from repo state alone.
- Keep `docs/progress/status.md`, `docs/progress/session_log.md`, the current step file,
  and any affected architecture/runbook/testing/eval docs in sync.
- If prompt instructions change later, append to `docs/codex/PROMPT_CHANGELOG.md`; do not overwrite history.

## Stop Conditions

- The current bounded step is complete and no larger user-approved batch remains.
- The user-approved batch boundary has been reached and more work would exceed it.
- Repository state is unsafe.
- Tests fail unexpectedly.
- A blocked dependency appears.
- A risky refactor would exceed the current bounded step.

## Durable Control-Plane Paths

- `AGENTS.md`
- `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`
- `docs/codex/RESUME_PROMPT.md`
- `docs/codex/PROMPT_CHANGELOG.md`
- `docs/roadmap/design_to_execution_roadmap.md`
- `docs/progress/status.md`
- `docs/progress/session_log.md`
- `docs/progress/decision_ledger.md`
- `docs/progress/steps/`
- `docs/testing/test_matrix.md`
- `docs/evals/eval_matrix.md`
- `docs/architecture/`
- `docs/runbooks/`

## Repo-Specific Commands Known So Far

- Sync dependencies: `uv sync --all-extras`
- Lint: `uv run ruff check .`
- Format check: `uv run ruff format --check .`
- Type check: `uv run ty check`
- Tests: `uv run pytest`
- Evals: `uv run maestro eval --json-output`
- UI build: `cd ui && npm run build`
- VS Code JSON validation: `python3 -m json.tool .vscode/settings.json`
- Local init: `uv run maestro init`
- Doctor: `uv run maestro doctor`
