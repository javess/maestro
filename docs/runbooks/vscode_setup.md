# VS Code Setup

## Workspace Files

The repository includes project-scoped VS Code configuration in `.vscode/`:

- `extensions.json`: recommended extensions for Python, Ruff, debugging, YAML, Docker, and GitHub Actions
- `settings.json`: pytest discovery, Python analysis path, Ruff integration, YAML validation, and workspace exclusions
- `tasks.json`: one-click commands for sync, lint, format check, type check, tests, evals, doctor, init, and UI workflows
- `launch.json`: debug profiles for `maestro` CLI commands and pytest

## Recommended Extensions

- `ms-python.python`
- `ms-python.vscode-pylance`
- `ms-python.debugpy`
- `charliermarsh.ruff`
- `redhat.vscode-yaml`
- `ms-azuretools.vscode-docker`
- `github.vscode-github-actions`

## Notes

- `ty` is integrated through the workspace task `maestro: typecheck`; there is no repo-required dedicated VS Code extension in this setup.
- The Python test explorer uses `pytest` with the repository `tests/` directory.
- The TypeScript SDK is pointed at `ui/node_modules/typescript/lib`, so run `npm install` in `ui/` before relying on TypeScript language features if dependencies are missing.

## Common Commands

- Run default tests: `Tasks: Run Test Task` -> `maestro: test`
- Start the UI dev server: `Tasks: Run Task` -> `ui: dev`
- Debug the CLI eval path: `Run and Debug` -> `Python: maestro eval`
- Debug the current test file: `Run and Debug` -> `Python: pytest current file`

