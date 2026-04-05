from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from maestro.providers.base import LlmProvider
from maestro.schemas.contracts import Backlog, CodeResult, ProductSpec, ReviewResult

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def _prompt_text(prompt_root: Path, name: str) -> str:
    return (prompt_root / f"{name}.md").read_text()


class StructuredAgent:
    def __init__(
        self,
        provider: LlmProvider,
        model: str,
        prompt_root: Path,
        prompt_name: str,
    ) -> None:
        self.provider = provider
        self.model = model
        self.prompt_root = prompt_root
        self.prompt_name = prompt_name

    def run(self, schema: type[SchemaT], payload: dict[str, Any]) -> SchemaT:
        prompt = _prompt_text(self.prompt_root, self.prompt_name)
        return self.provider.generate_structured(
            prompt=f"{prompt}\nINPUT={payload}",
            model=self.model,
            schema=schema,
            metadata=payload,
        )


class ProductDesignerAgent(StructuredAgent):
    def run_spec(self, payload: dict[str, Any]) -> ProductSpec:
        return self.run(ProductSpec, payload)


class CeremonyMasterAgent(StructuredAgent):
    def run_backlog(self, payload: dict[str, Any]) -> Backlog:
        return self.run(Backlog, payload)


class CoderAgent(StructuredAgent):
    def run_code(self, payload: dict[str, Any]) -> CodeResult:
        return self.run(CodeResult, payload)


class ReviewerAgent(StructuredAgent):
    def run_review(self, payload: dict[str, Any]) -> ReviewResult:
        return self.run(ReviewResult, payload)
