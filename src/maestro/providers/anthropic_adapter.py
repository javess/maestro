from __future__ import annotations

import importlib
import json
import logging
import os
from typing import Any

from pydantic import ValidationError

from maestro.core.structured import _extract_json_object
from maestro.logging import log_provider_request, log_provider_response
from maestro.providers.base import LlmProvider, SchemaT
from maestro.schemas.contracts import ProviderCapability, ProviderError, ProviderModelInfo

logger = logging.getLogger(__name__)


class AnthropicProvider(LlmProvider):
    def __init__(
        self,
        api_key_env: str = "ANTHROPIC_API_KEY",
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key_env = api_key_env
        self.api_key = api_key
        self._client = client
        self._capabilities = ProviderCapability(
            structured_outputs=False,
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

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing Anthropic API key in environment variable {self.api_key_env}"
            )
        try:
            module = importlib.import_module("anthropic")
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Anthropic Python SDK is not installed; run `uv sync --all-extras` to enable it"
            ) from error
        self._client = module.Anthropic(api_key=api_key)
        logger.info("anthropic_client_initialized api_key_env=%s", self.api_key_env)
        return self._client

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", None)
        if content is None and isinstance(response, dict):
            content = response.get("content", [])
        chunks: list[str] = []
        for part in content or []:
            text = getattr(part, "text", None)
            if isinstance(text, str):
                chunks.append(text)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
        if chunks:
            return "".join(chunks)
        raise ValueError("Anthropic response did not contain text output")

    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        logger.debug("anthropic_generate_text model=%s", model)
        log_provider_request(
            logger,
            provider="claude",
            action="generate_text",
            model=model,
            prompt=prompt,
            metadata=metadata,
        )
        response = self._get_client().messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        text = self._extract_text(response)
        log_provider_response(
            logger,
            provider="claude",
            action="generate_text",
            model=model,
            payload=text,
        )
        return text

    def generate_structured(
        self,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> SchemaT:
        raw = self.generate_text(
            prompt=(
                f"{prompt}\nReturn only valid JSON matching this schema exactly. "
                f"Schema name: {schema.__name__}.\n"
                f"JSON schema:\n{json.dumps(schema.model_json_schema(), indent=2, sort_keys=True)}"
            ),
            model=model,
            metadata=metadata,
        )
        try:
            return schema.model_validate_json(_extract_json_object(raw))
        except ValidationError:
            return schema.model_validate(json.loads(_extract_json_object(raw)))

    def supports_structured_output(self) -> bool:
        return False

    def supports_tool_calling(self) -> bool:
        return True

    def model_info(self, model: str) -> ProviderModelInfo:
        return ProviderModelInfo(provider="claude", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        retryable_names = {"APIConnectionError", "RateLimitError", "InternalServerError"}
        retryable = error.__class__.__name__ in retryable_names
        return ProviderError(provider="claude", retryable=retryable, message=str(error))
