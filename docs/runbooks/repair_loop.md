# Repair Loop Runbook

Use the repair loop to understand why `maestro` retried a ticket and what evidence was passed into
the next attempt.

## Artifacts

For a revised ticket, look for:

- `TICKET-ID_coder_attempt_N.json`
- `TICKET-ID_checks_N.json`
- `TICKET-ID_reviewer_N.json`
- `TICKET-ID_repair_context_N.json`

The repair-context artifact is the canonical explanation of why the next attempt happened.

## What the coder sees

On retry attempts, the coder payload now includes `repair_context` with:

- failing command outputs
- reviewer issues
- prior summary and notes
- violation codes

Prompt guidance now instructs the coder to treat that context as the authoritative failure evidence
for the next attempt.

## Validation coverage

`STEP-025` is covered by:

- `tests/test_engine.py`
  - repair-context artifact persistence
  - retry payload propagation after a failed check

Quick validation:

```bash
TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp tests/test_engine.py -k repair_context
uv run ruff check src/maestro/schemas/contracts.py src/maestro/core/engine.py prompts/coder.md skills/coder/SKILL.md tests/test_engine.py
uv run ty check
```
