# Assumption Tracking

## What Exists Today

The repository now persists explicit uncertainty records in product and planning artifacts.

Tracked categories:

- `stated_fact`
- `inferred_fact`
- `guess`
- `unresolved_question`

## Where To Inspect

1. Run `uv run maestro plan --brief examples/brief.md`.
2. Open the saved run directory under `runs/<RUN_ID>/`.
3. Inspect:
   - `product_brief_compiler.json`
   - `product_designer.json`
   - `ceremony_master.json`

## Operational Notes

- The current classifier is deterministic and intentionally narrow.
- Use explicit prefixes in briefs when you want precise assumption classification.
- Unresolved questions are surfaced both in `assumption_log` and `unresolved_questions`.
- Current ticket execution behavior does not change based on assumptions yet; this step only makes
  uncertainty visible and portable.
