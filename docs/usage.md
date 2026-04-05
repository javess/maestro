# Usage

## Run locally

```bash
uv sync --all-extras
uv run maestro init
uv run maestro doctor
uv run maestro plan --brief examples/brief.md
uv run maestro status
```

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
uv run maestro plan --brief examples/brief.md --config maestro.yaml
```

## Known limitations

- Real provider adapters expose capabilities and routing contracts but do not yet ship live API client calls.
- The coder role returns validated structured code-change plans; this baseline does not yet apply arbitrary file edits to target repositories.
- Git worktree isolation is represented by the tool layer and CLI contracts, but full ticket worktree lifecycle automation is still a follow-on implementation.

