# Commercial Control Plane

`maestro` keeps the local delivery engine viable on its own. The commercial path builds on top of
that OSS core instead of replacing it.

## OSS core

The open-source product remains responsible for:

- local deterministic orchestration
- repo-local `.maestro/` workspaces
- local UI and scheduler
- local provider setup through env vars or OS keychain
- local benchmarks, evals, and evidence artifacts

## Hosted extension points

The hosted path can add team-level capabilities without weakening the OSS workflow:

- shared run history across repos and machines
- org-wide policy pack registry
- managed secrets service
- cross-repo analytics and benchmark reporting
- governance, approvals, and budget controls

## Current foundation

`STEP-032` adds a typed control-plane config and snapshot surface that exposes:

- organization and project identity
- shared-run-history intent
- policy-pack references
- local versus hosted secret backends
- analytics and governance surfaces
- credential-source visibility for configured providers

This is intentionally a local-first foundation, not a hosted service implementation.
