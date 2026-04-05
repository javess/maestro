# Product Brief Compiler

## What Exists Today

The repository now normalizes raw brief text before product-definition planning.

Each run writes:

- a compiled brief artifact
- a richer `ProductSpec` artifact

## Where To Inspect

1. Run `uv run maestro plan --brief examples/brief.md`.
2. Open the saved run directory under `runs/<RUN_ID>/`.
3. Inspect:
   - `product_brief_compiler.json`
   - `product_designer.json`

## Supported Input Shape

The compiler handles:

- plain-text briefs
- markdown briefs with `#` title and `##` section headings

Recognized section headings include:

- `Problem`
- `Users`
- `Target Users`
- `Outcomes`
- `Scope`
- `Non-Goals`
- `Constraints`
- `Risks`
- `Assumptions`
- `Acceptance Criteria`

## Operational Notes

- The compiler is deterministic and does not depend on provider behavior.
- Missing sections remain empty instead of being inferred by hidden state.
- The product-designer role still owns the final normalized `ProductSpec`, but it now receives a
  stable structured brief payload instead of raw text only.
