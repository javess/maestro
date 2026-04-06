from __future__ import annotations

from typing import Any

from maestro.credentials import DEFAULT_CREDENTIAL_SERVICE, resolve_provider_secret
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
    api_key_env = config.get("api_key_env")
    credential_service = config.get("credential_service", DEFAULT_CREDENTIAL_SERVICE)
    credential_name = config.get("credential_name")
    api_key = (
        resolve_provider_secret(
            api_key_env=api_key_env,
            provider=provider_name,
            service_name=credential_service,
            credential_name=credential_name,
        )
        if api_key_env
        else None
    )
    if provider_class is OpenAIProvider:
        return provider_class(
            api_key_env=config.get("api_key_env", "OPENAI_API_KEY"),
            api_key=api_key,
        )
    if provider_class is AnthropicProvider:
        return provider_class(
            api_key_env=config.get("api_key_env", "ANTHROPIC_API_KEY"),
            api_key=api_key,
        )
    if provider_class is GeminiProvider:
        return provider_class(
            api_key_env=config.get("api_key_env", "GEMINI_API_KEY"),
            api_key=api_key,
        )
    return provider_class()
