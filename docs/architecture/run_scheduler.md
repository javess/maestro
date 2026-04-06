# Run Scheduler

`STEP-029` introduces a local scheduler that sits between UI/API run creation and background
execution.

## Responsibilities

- queue newly requested runs
- respect a worker limit
- dispatch queued runs to background workers
- report queue and running state
- allow cancellation of queued work

## Current model

The first implementation is a local in-process scheduler:

- `LocalRunScheduler`
- default worker count: `2`
- queue state is kept in memory
- run state and artifacts remain canonical on disk in `.maestro/`

This is enough to make UI-driven run management explicit before later hosted or shared control
plane work.
