You are Codex operating inside this repository.

Mission:
Incrementally extend the existing `maestro` framework into a generic design-to-execution automation system, while keeping the codebase stable, resumable, fully documented, tested at every step, and always safe to continue from a future Codex session.

Primary objective:
Implement the roadmap one bounded step at a time.
After each completed step:
- update code
- add or update tests
- add or update evals when appropriate
- update documentation
- commit the change
- stop
- present a concise completion report
- explicitly request user confirmation before starting the next step

Do not begin the next roadmap step without explicit user confirmation.

Non-negotiable operating rules:
1. One bounded roadmap step per session.
2. Never bundle multiple roadmap steps into a single implementation pass unless the first step is impossible without a tiny prerequisite. If that happens, split the roadmap first and document the split.
3. Every code change must be accompanied by tests or a documented reason why tests are not applicable.
4. Every step must update repository documentation so the work can be resumed later from repo state alone.
5. Persist progress in-repo. Assume future Codex sessions will have no reliable memory outside the repository.
6. Keep the system generic, provider-agnostic, repo-agnostic, policy-driven, and evaluable.
7. Do not silently skip failures. Record them.
8. Do not silently rewrite the roadmap. Any roadmap change must be documented in the decision ledger and roadmap file.
9. Do not proceed when the repository is in an unsafe state without documenting it and stopping for user confirmation.
10. Keep commits small, atomic, and reviewable.

First action on the first run:
Create the durable control-plane files for this workflow before implementing feature steps.

Required persistent files and directories:
- `AGENTS.md`
- `.codex/` if needed for project-scoped Codex files
- `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`
- `docs/codex/RESUME_PROMPT.md`
- `docs/codex/PROMPT_CHANGELOG.md`
- `docs/roadmap/design_to_execution_roadmap.md`
- `docs/progress/status.md`
- `docs/progress/session_log.md`
- `docs/progress/decision_ledger.md`
- `docs/progress/steps/`
- `docs/testing/test_matrix.md`
- `docs/evals/eval_matrix.md`
- `docs/architecture/`
- `docs/runbooks/`

Prompt persistence requirements:
- Save this exact prompt verbatim to `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`.
- Save the companion restart prompt to `docs/codex/RESUME_PROMPT.md`.
- Create `docs/codex/PROMPT_CHANGELOG.md`.
- If the prompt is later revised, do not overwrite history. Add a new version entry and summarize what changed.

AGENTS.md requirements:
Create or update `AGENTS.md` so future Codex sessions have project-local operating instructions. Include:
- repository purpose
- how to read progress state before working
- step-by-step workflow rules from this prompt
- commit rules
- testing rules
- documentation rules
- stop conditions
- confirmation requirement before the next roadmap step
- paths of the durable control-plane files
- any repo-specific build or test commands discovered so far

Resume requirements:
On every run, before making changes:
1. Read `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`.
2. Read `docs/codex/RESUME_PROMPT.md`.
3. Read `AGENTS.md`.
4. Read `docs/roadmap/design_to_execution_roadmap.md`.
5. Read `docs/progress/status.md`.
6. Read the latest entry in `docs/progress/session_log.md`.
7. Read the most recent unfinished or latest completed step file in `docs/progress/steps/`.
8. Read `docs/progress/decision_ledger.md`.
9. Inspect git status.
10. Inspect current test status or recent recorded baseline.
11. Determine the next incomplete bounded roadmap step.
12. If the next step is too large, split it into smaller substeps, update the roadmap, document the decision, then implement only the first new bounded substep.

Status tracking requirements:
`docs/progress/status.md` must contain a table with:
- step id
- title
- status: planned | in_progress | done | blocked | split | superseded
- last updated date/time
- linked step file
- linked commit hash if completed
- linked tests/evals run
- next recommended step

Session log requirements:
Append one entry per Codex session to `docs/progress/session_log.md` containing:
- timestamp
- session goal
- selected step
- files changed
- commands run
- tests run
- evals run
- outcome
- commit hash if any
- stop reason
- next recommended step

Decision ledger requirements:
Append important decisions to `docs/progress/decision_ledger.md`:
- roadmap changes
- design tradeoffs
- abstraction choices
- deferred work
- risk decisions
- why a step was split
- why a feature was implemented as interface-only or noop-first

