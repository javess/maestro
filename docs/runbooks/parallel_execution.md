# Parallel Execution Runbook

## Enable bounded parallel execution

Set `max_parallel_tickets` in the active policy pack:

```yaml
name: prototype
max_parallel_tickets: 2
```

Then point `maestro` at a config using that policy.

## What runs in parallel

- Only tickets that are ready according to the backlog graph.
- Tickets execute concurrently only during coder, validation, and reviewer work.
- Persistence, evidence writing, and approval/policy decisions remain deterministic and ordered.

## What to inspect after a parallel run

- `<target-repo>/.maestro/state/<RUN_ID>.json`
- `<target-repo>/.maestro/runs/<RUN_ID>/`
- `<target-repo>/.maestro/worktrees/<RUN_ID>/`

Look for:

- multiple `PICK_TICKET` events before the next `NEXT_TICKET`
- one coder/check/reviewer/evidence artifact per ticket
- workspace entries in `ticket_workdirs`

## Current operational guidance

- Keep `max_parallel_tickets` small until prompt quality and provider behavior are stable.
- Use isolated workspaces so parallel tickets do not mutate the repo root directly.
- Prefer prototype or custom policies for experimentation; strict/security-sensitive policies stay
  sequential by default.
