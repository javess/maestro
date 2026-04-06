# Control Plane Runbook

Inspect the local control-plane snapshot for a repo with:

```bash
maestro control-plane --repo .
maestro control-plane --repo . --json-output
```

Write the default repo-local control-plane config if it does not exist yet:

```bash
maestro control-plane --repo . --write-default
```

This creates:

`<target-repo>/.maestro/control_plane.yaml`

Use the snapshot to answer:

- which provider credentials are currently available through env vars or keyring
- which policy packs are referenced locally
- which capabilities remain OSS-local versus hosted extension points
- what shared-run-history, analytics, and governance surfaces the repo is configured for
