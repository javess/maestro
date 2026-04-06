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


class GeminiProvider(LlmProvider):
    def __init__(
        self,
        api_key_env: str = "GEMINI_API_KEY",
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key_env = api_key_env
        self.api_key = api_key
        self._client = client
        self._types_module: Any | None = None
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

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing Gemini API key in environment variable {self.api_key_env}")
        try:
            module = importlib.import_module("google.genai")
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Google Gen AI Python SDK is not installed; run `uv sync --all-extras` to enable it"
            ) from error
        self._types_module = getattr(module, "types", None)
        self._client = module.Client(api_key=api_key)
        logger.info("gemini_client_initialized api_key_env=%s", self.api_key_env)
        return self._client

    def _build_json_config(self, schema: type[SchemaT]) -> Any:
        if self._types_module is None:
            return {
                "response_mime_type": "application/json",
                "response_schema": schema.model_json_schema(),
            }
        return self._types_module.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema.model_json_schema(),
        )

    def _extract_text(self, response: Any) -> str:
        text = getattr(response, "text", None)
        if isinstance(text, str) and text:
            return text
        if isinstance(response, dict) and isinstance(response.get("text"), str):
            return response["text"]
        raise ValueError("Gemini response did not contain text output")

    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        logger.debug("gemini_generate_text model=%s", model)
        log_provider_request(
            logger,
            provider="gemini",
            action="generate_text",
            model=model,
            prompt=prompt,
            metadata=metadata,
        )
        response = self._get_client().models.generate_content(model=model, contents=prompt)
        text = self._extract_text(response)
        log_provider_response(
            logger,
            provider="gemini",
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
        client = self._get_client()
        log_provider_request(
            logger,
            provider="gemini",
            action="generate_structured_native",
            model=model,
            prompt=prompt,
            metadata=metadata,
            schema_name=schema.__name__,
        )
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=self._build_json_config(schema),
            )
            text = self._extract_text(response)
            log_provider_response(
                logger,
                provider="gemini",
                action="generate_structured_native",
                model=model,
                payload=text,
                schema_name=schema.__name__,
            )
            try:
                return schema.model_validate_json(_extract_json_object(text))
            except ValidationError:
                return schema.model_validate(json.loads(_extract_json_object(text)))
        except Exception as error:  # noqa: BLE001
            logger.warning(
                "gemini_generate_structured_fallback model=%s schema=%s error=%s",
                model,
                schema.__name__,
                error,
            )
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
        return True

    def supports_tool_calling(self) -> bool:
        return True

    def model_info(self, model: str) -> ProviderModelInfo:
        return ProviderModelInfo(provider="gemini", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        retryable_names = {"ServiceUnavailable", "TooManyRequests", "DeadlineExceeded"}
        retryable = error.__class__.__name__ in retryable_names
        return ProviderError(provider="gemini", retryable=retryable, message=str(error))
