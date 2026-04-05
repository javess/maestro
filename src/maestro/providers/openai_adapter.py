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


class OpenAIProvider(LlmProvider):
    def __init__(self, api_key_env: str = "OPENAI_API_KEY", client: Any | None = None) -> None:
        self.api_key_env = api_key_env
        self._client = client
        self._capabilities = ProviderCapability(
            structured_outputs=True,
            tool_calling=True,
            streaming=True,
            vision=True,
            long_context=True,
            code_specialized=True,
            json_mode=True,
        )

    @property
    def capabilities(self) -> ProviderCapability:
        return self._capabilities

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing OpenAI API key in environment variable {self.api_key_env}")
        try:
            module = importlib.import_module("openai")
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "OpenAI Python SDK is not installed; run `uv sync --all-extras` to enable it"
            ) from error
        self._client = module.OpenAI(api_key=api_key)
        logger.info("openai_client_initialized api_key_env=%s", self.api_key_env)
        return self._client

    def _extract_text(self, response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text:
            return output_text
        if isinstance(response, dict):
            if isinstance(response.get("output_text"), str):
                return response["output_text"]
            output = response.get("output", [])
        else:
            output = getattr(response, "output", [])
        chunks: list[str] = []
        for item in output or []:
            content = getattr(item, "content", None)
            if content is None and isinstance(item, dict):
                content = item.get("content", [])
            for part in content or []:
                text = getattr(part, "text", None)
                if isinstance(text, str):
                    chunks.append(text)
                elif isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
        if chunks:
            return "".join(chunks)
        raise ValueError("OpenAI response did not contain text output")

    def _extract_parsed(self, response: Any) -> Any:
        output_parsed = getattr(response, "output_parsed", None)
        if output_parsed is not None:
            return output_parsed
        if isinstance(response, dict) and "output_parsed" in response:
            return response["output_parsed"]
        output = getattr(response, "output", None)
        if output is None and isinstance(response, dict):
            output = response.get("output", [])
        for item in output or []:
            content = getattr(item, "content", None)
            if content is None and isinstance(item, dict):
                content = item.get("content", [])
            for part in content or []:
                parsed = getattr(part, "parsed", None)
                if parsed is not None:
                    return parsed
                if isinstance(part, dict) and "parsed" in part:
                    return part["parsed"]
        raise ValueError("OpenAI structured response did not contain parsed output")

    def _is_schema_compatibility_error(self, error: Exception) -> bool:
        message = str(error)
        markers = (
            "invalid_json_schema",
            "Invalid schema for response_format",
            "text.format.schema",
        )
        return any(marker in message for marker in markers)

    def _schema_has_unsupported_additional_properties(self, value: Any) -> bool:
        if isinstance(value, dict):
            additional_properties = value.get("additionalProperties")
            if isinstance(additional_properties, dict):
                return True
            return any(
                self._schema_has_unsupported_additional_properties(item)
                for item in value.values()
            )
        if isinstance(value, list):
            return any(self._schema_has_unsupported_additional_properties(item) for item in value)
        return False

    def _supports_native_schema(self, schema: type[SchemaT]) -> bool:
        schema_json = schema.model_json_schema()
        return not self._schema_has_unsupported_additional_properties(schema_json)

    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        logger.debug("openai_generate_text model=%s", model)
        log_provider_request(
            logger,
            provider="openai",
            action="generate_text",
            model=model,
            prompt=prompt,
            metadata=metadata,
        )
        response = self._get_client().responses.create(model=model, input=prompt)
        text = self._extract_text(response)
        log_provider_response(
            logger,
            provider="openai",
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
        if hasattr(client.responses, "parse") and self._supports_native_schema(schema):
            log_provider_request(
                logger,
                provider="openai",
                action="generate_structured_native",
                model=model,
                prompt=prompt,
                metadata=metadata,
                schema_name=schema.__name__,
            )
            try:
                logger.info(
                    "openai_generate_structured_native model=%s schema=%s",
                    model,
                    schema.__name__,
                )
                response = client.responses.parse(model=model, input=prompt, text_format=schema)
            except Exception as error:  # noqa: BLE001
                if not self._is_schema_compatibility_error(error):
                    raise
                logger.warning(
                    "openai_native_schema_rejected model=%s schema=%s error=%s",
                    model,
                    schema.__name__,
                    error,
                )
            else:
                parsed = self._extract_parsed(response)
                log_provider_response(
                    logger,
                    provider="openai",
                    action="generate_structured_native",
                    model=model,
                    payload=json.dumps(parsed, indent=2, sort_keys=True),
                    schema_name=schema.__name__,
                )
                return schema.model_validate(parsed)
        elif hasattr(client.responses, "parse"):
            logger.info(
                "openai_native_schema_skipped_incompatible model=%s schema=%s",
                model,
                schema.__name__,
            )

        logger.info(
            "openai_generate_structured_fallback model=%s schema=%s",
            model,
            schema.__name__,
        )
        log_provider_request(
            logger,
            provider="openai",
            action="generate_structured_fallback",
            model=model,
            prompt=prompt,
            metadata=metadata,
            schema_name=schema.__name__,
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
        return ProviderModelInfo(provider="openai", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        retryable_names = {
            "APIConnectionError",
            "APITimeoutError",
            "RateLimitError",
            "InternalServerError",
        }
        retryable = error.__class__.__name__ in retryable_names
        return ProviderError(provider="openai", retryable=retryable, message=str(error))
