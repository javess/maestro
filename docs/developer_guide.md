# Developer Guide

## Repository layout

- `src/maestro/core/`: deterministic orchestration, policies, evidence, risk, migration, observation
- `src/maestro/providers/`: provider interface and adapters
- `src/maestro/repo/`: repo discovery, adapters, impact analysis, context slicing
- `src/maestro/storage/`: JSON state/artifact storage plus SQLite indexing
- `src/maestro/schemas/`: typed contracts
- `prompts/` and `skills/`: runtime role guidance
- `tests/`: unit and integration coverage
- `docs/`: runbooks, architecture notes, roadmap, progress control plane

## Development commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp
TMPDIR=/var/tmp uv run maestro eval --json-output-path /tmp/maestro-eval-report.json
```

## Prompt changes

- edit `prompts/<role>.md` for schema/transport constraints
- edit `skills/<role>/SKILL.md` for durable role judgment guidance
- validate with `tests/test_agents.py`

## Documentation site

Build the docs locally:

```bash
uv run --group docs mkdocs build --strict
uv run --group docs mkdocs serve
```

## Publishing expectations

- keep JSON state canonical
- keep provider-specific logic outside the core engine
- prefer deterministic local logic where possible
- update progress docs for every roadmap change
