# Usage

## Run locally

```bash
uv sync --all-extras
uv run maestro init
uv run maestro doctor
uv run maestro plan examples/brief.md
uv run maestro status
```

Use `-v` for progress logs and `-vv` or `--log-level DEBUG` for the most detailed traces:

```bash
uv run maestro -v plan examples/brief.md
uv run maestro -vv plan examples/brief.md
uv run maestro --log-level DEBUG preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
```

In the highest-verbosity modes, `maestro` logs:

- provider request payloads
- provider response payloads
- provider routing and fallback decisions
- orchestrator state transitions
- shell command execution
- preview command execution

## Preview a local target repo

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
```

The preview command writes a preview artifact into `runs/<RUN_ID>/preview_<adapter>.json` and is
the first user-testable surface exposed by the roadmap.

## Test

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```

## Eval

```bash
uv run maestro eval
uv run maestro eval --json-output
```

## UI

```bash
uv run maestro ui
```

Or directly:

```bash
cd ui
npm install
npm run dev
```

## Containerized

```bash
docker compose up --build maestro
docker compose up --build ui
```

## Binary build

```bash
uv run pyinstaller -m maestro.cli.main
```

## Provider switching

Copy `examples/maestro.real-providers.yaml` to `maestro.yaml` and edit role mappings:

```bash
uv run maestro plan examples/brief.md --config maestro.yaml
```

For the bundled OpenAI hello-world example:

```bash
cp .env.example examples/.env
$EDITOR examples/.env
uv run maestro doctor --config examples/maestro.openai.yaml --repo examples/hello_world_cli_game
uv run maestro plan examples/hello_world_cli_game_brief.md --config examples/maestro.openai.yaml --repo examples/hello_world_cli_game
```

## Known limitations

- Real OpenAI planning requires a local `OPENAI_API_KEY`; deterministic evals still use `FakeProvider`.
- The coder role returns validated structured code-change plans; this baseline does not yet apply arbitrary file edits to target repositories.
- Preview environments currently support `noop` and local smoke-command execution, not hosted deployment stacks.
- Git worktree isolation is represented by the tool layer and CLI contracts, but full ticket worktree lifecycle automation is still a follow-on implementation.
