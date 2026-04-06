# Design To Execution Roadmap

## Principles

- Default to one bounded step per session.
- If the user explicitly requests a bounded batch, execute only that approved range and stop at the
  batch boundary.
- Preserve deterministic orchestration, provider neutrality, repo neutrality, policy-driven behavior, schema validation, evalability, and resumability.
- Split oversized steps before implementation and record the split in `docs/progress/decision_ledger.md`.
- Do not start work beyond the approved batch boundary without explicit user confirmation.

## Planned Steps

| Step ID | Title | Status | Notes |
| --- | --- | --- | --- |
| STEP-000 | Workflow bootstrap and prompt capture | done | Durable control-plane bootstrap |
| STEP-000A | VS Code workspace bootstrap | done | User-requested prerequisite developer workflow setup before STEP-001 |
| STEP-000C | VS Code settings finalization | done | User-requested follow-up workspace settings commit before STEP-013 |
| STEP-001 | Canonical run graph contracts | done | Typed DAG contracts and validation |
| STEP-002 | Run graph persistence, replay, and resume support | done | Persist and resume canonical run graphs |
| STEP-003 | Evidence bundle contracts and artifact manifest extensions | done | Approval and audit evidence contracts |
| STEP-004 | Evidence bundle generation in the existing flow | done | Generate evidence bundles from the current run path |
| STEP-005 | Risk scoring engine | done | Deterministic policy-driven risk scoring |
| STEP-006 | Approval gate framework | done | Deterministic approval policy modes |
| STEP-007 | Product brief compiler | done | Normalized product model from brief input |
| STEP-008 | Assumption tracker | done | Persisted assumptions and unresolved questions |
| STEP-009 | Architecture artifact model | done | Typed architecture contracts |
| STEP-010 | Architecture synthesizer | done | Artifact synthesis from product model and repo discovery |
| STEP-011 | Backlog graph | done | Dependency-aware execution graph |
| STEP-012 | Repo-aware impact analysis | done | Deterministic repo-local context slicing |
| STEP-012A | OpenAI provider wiring and local env loading | done | User-requested provider runtime integration before STEP-013 |
| STEP-013 | Preview environment abstraction | done | Generic preview surface with local/noop adapter |
| STEP-013A | README operator examples | done | User-requested follow-up docs for global install, repo bootstrap, and CLI game usage |
| STEP-013B | Ready-made OXO brief example | done | User-requested example brief and doc links for the CLI noughts-and-crosses use case |
| STEP-013C | OpenAI schema fallback compatibility fix | superseded | Folded into STEP-013D before commit when the user requested immediate runtime verification and logging |
| STEP-013D | OpenAI runtime verification and logging | done | User-requested live verification plus structured progress logging |
| STEP-013E | Maximum verbosity provider request logging | done | User-requested `-vv` request/response logging and repo guidance update |
| STEP-013F | OpenAI native parsed-model logging fix | done | Tiny prerequisite bugfix discovered during live `-vv` OpenAI verification; serializes parsed Pydantic models safely in debug logs |
| STEP-013G | Repo-local `.maestro` workspace storage | done | User-requested move of runtime state and artifacts into the target repo workspace |
| STEP-013H | Repo mutation execution path | done | Apply coder-produced file operations into target repos with validation-ready context |
| STEP-013I | Worktree isolation and parallel ticket execution | split | Split into `STEP-013IA` and `STEP-013IB` for safer rollout |
| STEP-013IA | Worktree isolation | done | Execute tickets in isolated git worktrees and sync approved changes back to the target repo |
| STEP-013IB | Parallel ticket execution | done | Execute dependency-safe ready tickets concurrently when configured |
| STEP-013J | Multi-provider runtime adapters | done | Wire Gemini and Claude runtime adapters with the same structured/fallback contract style as OpenAI |
| STEP-014 | Migration planner | done | Migration artifacts and sensitivity handling |
| STEP-015 | Observation-to-backlog loop | done | Convert observations into follow-up work |
| STEP-016 | Archetype pack system | done | Configurable application archetypes |
| STEP-017 | Scenario eval library expansion | done | Expand eval matrix for new roadmap coverage |
| STEP-018 | Local SQL persistence backend | planned | Add SQLite-first persistence backend with JSON compatibility; consider PostgreSQL later if justified |
| STEP-018A | Secure credential storage | planned | Add keyring-backed provider credentials alongside env-file support |
| STEP-019 | Prompt refinement and role guidance | done | Strengthen agent prompts and skills with design, implementation, and review guidance |
| STEP-020 | Documentation publishing and onboarding polish | done | Add MkDocs, navigation, API/operator docs, examples, and developer onboarding polish |
| STEP-020A | Documentation artifact cleanup | done | Tiny prerequisite to record the docs lockfile update and ignore generated `site/` output before publication |
| STEP-021 | Public GitHub publication | done | Publish the finished repo to the user’s GitHub account as a public repository |
| STEP-022 | Phase 2 roadmap extension | done | Add the post-publication roadmap for reliable autonomous feature delivery, OSS adoption, and commercial readiness |
| STEP-023 | Patch-based editing engine | planned | Add diff/patch editing alongside whole-file writes for safer repo mutation |
| STEP-024 | Branch and commit automation | planned | Create target-repo branches, checkpoint commits, and commit-on-green policies |
| STEP-025 | Validation-driven repair loop | planned | Retry failed implementations with structured failure context until green or escalated |
| STEP-026 | Diff approval workflow | planned | Add explicit diff approval, rejection, and rerun controls across CLI and UI |
| STEP-027 | Repo support tiers and readiness scoring | planned | Classify repos as supported, experimental, or planning-only with concrete diagnostics |
| STEP-028 | Interactive run console UI | planned | Turn the UI into a real run console for artifacts, diffs, approvals, and logs |
| STEP-029 | Multi-run scheduler and worker pools | planned | Support queued runs, concurrency limits, cancellation, and background workers |
| STEP-030 | Benchmark repos and execution scoring | planned | Measure end-to-end delivery quality across real fixture repos and providers |
| STEP-031 | OSS adoption kit | planned | Add contribution guides, benchmark demos, issue templates, and positioning docs |
| STEP-032 | Commercial control-plane foundation | planned | Define hosted/shared services for teams: org policies, managed secrets, analytics, and governance |

