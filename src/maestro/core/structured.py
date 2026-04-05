from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from maestro.providers.base import LlmProvider, SchemaT


@dataclass
class StructuredAttempt:
    strategy: str
    success: bool
    error: str | None = None


def _extract_json_object(raw: str) -> str:
    stripped = raw.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        body = "\n".join(line for line in lines[1:] if line.strip() != "```")
        return body.strip()
    start = min(
        [index for index in [stripped.find("{"), stripped.find("[")] if index != -1],
        default=0,
    )
    return stripped[start:]


class StructuredOutputRunner:
    def __init__(self, max_repair_attempts: int = 2) -> None:
        self.max_repair_attempts = max_repair_attempts

    def generate(
        self,
        provider: LlmProvider,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[SchemaT, list[StructuredAttempt]]:
        attempts: list[StructuredAttempt] = []
        if provider.supports_structured_output():
            result = provider.generate_structured(
                prompt=prompt,
                model=model,
                schema=schema,
                metadata=metadata,
            )
            attempts.append(StructuredAttempt(strategy="native_structured", success=True))
            return result, attempts

        raw = provider.generate_text(prompt=prompt, model=model, metadata=metadata)
        try:
            parsed = schema.model_validate_json(_extract_json_object(raw))
            attempts.append(StructuredAttempt(strategy="json_mode_parse", success=True))
            return parsed, attempts
        except ValidationError as error:
            attempts.append(
                StructuredAttempt(strategy="json_mode_parse", success=False, error=str(error))
            )

        repair_prompt = (
            f"Repair the following output into valid JSON for the requested schema.\nOUTPUT={raw}"
        )
        for _ in range(self.max_repair_attempts):
            candidate = provider.generate_text(
                prompt=repair_prompt,
                model=model,
                metadata=metadata,
            )
            try:
                payload = json.loads(_extract_json_object(candidate))
                parsed = schema.model_validate(payload)
                attempts.append(StructuredAttempt(strategy="repair_retry", success=True))
                return parsed, attempts
            except (ValidationError, json.JSONDecodeError) as error:
                attempts.append(
                    StructuredAttempt(strategy="repair_retry", success=False, error=str(error))
                )
        raise ValueError(f"Failed to produce valid structured output for {schema.__name__}")
