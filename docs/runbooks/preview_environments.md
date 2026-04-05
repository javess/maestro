# Preview Environments

`maestro preview` is the first user-testable product surface added after `STEP-012`.

## Supported adapters

- `noop`: returns a placeholder preview artifact without executing anything
- `local`: runs a local smoke command against the target repo and persists the result

## Basic usage

```bash
uv run maestro preview --repo examples/hello_world_cli_game --adapter local --command "python game.py --demo"
```

The command prints:

- `run_id`
- artifact path
- preview payload including smoke command output

The persisted artifact is stored at:

```text
<target-repo>/.maestro/runs/<RUN_ID>/preview_local.json
```

## When to use it

Use the preview command when you want a fast, deterministic validation surface before:

- adding hosted preview environments
- wiring screenshots
- adding product-specific deployment stacks

## Limitations

- no deployed URLs yet
- no browser automation yet
- no screenshot capture yet
- local previews only execute a single smoke command