## Step Sequencing

1. Complete `STEP-000`, stop, and request confirmation.
2. Complete `STEP-000A`, stop, and request confirmation.
3. Complete `STEP-001`, stop, and request confirmation.
4. Continue one bounded step at a time in roadmap order unless the user explicitly authorizes a
   bounded batch such as the next `N` steps or progress through a target step.
5. Reserve `STEP-018` for the end of the roadmap because the storage model is still evolving and JSON should remain the simpler source of truth until the contracts stabilize.
6. User-requested roadmap insertions may be added when needed, but they must be documented in the
   roadmap and decision ledger before implementation.

## Product Testability Note

- After completing `STEP-012`, start exposing a user-testable product path in the following bounded
  steps so the framework can be exercised beyond internal tests and evals.

## Added Future Step

### STEP-018 — Local SQL persistence backend

Objective:
Add a local SQL-backed persistence layer after the core model stabilizes.

Minimum scope:

- add a SQLite-backed persistence implementation first
- preserve compatibility with the existing JSON state and artifact model
- keep JSON as a migration and recovery-friendly format during rollout
- introduce an indexing/query layer for runs, statuses, and resume metadata
- document why PostgreSQL would or would not be introduced later

Acceptance:

- a local SQL backend can persist and query run metadata deterministically
- JSON compatibility and migration behavior are documented and tested
- the storage abstraction remains provider-agnostic and resumable

Tests:

- persistence backend tests
- migration and compatibility tests
- resume and query tests

Docs:

- storage architecture note
- migration runbook

## Phase 2: Autonomous Delivery Roadmap

