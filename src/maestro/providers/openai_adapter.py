from __future__ import annotations

import importlib
import json
import os
from typing import Any

from pydantic import ValidationError

from maestro.core.structured import _extract_json_object
from maestro.providers.base import LlmProvider, SchemaT
from maestro.schemas.contracts import ProviderCapability, ProviderError, ProviderModelInfo


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

    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        response = self._get_client().responses.create(model=model, input=prompt)
        return self._extract_text(response)

    def generate_structured(
        self,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> SchemaT:
        client = self._get_client()
        if hasattr(client.responses, "parse"):
            response = client.responses.parse(model=model, input=prompt, text_format=schema)
            return schema.model_validate(self._extract_parsed(response))

        raw = self.generate_text(
            prompt=(
                f"{prompt}\nReturn only valid JSON matching this schema name: "
                f"{schema.__name__}."
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
