# Commercial Control-Plane Foundation

The goal of `STEP-032` is to separate the OSS runtime from a potential hosted team product without
making the local engine depend on cloud infrastructure.

## Model

The foundation introduces a typed control-plane snapshot with:

- organization and project identity
- shared run history configuration
- org policy pack references
- managed secret backend definitions
- analytics and governance surfaces
- recent local runs
- provider credential-source visibility
- explicit OSS versus hosted capability boundaries

## Persistence

The control-plane config lives at:

`<target-repo>/.maestro/control_plane.yaml`

If that file does not exist, `maestro` derives a safe local-first default.

## Surfaces

- CLI: `maestro control-plane`
- API: `GET /api/control-plane`
- UI: the run console now shows a control-plane summary card

## Why this matters

This gives the project a concrete hosted-product seam:

- OSS users keep a full local workflow
- hosted features can layer on top of typed extension points
- secrets, policy, and analytics boundaries are explicit instead of implied
