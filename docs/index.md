# maestro

`maestro` is a deterministic, provider-agnostic software delivery framework that turns structured
briefs into planned, auditable implementation work across arbitrary repositories.

## What it does

- discovers repo structure across common stacks
- compiles briefs into normalized product specs
- synthesizes architecture and backlog execution graphs
- applies policy, risk, approval, and review gates deterministically
- persists run state, artifacts, evidence bundles, and metadata in repo-local `.maestro/`
- supports OpenAI, Gemini, Claude, and deterministic fake providers
- exposes both a CLI workflow and a Material UI shell

## Start here

- New user: [Getting Started](getting_started.md)
- Want a runnable example: [Examples](examples.md)
- Need commands: [CLI Reference](reference/cli.md)
- Operating or extending the system: [Developer Guide](developer_guide.md)

## Core storage model

Repo-local runs write:

- `.maestro/state/<RUN_ID>.json`
- `.maestro/runs/<RUN_ID>/...`
- `.maestro/maestro.db`

JSON stays canonical. SQLite provides indexed run and artifact metadata for faster local queries.
