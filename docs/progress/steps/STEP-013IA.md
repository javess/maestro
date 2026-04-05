# STEP-013IA

- Step id: `STEP-013IA`
- Title: Worktree isolation
- Status: in_progress
- Objective:
  - Execute tickets in isolated git worktrees and sync approved changes back to the target repo.
- Scope:
  - Expand `GitWorktreeManager` with add/remove helpers.
  - Route ticket implementation and validation through a ticket-specific execution root when the
    target repo is git-backed.
  - Sync changed files back to the target repo after approved completion.
- Non-goals:
  - No parallel ticket execution yet.
  - No provider changes yet.
- Prerequisites:
  - `STEP-013H` complete.
- Implementation plan:
  - Add persistent worktree-path tracking on run state.
  - Execute ticket attempts in worktrees.
  - Sync changed files back on approved completion.
  - Update tests and progress docs.
- Files changed:
  - `src/maestro/core/engine.py`
  - `src/maestro/core/workspace.py`
  - `src/maestro/tools/git.py`
  - `src/maestro/schemas/contracts.py`
  - `tests/test_engine.py`
  - `tests/test_git_tools.py`
  - `README.md`
  - `docs/usage.md`
  - `docs/architecture/worktree_isolation.md`
  - `docs/runbooks/worktree_isolation.md`
  - `docs/testing/test_matrix.md`
  - `docs/evals/eval_matrix.md`
  - `docs/roadmap/design_to_execution_roadmap.md`
  - `docs/progress/status.md`
  - `docs/progress/session_log.md`
  - `docs/progress/decision_ledger.md`
  - `docs/progress/steps/STEP-013IA.md`
- Tests added or updated:
  - Added `tests/test_git_tools.py` for dirty-repo workspace-copy exclusions.
  - Updated `tests/test_engine.py` for approved sync-back from isolated workspaces.
- Evals added or updated:
  - None. Worktree isolation changes execution location, not orchestrator transitions.
- Commands run:
  - `uv run ruff check src/maestro/core/engine.py src/maestro/core/workspace.py src/maestro/tools/git.py tests/test_engine.py tests/test_workspace.py`
  - `uv run ty check`
  - `TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp tests/test_engine.py tests/test_workspace.py`
  - `TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp tests/test_engine.py tests/test_workspace.py tests/test_git_tools.py`
  - `uv run ruff check src tests`
  - `TMPDIR=/var/tmp uv run pytest --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp`
- Results:
  - Git-backed repos now execute ticket implementation and validation in isolated per-ticket
    workspaces under `.maestro/worktrees/`.
  - Approved file changes sync back into the target repo only after the ticket clears review and
    policy gates.
  - Dirty-repo fallback copies now skip cache and dependency directories such as `.venv` and
    `node_modules`.
- Docs updated:
  - Added architecture and runbook docs for worktree isolation.
  - Updated README, usage docs, and progress tracking.
- Decisions made:
  - Split `STEP-013I` into `STEP-013IA` and `STEP-013IB` to isolate filesystem changes from
    concurrency changes.
  - Keep workspace cleanup for a later step so this change can focus on isolated execution and
    sync semantics.
- Known limitations:
  - Parallel execution remains the next split step.
  - Completed ticket workspaces are retained for inspection and are not yet cleaned up
    automatically.
- Next recommended step:
  - `STEP-013IB`
- Commit hash:
  - pending
