import json
from pathlib import Path

from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.core.models import OrchestratorState
from maestro.evals.harness import EvalScenario, build_eval_engine
from maestro.providers.fake import FakeProvider


def test_run_plan_completes(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    deps = build_engine_deps(project_root, project_root / "examples" / "maestro.example.yaml")
    engine = OrchestratorEngine(project_root, deps)
    state = engine.run_plan(repo, project_root / "examples" / "brief.md")
    assert state.status in {"done", "escalated"}


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