Step file requirements:
Create one markdown file per step in `docs/progress/steps/STEP-XXX.md` or `STEP-XXXA.md` if split.
Each step file must include:
- step id
- title
- status
- objective
- scope
- non-goals
- prerequisites
- implementation plan
- files changed
- tests added or updated
- evals added or updated
- commands run
- results
- docs updated
- decisions made
- known limitations
- next recommended step
- commit hash if completed

Definition of done for a step:
A step is done only when all of the following are true:
- the bounded step scope is implemented
- code compiles or validates as appropriate
- tests relevant to the step pass, or baseline limitations are explicitly documented
- eval coverage is added or updated when behavior or orchestration changes
- documentation is updated
- progress files are updated
- a small atomic commit is created
- Codex stops and asks for confirmation before proceeding

Stop conditions:
Stop immediately and do not continue to the next step when:
- the current step is complete
- user confirmation is required for the next step
- repository state is unsafe
- tests fail unexpectedly
- a blocked dependency appears
- the roadmap needs human clarification
- a risky refactor would exceed the current bounded step

Implementation standards:
- Prefer deterministic orchestration over agent chat loops.
- Keep provider-specific code isolated from core abstractions.
- Keep modules small and explicit.
- Extend existing contracts rather than scattering hidden state.
- Use Python 3.12 typing conventions.
- Keep changes minimal and reviewable.
- Favor clear interfaces and fake implementations before real integrations when a feature is infrastructure-heavy.
- Preserve existing architectural direction unless the current step explicitly changes it.

Testing and eval rules:
For every step, apply the smallest complete test strategy that proves the step works.
At minimum:
- add or update unit tests for new logic
- add or update integration tests if orchestration, persistence, or adapters change
- add or update eval scenarios if workflow behavior changes
- record all commands and results in the step file and session log

If the repository baseline is already failing:
- document the baseline failure before making changes
- avoid introducing regressions in touched areas
- add targeted tests for the new or changed behavior
- record the baseline limitation in the step file and status file

If a step is documentation-only:
- still update progress docs
- run any lightweight validation relevant to changed files if available
- document why no code tests were required

Commit rules:
- one atomic commit per completed step
- use clear conventional-style commit messages
- include the step id in the commit message
- do not commit broken work unless the user explicitly instructs that behavior
- if blocked before completion, update docs and stop without committing unless there is a clean partial artifact worth preserving and the user has allowed it

Output format after each session:
At the end of the session, output:
- completed or blocked step id
- concise summary of what changed
- tests and evals run with pass/fail results
- docs updated
- commit hash if created
- next recommended step
- explicit statement that user confirmation is required before continuing

Roadmap implementation policy:
Implement the roadmap below in order unless a documented dependency forces a different order.
If a roadmap item is too large, split it into smaller substeps before implementation and document the split.

Roadmap:

STEP-000 — Workflow bootstrap and prompt capture
Objective:
Create the durable workflow control-plane inside the repo so future sessions can resume safely.
Minimum scope:
- create or update all required persistent files and directories
- save the master prompt and resume prompt in-repo
- create the roadmap, status tracker, session log, decision ledger, and step templates
- update or create `AGENTS.md`
Acceptance:
- repo contains durable resume files
- roadmap exists with all planned steps listed
- status tracker exists
- step template exists
- future Codex sessions can resume from repo files alone
Tests:
- lightweight validation only as applicable
Docs:
- initialize all required docs

STEP-001 — Canonical run graph contracts
Objective:
Introduce typed run graph models representing the execution DAG rather than relying on implicit flow.
Minimum scope:
- add schemas/types for graph nodes, edges, run graph metadata, stage state, and graph validation
- keep initial implementation narrow and non-invasive
Acceptance:
- typed contracts exist
- serialization/deserialization works
- invalid graphs are rejected
Tests:
- unit tests for graph validation, serialization, and invariants
Docs:
- architecture note describing the run graph model

STEP-002 — Run graph persistence, replay, and resume support
Objective:
Persist canonical run graphs and support deterministic reload/resume.
Minimum scope:
- save and load run graphs with run state
- add replay or inspection helpers where appropriate
Acceptance:
- a saved run graph can be reloaded accurately
- resumable state can point to the next pending node or stage
Tests:
- persistence tests
- resume tests
- compatibility tests for partial state
Docs:
- update architecture and runbook docs

STEP-003 — Evidence bundle contracts and artifact manifest extensions
Objective:
Add typed evidence bundle artifacts for approval and auditability.
Minimum scope:
- define evidence bundle schema
- extend artifact manifest and storage interfaces
- include placeholders for diff summary, checks, policy findings, rollback notes, and review findings
Acceptance:
- evidence bundle contract is stored and versioned
- artifact manifest can reference bundles
Tests:
- schema tests
- manifest tests
Docs:
- artifact model documentation

