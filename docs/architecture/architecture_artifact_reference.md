# Architecture Artifact Reference

`STEP-009` introduces typed architecture artifacts without changing orchestration behavior yet.
These contracts give later synthesis and planning steps a stable, schema-validated target.

## Artifact Set

The canonical architecture container is `ArchitectureArtifacts` in
`src/maestro/schemas/architecture.py`.

It contains:

- `SystemContext`: system summary, primary user types, external dependencies, and constraints
- `ModuleBoundary`: module id, responsibility, paths, dependencies, and exposed interfaces
- `DomainEntity`: domain objects plus an optional owning module
- `DataFlow`: source module, target module, payloads, and triggers
- `ApiContract`: producer/consumer modules, protocol, request shape, response shape, and invariants
- `StateTransition`: named state-machine transitions relevant to the product or subsystem
- `ArchitectureDecision`: lightweight ADR-style decisions with status and consequences

## Validation Rules

The model remains intentionally narrow. The current validation surface is:

- module ids must be unique
- entity ids must be unique
- data flow ids must be unique
- API contract ids must be unique
- state transition ids must be unique
- architecture decision ids must be unique
- module dependency references must resolve to defined modules
- domain entity owners must resolve to defined modules
- data flow source and target modules must resolve to defined modules
- API contract producer and consumer modules must resolve to defined modules

These checks are enough to reject malformed artifacts now without overcommitting to a future
synthesis strategy.

## Why This Is Separate From `ProductSpec`

`ProductSpec` captures product intent and delivery scope. `ArchitectureArtifacts` captures a
structured design view of the system that later steps can synthesize from product input plus repo
discovery.

Keeping them separate avoids mixing:

- product framing
- implementation planning
- architecture structure

## Current Limitations

- No runtime flow consumes these artifacts yet.
- No synthesized architecture generation path exists until `STEP-010`.
- References are validated only against module ids; richer semantics such as bounded contexts,
  event schemas, or storage topology remain future work.
