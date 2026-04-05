from __future__ import annotations

import re

from maestro.core.assumptions import split_assumptions
from maestro.schemas.contracts import CompiledBrief

SECTION_ALIASES = {
    "problem": "problem",
    "problem framing": "problem",
    "users": "target_users",
    "target users": "target_users",
    "outcomes": "outcomes",
    "scope": "scope",
    "non goals": "non_goals",
    "non-goals": "non_goals",
    "constraints": "constraints",
    "risks": "risks",
    "assumptions": "assumptions",
    "questions": "unresolved_questions",
    "unresolved questions": "unresolved_questions",
    "acceptance criteria": "acceptance_criteria",
}


def _normalize_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _split_items(block: str) -> list[str]:
    lines = [line.rstrip() for line in block.splitlines()]
    bullet_items = [
        re.sub(r"^\s*[-*+]\s*", "", line).strip()
        for line in lines
        if re.match(r"^\s*[-*+]\s+", line)
    ]
    if bullet_items:
        return [item for item in bullet_items if item]
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", block) if part.strip()]
    return paragraphs


def compile_product_brief(raw_text: str) -> CompiledBrief:
    text = raw_text.strip()
    lines = text.splitlines()
    title_hint = ""
    section_keys = [
        "problem_points",
        "target_users",
        "outcomes",
        "scope",
        "non_goals",
        "constraints",
        "risks",
        "assumptions",
        "unresolved_questions",
        "acceptance_criteria",
    ]
    sections: dict[str, list[str]] = {field: [] for field in section_keys}
    preamble: list[str] = []
    current_key: str | None = None
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_key, current_lines
        if not current_lines:
            return
        block = "\n".join(current_lines).strip()
        if not block:
            current_lines = []
            return
        items = _split_items(block)
        if current_key is None:
            preamble.extend(items)
        else:
            sections[current_key].extend(items)
        current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            if not title_hint:
                title_hint = stripped.removeprefix("# ").strip()
            continue
        if stripped.startswith("## "):
            flush_current()
            heading = _normalize_heading(stripped.removeprefix("## ").strip())
            current_key = SECTION_ALIASES.get(heading)
            continue
        current_lines.append(line)
    flush_current()

    summary_hint = preamble[0] if preamble else text.splitlines()[0].strip() if text else ""
    if preamble and not sections["problem_points"]:
        sections["problem_points"].append(preamble[0])
    assumption_log, unresolved_questions = split_assumptions(
        sections["assumptions"] + sections["unresolved_questions"],
        source="brief",
    )
    return CompiledBrief(
        raw_text=text,
        title_hint=title_hint,
        summary_hint=summary_hint,
        problem_points=sections["problem_points"],
        target_users=sections["target_users"],
        outcomes=sections["outcomes"],
        scope=sections["scope"],
        non_goals=sections["non_goals"],
        constraints=sections["constraints"],
        risks=sections["risks"],
        assumptions=sections["assumptions"],
        assumption_log=assumption_log,
        unresolved_questions=unresolved_questions,
        acceptance_criteria=sections["acceptance_criteria"],
    )
