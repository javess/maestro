import os
from pathlib import Path

from maestro.config import load_config, load_env_file


def test_load_env_file_populates_missing_environment_variables(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_API_KEY=test-key\n# comment\nEMPTY=\n")

    load_env_file(env_path)

    assert os.environ["OPENAI_API_KEY"] == "test-key"
    assert os.environ["EMPTY"] == ""


def test_load_env_file_does_not_override_existing_values(tmp_path: Path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_API_KEY=from-file\n")
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")

    load_env_file(env_path)

    assert os.environ["OPENAI_API_KEY"] == "from-env"


def test_load_config_reads_env_file_next_to_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=from-config-dir\n")
    config_path = tmp_path / "maestro.yaml"
    config_path.write_text(
        "providers:\n"
        "  openai:\n"
        "    type: openai\n"
        "    api_key_env: OPENAI_API_KEY\n"
        "llm:\n"
        "  coder:\n"
        "    provider: openai\n"
        "    model: gpt-5\n"
        "fallbacks: {}\n"
        "policy: default\n"
    )

    config = load_config(config_path)

    assert config.providers["openai"]["api_key_env"] == "OPENAI_API_KEY"
    assert os.environ["OPENAI_API_KEY"] == "from-config-dir"
