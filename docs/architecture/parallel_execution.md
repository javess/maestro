# Parallel Ticket Execution

`STEP-013IB` adds bounded parallel execution for dependency-safe ticket batches.

## Execution model

- Planning still produces a deterministic `BacklogGraph`.
- The engine selects the next ready batch from ordered graph nodes whose dependencies are already
  complete.
- Batch size is controlled by `PolicyPack.max_parallel_tickets`.
- Ready tickets execute concurrently only inside the attempt phase:
  - coder generation
  - repo mutation in isolated ticket workspaces
  - validation commands
  - reviewer generation
- Artifact persistence, evidence emission, policy enforcement, and state transitions still happen
  on the main thread in deterministic ticket order.

## Why this shape

- Concurrency is useful for independent tickets, but the orchestrator must remain replayable and
  auditable.
- Keeping persistence and transitions ordered avoids hidden races in run state, artifact manifests,
  and approval handling.
- Parallelism therefore accelerates work execution without turning the state machine into an
  event-driven free-for-all.

## Configuration

- `PolicyPack.max_parallel_tickets` defaults to `1`.
- The `prototype` policy currently allows `2` parallel tickets.
- Other shipped policies stay at `1` to preserve conservative behavior.

## Current limitation

- Parallel batches stop at approval holds or escalations before moving on to later tickets.
- Cleanup and resource throttling remain follow-on concerns.