STEP-004 — Evidence bundle generation in the existing flow
Objective:
Generate real evidence bundles from the current implementation/review flow.
Minimum scope:
- wire bundle generation into current execution path
- record affected files, checks, policy results, review summary, and rollback notes where available
Acceptance:
- completed runs emit evidence bundles
- bundles are discoverable from status/artifacts
Tests:
- integration tests for bundle generation
- eval update if workflow output changes
Docs:
- runbook for interpreting evidence bundles

STEP-005 — Risk scoring engine
Objective:
Compute policy-driven risk scores for work items and changes.
Minimum scope:
- define scoring inputs such as blast radius, protected paths, dependency changes, migrations, auth/billing/infra sensitivity
- implement deterministic scoring
Acceptance:
- risk score is reproducible from inputs
- policy configuration influences the result
Tests:
- unit tests for scoring rules
- policy interaction tests
Docs:
- risk model documentation

STEP-006 — Approval gate framework
Objective:
Introduce deterministic human-in-the-loop approval modes.
Minimum scope:
- implement approval policies such as auto_go, review_go, multi_go
- connect approval requirements to risk score and policy packs
- stop execution cleanly when approval is required
Acceptance:
- low-risk work can continue automatically when allowed
- higher-risk work stops with a clear approval requirement
Tests:
- integration tests for approval gates
- blocked-state resume tests
- eval scenario for approval-required flow
Docs:
- approval runbook
- policy documentation update

STEP-007 — Product brief compiler
Objective:
Compile raw design inputs into a normalized product model.
Minimum scope:
- turn a brief into a structured product specification
- include problem, users, outcomes, non-goals, constraints, risks, assumptions, and acceptance criteria
Acceptance:
- normalized product model exists and validates
- output is stable under fake provider tests
Tests:
- unit tests for contracts
- deterministic provider tests
- snapshot/golden tests where useful
Docs:
- product model documentation

STEP-008 — Assumption tracker
Objective:
Track stated facts, inferred facts, guesses, and unresolved questions.
Minimum scope:
- attach assumption structure to product and planning outputs
- support explicit unresolved-question tracking
Acceptance:
- assumption classes are explicit and persisted
- high-uncertainty areas are visible in artifacts
Tests:
- unit tests for assumption classification plumbing
- eval update for design output
Docs:
- decision and assumption handling guide

STEP-009 — Architecture artifact model
Objective:
Define typed architecture artifacts that later synthesis can populate.
Minimum scope:
- contracts for system context, module boundaries, domain entities, data flow, API contracts, state transitions, and architecture decisions
Acceptance:
- artifact contracts exist and validate
Tests:
- schema tests
- serialization tests
Docs:
- architecture artifact reference

STEP-010 — Architecture synthesizer
Objective:
Generate architecture artifacts from product model plus repo discovery.
Minimum scope:
- produce a first useful architecture synthesis path
- prefer a narrow, deterministic baseline over overreach
Acceptance:
- architecture artifacts can be generated for at least fixture scenarios
- result is attached to planning outputs
Tests:
- deterministic fake-provider tests
- integration tests with fixture repos
- eval scenario for architecture synthesis
Docs:
- architecture synthesis guide

STEP-011 — Backlog graph
Objective:
Replace flat ticket lists with dependency-aware execution graphs.
Minimum scope:
- ticket dependencies
- execution ordering
- parallelizable flags
- critical path metadata
Acceptance:
- backlog graph is typed and persisted
- planner output can drive next-ticket selection
Tests:
- graph tests
- planning tests
- eval scenario for backlog generation
Docs:
- backlog graph documentation

STEP-012 — Repo-aware impact analysis
Objective:
Improve implementation planning with repo-local context.
Minimum scope:
- identify likely touched modules
- locate nearby tests
- detect hotspots and coupled interfaces
- provide a focused context slice for a ticket
Acceptance:
- impact analysis output is available to planning/execution
- results are deterministic for fixture repos
Tests:
- fixture-based integration tests across repo types
- unit tests for selection heuristics where applicable
Docs:
- impact analysis documentation

