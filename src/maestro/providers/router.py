from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from maestro.core.structured import StructuredAttempt, StructuredOutputRunner
from maestro.providers.base import LlmProvider, SchemaT
from maestro.schemas.contracts import MaestroConfig, ProviderError

logger = logging.getLogger(__name__)


@dataclass
class RoutedGeneration:
    provider_name: str
    model: str
    attempts: list[StructuredAttempt]


class ProviderRouter:
    def __init__(
        self,
        config: MaestroConfig,
        providers: Mapping[str, LlmProvider],
        runner: StructuredOutputRunner | None = None,
    ) -> None:
        self.config = config
        self.providers = providers
        self.runner = runner or StructuredOutputRunner()

    def generate_structured(
        self,
        *,
        role: str,
        prompt: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[SchemaT, RoutedGeneration]:
        sequence = [self.config.llm[role], *self.config.fallbacks.get(role, [])]
        errors: list[ProviderError] = []
        for target in sequence:
            provider = self.providers[target.provider]
            logger.info(
                "provider_attempt role=%s provider=%s model=%s",
                role,
                target.provider,
                target.model,
            )
            try:
                result, attempts = self.runner.generate(
                    provider,
                    prompt=prompt,
                    model=target.model,
                    schema=schema,
                    metadata=metadata,
                )
                return result, RoutedGeneration(
                    provider_name=target.provider,
                    model=target.model,
                    attempts=attempts,
                )
            except Exception as error:  # noqa: BLE001
                normalized = provider.normalize_error(error)
                errors.append(normalized)
                logger.warning(
                    "provider_failed role=%s provider=%s retryable=%s message=%s",
                    role,
                    normalized.provider,
                    normalized.retryable,
                    normalized.message,
                )
        formatted = ", ".join(f"{item.provider}:{item.message}" for item in errors)
        raise RuntimeError(f"All providers failed for role {role}: {formatted}")
