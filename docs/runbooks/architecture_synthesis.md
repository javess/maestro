# Architecture Synthesis Runbook

Use this when you need to inspect how `maestro` generated planning-time architecture artifacts.

## Where To Look

- run artifact: `runs/<RUN_ID>/architecture_synthesizer.json`
- planning artifact: `runs/<RUN_ID>/ceremony_master.json`
- in-memory contract: `Backlog.architecture_artifacts`

## What To Expect

The synthesized artifact should contain:

- a `system_context` derived from the normalized product spec
- module boundaries anchored to the repo adapter and orchestration responsibilities
- basic domain entities for product, backlog, and repo context
- stable data flows and API contracts for planning-time orchestration

## Validation Notes

- malformed references are rejected by `ArchitectureArtifacts`
- the fake provider preserves synthesized architecture when returning backlog payloads
- fixture repos should produce deterministic module layouts for their adapter types

## Current Troubleshooting

- If planning artifacts do not contain architecture data, confirm the synthesized artifact exists
  and that `Backlog.architecture_artifacts` is not `null`.
- If a repo-specific expectation is missing, start by checking the selected repo adapter and its
  `repo_type`, commands, and risky paths.
