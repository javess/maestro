from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from maestro.config import load_config
from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.evals.harness import build_eval_engine, default_scenarios
from maestro.logging import configure_logging
from maestro.preview.factory import build_preview_adapter
from maestro.repo.discovery import discover_repo
from maestro.schemas.contracts import TicketStatus
from maestro.schemas.preview import PreviewRequest
from maestro.storage.local import LocalStateStore, MaestroWorkspace, workspace_root_for_repo
from maestro.tools.git import GitWorktreeManager

app = typer.Typer(help="Deterministic multi-agent software delivery framework")
console = Console()
logger = logging.getLogger(__name__)


@app.callback()
def main(
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase log verbosity."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only emit errors."),
    log_level: str | None = typer.Option(
        None,
        "--log-level",
        help="Explicit log level override: DEBUG, INFO, WARNING, ERROR, or CRITICAL.",
    ),
) -> None:
    configure_logging(verbose=verbose, quiet=quiet, log_level=log_level)
    logger.debug(
        "cli_initialized verbose=%s quiet=%s log_level=%s",
        verbose,
        quiet,
        log_level,
    )


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _config_path(config: Path | None) -> Path:
    return config or _project_root() / "examples" / "maestro.example.yaml"


def _workspace(repo: Path) -> MaestroWorkspace:
    return MaestroWorkspace.for_repo(repo.resolve())


def _legacy_state_store() -> LocalStateStore:
    return LocalStateStore(_project_root() / "runs" / "state")


def _resolve_state_store(repo: Path, run_id: str | None = None) -> LocalStateStore:
    repo_store = LocalStateStore(_workspace(repo).state_dir)
    if run_id is None or repo_store.exists(run_id):
        return repo_store
    legacy_store = _legacy_state_store()
    if legacy_store.exists(run_id):
        return legacy_store
    return repo_store


@app.command()
def init(config: Path = Path("maestro.yaml"), repo: Path = Path(".")) -> None:
    root = _project_root()
    target = config.resolve()
    example = root / "examples" / "maestro.example.yaml"
    created = False
    if not target.exists():
        shutil.copyfile(example, target)
        created = True
    workspace = _workspace(repo)
    console.print(
        {
            "config": str(target),
            "created": created,
            "workspace_root": str(workspace.root),
            "runs_dir": str(workspace.runs_dir),
            "state_dir": str(workspace.state_dir),
        }
    )


@app.command()
def discover(path: Path = Path(".")) -> None:
    discovery = discover_repo(path.resolve())
    console.print_json(discovery.model_dump_json(indent=2))


@app.command()
def plan(brief: Path, config: Path | None = None, repo: Path = Path(".")) -> None:
    repo_root = repo.resolve()
    logger.info(
        "plan_start repo=%s brief=%s config=%s",
        repo_root,
        brief.resolve(),
        _config_path(config),
    )
    deps = build_engine_deps(
        _project_root(),
        _config_path(config),
        workspace_root=_workspace(repo_root).root,
    )
    engine = OrchestratorEngine(_project_root(), deps)
    state = engine.run_plan(repo_root, brief.resolve())
    logger.info(
        "plan_complete run_id=%s status=%s state=%s",
        state.run_id,
        state.status,
        state.current_state,
    )
    console.print_json(state.model_dump_json(indent=2))


@app.command("run-ticket")
def run_ticket(ticket_id: str, config: Path | None = None, repo: Path = Path(".")) -> None:
    repo_root = repo.resolve()
    deps = build_engine_deps(
        _project_root(),
        _config_path(config),
        workspace_root=_workspace(repo_root).root,
    )
    engine = OrchestratorEngine(_project_root(), deps)
    state = engine.new_state(repo_root, None)
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
    checks = engine.validate(state, commands, code_result)
    review = engine.review(state, ticket, code_result, checks)
    violations, approval_request = engine.write_evidence_bundle(
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
        approval_request=approval_request,
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
def status(run_id: str | None = None, repo: Path = Path(".")) -> None:
    state_store = _resolve_state_store(repo.resolve(), run_id)
    if run_id is None:
        rows = [state_store.root / f"{value}.json" for value in state_store.list_run_ids()]
        table = Table("run_id", "status", "state")
        for row in rows:
            state = state_store.load(row.stem)
            table.add_row(state.run_id, state.status, state.current_state)
        console.print(table)
        return
    state = state_store.load(run_id)
    console.print_json(state.model_dump_json(indent=2))


@app.command()
def resume(run_id: str, repo: Path = Path(".")) -> None:
    state_store = _resolve_state_store(repo.resolve(), run_id)
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
def preview(
    repo: Path = Path("."),
    command: str | None = None,
    adapter: str = "noop",
    config: Path | None = None,
) -> None:
    repo_path = repo.resolve()
    logger.info("preview_start repo=%s adapter=%s", repo_path, adapter)
    deps = build_engine_deps(
        _project_root(),
        _config_path(config),
        workspace_root=_workspace(repo_path).root,
    )
    discovery = discover_repo(repo_path)
    preview_adapter = build_preview_adapter(adapter, shell=deps.shell)
    artifact = preview_adapter.build_preview(
        PreviewRequest(repo_path=repo_path, repo_info=discovery.repo_info, command=command)
    )
    manifest = deps.artifact_store.create_run()
    path = deps.artifact_store.write_json(
        manifest,
        f"preview_{adapter}",
        artifact.model_dump(mode="json"),
    )
    console.print_json(
        json.dumps(
            {
                "run_id": manifest.run_id,
                "artifact_path": str(path),
                "workspace_root": str(workspace_root_for_repo(repo_path)),
                "preview": artifact.model_dump(mode="json"),
            },
            indent=2,
        )
    )
    logger.info(
        "preview_complete run_id=%s adapter=%s status=%s",
        manifest.run_id,
        adapter,
        artifact.status,
    )


@app.command()
def ui() -> None:
    subprocess.run(["npm", "install"], cwd=_project_root() / "ui", check=False)
    subprocess.run(["npm", "run", "dev"], cwd=_project_root() / "ui", check=False)


if __name__ == "__main__":
    app()
