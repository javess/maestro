# Decision Ledger

## 2026-04-05

- Decision: create a durable repo-local control-plane before any roadmap feature work.
- Rationale: the user explicitly required future sessions to resume from repository state alone.

- Decision: keep STEP-000 documentation-heavy and use baseline validation rather than feature changes.
- Rationale: STEP-000 is a workflow bootstrap step; no product-code changes are required.

- Decision: add `.codex/README.md` as a minimal project-scoped Codex placeholder.
- Rationale: the user allowed `.codex/` if needed; a small placeholder avoids ambiguity without adding hidden workflow state.

- Decision: record commit hash as pending in step-tracking docs for the step-closing commit.
- Rationale: embedding the exact hash into the same atomic commit would require an extra amend due to self-reference, which this workflow avoids.
