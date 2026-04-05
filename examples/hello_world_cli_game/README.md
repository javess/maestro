# Hello World CLI Game

This fixture is the smallest repo-level test target for `maestro`.

## Local checks

```bash
uv run pytest
uv run ruff check .
uv run ty check
```

## Demo preview

```bash
python game.py --demo
```

Expected output:

```text
Welcome to Guess Zero!
Pick a number: 0 or 1.
Demo guess: 0
You win!
```

Use this repo with:

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
uv run maestro plan examples/hello_world_cli_game_brief.md --repo examples/hello_world_cli_game
```
