from maestro.providers.anthropic_adapter import AnthropicProvider
from maestro.providers.factory import build_provider
from maestro.providers.gemini_adapter import GeminiProvider
from maestro.providers.openai_adapter import OpenAIProvider


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
