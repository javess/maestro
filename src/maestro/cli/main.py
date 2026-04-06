from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from maestro.config import load_config
from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.credentials import (
    DEFAULT_CREDENTIAL_SERVICE,
    credential_status,
    delete_provider_secret,
    store_provider_secret,
)
from maestro.evals.harness import run_eval_report
from maestro.logging import configure_logging
from maestro.preview.factory import build_preview_adapter
from maestro.repo.discovery import discover_repo
from maestro.repo.readiness import assess_repo_readiness
from maestro.schemas.contracts import TicketStatus
from maestro.schemas.preview import PreviewRequest
from maestro.storage.local import LocalStateStore, MaestroWorkspace, workspace_root_for_repo
from maestro.storage.sqlite import SqliteRunIndex
from maestro.tools.git import GitWorktreeManager

app = typer.Typer(help="Deterministic multi-agent software delivery framework")
creds_app = typer.Typer(help="Secure local provider credential storage")
app.add_typer(creds_app, name="creds")
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
    legacy_root = _project_root() / "runs"
    return LocalStateStore(legacy_root / "state", index=SqliteRunIndex(legacy_root / "maestro.db"))


def _resolve_state_store(repo: Path, run_id: str | None = None) -> LocalStateStore:
    workspace = _workspace(repo)
    repo_store = LocalStateStore(workspace.state_dir, index=SqliteRunIndex(workspace.index_path))
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
        table = Table("run_id", "status", "state")
        for row in state_store.list_runs():
            table.add_row(row.run_id, row.status, row.current_state)
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
def approve(run_id: str, ticket_id: str, repo: Path = Path(".")) -> None:
    repo_root = repo.resolve()
    deps = build_engine_deps(
        _project_root(),
        _config_path(None),
        workspace_root=_workspace(repo_root).root,
    )
    engine = OrchestratorEngine(_project_root(), deps)
    state_store = _resolve_state_store(repo_root, run_id)
    state = state_store.load(run_id)
    updated = engine.approve_diff(state, ticket_id)
    deps.state_store.save(updated)
    console.print_json(updated.model_dump_json(indent=2))


@app.command()
def reject(
    run_id: str,
    ticket_id: str,
    repo: Path = Path("."),
    comment: str = typer.Option("", "--comment", help="Reason for rejecting the proposed diff."),
) -> None:
    repo_root = repo.resolve()
    deps = build_engine_deps(
        _project_root(),
        _config_path(None),
        workspace_root=_workspace(repo_root).root,
    )
    engine = OrchestratorEngine(_project_root(), deps)
    state_store = _resolve_state_store(repo_root, run_id)
    state = state_store.load(run_id)
    updated = engine.reject_diff(state, ticket_id, comment, rerun=False)
    deps.state_store.save(updated)
    console.print_json(updated.model_dump_json(indent=2))


@app.command()
def rerun(
    run_id: str,
    ticket_id: str,
    repo: Path = Path("."),
    comment: str = typer.Option(
        "",
        "--comment",
        help="Optional guidance for the rerun request.",
    ),
) -> None:
    repo_root = repo.resolve()
    deps = build_engine_deps(
        _project_root(),
        _config_path(None),
        workspace_root=_workspace(repo_root).root,
    )
    engine = OrchestratorEngine(_project_root(), deps)
    state_store = _resolve_state_store(repo_root, run_id)
    state = state_store.load(run_id)
    updated = engine.reject_diff(state, ticket_id, comment, rerun=True)
    deps.state_store.save(updated)
    console.print_json(updated.model_dump_json(indent=2))


