# Repo-Aware Impact Analysis

`STEP-012` adds deterministic per-ticket repo impact analysis.

## Contract Surface

The impact contract lives in `src/maestro/schemas/impact.py` as `ImpactAnalysis`.

Planning artifacts now carry:

- `Backlog.impact_analyses`

Each analysis records:

- likely touched modules
- nearby tests
- hotspots
- coupled interfaces
- a focused context slice
- repo-aware notes

## Analysis Inputs

The analysis uses:

- `Ticket`
- `RepoDiscovery`
- repo filesystem heuristics

The implementation lives in `src/maestro/repo/impact.py`.

## Deterministic Heuristics

The baseline analyzer:

- tokenizes the ticket title, description, and acceptance criteria
- scores repo paths against those tokens
- maps matching files into likely modules
- finds nearby tests using common repo-type naming conventions
- surfaces hotspots from adapter risk paths
- records coupled interfaces from repo commands and build configuration files
- assembles a bounded context slice for downstream execution

## Execution Integration

The orchestrator now:

- computes impact analysis after planning
- persists the analysis as an `impact_analysis` artifact
- passes ticket-specific impact analysis into the coder `repo_context`

This keeps the core engine deterministic while making repo-local execution context explicit.

## Current Limitations

- Heuristics are filename- and path-driven rather than semantic code analysis.
- Context slicing is still shallow and bounded.
- Coupling detection does not yet infer call graphs or symbol relationships.
