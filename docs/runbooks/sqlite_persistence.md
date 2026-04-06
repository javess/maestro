# SQLite Persistence Runbook

## What gets created

After a repo-local run, expect:

- `<target-repo>/.maestro/state/<RUN_ID>.json`
- `<target-repo>/.maestro/runs/<RUN_ID>/...`
- `<target-repo>/.maestro/maestro.db`

## What the database is for

Use the SQLite file to:

- list runs quickly
- inspect run status without scanning every JSON file
- inspect indexed artifact paths for a run

## Inspect the database manually

```bash
sqlite3 <target-repo>/.maestro/maestro.db '.tables'
sqlite3 <target-repo>/.maestro/maestro.db 'select run_id,status,current_state,updated_at from runs order by updated_at desc limit 10;'
sqlite3 <target-repo>/.maestro/maestro.db 'select run_id,name,kind,path from artifacts order by created_at desc limit 20;'
```

## Recovery model

If `maestro.db` is deleted or corrupted:

- canonical JSON run state and artifact files are still present
- individual runs can still be loaded from JSON
- the index can be rebuilt in a future maintenance step without losing run history

## Current limitation

- The CLI still loads full run JSON for detailed single-run inspection.
- The database currently indexes metadata only; it does not replace JSON payload storage.
