import json
from pathlib import Path

from typer.testing import CliRunner

from maestro.cli.main import app
from maestro.evals.harness import run_eval_report


def test_run_eval_report_returns_summary_and_results() -> None:
    project_root = Path(__file__).resolve().parents[1]
    report = run_eval_report(project_root)

    assert report.summary.scenario_count == len(report.scenarios)
    assert report.summary.passed >= 1
    assert any(result.scenario == "migration-sensitive-flow" for result in report.scenarios)


def test_eval_cli_writes_json_report(tmp_path: Path) -> None:
    runner = CliRunner()
    output_path = tmp_path / "eval-report.json"

    result = runner.invoke(app, ["eval", "--json-output-path", str(output_path)])

    assert result.exit_code == 0
    report = json.loads(output_path.read_text())
    assert report["summary"]["scenario_count"] >= 1
    assert any(item["scenario"] == "observation-driven-followup" for item in report["scenarios"])
