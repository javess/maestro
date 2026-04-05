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

- Decision: add `STEP-000A` as a prerequisite developer workflow substep before `STEP-001`.
- Rationale: the user explicitly requested a proper VS Code workspace setup before further roadmap feature work, and the step is bounded, non-invasive, and separate from runtime functionality.

- Decision: keep `STEP-000A` editor-focused and avoid runtime code changes.
- Rationale: the goal is a reviewable workspace setup with tasks, launch configs, test discovery, and extension recommendations, not a behavioral change to the product itself.

- Decision: model `STEP-001` as a bounded DAG contract rather than mirroring runtime loops directly.
- Rationale: the roadmap explicitly calls for an execution DAG, so retry and next-ticket loops are represented as bounded unrolling or graph handoff points instead of cyclic edges.

- Decision: persist the run graph directly inside `RunState` for STEP-002.
- Rationale: this is the smallest compatible way to make saved runs resumable and inspectable without adding a second persistence surface prematurely.

- Decision: keep run-graph fields optional on `RunState`.
- Rationale: older saved state files must continue to load while the persistence surface evolves.

- Decision: add a final roadmap step for a local SQL persistence backend, with SQLite as the default target and PostgreSQL only as a later consideration if justified.
- Rationale: SQL-backed indexing and query support will likely be valuable, but the current model is still evolving, so the migration should happen after the core orchestration, artifact, and approval contracts stabilize.

- Decision: keep `STEP-003` contract-first and avoid generating evidence bundles yet.
- Rationale: generation belongs in `STEP-004`; this step should only stabilize the schema, manifest references, and storage surface.

- Decision: add a dedicated `evidence_bundles` list to `ArtifactManifest`.
- Rationale: bundles are a first-class audit surface and should be discoverable without filtering generic artifact entries.
