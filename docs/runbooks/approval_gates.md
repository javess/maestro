# Approval Gates

## What Exists Today

The repository now supports deterministic approval holds for high-risk work.

When a run reaches a successful automated review but the active policy requires human approval:

- the run stops with `status: awaiting_approval`
- the current state remains `REVIEW`
- the pending `approval_request` is stored in the run state
- the matching evidence bundle includes the same approval request

## Where To Inspect

1. Run `uv run maestro eval --json-output` or `uv run maestro plan --brief examples/brief.md`.
2. Open `runs/state/<RUN_ID>.json`.
3. Inspect:
   - `status`
   - `approval_request`
   - `current_ticket_id`
4. Open the referenced evidence bundle from `artifacts.evidence_bundles`.

## Policy Controls

Approval behavior is configured per policy pack using:

- `approval_mode`
- `approval_risk_level`
- `multi_approval_count`

## Operational Notes

- Approval gating only applies after automated checks and review would otherwise allow completion.
- Approval holds are not escalations.
- Approval requests are deterministic and derived from the active policy and persisted risk score.
- Explicit approval resolution and resume commands are deferred to later roadmap work.
