from pathlib import Path

from maestro.core.architecture_synthesizer import synthesize_architecture
from maestro.providers.fake import FakeProvider
from maestro.repo.discovery import discover_repo
from maestro.schemas.contracts import Backlog, ProductSpec


def sample_spec() -> ProductSpec:
    return ProductSpec(
        title="Maestro",
        summary="Deterministic orchestration baseline",
        problem="Teams need design-to-execution automation.",
        target_users=["platform engineers"],
        outcomes=["predictable planning"],
        scope=["planning", "review"],
        constraints=["deterministic"],
        risks=["provider drift"],
        acceptance_criteria=["artifacts validate"],
    )


def test_synthesize_architecture_for_python_fixture() -> None:
    root = Path(__file__).parent / "fixtures" / "python_repo"
    artifacts = synthesize_architecture(sample_spec(), discover_repo(root))

    assert artifacts.system_context.system_name == "Maestro"
    assert any(module.module_id == "python_repo" for module in artifacts.module_boundaries)
    assert any(flow.flow_id == "brief_to_architecture" for flow in artifacts.data_flows)
    assert artifacts.api_contracts[0].producer_module_id == "delivery_orchestrator"


def test_synthesize_architecture_adds_workspace_slice_for_monorepo_fixture() -> None:
    root = Path(__file__).parent / "fixtures" / "monorepo"
    artifacts = synthesize_architecture(sample_spec(), discover_repo(root))

    assert any(module.module_id == "workspace_slice" for module in artifacts.module_boundaries)


def test_fake_provider_backlog_preserves_architecture_artifacts() -> None:
    architecture = synthesize_architecture(
        sample_spec(),
        discover_repo(Path(__file__).parent / "fixtures" / "python_repo"),
    )
    provider = FakeProvider()

    backlog = provider.generate_structured(
        prompt="x",
        model="fake",
        schema=Backlog,
        metadata={
            "product_spec": sample_spec().model_dump(mode="json"),
            "architecture_artifacts": architecture.model_dump(mode="json"),
        },
    )

    assert backlog.architecture_artifacts is not None
    assert backlog.architecture_artifacts.system_context.system_name == "Maestro"
