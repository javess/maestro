from maestro.core.product_brief import compile_product_brief


def test_compile_product_brief_extracts_markdown_sections() -> None:
    brief = compile_product_brief(
        """# Payments Console

Build a safer billing workflow.

## Users
- Finance operators
- Support engineers

## Outcomes
- Reduce manual billing errors

## Constraints
- Keep deterministic outputs

## Acceptance Criteria
- Billing changes are reviewable
"""
    )

    assert brief.title_hint == "Payments Console"
    assert brief.summary_hint == "Build a safer billing workflow."
    assert brief.problem_points == ["Build a safer billing workflow."]
    assert brief.target_users == ["Finance operators", "Support engineers"]
    assert brief.outcomes == ["Reduce manual billing errors"]
    assert brief.constraints == ["Keep deterministic outputs"]
    assert brief.acceptance_criteria == ["Billing changes are reviewable"]
    assert brief.unresolved_questions == []


def test_compile_product_brief_handles_plain_text_without_sections() -> None:
    brief = compile_product_brief("Build a deterministic orchestration framework.")

    assert brief.title_hint == ""
    assert brief.summary_hint == "Build a deterministic orchestration framework."
    assert brief.problem_points == ["Build a deterministic orchestration framework."]


def test_compile_product_brief_tracks_assumptions_and_questions() -> None:
    brief = compile_product_brief(
        """# Release Tool

## Assumptions
- fact: CI already exists
- inferred: deploy steps are manual

## Questions
- Who approves production releases?
"""
    )

    assert [item.kind.value for item in brief.assumption_log] == [
        "stated_fact",
        "inferred_fact",
        "unresolved_question",
    ]
    assert brief.unresolved_questions == ["Who approves production releases?"]
