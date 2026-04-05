# maestro

`maestro` is a deterministic, repo-agnostic multi-agent software delivery framework.

It orchestrates narrow, schema-constrained agents through a deterministic Python state
machine. The baseline includes:

- deterministic orchestrator
- typed schemas and artifact persistence
- evidence bundle emission for implementation and review attempts
- repo adapters for common ecosystems
- provider abstraction with fake and real provider adapters
- CLI, eval harness, tests, CI, container support, and a Material UI dashboard shell
- provider fallback routing and structured output repair paths

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

See `docs/usage.md` for local, container, eval, UI, and binary workflows.
Workflow control-plane and resume state live in `AGENTS.md`, `docs/codex/`,
`docs/roadmap/`, and `docs/progress/`.
VS Code workspace setup lives under `.vscode/` and is described in `docs/runbooks/vscode_setup.md`.

## Tooling

- lint: `uv run ruff check .`
- format: `uv run ruff format .`
- type check: `uv run ty check`
- tests: `uv run pytest`

## Providers

Configure providers in `examples/maestro.example.yaml`. The default test and eval path
uses `FakeProvider` for deterministic execution without secrets.

Provider routing is per role and supports fallbacks:

```yaml
llm:
  reviewer:
    provider: claude
    model: claude-sonnet

fallbacks:
  reviewer:
    - provider: openai
      model: gpt-5
```

## UI

The UI lives in `ui/` and uses React, Vite, TypeScript, and Material UI. It visualizes
run state, policies, ticket status, and artifacts from local JSON data.

Runs now persist evidence bundle artifacts alongside other run outputs. These bundles capture
changed-file summaries, validation checks, policy findings, review outcomes, and rollback
guidance for each ticket attempt.

## Binary packaging

The project includes a `PyInstaller` entry in the build configuration so a standalone
binary can be produced with:

```bash
uv run pyinstaller -m maestro.cli.main
```
