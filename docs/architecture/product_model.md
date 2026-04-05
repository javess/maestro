# Product Model

## Purpose

`STEP-007` introduces a deterministic brief compiler and a richer normalized `ProductSpec`.

The goal is to make product-definition inputs explicit and resumable before later steps add
assumptions, architecture artifacts, and richer planning graphs.

## Contracts

The primary types live in [contracts.py](/Users/javiersierra/dev/maestro/src/maestro/schemas/contracts.py):

- `CompiledBrief`
- `ProductSpec`

`CompiledBrief` captures deterministic normalization of raw brief text:

- `title_hint`
- `summary_hint`
- `problem_points`
- `target_users`
- `outcomes`
- `scope`
- `non_goals`
- `constraints`
- `risks`
- `assumptions`
- `acceptance_criteria`

`ProductSpec` now includes:

- `problem`
- `target_users`
- `constraints`
- `assumptions`

alongside the earlier summary, outcomes, scope, non-goals, risks, and acceptance criteria.

## Compilation Path

The compiler in [product_brief.py](/Users/javiersierra/dev/maestro/src/maestro/core/product_brief.py)
normalizes raw markdown or plain-text briefs before the product-designer role runs.

Current behavior:

- first-level `#` heading becomes `title_hint`
- recognized `##` sections map into typed fields
- plain-text or preamble content becomes `summary_hint`
- the first preamble paragraph also seeds `problem_points` when no explicit problem section exists

## Current Integration

[OrchestratorEngine](/Users/javiersierra/dev/maestro/src/maestro/core/engine.py) now:

1. compiles raw brief text deterministically
2. persists the compiled brief artifact
3. passes the normalized payload to the product-designer role
4. persists the richer `ProductSpec`

## Follow-On Work

- `STEP-008` will add explicit assumption tracking beyond the current product-model field.
- Later synthesis steps can consume the compiled brief and normalized product spec directly.
