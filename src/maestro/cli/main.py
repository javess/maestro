from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from maestro.config import load_config
from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.evals.harness import build_eval_engine, default_scenarios
from maestro.repo.discovery import discover_repo
from maestro.schemas.contracts import TicketStatus
from maestro.storage.local import LocalStateStore
from maestro.tools.git import GitWorktreeManager

app = typer.Typer(help="Deterministic multi-agent software delivery framework")
console = Console()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _config_path(config: Path | None) -> Path:
    return config or _project_root() / "examples" / "maestro.example.yaml"


@app.command()
def init(config: Path = Path("maestro.yaml")) -> None:
    root = _project_root()
    target = config.resolve()
    example = root / "examples" / "maestro.example.yaml"
    created = False
    if not target.exists():
        shutil.copyfile(example, target)
        created = True
    (root / "runs" / "state").mkdir(parents=True, exist_ok=True)
    console.print({"config": str(target), "created": created})


@app.command()
def discover(path: Path = Path(".")) -> None:
    discovery = discover_repo(path.resolve())
    console.print_json(discovery.model_dump_json(indent=2))


@app.command()
def plan(brief: Path, config: Path | None = None, repo: Path = Path(".")) -> None:
    deps = build_engine_deps(_project_root(), _config_path(config))
    engine = OrchestratorEngine(_project_root(), deps)
    state = engine.run_plan(repo.resolve(), brief.resolve())
    console.print_json(state.model_dump_json(indent=2))


@app.command("run-ticket")
def run_ticket(ticket_id: str, config: Path | None = None, repo: Path = Path(".")) -> None:
    deps = build_engine_deps(_project_root(), _config_path(config))
    engine = OrchestratorEngine(_project_root(), deps)
    state = engine.new_state(repo.resolve(), None)
    discovery = engine.discover(state)
    fake_brief = _project_root() / "examples" / "brief.md"
    spec = engine.define_product(state, fake_brief.read_text())
    backlog = engine.plan_tickets(state, spec.model_dump(mode="json"))
    ticket = next((item for item in backlog.tickets if item.id == ticket_id), None)
    if ticket is None:
        raise typer.BadParameter(f"Unknown ticket id: {ticket_id}")
    ticket.status = TicketStatus.in_progress
    code_result = engine.implement(state, ticket, discovery.model_dump(mode="json"))
    commands = discovery.repo_info.lint_commands + discovery.repo_info.test_commands
    checks = engine.validate(state, commands)
    review = engine.review(state, ticket, code_result, checks)
    violations = engine.write_evidence_bundle(
        state,
        ticket,
        code_result,
        checks,
        review,
        discovery.repo_info,
    )
    result = engine.advance_ticket(
        state,
        ticket,
        code_result,
        checks,
        review,
        violations=violations,
    )
    console.print_json(
        json.dumps(
            {"final_state": result.value, "ticket": ticket.model_dump(mode="json")},
            indent=2,
        )
    )


@app.command()
def review(ticket_id: str, config: Path | None = None, repo: Path = Path(".")) -> None:
    console.print(f"Review entrypoint available for {ticket_id} in repo {repo.resolve()}")
    _ = load_config(_config_path(config))


@app.command()
def status(run_id: str | None = None) -> None:
    state_store = LocalStateStore(_project_root() / "runs" / "state")
    if run_id is None:
        rows = sorted((_project_root() / "runs" / "state").glob("*.json"))
        table = Table("run_id", "status", "state")
        for row in rows:
            state = state_store.load(row.stem)
            table.add_row(state.run_id, state.status, state.current_state)
        console.print(table)
        return
    state = state_store.load(run_id)
    console.print_json(state.model_dump_json(indent=2))


@app.command()
def resume(run_id: str) -> None:
    state_store = LocalStateStore(_project_root() / "runs" / "state")
    state = state_store.load(run_id)
    console.print_json(state.model_dump_json(indent=2))


@app.command()
def eval(json_output: bool = False) -> None:
    root = _project_root()
    report: list[dict[str, str]] = []
    for scenario in default_scenarios():
        engine = build_eval_engine(root, scenario)
        state = engine.run_plan(root, root / "examples" / "brief.md")
        report.append(
            {
                "scenario": scenario.name,
                "status": state.status,
                "current_state": state.current_state,
                "expected_state": scenario.expected_final_state.value,
                "evidence_bundles": str(len(state.artifacts.evidence_bundles)),
            }
        )
    if json_output:
        console.print_json(json.dumps(report, indent=2))
        return
    table = Table("scenario", "status", "state", "evidence bundles")
    for row in report:
        table.add_row(
            row["scenario"],
            row["status"],
            row["current_state"],
            row["evidence_bundles"],
        )
    console.print(table)


@app.command()
def doctor(config: Path | None = None, repo: Path = Path(".")) -> None:
    cfg = load_config(_config_path(config))
    repo_manager = GitWorktreeManager(repo.resolve())
    discovery = discover_repo(repo.resolve())
    console.print(
        {
            "config_policy": cfg.policy,
            "git_branch": repo_manager.current_branch() if (repo / ".git").exists() else "unknown",
            "git_dirty": repo_manager.is_dirty() if (repo / ".git").exists() else False,
            "repo_type": discovery.repo_info.repo_type,
        }
    )


@app.command()
def ui() -> None:
    subprocess.run(["npm", "install"], cwd=_project_root() / "ui", check=False)
    subprocess.run(["npm", "run", "dev"], cwd=_project_root() / "ui", check=False)


if __name__ == "__main__":
    app()
