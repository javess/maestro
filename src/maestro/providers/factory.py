from __future__ import annotations

from maestro.providers.anthropic_adapter import AnthropicProvider
from maestro.providers.base import LlmProvider
from maestro.providers.fake import FakeProvider
from maestro.providers.gemini_adapter import GeminiProvider
from maestro.providers.openai_adapter import OpenAIProvider


def build_provider(provider_type: str) -> LlmProvider:
    mapping = {
        "fake": FakeProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "gemini": GeminiProvider,
    }
    provider_class = mapping.get(provider_type)
    if provider_class is None:
        raise ValueError(f"Unsupported provider type: {provider_type}")
    return provider_class()
