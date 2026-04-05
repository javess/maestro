from __future__ import annotations

from typing import Any

from maestro.providers.base import LlmProvider, SchemaT
from maestro.schemas.contracts import ProviderCapability, ProviderError, ProviderModelInfo


class GeminiProvider(LlmProvider):
    def __init__(self) -> None:
        self._capabilities = ProviderCapability(
            structured_outputs=True,
            tool_calling=True,
            streaming=True,
            vision=True,
            long_context=True,
            code_specialized=False,
            json_mode=True,
        )

    @property
    def capabilities(self) -> ProviderCapability:
        return self._capabilities

    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        raise NotImplementedError(
            "Gemini integration requires credentials and runtime client wiring"
        )

    def generate_structured(
        self,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> SchemaT:
        raise NotImplementedError(
            "Gemini integration requires credentials and runtime client wiring"
        )

    def supports_structured_output(self) -> bool:
        return True

    def supports_tool_calling(self) -> bool:
        return True

    def model_info(self, model: str) -> ProviderModelInfo:
        return ProviderModelInfo(provider="gemini", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        return ProviderError(provider="gemini", retryable=True, message=str(error))
