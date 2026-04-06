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

- Decision: evaluate approval gates only after the automated path would otherwise complete successfully.
- Rationale: approval holds should not hide revise or escalation causes behind a manual-review requirement.

- Decision: represent approval holds with `RunState.status="awaiting_approval"` plus a persisted `ApprovalRequest`.
- Rationale: this keeps the deterministic state machine intact without inventing a new orchestration state for this bounded step.

- Decision: compile raw brief text deterministically before invoking the product-designer role.
- Rationale: STEP-007 needs a stable, resumable normalization surface that does not depend on provider behavior.

- Decision: expand `ProductSpec` rather than introducing a second final product artifact.
- Rationale: later planning and synthesis steps should consume one canonical normalized product model.

- Decision: classify assumptions with deterministic local rules rather than provider output.
- Rationale: STEP-008 needs resumable, testable uncertainty tracking that does not depend on model behavior.

- Decision: add assumption tracking to `Backlog` now even though planning behavior is unchanged.
- Rationale: later graph and planning steps need structured uncertainty on planning artifacts without another contract migration.

- Decision: introduce architecture artifacts in a dedicated schema module instead of expanding `contracts.py` again.
- Rationale: STEP-009 is a bounded contract step, and a separate module keeps the design surface explicit and easier to evolve before synthesis logic arrives.

- Decision: record a roadmap note that after `STEP-012` the following steps should start exposing a user-testable product path.
- Rationale: the user explicitly wants a practical way to exercise the product once the architecture, graph, and impact-analysis foundations are in place.

- Decision: relax the repo-local execution policy from strictly one step per session to user-directed bounded batches.
- Rationale: the user wants to choose whether a session should stop after one step, advance the next `N` steps, or continue through a named target step while still preserving explicit boundaries and resumability.

- Decision: implement STEP-010 with a deterministic local synthesizer instead of another model-driven role.
- Rationale: the first architecture synthesis path needs fixture-level determinism and provider neutrality before richer synthesis logic is introduced.

- Decision: keep the backlog graph additive to `Backlog` instead of replacing the ticket list.
- Rationale: existing planning and execution code still needs the flat ticket collection, while the graph makes ordering and dependencies explicit for later steps.

- Decision: keep repo-aware impact analysis deterministic and filesystem-driven for the first implementation.
- Rationale: STEP-012 needs fixture-level reproducibility across repo types before introducing deeper semantic analysis.

- Decision: after STEP-012, the next bounded step should start exposing a user-testable product path.
- Rationale: this was recorded earlier as a roadmap note, and the approved batch now reaches that threshold.

- Decision: insert a user-requested `STEP-012A` for OpenAI provider runtime wiring before `STEP-013`.
- Rationale: the user explicitly requested real OpenAI support and local `.env` loading before continuing with the preview/testability roadmap work.

- Decision: use `.env` loading only for local development and defer secure secret storage to a later dedicated step.
- Rationale: provider wiring and secure credential storage are different risk surfaces and should not be bundled into one review step.

- Decision: preserve the outstanding `.vscode/settings.json` change in its own tiny setup commit before `STEP-013`.
- Rationale: the user explicitly requested that the workspace setting change be committed, and isolating it avoids mixing editor setup with preview-runtime work.

- Decision: implement `STEP-013` as a CLI-level preview surface with `noop` and local smoke-command adapters before wiring preview behavior into orchestration.
- Rationale: the roadmap calls for a generic preview abstraction, and a separate CLI entrypoint is the smallest user-testable path that preserves deterministic core orchestration while avoiding early deployment-stack coupling.

- Decision: use the bundled `examples/hello_world_cli_game` fixture as the first documented user test path.
- Rationale: the user explicitly asked for a trivially simple hello-world test run, and a tiny Python CLI game provides a stable preview target and planning example with minimal moving parts.

- Decision: add a small documentation-only `STEP-013A` after preview abstraction.
- Rationale: the user requested concrete operator examples for global CLI installation, fresh repo bootstrap, and a richer CLI game use case, and that follow-up is bounded, reviewable, and does not justify bundling into `STEP-014`.

- Decision: document fresh-repo and CLI-game usage as planning-and-preview workflows, not autonomous repo authoring.
- Rationale: the current product baseline does not yet perform general codebase mutation, so the README must stay accurate about what `maestro` can do today.

