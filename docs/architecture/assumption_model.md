# Assumption Model

## Purpose

`STEP-008` adds explicit assumption tracking so product and planning artifacts can distinguish:

- stated facts
- inferred facts
- guesses
- unresolved questions

This keeps uncertainty visible and resumable instead of flattening it into plain strings.

## Contracts

The typed contracts live in [contracts.py](/Users/javiersierra/dev/maestro/src/maestro/schemas/contracts.py):

- `AssumptionKind`
- `AssumptionRecord`

The following artifacts now expose structured assumption data:

- `CompiledBrief`
- `ProductSpec`
- `Backlog`

Each of those includes:

- `assumption_log`
- `unresolved_questions`

`ProductSpec` also keeps the earlier `assumptions` string list for compatibility with current
prompting and provider behavior.

## Deterministic Classification

The classifier in [assumptions.py](/Users/javiersierra/dev/maestro/src/maestro/core/assumptions.py)
uses deterministic rules only:

- explicit prefixes such as `fact:`, `inferred:`, `guess:`, `question:`
- trailing question marks for unresolved questions
- soft heuristics like `likely`, `probably`, `maybe`, or `assume` for guesses
- default fallback to `stated_fact`

## Current Integration

- The brief compiler classifies assumption and question sections into `assumption_log`.
- The fake product-designer path returns structured assumptions and unresolved questions.
- The fake backlog planner carries assumption structures forward from the product spec.

## Follow-On Work

- `STEP-009` and `STEP-010` can use the explicit uncertainty model as architecture-synthesis input.
- Later planner work can prioritize unresolved-question resolution explicitly.
