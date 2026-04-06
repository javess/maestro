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
- repo mutation through coder-produced file operations applied into the target repo workspace
- anchored patch editing for safer in-place mutation of existing repo files
- git-backed ticket execution in isolated per-ticket workspaces under `<target-repo>/.maestro/worktrees/`
- bounded parallel execution for dependency-safe ready ticket batches when policy allows it
- migration-aware evidence bundles and standalone migration plan artifacts for schema-sensitive work
- observation-driven follow-up proposal artifacts generated from failed checks and review issues
- configurable archetype packs so planning can start from SaaS or API-service defaults
- typed eval reports with summary metrics and optional JSON export
- SQLite-backed run indexing alongside canonical JSON state and artifact storage
- layered prompt plus `SKILL.md` guidance for each specialized agent role

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
uv run maestro -v plan examples/brief.md
uv run maestro run-ticket TICKET-1
uv run maestro review TICKET-1
uv run maestro status
uv run maestro resume <RUN_ID>
uv run maestro eval
uv run maestro creds status openai
uv run maestro doctor
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
uv run maestro ui
```

See `docs/usage.md` for local, container, eval, UI, and binary workflows.
Workflow control-plane and resume state live in `AGENTS.md`, `docs/codex/`,
`docs/roadmap/`, and `docs/progress/`.
VS Code workspace setup lives under `.vscode/` and is described in `docs/runbooks/vscode_setup.md`.
The first user-testable preview path is documented in `docs/runbooks/hello_world_openai.md`.
Runtime plan, state, preview, and evidence artifacts now persist in the target repo under
`.maestro/`. Git-backed repos also execute ticket attempts in isolated per-ticket workspaces
under `.maestro/worktrees/`, syncing approved changes back into the repo root only after review
and policy gates pass.
Repo-local workspaces now also maintain `.maestro/maestro.db` as a SQLite run index for fast run
and artifact metadata queries while keeping JSON files canonical.
Existing files can now be updated through anchored patch hunks as well as whole-file writes, which
reduces blast radius for localized repo edits.

## Install as a global CLI

For local development, the simplest global install path is:

```bash
cd /Users/javiersierra/dev/maestro
uv tool install --editable '.[providers]'
maestro doctor
```

That installs `maestro` as a shell command backed by your local checkout.

If you want a packaged build artifact first, create a wheel and install from it:

```bash
cd /Users/javiersierra/dev/maestro
uv build
uv tool install --from dist/maestro_framework-0.1.0-py3-none-any.whl maestro-framework[providers]
maestro doctor
```

If you want a standalone binary instead of a Python-installed CLI:

```bash
cd /Users/javiersierra/dev/maestro
uv run pyinstaller -m maestro.cli.main
./dist/maestro
```

## Tooling

- lint: `uv run ruff check .`
- format: `uv run ruff format .`
- type check: `uv run ty check`
- tests: `uv run pytest`
- docs: `uv run --group docs mkdocs build --strict`
- progress logs: `uv run maestro -v ...` or `uv run maestro --log-level DEBUG ...`

Parallel batch execution is controlled by `max_parallel_tickets` in the active policy pack.
Shipped policies stay conservative by default except `prototype`, which currently allows `2`.

## Providers

Configure providers in `examples/maestro.example.yaml`. The default test and eval path
uses `FakeProvider` for deterministic execution without secrets.

For local real-provider development, `maestro` loads a `.env` file from the same directory as your
config file and can also resolve provider keys from the OS keychain via `keyring`. Start from
[.env.example](/Users/javiersierra/dev/maestro/.env.example), or store a secure local secret with:

```bash
uv run maestro creds set openai
uv run maestro creds status openai
```

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

The OpenAI, Gemini, and Claude adapters are now runtime-wired. OpenAI prefers native structured
output when possible, Gemini uses SDK JSON-schema generation plus fallback parsing, and Claude uses
text-plus-JSON parsing. Secure local key storage is now supported through the OS keychain, while
shell env vars and `.env` remain the simpler fallback paths.

If `maestro` detects that one of the richer Pydantic schemas is unlikely to fit OpenAI's native
structured-output validator, it now skips that path up front and uses text generation plus JSON
extraction instead. If a schema still slips through and OpenAI rejects it, the runtime keeps the
same fallback as a safety net.

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
cp .env.example examples/.env
uv run maestro plan examples/hello_world_cli_game_brief.md --config examples/maestro.openai.yaml --repo examples/hello_world_cli_game
```

The local preview path above was validated in this repository. The OpenAI-backed plan command
requires your API key and was documented but not executed in this session.

After a run against a target repo, inspect:

- `<target-repo>/.maestro/state/<RUN_ID>.json`
- `<target-repo>/.maestro/runs/<RUN_ID>/`

## New Repo Example

To point `maestro` at a brand-new repo anywhere on your machine:

```bash
mkdir -p ~/dev/scratch/cli-oxo
cd ~/dev/scratch/cli-oxo
git init
cp /Users/javiersierra/dev/maestro/examples/oxo_cli_game_brief.md brief.md
maestro plan brief.md --repo .
```

If you want OpenAI-backed planning for that repo, place an `.env` file next to your config with
`OPENAI_API_KEY=...`, then run:

```bash
cp /Users/javiersierra/dev/maestro/.env.example /Users/javiersierra/dev/maestro/examples/.env
$EDITOR /Users/javiersierra/dev/maestro/examples/.env
maestro doctor --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
maestro plan brief.md --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
```

## CLI Game Example

The current baseline can now materialize repo changes through coder-produced file operations,
though prompt quality and execution isolation continue to improve in later steps. A practical
simple target is a CLI noughts-and-crosses game with:

- player names
- score keeping across rounds
- deterministic demo mode
- `pytest`, `ruff`, and `ty` checks

The shortest path today is:

```bash
mkdir -p ~/dev/scratch/cli-oxo
cd ~/dev/scratch/cli-oxo
git init
cp /Users/javiersierra/dev/maestro/examples/oxo_cli_game_brief.md brief.md
maestro plan brief.md --repo .
```

The ready-made brief already includes:

- a 3x3 board
- two named players
- score tracking between rounds
- a deterministic `--demo` path for preview
- explicit testability requirements

To run the OXO planning path with OpenAI, use this exact setup:

```bash
cp /Users/javiersierra/dev/maestro/.env.example /Users/javiersierra/dev/maestro/examples/.env
$EDITOR /Users/javiersierra/dev/maestro/examples/.env
maestro doctor --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
maestro plan brief.md --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
```

The `.env` file must live in `/Users/javiersierra/dev/maestro/examples/.env` because
`maestro.openai.yaml` lives in `/Users/javiersierra/dev/maestro/examples/` and the current config
loader reads provider keys from that config directory.

Once you have a runnable target repo, you can use the preview surface like this:

```bash
maestro preview --repo . --adapter local --command "python game.py --demo"
```

This repository includes a validated minimal fixture at
`examples/hello_world_cli_game/`. It demonstrates the current product shape: deterministic
planning, artifact generation, local preview execution, and now repo mutation via generated file
operations.

For any target repo you run against, artifacts are stored locally in `.maestro/`:

```text
<target-repo>/.maestro/state/<RUN_ID>.json
<target-repo>/.maestro/runs/<RUN_ID>/
```

The ready-made planning brief for the richer OXO example lives at
`examples/oxo_cli_game_brief.md`.

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
