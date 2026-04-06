# Archetype Packs

`STEP-016` adds configurable archetype packs so planning can start from a known product shape
without hardcoding one global default.

## Current pack types

- `saas_app`
- `api_service`

## What a pack provides

- descriptive metadata
- architecture defaults
- policy defaults
- common work patterns

## Runtime behavior

- `MaestroConfig.archetype` selects a pack by name.
- The selected pack is loaded from `archetypes/<name>.yaml`.
- Planning receives the pack as structured metadata and persists it as an artifact for the run.
