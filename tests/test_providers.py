import sys
from types import ModuleType

import pytest

from maestro.providers.anthropic_adapter import AnthropicProvider
from maestro.providers.factory import build_provider
from maestro.providers.gemini_adapter import GeminiProvider
from maestro.providers.openai_adapter import OpenAIProvider


class _FakeKeyring(ModuleType):
    def __init__(self) -> None:
        super().__init__("keyring")
        self.values: dict[tuple[str, str], str] = {}

    def get_password(self, service_name: str, credential_name: str) -> str | None:
        return self.values.get((service_name, credential_name))

    def set_password(self, service_name: str, credential_name: str, secret: str) -> None:
        self.values[(service_name, credential_name)] = secret


@pytest.fixture
def fake_keyring(monkeypatch: pytest.MonkeyPatch) -> _FakeKeyring:
    module = _FakeKeyring()
    monkeypatch.setitem(sys.modules, "keyring", module)
    return module


def test_provider_factory_builds_known_adapters() -> None:
    assert isinstance(build_provider("openai"), OpenAIProvider)
    assert isinstance(build_provider("anthropic"), AnthropicProvider)
    assert isinstance(build_provider("gemini"), GeminiProvider)


def test_provider_factory_passes_api_key_env_overrides() -> None:
    gemini = build_provider({"type": "gemini", "api_key_env": "ALT_GEMINI"})
    claude = build_provider({"type": "anthropic", "api_key_env": "ALT_CLAUDE"})

    assert isinstance(gemini, GeminiProvider)
    assert gemini.api_key_env == "ALT_GEMINI"
    assert isinstance(claude, AnthropicProvider)
    assert claude.api_key_env == "ALT_CLAUDE"


def test_provider_capabilities_are_exposed() -> None:
    provider = OpenAIProvider()
    info = provider.model_info("codex")
    assert info.capabilities.structured_outputs is True
    assert info.capabilities.tool_calling is True


def test_provider_factory_uses_keyring_when_env_is_missing(
    monkeypatch: pytest.MonkeyPatch, fake_keyring: _FakeKeyring
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    fake_keyring.set_password("maestro", "OPENAI_API_KEY", "secure-value")

    provider = build_provider({"type": "openai", "api_key_env": "OPENAI_API_KEY"})

    assert isinstance(provider, OpenAIProvider)
    assert provider.api_key == "secure-value"
