# Hello World OpenAI Run

This is the simplest supported manual test path for `maestro` after `STEP-013`.

## What it demonstrates

- repo discovery against a tiny Python repo
- local preview generation through a deterministic smoke command
- planning against the same repo with either the fake provider or OpenAI
- persisted run artifacts under the target repo's `.maestro/`

## Files involved

- repo: `examples/hello_world_cli_game/`
- brief: `examples/hello_world_cli_game_brief.md`
- richer planning brief: `examples/oxo_cli_game_brief.md`
- OpenAI config: `examples/maestro.openai.yaml`

## 1. Install project dependencies

```bash
uv sync --all-extras
```

## 2. Validate the example repo itself

```bash
cd examples/hello_world_cli_game
uv run pytest
uv run ruff check .
uv run ty check
cd ../..
```

## 3. Run a deterministic local preview

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
```

Expected smoke output:

```text
Welcome to Guess Zero!
Pick a number: 0 or 1.
Demo guess: 0
You win!
```

## 4. Run the planning flow without secrets

```bash
uv run maestro plan examples/hello_world_cli_game_brief.md --repo examples/hello_world_cli_game
```

This uses the default fake-provider config and should complete deterministically.

## Optional: use the ready-made OXO brief

If you want a slightly richer planning target than the bundled hello-world fixture, use:

```bash
uv run maestro plan examples/oxo_cli_game_brief.md --repo examples/hello_world_cli_game
```

Or copy that brief into a fresh repo:

```bash
mkdir -p ~/dev/scratch/cli-oxo
cd ~/dev/scratch/cli-oxo
git init
cp /Users/javiersierra/dev/maestro/examples/oxo_cli_game_brief.md brief.md
maestro plan brief.md --repo .
```

## 5. Switch the same planning flow to OpenAI

The current config loader reads `.env` from the same directory as the config file. For the bundled
OpenAI config, that means the env file path is:

```text
/Users/javiersierra/dev/maestro/examples/.env
```

Create it from the repo root:

```bash
cp .env.example examples/.env
```

Edit `examples/.env` and set:

```text
OPENAI_API_KEY=your_key_here
```

Then run:

```bash
uv run maestro -v doctor --config examples/maestro.openai.yaml --repo examples/hello_world_cli_game
uv run maestro -v plan examples/hello_world_cli_game_brief.md --config examples/maestro.openai.yaml --repo examples/hello_world_cli_game
```

If `maestro` detects that a schema is not a good fit for OpenAI native structured output, it skips
that API path and goes straight to plain text generation plus JSON extraction. If a schema still
gets sent to the native path and OpenAI rejects it, the runtime keeps the same fallback as a safety
net. You should be able to rerun the same command without changing the config.

Useful log lines in `-v` mode include:

- `provider_attempt`
- `openai_generate_structured_native`
- `openai_native_schema_skipped_incompatible`
- `openai_native_schema_rejected`
- `openai_generate_structured_fallback`
- `state_transition`

In `-vv` or `--log-level DEBUG`, `maestro` also logs the full provider request and response
payloads through `provider_request` and `provider_response`.

## 6. OpenAI setup for the ready-made OXO brief

From a fresh target repo:

```bash
mkdir -p ~/dev/scratch/cli-oxo
cd ~/dev/scratch/cli-oxo
git init
cp /Users/javiersierra/dev/maestro/examples/oxo_cli_game_brief.md brief.md
cp /Users/javiersierra/dev/maestro/.env.example /Users/javiersierra/dev/maestro/examples/.env
$EDITOR /Users/javiersierra/dev/maestro/examples/.env
uv run --directory /Users/javiersierra/dev/maestro maestro -v doctor --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
uv run --directory /Users/javiersierra/dev/maestro maestro -v plan brief.md --config /Users/javiersierra/dev/maestro/examples/maestro.openai.yaml --repo .
```

That sequence gives you:

- the reusable OXO brief copied into your new repo
- the OpenAI key loaded from the `examples/.env` file beside the config
- a config validation check before the planning run
- automatic fallback to text+JSON parsing if OpenAI rejects a native structured schema
- repo-local artifacts and run state under `.maestro/`

## What was validated in this step

Validated in-repo during `STEP-013`:

- the local preview command
- deterministic planning with the fake provider
- the example repo's `pytest`, `ruff`, and `ty` commands

Not validated in-repo during `STEP-013`:

- the live OpenAI plan command, because it depends on your local API key and account access

## Where to look after a run

- run state: `<target-repo>/.maestro/state/<RUN_ID>.json`
- preview artifact: `<target-repo>/.maestro/runs/<RUN_ID>/preview_local.json`
- planner and evidence artifacts: `<target-repo>/.maestro/runs/<RUN_ID>/`
