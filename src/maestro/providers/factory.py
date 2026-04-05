from __future__ import annotations

from typing import Any

from maestro.providers.anthropic_adapter import AnthropicProvider
from maestro.providers.base import LlmProvider
from maestro.providers.fake import FakeProvider
from maestro.providers.gemini_adapter import GeminiProvider
from maestro.providers.openai_adapter import OpenAIProvider


def build_provider(provider_type: str | dict[str, Any]) -> LlmProvider:
    config = provider_type if isinstance(provider_type, dict) else {"type": provider_type}
    provider_name = config["type"]
    mapping = {
        "fake": FakeProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "gemini": GeminiProvider,
    }
    provider_class = mapping.get(provider_name)
    if provider_class is None:
        raise ValueError(f"Unsupported provider type: {provider_name}")
    if provider_class is OpenAIProvider:
        return provider_class(api_key_env=config.get("api_key_env", "OPENAI_API_KEY"))
    return provider_class()
