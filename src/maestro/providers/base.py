from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from maestro.schemas.contracts import ProviderCapability, ProviderError, ProviderModelInfo

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LlmProvider(ABC):
    @abstractmethod
    def generate_text(
        self,
        *,
        prompt: str,
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        *,
        prompt: str,
        model: str,
        schema: type[SchemaT],
        metadata: dict[str, Any] | None = None,
    ) -> SchemaT:
        raise NotImplementedError

    @abstractmethod
    def supports_structured_output(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def supports_tool_calling(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def model_info(self, model: str) -> ProviderModelInfo:
        raise NotImplementedError

    @abstractmethod
    def normalize_error(self, error: Exception) -> ProviderError:
        raise NotImplementedError

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapability:
        raise NotImplementedError
