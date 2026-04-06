# Branch And Commit Automation Runbook

Use commit automation when you want `maestro` to leave behind a reviewable git branch in the target
repo instead of only modified files.

## Policy settings

Commit automation is controlled by the active policy pack:

- `commit_mode`
  - `no_commit`
  - `commit_on_green`
  - `checkpoint_commits`
- `commit_branch_prefix`
  - defaults to `maestro`

Current shipped defaults:

- `default`, `strict`, `security_sensitive`
  - `no_commit`
- `legacy`
  - `commit_on_green`
- `prototype`
  - `checkpoint_commits`

## What to expect

For a clean git repo:

- `checkpoint_commits`
  - creates `maestro/<RUN_ID>`
  - commits each approved ticket as it completes
- `commit_on_green`
  - creates `maestro/<RUN_ID>`
  - waits until the run completes successfully
  - writes one final run commit

For a dirty git repo:

- `maestro` still executes the run
- commit automation is skipped deliberately
- the state log records `commit_skipped_dirty_repo`

## Validation coverage

`STEP-024` is covered by:

- `tests/test_git_tools.py`
  - branch checkout and path-limited commit helpers
- `tests/test_engine.py`
  - checkpoint commit flow
  - final run commit flow
- `tests/test_evidence.py`
  - evidence bundle propagation of commit metadata

Recommended quick validation:

```bash
TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp tests/test_git_tools.py tests/test_evidence.py tests/test_engine.py
uv run ruff check src/maestro/schemas/contracts.py src/maestro/core/evidence.py src/maestro/core/engine.py src/maestro/tools/git.py policies tests/test_git_tools.py tests/test_evidence.py tests/test_engine.py
uv run ty check
```
