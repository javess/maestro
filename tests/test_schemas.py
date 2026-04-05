from maestro.schemas.contracts import (
    ArtifactManifest,
    Backlog,
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
        outcomes=["a"],
        scope=["b"],
        acceptance_criteria=["c"],
    )
    assert spec.title == "x"


def test_backlog_requires_tickets() -> None:
    backlog = Backlog(
        tickets=[
            Ticket(
                id="T-1",
                title="t",
                description="d",
                acceptance_criteria=["a"],
            )
        ]
    )
    assert backlog.tickets[0].id == "T-1"


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
