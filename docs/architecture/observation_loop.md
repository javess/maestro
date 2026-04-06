# Observation-to-Backlog Loop

`STEP-015` closes the loop between execution signals and future planning work.

## Observation sources

- failed checks
- reviewer issues
- future user feedback or runtime signals

## Compiler behavior

- Observations are normalized into a typed `ObservationCompilation`.
- Each observation becomes a deterministic follow-up proposal with:
  - stable ids
  - title and description
  - priority derived from severity
  - basic acceptance criteria

## Runtime integration

- When checks fail or reviewer issues are present, the engine now persists:
  - `<ticket_id>_observation_followups_<review_cycle>.json`
- This keeps follow-up work attached to the originating run artifacts instead of living as an
  undocumented side effect.