- Decision: add a ready-made `examples/oxo_cli_game_brief.md` instead of keeping the OXO example embedded only in README snippets.
- Rationale: the user explicitly wants a reusable version of that brief, and storing it in `examples/` makes the workflow repeatable and easier to reference from docs and future sessions.

- Decision: fall back from OpenAI native structured output to text-plus-JSON parsing when the API rejects a schema as invalid.
- Rationale: some of the current rich Pydantic schemas are stricter or more complex than the OpenAI schema validator accepts, and runtime planning should degrade gracefully instead of failing before model generation starts.

- Decision: fold the uncommitted `STEP-013C` changes into `STEP-013D` before commit.
- Rationale: the user immediately requested live verification and better progress logging before `STEP-013C` was finalized, so the cleanest atomic history is one follow-up commit covering runtime verification plus observability.

- Decision: use the standard library logger with Rich logging output and CLI-controlled verbosity.
- Rationale: it adds no new heavy dependency, works cleanly with Typer, and is sufficient for state transitions, provider routing, fallback behavior, and shell command tracing.

- Decision: use `-vv` and `--log-level DEBUG` to emit full provider request and response payloads.
- Rationale: the user explicitly wants maximum observability for LLM calls, and the highest verbosity tier is the right place to show complete payloads without overwhelming normal runs.

- Decision: update repo guidance to require logging for runtime-facing changes by default.
- Rationale: observability needs to stay part of the implementation standard instead of depending on ad hoc follow-up requests.

- Decision: split a tiny prerequisite `STEP-013F` before the requested repo-local `.maestro/` storage change.
- Rationale: the repository had uncommitted runtime bugfix changes from live OpenAI verification, and the workflow requires resolving that unsafe state in a small atomic step before layering a storage refactor on top.

- Decision: treat OpenAI native parsed-model debug logging as a provider-adapter responsibility rather than constraining provider outputs to raw dicts.
- Rationale: native structured parse results may legitimately be returned as Pydantic model instances, and very-verbose logging must serialize them safely without changing canonical schema handling.

- Decision: insert `STEP-013G` before `STEP-014` for repo-local `.maestro` workspace storage.
- Rationale: the user explicitly wants plan/state artifacts to live with the target repository, and that storage-path move is a bounded product-behavior change that should happen before broader roadmap work resumes.

- Decision: make repo-local `.maestro/` storage the default for runtime CLI commands while keeping eval storage framework-local.
- Rationale: runtime outputs should travel with the operated-on repo, but evals need isolated deterministic storage that does not pollute target repositories.

- Decision: keep `status` and `resume` backward-compatible by falling back to the legacy central state store for older run ids.
- Rationale: existing run ids should remain inspectable without forcing a migration step during this storage-path change.

- Decision: extend `CodeResult` with concrete `file_operations` rather than introducing a second
  execution artifact type.
- Rationale: the coder contract already represents implementation output, so adding file writes and
  deletes there is the smallest way to move from planning-only execution into actual repo mutation.

- Decision: build coder repo context from the impact-analysis context slice plus file contents.
- Rationale: the live execution path needs nearby source content without scanning entire repos or
  passing hidden global state into prompts.

- Decision: split `STEP-013I` into `STEP-013IA` and `STEP-013IB`.
- Rationale: worktree isolation changes the execution filesystem semantics, while parallel ticket
  execution adds concurrency and state-coordination risk; shipping them separately keeps each
  commit reviewable and easier to debug.

- Decision: dirty-repo workspace copies must skip bulky cache and dependency directories such as
  `.venv`, `node_modules`, and local build caches.
- Rationale: isolated execution should preserve source context, but copying local tool caches makes
  the fallback path fragile and wasteful, especially on low-disk developer machines.

- Decision: keep ticket attempt execution concurrent, but persist artifacts, evidence, and
  orchestrator state transitions on the main thread in graph order.
- Rationale: that preserves deterministic replay and auditability while still unlocking meaningful
  speedup for independent tickets.

- Decision: let each provider adapter choose its own structured-output strategy while preserving
  one shared provider interface for the engine.
