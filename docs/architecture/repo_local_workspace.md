# Repo-Local Workspace Storage

`STEP-013G` moves runtime state and artifact persistence from the framework repository into the
target repository workspace.

## Runtime Layout

For a target repo at `<target-repo>`, `maestro` now writes runtime outputs to:

```text
<target-repo>/.maestro/state/<RUN_ID>.json
<target-repo>/.maestro/runs/<RUN_ID>/
```

This keeps planning, preview, evidence, and resume state colocated with the repo being operated on.

## Scope

The repo-local workspace is now the default for:

- `maestro init --repo <target-repo>`
- `maestro plan --repo <target-repo>`
- `maestro run-ticket --repo <target-repo>`
- `maestro preview --repo <target-repo>`
- `maestro status --repo <target-repo>`
- `maestro resume <RUN_ID> --repo <target-repo>`

## Compatibility

`status` and `resume` keep backward-compatible fallback reads from the legacy central store under
the `maestro` framework repo:

```text
/Users/javiersierra/dev/maestro/runs/state/<RUN_ID>.json
```

This allows older run ids to remain inspectable while new runs move to the repo-local layout.

## Non-Goals

- Eval harness storage remains framework-local and isolated from target repos.
- This step does not yet introduce SQL-backed indexing or cross-repo workspace discovery.
