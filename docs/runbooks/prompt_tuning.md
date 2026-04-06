# Prompt Tuning Runbook

## Where to edit role behavior

- Runtime contract instructions: `prompts/<role>.md`
- Durable best-practice guidance: `skills/<role>/SKILL.md`

## Editing rule

Keep schema and transport constraints in `prompts/`.
Keep role judgment guidance in `skills/`.

## Validation

After changing prompt or skill content:

```bash
uv run pytest tests/test_agents.py tests/test_fake_provider.py
uv run ruff check prompts skills tests/test_agents.py
```

For larger workflow changes, also rerun:

```bash
TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp
TMPDIR=/var/tmp uv run maestro eval --json-output-path /tmp/maestro-eval-report.json
```

## Current runtime behavior

If `skills/<role>/SKILL.md` exists, it is appended to the prompt payload automatically under the
`ROLE_SKILL:` section before the provider call is made.
