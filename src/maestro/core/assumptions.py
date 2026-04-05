from __future__ import annotations

import re
from typing import Literal

from maestro.schemas.contracts import AssumptionKind, AssumptionRecord

PREFIX_RULES = (
    ("fact:", AssumptionKind.stated_fact),
    ("stated:", AssumptionKind.stated_fact),
    ("inferred:", AssumptionKind.inferred_fact),
    ("infer:", AssumptionKind.inferred_fact),
    ("guess:", AssumptionKind.guess),
    ("question:", AssumptionKind.unresolved_question),
    ("unknown:", AssumptionKind.unresolved_question),
)


def classify_assumption(
    statement: str,
    *,
    source: Literal["brief", "product_spec", "planning"] = "brief",
) -> AssumptionRecord:
    text = re.sub(r"\s+", " ", statement.strip())
    lowered = text.lower()
    for prefix, kind in PREFIX_RULES:
        if lowered.startswith(prefix):
            normalized = text[len(prefix) :].strip() or text
            return AssumptionRecord(kind=kind, statement=normalized, source=source)
    if text.endswith("?"):
        return AssumptionRecord(
            kind=AssumptionKind.unresolved_question,
            statement=text,
            source=source,
        )
    if any(token in lowered for token in ("likely", "probably", "maybe", "assume")):
        return AssumptionRecord(kind=AssumptionKind.guess, statement=text, source=source)
    return AssumptionRecord(kind=AssumptionKind.stated_fact, statement=text, source=source)


def split_assumptions(
    statements: list[str],
    *,
    source: Literal["brief", "product_spec", "planning"] = "brief",
) -> tuple[list[AssumptionRecord], list[str]]:
    records = [
        classify_assumption(statement, source=source)
        for statement in statements
        if statement
    ]
    unresolved = [
        record.statement for record in records if record.kind is AssumptionKind.unresolved_question
    ]
    return records, unresolved
