from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from maestro.providers.router import ProviderRouter
from maestro.schemas.contracts import Backlog, CodeResult, ProductSpec, ReviewResult


def _prompt_text(prompt_root: Path, name: str) -> str:
    return (prompt_root / f"{name}.md").read_text()


class StructuredAgent:
    def __init__(self, router: ProviderRouter, prompt_root: Path, prompt_name: str) -> None:
        self.router = router
        self.prompt_root = prompt_root
        self.prompt_name = prompt_name

    def run(self, role: str, schema: type[BaseModel], payload: dict[str, Any]) -> BaseModel:
        prompt = _prompt_text(self.prompt_root, self.prompt_name)
        result, _route = self.router.generate_structured(
            role=role,
            prompt=f"{prompt}\nINPUT={payload}",
            schema=schema,
            metadata=payload,
        )
        return result


class ProductDesignerAgent(StructuredAgent):
    def run_spec(self, payload: dict[str, Any]) -> ProductSpec:
        return ProductSpec.model_validate(self.run("product_designer", ProductSpec, payload))


class CeremonyMasterAgent(StructuredAgent):
    def run_backlog(self, payload: dict[str, Any]) -> Backlog:
        return Backlog.model_validate(self.run("ceremony_master", Backlog, payload))


class CoderAgent(StructuredAgent):
    def run_code(self, payload: dict[str, Any]) -> CodeResult:
        return CodeResult.model_validate(self.run("coder", CodeResult, payload))


class ReviewerAgent(StructuredAgent):
    def run_review(self, payload: dict[str, Any]) -> ReviewResult:
        return ReviewResult.model_validate(self.run("reviewer", ReviewResult, payload))
