# Benchmark Demo Repos

This directory documents the public benchmark demo targets used by `maestro`.

The actual fixture repos live under:

- `/Users/javiersierra/dev/maestro/tests/fixtures/python_repo`
- `/Users/javiersierra/dev/maestro/tests/fixtures/node_repo`
- `/Users/javiersierra/dev/maestro/tests/fixtures/broken_repo`

## Run the aggregate harness

```bash
cd /Users/javiersierra/dev/maestro
uv run maestro benchmark
uv run maestro benchmark --json-output
```

## Inspect a single fixture manually

```bash
cd /Users/javiersierra/dev/maestro
uv run maestro doctor --repo tests/fixtures/python_repo
uv run maestro plan examples/brief.md --repo tests/fixtures/python_repo
```

Swap `python_repo` for `node_repo` or `broken_repo` to compare behavior.

## Why these repos matter

- `python_repo` exercises a healthy specialized adapter path
- `node_repo` exercises a second healthy specialized adapter path
- `broken_repo` shows degraded generic handling and lower confidence execution

These fixtures are meant for repeatable regression tracking, not as full product examples.
