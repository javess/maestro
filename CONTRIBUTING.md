# Contributing to maestro

Thanks for contributing to `maestro`.

`maestro` is opinionated about determinism, explicit schemas, repo-local persistence, and auditable
automation. Contributions should preserve those properties unless a change is explicitly expanding
the architecture in a documented way.

## Before you start

- Read [README.md](/Users/javiersierra/dev/maestro/README.md).
- Read [AGENTS.md](/Users/javiersierra/dev/maestro/AGENTS.md) for the repo-local implementation
  workflow.
- Read [docs/developer_guide.md](/Users/javiersierra/dev/maestro/docs/developer_guide.md).
- Review the active roadmap in
  [docs/roadmap/design_to_execution_roadmap.md](/Users/javiersierra/dev/maestro/docs/roadmap/design_to_execution_roadmap.md).

## Local setup

```bash
uv sync --all-extras --group docs
uv run ruff check .
uv run ty check
uv run pytest
uv run maestro eval --json-output
cd ui && npm install && npm run build
```

## Contribution principles

- Keep orchestration deterministic.
- Keep provider-specific behavior inside provider adapters.
- Prefer typed contracts before adding orchestration behavior.
- Preserve repo-agnostic and provider-agnostic boundaries.
- Add logging for runtime-facing changes.
- Update docs and progress tracking for any material behavior change.

## Common contribution areas

- New repo adapters or readiness heuristics
- Better prompt and skill guidance
- Provider runtime improvements
- UI/operator console improvements
- Eval scenarios and benchmark coverage
- Safer repo mutation and validation workflows

## Pull request expectations

- Keep changes small and reviewable.
- Include tests for new logic, or document why tests do not apply.
- Update affected docs, especially runbooks and architecture notes.
- Mention any eval or benchmark impact.
- Record known limitations directly in the PR description.

## Working on prompts and agents

- Prompt changes should remain narrow and role-specific.
- Do not move hidden reasoning into prompts that should instead exist as typed state or policy.
- Keep `prompts/` and `skills/` in sync when guidance changes runtime behavior.

## Working on providers

- Do not leak provider-specific schema quirks into core contracts.
- Prefer adapter translation, capability checks, and graceful fallback behavior.
- Add targeted tests for structured output, error normalization, and capability handling.

## Working on the UI

- The UI should expose real run control and visibility, not a decorative dashboard.
- Preserve the existing visual language unless a step explicitly changes the design direction.
- Keep the UI usable for local-first operation without a hosted backend.

## Reproducing the benchmark demos

Start with:

```bash
uv run maestro benchmark
uv run maestro benchmark --json-output
```

Then inspect the demo walkthrough in
[examples/benchmark_demos/README.md](/Users/javiersierra/dev/maestro/examples/benchmark_demos/README.md).

## Questions

If you are unsure whether a change belongs in the OSS core, check the commercial boundary note in
[docs/commercial_control_plane.md](/Users/javiersierra/dev/maestro/docs/commercial_control_plane.md)
and prefer keeping the local engine self-sufficient.
