# Examples

## Hello world CLI game

Preview and plan against the bundled example:

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
uv run maestro plan examples/hello_world_cli_game_brief.md --repo examples/hello_world_cli_game
```

## OXO / noughts-and-crosses brief

Bootstrap a fresh repo and use the ready-made brief:

```bash
mkdir -p ~/dev/scratch/cli-oxo
cd ~/dev/scratch/cli-oxo
git init
cp /Users/javiersierra/dev/maestro/examples/oxo_cli_game_brief.md brief.md
maestro plan brief.md --repo .
```

To use OpenAI-backed planning:

```bash
cp /Users/javiersierra/dev/maestro/.env.example /Users/javiersierra/dev/maestro/examples/.env
maestro doctor --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
maestro plan brief.md --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
```

## Deterministic eval workflow

```bash
uv run maestro eval
uv run maestro eval --json-output-path eval-report.json
```
