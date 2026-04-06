# OSS Adoption

`maestro` is intended to be understandable and useful without private context from the original
authors.

## What makes the project different

Most agentic coding tools optimize first for conversational autonomy. `maestro` optimizes first for:

- deterministic orchestration
- typed artifacts and explicit state
- repo-local persistence
- policy and approval surfaces
- repeatable evals and benchmarkable behavior

That means the project should feel closer to a delivery control plane than an agent chat wrapper.

## Recommended evaluation path for new contributors

1. Run the local quality gates.
2. Run the deterministic eval suite.
3. Run the benchmark harness.
4. Try the hello-world example.
5. Try the OXO brief against a scratch repo.
6. Inspect the generated `.maestro/` workspace contents.

## Where to contribute first

- repo readiness heuristics
- eval and benchmark scenario coverage
- provider adapter robustness
- UI operator flow polish
- safer repo mutation and diff review
- docs and example quality

## Contribution boundaries

Prefer contributions that strengthen the OSS core:

- local-first execution
- deterministic contracts
- inspectable artifacts
- reproducible tests and evals

Be cautious about changes that would:

- require hosted infrastructure for the main workflow
- move secrets or state out of the repo-local workspace by default
- make the engine provider-specific
- reduce auditability in favor of opaque autonomy
