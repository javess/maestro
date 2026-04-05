from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from maestro.schemas.contracts import RepoDiscovery, RepoInfo


class RepoAdapter(ABC):
    name = "generic"

    @abstractmethod
    def matches(self, root: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def discover(self, root: Path) -> RepoDiscovery:
        raise NotImplementedError


class PythonRepoAdapter(RepoAdapter):
    name = "python"

    def matches(self, root: Path) -> bool:
        return (root / "pyproject.toml").exists()

    def discover(self, root: Path) -> RepoDiscovery:
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["Detected pyproject.toml"],
            repo_info=RepoInfo(
                root=root,
                repo_type="python",
                build_commands=["uv sync"],
                test_commands=["uv run pytest"],
                lint_commands=["uv run ruff check .", "uv run ty check"],
                risky_paths=["migrations/", ".github/"],
                guidance=["Use isolated virtual environments", "Preserve typing discipline"],
            ),
        )


class NodeRepoAdapter(RepoAdapter):
    name = "node"

    def matches(self, root: Path) -> bool:
        return (root / "package.json").exists()

    def discover(self, root: Path) -> RepoDiscovery:
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["Detected package.json"],
            repo_info=RepoInfo(
                root=root,
                repo_type="node",
                build_commands=["npm install"],
                test_commands=["npm test"],
                lint_commands=["npm run lint"],
                risky_paths=["package-lock.json"],
                guidance=["Prefer package manager scripts"],
            ),
        )


class GoRepoAdapter(RepoAdapter):
    name = "go"

    def matches(self, root: Path) -> bool:
        return (root / "go.mod").exists()

    def discover(self, root: Path) -> RepoDiscovery:
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["Detected go.mod"],
            repo_info=RepoInfo(
                root=root,
                repo_type="go",
                build_commands=["go build ./..."],
                test_commands=["go test ./..."],
                lint_commands=["gofmt -w ."],
                risky_paths=["vendor/"],
                guidance=["Run gofmt on touched files"],
            ),
        )


class RustRepoAdapter(RepoAdapter):
    name = "rust"

    def matches(self, root: Path) -> bool:
        return (root / "Cargo.toml").exists()

    def discover(self, root: Path) -> RepoDiscovery:
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["Detected Cargo.toml"],
            repo_info=RepoInfo(
                root=root,
                repo_type="rust",
                build_commands=["cargo build"],
                test_commands=["cargo test"],
                lint_commands=["cargo fmt --check", "cargo clippy --all-targets --all-features"],
                risky_paths=["Cargo.lock"],
                guidance=["Run formatting and clippy before review"],
            ),
        )


class JavaRepoAdapter(RepoAdapter):
    name = "java"

    def matches(self, root: Path) -> bool:
        return (root / "pom.xml").exists() or (root / "build.gradle").exists()

    def discover(self, root: Path) -> RepoDiscovery:
        build = ["./gradlew build"] if (root / "build.gradle").exists() else ["mvn test"]
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["Detected Java build file"],
            repo_info=RepoInfo(
                root=root,
                repo_type="java",
                build_commands=build,
                test_commands=build,
                lint_commands=[],
                risky_paths=["src/main/resources/"],
                guidance=["Respect wrapper scripts when available"],
            ),
        )


class MonorepoAdapter(RepoAdapter):
    name = "monorepo"
    markers = ["pnpm-workspace.yaml", "turbo.json", "nx.json"]

    def matches(self, root: Path) -> bool:
        return any((root / marker).exists() for marker in self.markers)

    def discover(self, root: Path) -> RepoDiscovery:
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["Detected monorepo workspace marker"],
            repo_info=RepoInfo(
                root=root,
                repo_type="monorepo",
                build_commands=["npm run build --workspaces"],
                test_commands=["npm test --workspaces"],
                lint_commands=["npm run lint --workspaces"],
                risky_paths=["packages/shared/", "infra/"],
                guidance=["Slice context to affected package paths"],
            ),
        )


class GenericFallbackAdapter(RepoAdapter):
    name = "generic"

    def matches(self, root: Path) -> bool:
        return True

    def discover(self, root: Path) -> RepoDiscovery:
        return RepoDiscovery(
            adapter_name=self.name,
            reasons=["No specialized adapter matched"],
            repo_info=RepoInfo(
                root=root,
                repo_type="generic",
                build_commands=[],
                test_commands=[],
                lint_commands=[],
                risky_paths=[],
                guidance=["Inspect repository conventions before coding"],
            ),
        )


def default_adapters() -> list[RepoAdapter]:
    return [
        MonorepoAdapter(),
        PythonRepoAdapter(),
        NodeRepoAdapter(),
        GoRepoAdapter(),
        RustRepoAdapter(),
        JavaRepoAdapter(),
        GenericFallbackAdapter(),
    ]
