from pydantic import BaseModel

from maestro.core.structured import StructuredOutputRunner
from maestro.providers.base import LlmProvider
from maestro.schemas.contracts import ProviderCapability, ProviderError, ProviderModelInfo


class DemoSchema(BaseModel):
    value: str


class TextOnlyProvider(LlmProvider):
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self._capabilities = ProviderCapability(json_mode=True)

    @property
    def capabilities(self) -> ProviderCapability:
        return self._capabilities

    def generate_text(self, *, prompt: str, model: str, metadata=None) -> str:
        return self.responses.pop(0)

    def generate_structured(self, *, prompt: str, model: str, schema: type, metadata=None):
        raise NotImplementedError

    def supports_structured_output(self) -> bool:
        return False

    def supports_tool_calling(self) -> bool:
        return False

    def model_info(self, model: str) -> ProviderModelInfo:
        return ProviderModelInfo(provider="text-only", model=model, capabilities=self.capabilities)

    def normalize_error(self, error: Exception) -> ProviderError:
        return ProviderError(provider="text-only", retryable=False, message=str(error))


def test_structured_output_runner_parses_text_json() -> None:
    runner = StructuredOutputRunner()
    provider = TextOnlyProvider(['{"value":"ok"}'])
    result, attempts = runner.generate(provider, prompt="x", model="demo", schema=DemoSchema)
    assert result.value == "ok"
    assert attempts[0].strategy == "json_mode_parse"


def test_structured_output_runner_repairs_after_invalid_text() -> None:
    runner = StructuredOutputRunner()
    provider = TextOnlyProvider(["not-json", '{"value":"repaired"}'])
    result, attempts = runner.generate(provider, prompt="x", model="demo", schema=DemoSchema)
    assert result.value == "repaired"
    assert attempts[-1].strategy == "repair_retry"
