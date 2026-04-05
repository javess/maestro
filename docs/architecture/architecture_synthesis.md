# Architecture Synthesis

`STEP-010` adds the first deterministic architecture synthesis path.

## Input Surface

The synthesizer combines:

- `ProductSpec`
- `RepoDiscovery`

The implementation lives in `src/maestro/core/architecture_synthesizer.py`.

## Output Surface

The synthesizer produces `ArchitectureArtifacts` and attaches them to planning in two places:

- as a standalone persisted artifact named `architecture_synthesizer`
- as `Backlog.architecture_artifacts`

This keeps the synthesized design visible to both artifact inspection and downstream planning.

## Deterministic Baseline Rules

The current synthesis path is intentionally narrow and rule-based:

- create a repo-facing module boundary based on the detected adapter
- create orchestration and quality-gate module boundaries
- add a monorepo workspace-slice module when the repo adapter is `monorepo`
- derive a stable set of domain entities, data flows, API contracts, and state transitions
- emit one ADR-style decision describing the deterministic synthesis baseline

## Why This Is Not Model-Driven Yet

The roadmap requires fake-provider determinism and provider neutrality. Starting with a local
synthesizer gives later steps a stable contract without coupling architecture generation to one LLM
provider or prompt behavior.

Later work can add richer synthesis without replacing the typed output contract.

## Current Limitations

- synthesis is heuristic and intentionally conservative
- repo structure is inferred mostly from adapter type and command surfaces, not deep code analysis
- architecture artifacts influence planning context, but they do not yet drive ticket dependency
  graphs or impact analysis directly
