# maestro

`maestro` is a deterministic, repo-agnostic multi-agent software delivery framework.

It orchestrates narrow, schema-constrained agents through a deterministic Python state
machine. The baseline includes:

- deterministic orchestrator
- typed schemas and artifact persistence
- evidence bundle emission for implementation and review attempts
- deterministic policy-driven risk scoring for ticket changes
- deterministic approval gates that can pause high-risk work for human review
- deterministic product brief compilation into a normalized product model
- explicit assumption tracking across product and planning artifacts
- repo adapters for common ecosystems
- provider abstraction with fake and real provider adapters
- CLI, eval harness, tests, CI, container support, and a Material UI dashboard shell
- provider fallback routing and structured output repair paths

## Quick start

```bash
uv sync --all-extras
uv run maestro doctor
uv run pytest
uv run maestro eval
uv run maestro ui
```

## Commands

```bash
uv run maestro init
uv run maestro discover
uv run maestro plan examples/brief.md
uv run maestro run-ticket TICKET-1
uv run maestro review TICKET-1
uv run maestro status
uv run maestro resume <RUN_ID>
uv run maestro eval
uv run maestro doctor
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
uv run maestro ui
```

See `docs/usage.md` for local, container, eval, UI, and binary workflows.
Workflow control-plane and resume state live in `AGENTS.md`, `docs/codex/`,
`docs/roadmap/`, and `docs/progress/`.
VS Code workspace setup lives under `.vscode/` and is described in `docs/runbooks/vscode_setup.md`.
The first user-testable preview path is documented in `docs/runbooks/hello_world_openai.md`.

## Tooling

- lint: `uv run ruff check .`
- format: `uv run ruff format .`
- type check: `uv run ty check`
- tests: `uv run pytest`

## Providers

Configure providers in `examples/maestro.example.yaml`. The default test and eval path
uses `FakeProvider` for deterministic execution without secrets.

For local real-provider development, `maestro` now loads a `.env` file from the same directory as
your config file. Start from [.env.example](/Users/javiersierra/dev/maestro/.env.example), then set
`OPENAI_API_KEY` there before using the OpenAI adapter.

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

The OpenAI adapter is now runtime-wired for text and structured generation. Secure key storage is
still future work; the current supported local-development path is `.env` plus environment
variables.

## Hello World

Use the bundled Python example in `examples/hello_world_cli_game/` for the first end-to-end
framework test:

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
uv run maestro plan examples/hello_world_cli_game_brief.md --repo examples/hello_world_cli_game
```

To switch the same flow to OpenAI-backed planning, create a `.env` file next to
`examples/maestro.openai.yaml`, set `OPENAI_API_KEY`, then run:

```bash
uv run maestro plan examples/hello_world_cli_game_brief.md --config examples/maestro.openai.yaml --repo examples/hello_world_cli_game
```

The local preview path above was validated in this repository. The OpenAI-backed plan command
requires your API key and was documented but not executed in this session.

## UI

The UI lives in `ui/` and uses React, Vite, TypeScript, and Material UI. It visualizes
run state, policies, ticket status, and artifacts from local JSON data.

Runs now persist evidence bundle artifacts alongside other run outputs. These bundles capture
changed-file summaries, validation checks, policy findings, review outcomes, and rollback
guidance for each ticket attempt, along with a deterministic risk score derived from policy and
change context.

When a policy requires human approval, runs stop in an `awaiting_approval` state with a persisted
approval request instead of escalating or silently continuing.

Raw brief text is also normalized through a deterministic compiler before the product-designer role
produces the typed `ProductSpec`.

Assumptions, inferred facts, guesses, and unresolved questions are now persisted explicitly on the
compiled brief, product spec, and backlog artifacts.

## Binary packaging

The project includes a `PyInstaller` entry in the build configuration so a standalone
binary can be produced with:

```bash
uv run pyinstaller -m maestro.cli.main
```
