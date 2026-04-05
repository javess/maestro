from maestro.schemas.architecture import ArchitectureArtifacts, SystemContext
from maestro.schemas.contracts import (
    ArtifactManifest,
    AssumptionKind,
    AssumptionRecord,
    Backlog,
    CompiledBrief,
    DiffSummary,
    EvidenceBundle,
    PolicyFinding,
    ProductSpec,
    RollbackNote,
    Ticket,
)


def test_product_spec_round_trip() -> None:
    spec = ProductSpec(
        title="x",
        summary="y",
        problem="z",
        target_users=["u"],
        outcomes=["a"],
        scope=["b"],
        constraints=["c1"],
        assumptions=["a1"],
        assumption_log=[
            AssumptionRecord(
                kind=AssumptionKind.stated_fact,
                statement="a1",
                source="product_spec",
            )
        ],
        unresolved_questions=["q1?"],
        acceptance_criteria=["c"],
    )
    assert spec.title == "x"
    assert spec.problem == "z"
    assert spec.assumption_log[0].kind is AssumptionKind.stated_fact


def test_compiled_brief_defaults() -> None:
    brief = CompiledBrief(raw_text="Build something")
    assert brief.title_hint == ""
    assert brief.problem_points == []
    assert brief.assumption_log == []


def test_backlog_requires_tickets() -> None:
    backlog = Backlog(
        tickets=[
            Ticket(
                id="T-1",
                title="t",
                description="d",
                acceptance_criteria=["a"],
            )
        ],
        assumption_log=[
            AssumptionRecord(
                kind=AssumptionKind.guess,
                statement="API shape may change",
                source="planning",
            )
        ],
        architecture_artifacts=ArchitectureArtifacts(
            system_context=SystemContext(system_name="maestro", summary="x")
        ),
    )
    assert backlog.tickets[0].id == "T-1"
    assert backlog.assumption_log[0].source == "planning"
    assert backlog.architecture_artifacts is not None


def test_evidence_bundle_defaults_and_manifest_reference() -> None:
    bundle = EvidenceBundle(bundle_id="bundle-1", run_id="run-1", ticket_id="T-1")
    manifest = ArtifactManifest(run_id="run-1")
    assert bundle.diff_summary == DiffSummary()
    assert manifest.evidence_bundles == []


def test_evidence_bundle_supports_placeholder_sections() -> None:
    bundle = EvidenceBundle(
        bundle_id="bundle-2",
        run_id="run-1",
        diff_summary=DiffSummary(changed_files=["src/x.py"], file_count=1, summary="one file"),
        policy_findings=[PolicyFinding(rule="require_tests", outcome="warn", detail="placeholder")],
        rollback_notes=[RollbackNote(summary="manual rollback", steps=["revert commit"])],
    )
    assert bundle.diff_summary.file_count == 1
    assert bundle.policy_findings[0].rule == "require_tests"
    assert bundle.rollback_notes[0].summary == "manual rollback"
