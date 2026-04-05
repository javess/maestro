import shutil
from pathlib import Path

from maestro.repo.discovery import discover_repo
from maestro.repo.impact import analyze_ticket_impact
from maestro.schemas.contracts import Ticket


def _prepare_fixture(tmp_path: Path, fixture: str, extra_files: dict[str, str]) -> Path:
    source = Path(__file__).parent / "fixtures" / fixture
    target = tmp_path / fixture
    shutil.copytree(source, target)
    for relative, content in extra_files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return target


def test_python_impact_analysis_finds_modules_and_tests(tmp_path: Path) -> None:
    root = _prepare_fixture(
        tmp_path,
        "python_repo",
        {
            "src/payments/service.py": "def run(): pass\n",
            "tests/test_payments.py": "def test_run(): pass\n",
            "migrations/0001_init.py": "# migration\n",
        },
    )
    analysis = analyze_ticket_impact(
        Ticket(
            id="TICKET-1",
            title="Payments service flow",
            description="Update payments logic",
            acceptance_criteria=["payments tests pass"],
        ),
        discover_repo(root),
    )

    assert "src/payments" in analysis.likely_touched_modules
    assert "tests/test_payments.py" in analysis.nearby_tests
    assert "migrations/" in analysis.hotspots


def test_monorepo_impact_analysis_slices_workspace_context(tmp_path: Path) -> None:
    root = _prepare_fixture(
        tmp_path,
        "monorepo",
        {
            "packages/api/src/index.ts": "export const api = true;\n",
            "packages/api/test/index.test.ts": "it('works', () => {});\n",
            "infra/deploy.yaml": "kind: Deployment\n",
        },
    )
    analysis = analyze_ticket_impact(
        Ticket(
            id="TICKET-2",
            title="API package changes",
            description="Refine api workspace behavior",
            acceptance_criteria=["api tests pass"],
        ),
        discover_repo(root),
    )

    assert "packages/api" in analysis.likely_touched_modules
    assert any(path.endswith("index.test.ts") for path in analysis.nearby_tests)
    assert "infra/" in analysis.hotspots
    assert any("workspace" in note.lower() for note in analysis.notes)


def test_repo_impact_analysis_supports_fixture_repo_types(tmp_path: Path) -> None:
    fixture_inputs = {
        "node_repo": {
            "src/users/index.ts": "export const users = true;\n",
            "test/users/index.test.ts": "it('works', () => {});\n",
        },
        "go_repo": {
            "internal/auth/service.go": "package auth\n",
            "internal/auth/service_test.go": "package auth\n",
        },
        "rust_repo": {
            "src/lib.rs": "pub fn auth() {}\n",
            "tests/lib_test.rs": "#[test] fn auth() {}\n",
        },
        "java_repo": {
            "src/main/java/com/example/App.java": "class App {}\n",
            "src/test/java/com/example/AppTest.java": "class AppTest {}\n",
        },
    }
    for fixture, files in fixture_inputs.items():
        root = _prepare_fixture(tmp_path, fixture, files)
        analysis = analyze_ticket_impact(
            Ticket(
                id=f"{fixture}-ticket",
                title="Auth service update",
                description="Refine auth behavior",
                acceptance_criteria=["tests pass"],
            ),
            discover_repo(root),
        )
        assert analysis.likely_touched_modules
        assert analysis.coupled_interfaces
        assert analysis.context_slice
