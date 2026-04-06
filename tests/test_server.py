from pathlib import Path

from fastapi.testclient import TestClient

from maestro.server.app import create_app


def test_doctor_endpoint_returns_readiness(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    client = TestClient(create_app())
    config = Path(__file__).resolve().parents[1] / "examples" / "maestro.example.yaml"

    response = client.get(
        "/api/doctor",
        params={
            "repo_path": str(tmp_path),
            "config_path": str(config),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["repo_type"] == "python"
    assert "support_tier" in payload


def test_plan_endpoint_starts_run_and_lists_it(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    brief = project_root / "examples" / "brief.md"
    config = project_root / "examples" / "maestro.example.yaml"

    client = TestClient(create_app())
    response = client.post(
        "/api/plan",
        json={
            "repo_path": str(repo),
            "brief_path": str(brief),
            "config_path": str(config),
        },
    )

    assert response.status_code == 200
    run_id = response.json()["run_id"]

    runs = client.get("/api/runs", params={"repo_path": str(repo)})
    assert runs.status_code == 200
    assert any(item["run_id"] == run_id for item in runs.json())

    scheduler = client.get("/api/scheduler")
    assert scheduler.status_code == 200
    assert any(item["run_id"] == run_id for item in scheduler.json())


def test_scheduler_cancel_endpoint(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    brief = project_root / "examples" / "brief.md"
    config = project_root / "examples" / "maestro.example.yaml"

    client = TestClient(create_app())
    response = client.post(
        "/api/plan",
        json={
            "repo_path": str(repo),
            "brief_path": str(brief),
            "config_path": str(config),
        },
    )
    run_id = response.json()["run_id"]
    cancel = client.post(f"/api/runs/{run_id}/cancel")
    assert cancel.status_code == 200
    assert "cancelled" in cancel.json()


def test_control_plane_endpoint_returns_snapshot(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    config = project_root / "examples" / "maestro.example.yaml"

    client = TestClient(create_app())
    response = client.get(
        "/api/control-plane",
        params={
            "repo_path": str(repo),
            "config_path": str(config),
            "write_default": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["config"]["organization"] == "local"
    assert "hosted_extension_points" in payload["boundary"]
