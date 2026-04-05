# Architecture

`maestro` separates deterministic orchestration from provider-specific generation.

- `core/`: state machine, policy gates, orchestration services
- `providers/`: provider-neutral interface and adapters
- `repo/`: repository discovery and adapter abstractions
- `agents/`: typed role wrappers around provider calls
- `storage/`: local state and artifact persistence
- `evals/`: deterministic scenario runner
- `ui/`: local Material UI dashboard

