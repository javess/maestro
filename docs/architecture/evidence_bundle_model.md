# Evidence Bundle Model

## Purpose

`STEP-003` adds a typed evidence bundle contract for approval and auditability without yet
generating concrete bundles from the execution flow.

This step is intentionally contract-first:

- define the bundle shape
- extend the artifact manifest so bundles are discoverable
- add local storage support for writing bundle artifacts
- defer bundle generation to `STEP-004`

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

## Placeholder Sections

The contract intentionally includes placeholder-first sections so later steps can fill them with
real execution data:

- diff summary
- checks
- policy findings
- rollback notes
- review result

## Storage

[LocalArtifactStore](/Users/javiersierra/dev/maestro/src/maestro/storage/local.py) now exposes
`write_evidence_bundle(...)` to persist bundle JSON and register it in the manifest.

## Follow-On Work

- `STEP-004` will populate evidence bundles from the current implementation/review flow
- later approval and audit steps can consume the bundle contract directly

