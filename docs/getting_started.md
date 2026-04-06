# Getting Started

## Install dependencies

```bash
uv sync --all-extras
```

## Verify the repository

```bash
uv run maestro doctor
uv run pytest
uv run maestro eval
```

## Install as a global editable CLI

```bash
uv tool install --editable '.[providers]'
maestro doctor
```

## First local example

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
uv run maestro plan examples/hello_world_cli_game_brief.md --repo examples/hello_world_cli_game
```

## Secure provider credentials

Use the OS keychain:

```bash
uv run maestro creds set openai
uv run maestro creds status openai
```

Or use `.env` next to the active config file.

## Where outputs go

For a target repo, inspect:

- `<target-repo>/.maestro/state/<RUN_ID>.json`
- `<target-repo>/.maestro/runs/<RUN_ID>/`
- `<target-repo>/.maestro/maestro.db`
