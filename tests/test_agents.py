from pathlib import Path

from maestro.agents.roles import _prompt_text


def test_prompt_text_includes_role_skill_when_present(tmp_path: Path) -> None:
    prompt_root = tmp_path / "prompts"
    skill_root = tmp_path / "skills" / "coder"
    prompt_root.mkdir(parents=True)
    skill_root.mkdir(parents=True)
    (prompt_root / "coder.md").write_text("Return only CodeResult.")
    (skill_root / "SKILL.md").write_text("# coder\n- Keep changes small.")

    prompt = _prompt_text(prompt_root, "coder")

    assert "Return only CodeResult." in prompt
    assert "ROLE_SKILL:" in prompt
    assert "Keep changes small." in prompt


def test_prompt_text_returns_prompt_only_when_skill_is_missing(tmp_path: Path) -> None:
    prompt_root = tmp_path / "prompts"
    prompt_root.mkdir(parents=True)
    (prompt_root / "reviewer.md").write_text("Return only ReviewResult.")

    prompt = _prompt_text(prompt_root, "reviewer")

    assert prompt == "Return only ReviewResult."
