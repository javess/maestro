# UI Run Console Runbook

Start the UI from the repo root:

```bash
uv sync --all-extras
maestro ui
```

The command now starts:

- a local API on `http://127.0.0.1:8765`
- the Vite UI dev server in `ui/`

## Workflow

1. enter a target repo path
2. enter a brief path
3. optionally enter a config path
4. run doctor to inspect readiness
5. start a plan run
6. watch the run list and selected run detail update as state files change
7. if diff approval is required, use the inline approve/reject/rerun controls

The UI currently reads and controls repo-local `.maestro/` state. It is a local operator console,
not a shared hosted control plane.
