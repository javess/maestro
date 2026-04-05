# Preview Environment Abstraction

`STEP-013` introduces a narrow preview surface so `maestro` can expose a user-testable path
without committing to a deployment platform too early.

## Goals

- keep preview generation provider-agnostic
- keep preview requests deterministic and schema-validated
- support local smoke execution before hosted preview systems exist
- persist preview artifacts alongside other run artifacts

## Contract

The preview contract lives in `src/maestro/schemas/preview.py` and defines:

- `PreviewRequest` for the repo path, repo metadata, and optional smoke command
- `PreviewArtifact` for the generated preview result
- `PreviewStatus` for `ready`, `failed`, and `placeholder`

The contract is intentionally generic. A preview may expose:

- a local smoke-command result
- a URL
- screenshot paths or URLs
- placeholder notes when no real adapter is available yet

## Adapters

The first adapter set is deliberately small:

- `NoopPreviewAdapter` returns a placeholder artifact
- `LocalPreviewAdapter` executes a local smoke command through the existing shell runner

The factory in `src/maestro/preview/factory.py` keeps adapter selection outside the core engine.

## Persistence

Preview artifacts are written through the existing artifact store as standard JSON artifacts. This
keeps them resumable, inspectable, and compatible with later SQL indexing work.

## Deferred Work

- hosted preview providers
- screenshot capture
- preview lifecycle cleanup
- preview-aware orchestration states
- approval and evidence integration for preview surfaces
