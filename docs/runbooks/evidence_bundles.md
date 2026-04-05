# Evidence Bundles

## What Exists Today

The repository now has a typed evidence bundle contract and manifest references for persisted
bundle artifacts.

Current behavior:

- bundles can be represented and written to disk
- manifests can list bundle artifact references
- bundle generation is not yet wired into the execution path

## Bundle Contents

The contract supports:

- diff summary
- checks
- policy findings
- rollback notes
- review result
- optional metadata

## Operational Guidance

- Treat evidence bundles as audit-oriented run artifacts.
- Do not assume every run currently emits a bundle; generation is a follow-on step.
- Use manifest references rather than ad hoc file scanning once bundle generation is wired in.