@app.command()
def eval(json_output: bool = False, json_output_path: Path | None = None) -> None:
    root = _project_root()
    report = run_eval_report(root)
    if json_output_path is not None:
        json_output_path.write_text(report.model_dump_json(indent=2))
    if json_output:
        console.print_json(report.model_dump_json(indent=2))
        return
    summary = Table(
        "scenarios",
        "passed",
        "failed",
        "retries",
        "schema errors",
        "policy violations",
    )
    summary.add_row(
        str(report.summary.scenario_count),
        str(report.summary.passed),
        str(report.summary.failed),
        str(report.summary.total_retries),
        str(report.summary.total_schema_errors),
        str(report.summary.total_policy_violations),
    )
    console.print(summary)
    table = Table(
        "scenario",
        "status",
        "state",
        "expected",
        "evidence bundles",
        "retries",
        "passed",
    )
    for row in report.scenarios:
        table.add_row(
            row.scenario,
            row.status,
            row.current_state,
            row.expected_state,
            str(row.evidence_bundles),
            str(row.retries),
            "yes" if row.passed else "no",
        )
    console.print(table)


@app.command()
def doctor(config: Path | None = None, repo: Path = Path(".")) -> None:
    cfg = load_config(_config_path(config))
    repo_manager = GitWorktreeManager(repo.resolve())
    discovery = discover_repo(repo.resolve())
    readiness = assess_repo_readiness(repo.resolve(), discovery)
    console.print(
        {
            "config_policy": cfg.policy,
            "git_branch": repo_manager.current_branch() if (repo / ".git").exists() else "unknown",
            "git_dirty": repo_manager.is_dirty() if (repo / ".git").exists() else False,
            "repo_type": discovery.repo_info.repo_type,
            "support_tier": readiness.tier,
            "readiness_score": readiness.score,
            "blockers": readiness.blockers,
            "recommendations": readiness.recommendations,
        }
    )


@creds_app.command("set")
def creds_set(
    provider: str,
    value: str = typer.Option(
        ...,
        "--value",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="Provider secret value to store in the OS keychain.",
    ),
    service: str = typer.Option(
        DEFAULT_CREDENTIAL_SERVICE,
        "--service",
        help="Keychain service name.",
    ),
    credential_name: str | None = typer.Option(
        None,
        "--credential-name",
        help="Override the stored credential name. Defaults to the provider env var name.",
    ),
) -> None:
    target = store_provider_secret(
        provider=provider,
        secret=value,
        service_name=service,
        credential_name=credential_name,
    )
    console.print(
        {
            "provider": target.provider,
            "service_name": target.service_name,
            "credential_name": target.credential_name,
            "stored": True,
        }
    )


@creds_app.command("status")
def creds_status(
    provider: str,
    service: str = typer.Option(
        DEFAULT_CREDENTIAL_SERVICE,
        "--service",
        help="Keychain service name.",
    ),
    credential_name: str | None = typer.Option(
        None,
        "--credential-name",
        help="Override the stored credential name. Defaults to the provider env var name.",
    ),
) -> None:
    console.print(
        credential_status(
            provider=provider,
            service_name=service,
            credential_name=credential_name,
        )
    )


@creds_app.command("delete")
def creds_delete(
    provider: str,
    service: str = typer.Option(
        DEFAULT_CREDENTIAL_SERVICE,
        "--service",
        help="Keychain service name.",
    ),
    credential_name: str | None = typer.Option(
        None,
        "--credential-name",
        help="Override the stored credential name. Defaults to the provider env var name.",
    ),
) -> None:
    target = delete_provider_secret(
        provider=provider,
        service_name=service,
        credential_name=credential_name,
    )
    console.print(
        {
            "provider": target.provider,
            "service_name": target.service_name,
            "credential_name": target.credential_name,
            "deleted": True,
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
    ui_root = _project_root() / "ui"
    env = os.environ.copy()
    env.setdefault("VITE_MAESTRO_API_URL", "http://127.0.0.1:8765")
    backend = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "maestro.server.app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
        ],
        cwd=_project_root(),
        env=env,
    )
    try:
        subprocess.run(["npm", "install"], cwd=ui_root, check=False, env=env)
        subprocess.run(["npm", "run", "dev"], cwd=ui_root, check=False, env=env)
    finally:
        backend.terminate()


if __name__ == "__main__":
    app()