- Rationale: OpenAI, Gemini, and Claude expose materially different structured-output capabilities,
  so the adapter boundary is the correct place to absorb those differences.

- Decision: represent migration handling as deterministic planning artifacts instead of executing
  framework-specific migration commands in this step.
- Rationale: first-class migration artifacts satisfy auditability and risk requirements while
  keeping the planner generic across repos and stacks.

- Decision: emit observation-derived follow-up proposals as persisted artifacts before wiring them
  back into the live backlog graph.
- Rationale: it keeps the observation loop deterministic and reviewable without silently mutating
  active planning state.

- Decision: start archetype packs as advisory planning inputs rather than hard overrides of policy
  or architecture synthesis.
- Rationale: that keeps the initial pack system generic and low-risk while still making the product
  shape explicit to planning.

- Decision: centralize eval execution into a typed report builder shared by the CLI and tests.
- Rationale: one reporting path keeps metrics, assertions, and output modes consistent and easier
  to extend.

- Decision: harden copy-workspace cleanup in the git tool layer while landing `STEP-017`.
- Rationale: repeated eval runs against the repo-root fixture exposed a stale nested workspace
  deletion failure, and fixing it at the shared git utility boundary is safer than special-casing
  eval behavior.

- Decision: add explicit final publication step `STEP-021` for GitHub release to the user account.
- Rationale: repository publication should be treated as a deliberate end-state action after the
  implementation, docs, storage, security, and polish steps are complete.

- Decision: implement STEP-018 as a SQLite index alongside canonical JSON storage.
- Rationale: SQLite gives fast local run/artifact queries and resumable metadata without forcing a
  risky migration away from the simpler JSON source of truth.

- Decision: implement STEP-018A with OS keychain support via `keyring` while keeping `.env` and
  shell env vars as fallback paths.
- Rationale: this adds a materially safer local secret path without forcing a new remote secret
  manager dependency or rewriting provider setup.

- Decision: make `STEP-019` runtime-effective by concatenating each role prompt with its matching
  `SKILL.md` content.
- Rationale: prompt refinement should actually reach providers at runtime instead of only updating
  parallel documentation files that the agent layer never reads.

- Decision: keep STEP-020 documentation publishing markdown-first with MkDocs Material and a static
  nav tree instead of introducing auto-generated API-reference plugins.
- Rationale: the repo already has extensive hand-authored architecture and runbook material, and a
  static site is the lowest-risk way to make it publishable on GitHub Pages now.

- Decision: split a tiny `STEP-020A` cleanup before publication.
- Rationale: adding MkDocs introduced a legitimate `uv.lock` update and a generated `site/`
  directory; publishing should happen from a clean repo with lockfile changes captured and build
  artifacts ignored.

- Decision: extend the roadmap after `STEP-021` with a second phase focused on real autonomous
  feature delivery, OSS adoption, and commercial readiness.
- Rationale: the published repo is now a strong framework baseline, but the highest-value next work
  is execution reliability, git output, operator trust, UI supervision, benchmarks, and a clearer
  OSS/commercial split.

- Decision: make full UI-driven execution explicit in Phase 2 rather than leaving it implicit under
  the generic UI step.
- Rationale: the user wants the product operable from the UI from scratch, including starting runs,
  viewing progress, and controlling approvals/retries, so the roadmap should state that clearly.

- Decision: extend repo mutation with anchored patch hunks inside the existing `CodeResult`
  contract instead of introducing a second patch-specific artifact type.
- Rationale: patch editing is the smallest compatible way to improve mutation safety for existing
  files while preserving current execution, evidence, and persistence flows.

- Decision: create and commit onto a dedicated run branch in the target repo instead of trying to
  preserve detached worktree commits.
- Rationale: the target repo is the operator’s durable working copy, so branch visibility and local
  commit history need to exist there rather than only inside isolated execution workspaces.

- Decision: build the repair loop on top of the existing `REVISE` transition instead of adding a
  second retry state.
- Rationale: the state machine already models bounded retries correctly; what was missing was typed
  repair evidence, not another transition.

- Decision: implement diff approval as a separate hold before repo sync and commit finalization.
- Rationale: users need to inspect the generated change set before it lands in the target repo, so
  diff approval must pause before finalization rather than only annotating already-applied changes.
