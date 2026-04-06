# Archetype Packs Runbook

## Select an archetype

Add an archetype name to your config:

```yaml
archetype: saas_app
```

## Built-in packs

- `saas_app`
- `api_service`

## Where to inspect it

- `<target-repo>/.maestro/runs/<RUN_ID>/archetype_pack.json`

## Current limitation

- Packs influence planning context only in this step.
- They do not yet rewrite policies or architecture synthesis automatically.
