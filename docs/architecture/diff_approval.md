# Diff Approval

`STEP-026` adds an explicit diff-approval gate between successful review and repo finalization.

## Flow

When `PolicyPack.require_diff_approval` is enabled and a ticket has no policy or review
violations, `maestro` now:

1. builds a structured diff artifact from the repo root and the isolated execution workspace
2. persists the diff artifact alongside the other ticket artifacts
3. creates a `DiffApprovalRequest` on the run state
4. stops the run with `status="awaiting_diff_approval"`

At that point no repo sync or commit finalization happens yet.

## Resolution

The operator can then:

- approve
  - sync the approved changes into the target repo
  - perform any configured commit automation
- reject
  - clear the pending diff request
  - persist a repair context containing the rejection comment
- rerun
  - same as reject, but marks the diff request as `rerun_requested`

This keeps diff supervision deterministic and resumable instead of treating approval as an
out-of-band human process.
