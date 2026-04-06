# UI Run Console

`STEP-028` turns the frontend into a local operator console backed by a lightweight FastAPI server.

## Design

The UI is intentionally thin:

- the Python server owns run start, doctor, status, and diff-approval actions
- the frontend polls repo-local state rather than keeping a second source of truth
- existing CLI and engine code stay canonical for orchestration behavior

## Current capabilities

The UI can now:

- enter repo, brief, and config paths
- run doctor/readiness checks
- start a plan run from scratch
- poll and list repo-local runs
- inspect run events and artifact paths
- approve, reject, or rerun diff approvals

This satisfies the first real UI-driven execution surface without yet introducing queueing or
multi-worker orchestration.
