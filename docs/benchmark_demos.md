# Benchmark Demos

The benchmark harness gives new contributors a fast way to inspect how `maestro` behaves across
different repo shapes without needing private repos or provider keys.

## Quick commands

```bash
uv run maestro benchmark
uv run maestro benchmark --json-output
```

## Included demo targets

- `tests/fixtures/python_repo`
- `tests/fixtures/node_repo`
- `tests/fixtures/broken_repo`

Each benchmark scenario copies a fixture into a temporary workspace before running, so the source
fixtures remain unchanged.

## What to look for

- completion status
- retry count
- score trend over time
- whether a specialized adapter or only the generic fallback was used

## Next step

Use the fixture walkthrough in
[examples/benchmark_demos/README.md](/Users/javiersierra/dev/maestro/examples/benchmark_demos/README.md)
if you want to inspect the scenarios individually instead of only through the aggregate report.
