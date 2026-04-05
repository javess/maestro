# Evidence Bundle Model

## Purpose

`STEP-003` and `STEP-004` establish a typed evidence bundle contract and then wire it into the
current execution flow.

## Contracts

The evidence bundle schema lives in [src/maestro/schemas/contracts.py](/Users/javiersierra/dev/maestro/src/maestro/schemas/contracts.py).

Key types:

- `DiffSummary`
- `RollbackNote`
- `PolicyFinding`
- `EvidenceBundle`

`ArtifactManifest` now has:

- `artifacts`: generic run artifacts
- `evidence_bundles`: explicit references to persisted evidence bundle artifacts

## Populated Sections

Each evidence bundle now records deterministic data from a single implementation and review
attempt:

- diff summary
- checks
- policy findings
- rollback notes
- review result

## Storage

[LocalArtifactStore](/Users/javiersierra/dev/maestro/src/maestro/storage/local.py) now exposes
`write_evidence_bundle(...)` to persist bundle JSON and register it in the manifest.

## Generation Path

[OrchestratorEngine](/Users/javiersierra/dev/maestro/src/maestro/core/engine.py) now emits one
bundle per ticket attempt after review input is available and before the ticket transitions to
`COMPLETE_TICKET`, `REVISE`, or `ESCALATE`.

The bundle builder uses:

- `CodeResult.changed_files` and `CodeResult.summary` for diff context
- `CheckResult` records for validation evidence
- deterministic policy evaluation results
- `ReviewResult` for approval state and findings
- generated rollback guidance when changed files, failed checks, or review rejection are present

## Follow-On Work

- later approval and audit steps can consume the bundle contract directly
- risk scoring and approval gates can treat bundle contents as their evidence input surface
