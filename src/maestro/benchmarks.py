from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from maestro.core.models import OrchestratorState
from maestro.evals.harness import EvalScenario, build_eval_engine
from maestro.providers.fake import FakeProvider
from maestro.repo.discovery import discover_repo
from maestro.schemas.benchmark import BenchmarkReport, BenchmarkScenarioResult


@dataclass
class BenchmarkScenario:
    name: str
    repo_fixture: Path
    brief: Path
    provider_name: str = "fake"


def default_benchmark_scenarios(project_root: Path) -> list[BenchmarkScenario]:
    fixtures = project_root / "tests" / "fixtures"
    return [
        BenchmarkScenario(
            name="python-feature-flow",
            repo_fixture=fixtures / "python_repo",
            brief=project_root / "examples" / "brief.md",
        ),
        BenchmarkScenario(
            name="node-planning-flow",
            repo_fixture=fixtures / "node_repo",
            brief=project_root / "examples" / "brief.md",
        ),
        BenchmarkScenario(
            name="generic-broken-flow",
            repo_fixture=fixtures / "broken_repo",
            brief=project_root / "examples" / "brief.md",
        ),
    ]


def run_benchmarks(project_root: Path, workspace_root: Path) -> BenchmarkReport:
    results: list[BenchmarkScenarioResult] = []
    for scenario in default_benchmark_scenarios(project_root):
        repo_copy = workspace_root / scenario.name
        if repo_copy.exists():
            shutil.rmtree(repo_copy)
        shutil.copytree(scenario.repo_fixture, repo_copy)
        eval_engine = build_eval_engine(
            project_root,
            EvalScenario(
                name=scenario.name,
                provider=FakeProvider(),
                expected_final_state=OrchestratorState.DONE,
                expected_status="done",
            ),
        )
        state = eval_engine.run_plan(repo_copy, scenario.brief)
        retries = sum(1 for event in state.events if event.state == OrchestratorState.REVISE.value)
        discovery = discover_repo(repo_copy)
        score = 50 if state.status == "done" else 10
        score += 20 if discovery.adapter_name != "generic" else 0
        score += max(0, 20 - (retries * 5))
        score += min(10, len(state.artifacts.evidence_bundles) * 5)
        notes: list[str] = []
        if discovery.adapter_name == "generic":
            notes.append("generic adapter")
        if state.status != "done":
            notes.append(f"ended:{state.status}")
        results.append(
            BenchmarkScenarioResult(
                scenario=scenario.name,
                repo_type=discovery.repo_info.repo_type,
                provider=scenario.provider_name,
                status=state.status,
                score=score,
                retries=retries,
                notes=notes,
            )
        )
    total_score = sum(item.score for item in results)
    return BenchmarkReport(
        total_score=total_score,
        scenario_count=len(results),
        average_score=(total_score / len(results)) if results else 0.0,
        scenarios=results,
    )
