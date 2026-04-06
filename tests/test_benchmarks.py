from pathlib import Path

from maestro.benchmarks import run_benchmarks


def test_run_benchmarks_returns_scored_results(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    report = run_benchmarks(project_root, tmp_path / "benchmarks")

    assert report.scenario_count >= 3
    assert report.total_score > 0
    assert all(item.provider == "fake" for item in report.scenarios)
