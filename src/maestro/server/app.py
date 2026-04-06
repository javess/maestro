from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from maestro.cli.main import _config_path, _project_root, _resolve_state_store, _workspace
from maestro.config import load_config
from maestro.core.engine import OrchestratorEngine, build_engine_deps
from maestro.repo.discovery import discover_repo
from maestro.repo.readiness import assess_repo_readiness


class PlanRequest(BaseModel):
    repo_path: str
    brief_path: str
    config_path: str | None = None


class RunActionRequest(BaseModel):
    repo_path: str
    ticket_id: str
    comment: str = ""


class ApiServer:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.futures: dict[str, Future[object]] = {}

    def create_app(self) -> FastAPI:
        app = FastAPI(title="maestro local api", version="0.1.0")

        @app.get("/api/doctor")
        def doctor(repo_path: str, config_path: str | None = None) -> dict[str, object]:
            repo = Path(repo_path).resolve()
            discovery = discover_repo(repo)
            readiness = assess_repo_readiness(repo, discovery)
            cfg = load_config(_config_path(Path(config_path) if config_path else None))
            return {
                "repo_path": str(repo),
                "policy": cfg.policy,
                "repo_type": discovery.repo_info.repo_type,
                "support_tier": readiness.tier,
                "readiness_score": readiness.score,
                "blockers": readiness.blockers,
                "recommendations": readiness.recommendations,
            }

        @app.get("/api/runs")
        def list_runs(repo_path: str) -> list[dict[str, object]]:
            store = _resolve_state_store(Path(repo_path).resolve())
            return [row.model_dump(mode="json") for row in store.list_runs()]

        @app.get("/api/runs/{run_id}")
        def get_run(run_id: str, repo_path: str) -> dict[str, object]:
            store = _resolve_state_store(Path(repo_path).resolve(), run_id)
            return store.load(run_id).model_dump(mode="json")

        @app.post("/api/plan")
        def start_plan(request: PlanRequest) -> dict[str, str]:
            repo = Path(request.repo_path).resolve()
            brief = Path(request.brief_path).resolve()
            deps = build_engine_deps(
                _project_root(),
                _config_path(Path(request.config_path) if request.config_path else None),
                workspace_root=_workspace(repo).root,
            )
            engine = OrchestratorEngine(_project_root(), deps)
            state = engine.new_state(repo, brief)

            def runner() -> object:
                return engine.run_plan(repo, brief)

            self.futures[state.run_id] = self.executor.submit(runner)
            return {"run_id": state.run_id}

        @app.post("/api/runs/{run_id}/approve")
        def approve(run_id: str, request: RunActionRequest) -> dict[str, object]:
            repo = Path(request.repo_path).resolve()
            deps = build_engine_deps(
                _project_root(),
                _config_path(None),
                workspace_root=_workspace(repo).root,
            )
            engine = OrchestratorEngine(_project_root(), deps)
            store = _resolve_state_store(repo, run_id)
            state = store.load(run_id)
            updated = engine.approve_diff(state, request.ticket_id)
            deps.state_store.save(updated)
            return updated.model_dump(mode="json")

        @app.post("/api/runs/{run_id}/reject")
        def reject(run_id: str, request: RunActionRequest) -> dict[str, object]:
            repo = Path(request.repo_path).resolve()
            deps = build_engine_deps(
                _project_root(),
                _config_path(None),
                workspace_root=_workspace(repo).root,
            )
            engine = OrchestratorEngine(_project_root(), deps)
            store = _resolve_state_store(repo, run_id)
            state = store.load(run_id)
            updated = engine.reject_diff(state, request.ticket_id, request.comment, rerun=False)
            deps.state_store.save(updated)
            return updated.model_dump(mode="json")

        @app.post("/api/runs/{run_id}/rerun")
        def rerun(run_id: str, request: RunActionRequest) -> dict[str, object]:
            repo = Path(request.repo_path).resolve()
            deps = build_engine_deps(
                _project_root(),
                _config_path(None),
                workspace_root=_workspace(repo).root,
            )
            engine = OrchestratorEngine(_project_root(), deps)
            store = _resolve_state_store(repo, run_id)
            state = store.load(run_id)
            updated = engine.reject_diff(state, request.ticket_id, request.comment, rerun=True)
            deps.state_store.save(updated)
            return updated.model_dump(mode="json")

        @app.get("/api/runs/{run_id}/future")
        def future_status(run_id: str) -> dict[str, object]:
            future = self.futures.get(run_id)
            if future is None:
                raise HTTPException(status_code=404, detail="Unknown run id")
            return {"done": future.done(), "cancelled": future.cancelled()}

        return app


def create_app() -> FastAPI:
    return ApiServer().create_app()
