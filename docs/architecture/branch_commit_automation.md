# Branch And Commit Automation

`STEP-024` makes target-repo git output a first-class part of execution instead of leaving repo
mutation as uncommitted working-tree changes only.

## Core behavior

When commit automation is enabled and the target repo is git-backed, `maestro`:

1. creates a dedicated run branch in the target repo
2. syncs approved changes from the isolated workspace into the repo root
3. stages only the changed paths reported by `CodeResult`
4. creates commits according to the active policy pack
5. records commit metadata in artifacts and evidence bundles

The branch name is policy-driven and currently defaults to:

- `maestro/<RUN_ID>`

## Commit modes

`PolicyPack.commit_mode` now controls git output:

- `no_commit`
  - sync approved changes back into the repo without creating local commits
- `commit_on_green`
  - accumulate approved repo changes during the run and create one final commit when the run
    completes successfully
- `checkpoint_commits`
  - create a commit after each approved ticket completes

This keeps commit behavior explicit and resumable instead of burying it in ad hoc CLI flags.

## Safety model

The run branch is only created automatically when the target repo is clean apart from `.maestro/`
runtime metadata. If the repo has unrelated local changes, `maestro` records a
`commit_skipped_dirty_repo` note and leaves commit automation disabled for that run.

That prevents the execution path from silently mixing user edits with generated changes.

## Metadata surfaces

Commit metadata is now typed and propagated through:

- `CodeResult.commit_metadata`
- `EvidenceBundle.commit_metadata`
- per-ticket commit artifacts such as `TICKET-1_commit_1.json`
- final run-level commit artifact `run_commit.json` for `commit_on_green`
- `RunState.base_branch` and `RunState.run_branch`

These surfaces are designed so later approval and UI steps can show the exact branch and commit
created by the execution path.
