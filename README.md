# maestro

`maestro` is a deterministic, repo-agnostic multi-agent software delivery framework.

It orchestrates narrow, schema-constrained agents through a deterministic Python state
machine. The baseline includes:

- deterministic orchestrator
- typed schemas and artifact persistence
- repo adapters for common ecosystems
- provider abstraction with fake and real provider adapters
- CLI, eval harness, tests, CI, container support, and a Material UI dashboard shell

## Quick start

```bash
uv sync
uv run maestro doctor
uv run pytest
uv run maestro eval
uv run maestro ui
```

## Commands

```bash
uv run maestro init
uv run maestro discover
uv run maestro plan --brief examples/brief.md
uv run maestro run-ticket TICKET-1
uv run maestro review TICKET-1
uv run maestro status
uv run maestro resume <RUN_ID>
uv run maestro eval
uv run maestro doctor
uv run maestro ui
```

## Tooling

- lint: `uv run ruff check .`
- format: `uv run ruff format .`
- type check: `uv run ty check`
- tests: `uv run pytest`

## Providers

Configure providers in `examples/maestro.example.yaml`. The default test and eval path
uses `FakeProvider` for deterministic execution without secrets.

## UI

The UI lives in `ui/` and uses React, Vite, TypeScript, and Material UI. It visualizes
run state, policies, ticket status, and artifacts from local JSON data.

## Binary packaging

The project includes a `PyInstaller` entry in the build configuration so a standalone
binary can be produced with:

```bash
uv run pyinstaller -m maestro.cli.main
```

