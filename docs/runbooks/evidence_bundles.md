# Evidence Bundles

## What Exists Today

The repository now emits evidence bundle artifacts during the existing implementation, validate,
and review flow.

Current behavior:

- one bundle is written for each ticket attempt
- bundles are registered in `RunState.artifacts.evidence_bundles`
- bundle files live under `<target-repo>/.maestro/runs/<RUN_ID>/<TICKET_ID>_evidence_<N>.json`

## Bundle Contents

Each emitted bundle can contain:

- diff summary
- checks
- policy findings
- rollback notes
- review result
- optional metadata

## Operational Guidance

- Treat evidence bundles as audit-oriented run artifacts.
- Use manifest references rather than ad hoc file scanning.
- Expect multiple bundles for the same ticket when review or validation loops require retries.
- Inspect `metadata.violations` for the deterministic reasons a ticket moved to revise or escalate.
- Treat rollback notes as generated operational guidance, not as a substitute for future
  migration-aware rollback planning.

## How To Inspect

1. Run `uv run maestro plan --brief examples/brief.md` or `uv run maestro eval`.
2. Open the saved run state in `<target-repo>/.maestro/state/<RUN_ID>.json`.
3. Read `artifacts.evidence_bundles` for the persisted bundle paths.
4. Inspect the referenced JSON bundle files for checks, findings, review status, and rollback
   guidance.
