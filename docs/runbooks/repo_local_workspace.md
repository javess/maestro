# Repo-Local Workspace Runbook

## Where Outputs Go

After running `maestro` against a target repo, inspect:

```text
<target-repo>/.maestro/state/<RUN_ID>.json
<target-repo>/.maestro/runs/<RUN_ID>/
```

Examples:

- `/Users/javiersierra/dev/scratch/cli-oxo/.maestro/state/<RUN_ID>.json`
- `/Users/javiersierra/dev/scratch/cli-oxo/.maestro/runs/<RUN_ID>/ceremony_master.json`

## Useful Commands

```bash
maestro status --repo .
maestro resume <RUN_ID> --repo .
maestro preview --repo . --adapter local --command "python game.py --demo"
```

## Legacy Runs

If you inspect an older run id that predates the repo-local move, `status` and `resume` will still
fall back to the legacy central store automatically when needed.
