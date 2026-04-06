import json
import subprocess
import threading
import time
from pathlib import Path
from typing import cast

from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.core.models import OrchestratorState
from maestro.evals.harness import EvalScenario, build_eval_engine
from maestro.providers.fake import FakeProvider
from maestro.schemas.contracts import (
    Backlog,
    CodeChange,
    CodeResult,
    CommitMode,
    DiffArtifact,
    FileOperation,
    PatchHunk,
    PolicyPack,
    ReviewResult,
    Ticket,
)


def test_run_plan_completes(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    deps = build_engine_deps(
        project_root,
        project_root / "examples" / "maestro.example.yaml",
        workspace_root=repo / ".maestro",
    )
    engine = OrchestratorEngine(project_root, deps)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")
    assert state.status in {"done", "escalated", "awaiting_approval"}
    assert (repo / ".maestro" / "state" / f"{state.run_id}.json").exists()
    assert (repo / ".maestro" / "runs" / state.run_id).exists()
    assert (repo / ".maestro" / "maestro.db").exists()


def test_run_plan_emits_evidence_bundle_for_completed_ticket(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    scenario = EvalScenario(
        name="evidence-complete",
        provider=FakeProvider(),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    assert len(state.artifacts.evidence_bundles) == 1
    bundle_path = Path(state.artifacts.evidence_bundles[0].path)
    bundle = json.loads(bundle_path.read_text())
    assert bundle["ticket_id"] == "TICKET-1"
    assert bundle["review_result"]["approved"] is True
    assert bundle["risk_score"]["level"] in {"low", "medium", "high", "critical"}
    assert bundle["metadata"]["review_cycle"] == 1
    assert state.backlog.architecture_artifacts is not None


def test_run_plan_emits_evidence_bundle_for_escalated_ticket(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    scenario = EvalScenario(
        name="evidence-escalated",
        provider=FakeProvider({"force_review_issue": True}),
        expected_final_state=OrchestratorState.ESCALATE,
        expected_status="escalated",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    assert len(state.artifacts.evidence_bundles) == 3
    bundle_path = Path(state.artifacts.evidence_bundles[-1].path)
    bundle = json.loads(bundle_path.read_text())
    assert bundle["review_result"]["approved"] is False
    assert bundle["risk_score"]["score"] >= 0
    assert "review_rejected" in bundle["metadata"]["violations"]
    assert bundle["rollback_notes"]


def test_run_plan_waits_for_approval_when_policy_requires_it(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    from maestro.schemas.contracts import ApprovalMode, PolicyPack, RiskLevel

    scenario = EvalScenario(
        name="approval-required",
        provider=FakeProvider(),
        expected_final_state=OrchestratorState.REVIEW,
        expected_status="awaiting_approval",
        policy=PolicyPack(
            name="strict",
            approval_mode=ApprovalMode.review_go,
            approval_risk_level=RiskLevel.low,
        ),
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    assert state.status == "awaiting_approval"
    assert state.current_state == OrchestratorState.REVIEW.value
    assert state.approval_request is not None
    assert state.approval_request.required_approvals == 1
    assert state.current_ticket_id == "TICKET-1"


def test_run_plan_persists_architecture_artifact(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    scenario = EvalScenario(
        name="architecture-synthesis",
        provider=FakeProvider(),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "architecture_synthesizer" in artifact_names
    assert state.backlog.architecture_artifacts is not None


def test_run_plan_uses_backlog_graph_ordering() -> None:
    project_root = Path(__file__).resolve().parents[1]
    scenario = EvalScenario(
        name="backlog-graph-ordering",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="First",
                            description="first",
                            acceptance_criteria=["one"],
                            priority=3,
                        ),
                        Ticket(
                            id="TICKET-2",
                            title="Second",
                            description="second",
                            acceptance_criteria=["two"],
                            dependencies=["TICKET-1"],
                            priority=2,
                        ),
                    ]
                )
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    pick_events = [
        event.detail for event in state.events if event.state == OrchestratorState.PICK_TICKET
    ]
    assert pick_events == ["TICKET-1", "TICKET-2"]
    assert state.backlog.execution_graph is not None


def test_run_plan_attaches_impact_analysis_to_execution_context() -> None:
    project_root = Path(__file__).resolve().parents[1]
    class CapturingFakeProvider(FakeProvider):
        def __init__(self) -> None:
            super().__init__()
            self.captured_repo_context: dict[str, object] | None = None

        def generate_structured(self, *, prompt: str, model: str, schema, metadata=None):
            if schema.__name__ == "CodeResult":
                assert metadata is not None
                repo_context = metadata["repo_context"]
                assert isinstance(repo_context, dict)
                self.captured_repo_context = repo_context
            return super().generate_structured(
                prompt=prompt,
                model=model,
                schema=schema,
                metadata=metadata,
            )

    provider = CapturingFakeProvider()

    scenario = EvalScenario(
        name="impact-analysis",
        provider=provider,
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    assert provider.captured_repo_context is not None
    impact_analysis = cast(dict[str, object], provider.captured_repo_context["impact_analysis"])
    assert impact_analysis["ticket_id"] == "TICKET-1"
    assert "TICKET-1" in state.backlog.impact_analyses
    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "impact_analysis" in artifact_names


def test_run_plan_applies_file_operations_to_repo(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")

    scenario = EvalScenario(
        name="repo-mutation",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Create app",
                            description="Create the first app file",
                            acceptance_criteria=["app exists"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Create app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="def main() -> None:\n    print('ok')\n",
                        )
                    ],
                    commands=[],
                    tests_added=["tests/test_app.py"],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.status == "done"
    assert (repo / "src" / "app.py").read_text() == "def main() -> None:\n    print('ok')\n"


def test_run_plan_syncs_approved_changes_back_from_workspace(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    scenario = EvalScenario(
        name="worktree-sync",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Create app",
                            description="Create the first app file",
                            acceptance_criteria=["app exists"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Create app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="def main() -> None:\n    print('from worktree')\n",
                        )
                    ],
                    commands=[],
                    tests_added=["tests/test_app.py"],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.status == "done"
    assert (repo / "src" / "app.py").read_text() == (
        "def main() -> None:\n    print('from worktree')\n"
    )
    assert "TICKET-1" in state.ticket_workdirs


def test_run_plan_creates_checkpoint_commit_on_feature_branch(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    scenario = EvalScenario(
        name="checkpoint-commit",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Create app",
                            description="Create the first app file",
                            acceptance_criteria=["app exists"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Create app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="def main() -> None:\n    print('committed')\n",
                        )
                    ],
                    commands=[],
                    tests_added=["tests/test_app.py"],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
        policy=PolicyPack(
            name="prototype",
            require_tests=False,
            commit_mode=CommitMode.checkpoint_commits,
        ),
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.run_branch == f"maestro/{state.run_id}"
    assert Path(state.artifacts.evidence_bundles[0].path).exists()
    bundle = json.loads(Path(state.artifacts.evidence_bundles[0].path).read_text())
    assert bundle["commit_metadata"]["branch"] == state.run_branch
    assert bundle["commit_metadata"]["mode"] == CommitMode.checkpoint_commits.value
    current_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    assert current_branch.stdout.strip() == state.run_branch
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "maestro: checkpoint TICKET-1" in log.stdout


def test_run_plan_creates_final_run_commit_when_commit_on_green(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    scenario = EvalScenario(
        name="run-commit",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Create app",
                            description="Create the first app file",
                            acceptance_criteria=["app exists"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Create app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="def main() -> None:\n    print('green')\n",
                        )
                    ],
                    commands=[],
                    tests_added=["tests/test_app.py"],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
        policy=PolicyPack(
            name="legacy",
            require_tests=False,
            commit_mode=CommitMode.commit_on_green,
        ),
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.run_branch == f"maestro/{state.run_id}"
    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "run_commit" in artifact_names
    bundle = json.loads(Path(state.artifacts.evidence_bundles[0].path).read_text())
    assert bundle["commit_metadata"]["branch"] == state.run_branch
    assert bundle["commit_metadata"]["mode"] == CommitMode.commit_on_green.value
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    assert f"maestro: complete run {state.run_id}" in log.stdout


def test_run_plan_waits_for_diff_approval_and_can_approve(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    scenario = EvalScenario(
        name="diff-approval",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Create app",
                            description="Create the first app file",
                            acceptance_criteria=["app exists"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Create app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="def main() -> None:\n    print('diff')\n",
                        )
                    ],
                    commands=[],
                    tests_added=[],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.REVIEW,
        expected_status="awaiting_diff_approval",
        policy=PolicyPack(name="strict", require_tests=False, require_diff_approval=True),
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.status == "awaiting_diff_approval"
    assert state.diff_approval_request is not None
    diff_path = next(
        Path(artifact.path)
        for artifact in state.artifacts.artifacts
        if artifact.name == state.diff_approval_request.diff_artifact_name
    )
    diff_artifact = DiffArtifact.model_validate_json(diff_path.read_text())
    assert diff_artifact.files[0].path == "src/app.py"
    approved = engine.approve_diff(state, "TICKET-1")
    assert approved.status == "done"
    assert (repo / "src" / "app.py").read_text() == "def main() -> None:\n    print('diff')\n"


def test_run_plan_reject_diff_creates_repair_context(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")

    scenario = EvalScenario(
        name="diff-reject",
        provider=FakeProvider(
            {
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Create app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="print('draft')\n",
                        )
                    ],
                    commands=[],
                    tests_added=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.REVIEW,
        expected_status="awaiting_diff_approval",
        policy=PolicyPack(name="strict", require_tests=False, require_diff_approval=True),
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    updated = engine.reject_diff(state, "TICKET-1", "needs smaller diff", rerun=True)
    assert updated.status == "running"
    assert updated.repair_contexts["TICKET-1"].prior_notes == ["needs smaller diff"]


def test_run_plan_applies_patch_operations_to_repo(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    app = repo / "src" / "app.py"
    app.parent.mkdir(parents=True)
    app.write_text("def greet() -> str:\n    return 'old'\n")

    scenario = EvalScenario(
        name="patch-mutation",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Patch app",
                            description="Patch the app file",
                            acceptance_criteria=["app returns new"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Patch app file",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="patch",
                            hunks=[
                                PatchHunk(
                                    kind="replace",
                                    match="return 'old'",
                                    content="return 'new'",
                                )
                            ],
                        )
                    ],
                    commands=[],
                    tests_added=["tests/test_app.py"],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.status == "done"
    assert app.read_text() == "def greet() -> str:\n    return 'new'\n"


def test_run_plan_executes_ready_tickets_in_parallel_when_policy_allows(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    from maestro.schemas.contracts import PolicyPack

    class ConcurrentCodeProvider(FakeProvider):
        def __init__(self) -> None:
            super().__init__(
                {
                    "Backlog": Backlog(
                        tickets=[
                            Ticket(
                                id="TICKET-1",
                                title="Create one",
                                description="first",
                                acceptance_criteria=["one"],
                            ),
                            Ticket(
                                id="TICKET-2",
                                title="Create two",
                                description="second",
                                acceptance_criteria=["two"],
                            ),
                        ]
                    )
                }
            )
            self.lock = threading.Lock()
            self.inflight = 0
            self.max_inflight = 0

        def generate_structured(self, *, prompt: str, model: str, schema, metadata=None):
            if schema.__name__ == "CodeResult":
                ticket_id = cast(str, (metadata or {})["ticket_id"])
                with self.lock:
                    self.inflight += 1
                    self.max_inflight = max(self.max_inflight, self.inflight)
                time.sleep(0.2)
                with self.lock:
                    self.inflight -= 1
                return CodeResult(
                    ticket_id=ticket_id,
                    summary=f"Create {ticket_id}",
                    file_operations=[
                        FileOperation(
                            path=f"src/{ticket_id.lower()}.py",
                            action="write",
                            content=f"print('{ticket_id.lower()}')\n",
                        )
                    ],
                    commands=[],
                    tests_added=[],
                )
            if schema.__name__ == "ReviewResult":
                ticket_id = cast(str, (metadata or {})["ticket_id"])
                return ReviewResult(
                    ticket_id=ticket_id,
                    approved=True,
                    summary="approved",
                    issues=[],
                )
            return super().generate_structured(
                prompt=prompt,
                model=model,
                schema=schema,
                metadata=metadata,
            )

    provider = ConcurrentCodeProvider()
    scenario = EvalScenario(
        name="parallel-batch",
        provider=provider,
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
        policy=PolicyPack(name="prototype", max_parallel_tickets=2, require_tests=False),
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.status == "done"
    assert provider.max_inflight >= 2
    assert (repo / "src" / "ticket-1.py").read_text() == "print('ticket-1')\n"
    assert (repo / "src" / "ticket-2.py").read_text() == "print('ticket-2')\n"


def test_run_plan_persists_migration_plan_artifact(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    scenario = EvalScenario(
        name="migration-artifact",
        provider=FakeProvider(
            {
                "Backlog": Backlog(
                    tickets=[
                        Ticket(
                            id="TICKET-1",
                            title="Add migration",
                            description="Update schema",
                            acceptance_criteria=["schema updated"],
                        )
                    ]
                ),
                "CodeResult": CodeResult(
                    ticket_id="TICKET-1",
                    summary="Add migration",
                    changed_files=[
                        CodeChange(
                            path="migrations/001_add_table.sql",
                            summary="migration",
                        )
                    ],
                    commands=["uv run pytest"],
                    tests_added=[],
                ),
                "ReviewResult": ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                ),
            }
        ),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "TICKET-1_migration_plan_1" in artifact_names


def test_run_plan_persists_observation_followups_for_failed_review() -> None:
    project_root = Path(__file__).resolve().parents[1]
    scenario = EvalScenario(
        name="observation-followups",
        provider=FakeProvider({"force_review_issue": True}),
        expected_final_state=OrchestratorState.ESCALATE,
        expected_status="escalated",
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "TICKET-1_observation_followups_1" in artifact_names


def test_run_plan_passes_repair_context_on_retry(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")

    class RepairAwareProvider(FakeProvider):
        def __init__(self) -> None:
            super().__init__()
            self.code_attempts = 0

        def generate_structured(self, *, prompt: str, model: str, schema, metadata=None):
            if schema.__name__ == "CodeResult":
                self.code_attempts += 1
                if self.code_attempts == 1:
                    assert (metadata or {}).get("repair_context") is None
                    return CodeResult(
                        ticket_id="TICKET-1",
                        summary="First attempt",
                        file_operations=[
                            FileOperation(
                                path="src/app.py",
                                action="write",
                                content="print('first')\n",
                            )
                        ],
                        commands=["run-failing-check"],
                        tests_added=[],
                    )
                repair_context = cast(
                    dict[str, object] | None,
                    (metadata or {}).get("repair_context"),
                )
                assert repair_context is not None
                assert repair_context["ticket_id"] == "TICKET-1"
                failing_checks = cast(list[dict[str, object]], repair_context["failing_checks"])
                assert "forced failure" in cast(str, failing_checks[0]["output"])
                return CodeResult(
                    ticket_id="TICKET-1",
                    summary="Second attempt",
                    file_operations=[
                        FileOperation(
                            path="src/app.py",
                            action="write",
                            content="print('fixed')\n",
                        )
                    ],
                    commands=[],
                    tests_added=[],
                )
            if schema.__name__ == "ReviewResult":
                return ReviewResult(
                    ticket_id="TICKET-1",
                    approved=True,
                    summary="approved",
                    issues=[],
                )
            return super().generate_structured(
                prompt=prompt,
                model=model,
                schema=schema,
                metadata=metadata,
            )

    scenario = EvalScenario(
        name="repair-loop",
        provider=RepairAwareProvider(),
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
        policy=PolicyPack(name="prototype", require_tests=False, max_review_cycles=2),
        shell_failures={"run-failing-check"},
    )
    engine = build_eval_engine(project_root, scenario)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")

    assert state.status == "done"
    assert (repo / "src" / "app.py").read_text() == "print('fixed')\n"
    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "TICKET-1_repair_context_1" in artifact_names


def test_plan_tickets_passes_archetype_pack_to_planner(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]

    class CapturingArchetypeProvider(FakeProvider):
        def __init__(self) -> None:
            super().__init__()
            self.captured_archetype: dict[str, object] | None = None

        def generate_structured(self, *, prompt: str, model: str, schema, metadata=None):
            if schema.__name__ == "Backlog":
                self.captured_archetype = cast(
                    dict[str, object] | None,
                    (metadata or {}).get("archetype_pack"),
                )
            return super().generate_structured(
                prompt=prompt,
                model=model,
                schema=schema,
                metadata=metadata,
            )

    provider = CapturingArchetypeProvider()
    scenario = EvalScenario(
        name="archetype-pack",
        provider=provider,
        expected_final_state=OrchestratorState.DONE,
        expected_status="done",
    )
    engine = build_eval_engine(project_root, scenario)
    engine.deps.config.archetype = "saas_app"
    state = engine.run_plan(project_root, project_root / "examples" / "brief.md")

    assert provider.captured_archetype is not None
    assert provider.captured_archetype["name"] == "saas_app"
    artifact_names = {artifact.name for artifact in state.artifacts.artifacts}
    assert "archetype_pack" in artifact_names
