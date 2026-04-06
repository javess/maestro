# Benchmark Scoring Runbook

Run the benchmark suite with:

```bash
maestro benchmark
maestro benchmark --json-output
```

The benchmark harness copies fixture repos into a local benchmark workspace before running them, so
the source fixtures stay unchanged.

Use the benchmark results to answer:

- which repo shapes complete reliably
- which shapes require retries
- whether new changes improve or degrade delivery quality