The original roadmap established `maestro` as a deterministic orchestration framework with repo
execution, evals, docs, and publication. The next phase focuses on making it a genuinely useful
autonomous delivery product.

### STEP-023 — Patch-based editing engine

Objective:
Replace the current whole-file-first mutation strategy with a safer diff and patch engine.

Minimum scope:

- add patch operations to the code-change contract
- support hunk-based edits and targeted insert/replace flows
- preserve existing formatting and nearby code when possible
- retain whole-file writes as a fallback

Acceptance:

- target repos can be edited through structured patches instead of only full rewrites
- patch failures are surfaced explicitly and recoverably

### STEP-024 — Branch and commit automation

Objective:
Make target-repo git output a first-class product behavior.

Minimum scope:

- create feature branches in target repos
- support commit modes such as `no_commit`, `commit_on_green`, and `checkpoint_commits`
- emit commit metadata into artifacts and evidence bundles

Acceptance:

- successful runs can leave behind a validated feature branch with local commits
- commit behavior is policy-driven and resumable

### STEP-025 — Validation-driven repair loop

Objective:
Teach the execution path to recover from failed checks, not just stop or escalate immediately.

Minimum scope:

- capture failing command output into structured repair context
- re-invoke implementation with bounded retry policies
- persist each repair attempt and failure cause

Acceptance:

- failed tests and lint checks can trigger a deterministic repair loop
- repair retries remain visible and bounded

### STEP-026 — Diff approval workflow

Objective:
Add operator trust and supervision around generated repo changes.

Minimum scope:

- persist structured diffs for each attempt
- allow approve, reject, rerun, and edit-request flows
- expose approvals in CLI and UI surfaces

Acceptance:

- users can inspect and approve/reject diffs before target-repo commits finalize

### STEP-027 — Repo support tiers and readiness scoring

Objective:
Set realistic expectations about where `maestro` is reliable.

Minimum scope:

- classify repos into support tiers
- add a readiness score based on toolchain, testability, repo structure, and policy fit
- expose concrete blockers and recommendations

Acceptance:

- `maestro doctor` and onboarding flows can say what is supported well versus experimental

### STEP-028 — Interactive run console UI

Objective:
Turn the UI from a shell into an operator-facing run console.

Minimum scope:

- runs list, run detail view, ticket state, diffs, approvals, evidence, and logs
- artifact browsing and replay/resume support
- progress visibility for multi-ticket runs

Acceptance:

- a user can supervise a run from the UI without reading raw JSON files

### STEP-029 — Multi-run scheduler and worker pools

Objective:
Allow multiple repo runs to execute safely in parallel.

Minimum scope:

- queued runs
- worker concurrency controls
- cancellation and retry controls
- persistence and UI visibility for active versus pending runs

Acceptance:

- multiple runs can execute concurrently with deterministic limits and visibility

### STEP-030 — Benchmark repos and execution scoring

Objective:
Measure whether `maestro` is actually getting better at full delivery.

Minimum scope:

- add benchmark repos and benchmark briefs
- score applies-cleanly, tests-pass, retries, diff quality, and review quality
- compare provider performance

Acceptance:

- releases can be evaluated against meaningful end-to-end execution metrics

### STEP-031 — OSS adoption kit

Objective:
Make the project easier to understand, evaluate, and contribute to from outside the core team.

Minimum scope:

- contributor guide
- issue templates
- benchmark demo repos
- positioning docs explaining deterministic orchestration versus agent chat loops

Acceptance:

- a new OSS contributor can evaluate, run, and contribute without private context

### STEP-032 — Commercial control-plane foundation

Objective:
Outline and begin separating the OSS core from a possible hosted team product.

Minimum scope:

- define shared run history, org policy packs, managed secrets, analytics, and governance surfaces
- keep the OSS local engine viable on its own
- document cloud-only versus OSS boundaries clearly

Acceptance:

- the repo has a concrete commercial path without weakening the OSS core proposition
