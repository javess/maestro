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

- Decision: emit evidence bundles once per ticket attempt, before the state machine decides whether to complete, revise, or escalate.
- Rationale: this preserves audit evidence for failed and revised attempts instead of only the terminal outcome.

- Decision: derive policy findings in evidence bundles from existing deterministic policy checks and review outcomes.
- Rationale: STEP-004 should expose current enforcement results without introducing new risk or approval logic ahead of the roadmap.

- Decision: make risk scoring policy-configurable through explicit weights, thresholds, and sensitive path patterns on `PolicyPack`.
- Rationale: STEP-005 needs policy-driven scores without hardcoding one universal risk profile.

- Decision: persist `RiskScore` in evidence bundles instead of creating a separate artifact stream.
- Rationale: the score is part of the per-attempt audit record and will be consumed by later approval work.
