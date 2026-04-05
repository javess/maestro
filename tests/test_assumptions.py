from maestro.core.assumptions import classify_assumption, split_assumptions
from maestro.schemas.contracts import AssumptionKind


def test_classify_assumption_uses_prefix_rules() -> None:
    assert classify_assumption("fact: Repo already has CI").kind is AssumptionKind.stated_fact
    assert (
        classify_assumption("inferred: billing is sensitive").kind
        is AssumptionKind.inferred_fact
    )
    assert classify_assumption("guess: deployment is manual").kind is AssumptionKind.guess
    assert (
        classify_assumption("question: who approves release?").kind
        is AssumptionKind.unresolved_question
    )


def test_split_assumptions_returns_unresolved_questions() -> None:
    records, unresolved = split_assumptions(
        ["fact: CI exists", "Which team owns deploys?", "maybe there is a staging env"],
        source="brief",
    )

    assert len(records) == 3
    assert unresolved == ["Which team owns deploys?"]
    assert records[2].kind is AssumptionKind.guess