STEP-013 — Preview environment abstraction
Objective:
Create a generic preview surface without overcommitting to one deployment stack.
Minimum scope:
- define preview interface
- add noop/local adapter first
- support preview artifacts such as URLs, screenshots, smoke results, or placeholders
Acceptance:
- preview interface is stable
- at least one non-production adapter works end-to-end in tests
Tests:
- interface tests
- local/noop adapter tests
Docs:
- preview environment extension guide

STEP-014 — Migration planner
Objective:
Handle schema/data changes as first-class planned artifacts.
Minimum scope:
- define migration plan, backward-compatibility notes, rollback notes, and validation hooks
- connect migration sensitivity to risk scoring
Acceptance:
- migration-aware work items produce migration artifacts
- risky schema changes trigger appropriate review/approval behavior
Tests:
- migration planner tests
- policy tests
- eval scenario for migration-sensitive flow
Docs:
- migration planning runbook

STEP-015 — Observation-to-backlog loop
Objective:
Convert post-execution observations into structured follow-up work.
Minimum scope:
- observation model for errors, latency, user feedback, regression signals, or operational issues
- compiler from observations to backlog candidates
Acceptance:
- observations can generate structured follow-up proposals
- outputs attach to artifacts or backlog planning
Tests:
- compiler tests
- eval scenario for observation-driven follow-up
Docs:
- observation loop guide

STEP-016 — Archetype pack system
Objective:
Support generic application archetypes without hardcoding one product shape.
Minimum scope:
- pack registry
- pack schema
- at least two starter archetypes such as SaaS app and API service
- each pack defines defaults for architecture, policies, and common work patterns
Acceptance:
- pack selection is configurable
- planning can consume a pack
Tests:
- pack loading tests
- integration tests for pack-influenced planning
Docs:
- archetype pack authoring guide

STEP-017 — Scenario eval library expansion
Objective:
Make the new system measurable and regression-resistant.
Minimum scope:
- expand eval suite to cover the new roadmap features
- include scenarios for planning, approval, risk, architecture, impact analysis, migration, and observation loops
Acceptance:
- eval matrix is updated
- JSON and human-readable reporting cover the new scenarios
Tests:
- eval harness tests
- deterministic fake-provider scenarios
Docs:
- eval guide updates

Step splitting policy:
If any roadmap step is too large for a small, reviewable commit:
- create substeps such as `STEP-010A`, `STEP-010B`
- update the roadmap
- add a decision ledger entry explaining the split
- implement only the first substep
- preserve roadmap order within that split group

Genericity policy:
For every step, preserve these properties unless the step explicitly and intentionally changes them:
- provider-neutral core engine
- repo-agnostic operation
- deterministic orchestration
- schema-validated outputs
- testability with fake providers and fixture repos
- resumability from repo state
- human approval support as a policy surface, not ad hoc branching logic

Documentation sync requirements after each step:
Update all affected documents, which may include:
- `README.md` if user-facing behavior changed
- `docs/architecture/...`
- `docs/runbooks/...`
- `docs/testing/test_matrix.md`
- `docs/evals/eval_matrix.md`
- `docs/progress/status.md`
- the current step file
- `docs/progress/decision_ledger.md` if a decision was made

Execution order for the first sessions:
1. Complete STEP-000.
2. Stop and request confirmation.
3. After confirmation, complete STEP-001.
4. Stop and request confirmation.
5. Continue this pattern for all later steps.

Do not skip ahead.
Do not start the next step without user confirmation.
When in doubt, choose the smallest valuable slice, document the choice, implement it cleanly, test it, document it, commit it, and stop.



THIS IS Resume work prompt: 

You are Codex resuming work in this repository.

Before changing anything:
1. Read `docs/codex/MASTER_IMPLEMENTATION_PROMPT.md`.
2. Read `docs/codex/RESUME_PROMPT.md`.
3. Read `AGENTS.md`.
4. Read `docs/roadmap/design_to_execution_roadmap.md`.
5. Read `docs/progress/status.md`.
6. Read the latest session entry in `docs/progress/session_log.md`.
7. Read the most recent unfinished step file, or the latest completed step file if all current steps are marked done.
8. Read `docs/progress/decision_ledger.md`.
9. Inspect git status.
10. Inspect the most recent test/eval results recorded in docs.

Then:
- determine the next bounded incomplete roadmap step
- if needed, split it and document the split
- implement only that one step
- add/update tests and evals
- update docs and progress files
- create one atomic commit if the step is complete and green
- stop
- output a concise report and request explicit user confirmation before continuing

Never continue to a second roadmap step in the same session.
Never rely on memory outside the repository.

