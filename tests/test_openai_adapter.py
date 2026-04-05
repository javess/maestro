import os

import pytest

from maestro.providers.openai_adapter import OpenAIProvider
from maestro.schemas.contracts import ProductSpec


class _CreateOnlyResponses:
    def __init__(self, text: str) -> None:
        self.text = text

    def create(self, *, model: str, input: str):  # noqa: A002
        return type("Response", (), {"output_text": self.text})()


class _ParseResponses:
    def parse(self, *, model: str, input: str, text_format):  # noqa: A002
        return type(
            "Response",
            (),
            {
                "output_parsed": {
                    "title": "Maestro",
                    "summary": "Structured response",
                    "problem": "Need deterministic orchestration.",
                    "outcomes": ["Plan"],
                    "scope": ["Code"],
                    "acceptance_criteria": ["Valid schema"],
                }
            },
        )()


class _Client:
    def __init__(self, responses: object) -> None:
        self.responses = responses


def test_openai_provider_generate_text_uses_responses_api() -> None:
    provider = OpenAIProvider(client=_Client(_CreateOnlyResponses("hello")))
    assert provider.generate_text(prompt="Say hi", model="gpt-5") == "hello"


def test_openai_provider_generate_structured_uses_parse_when_available() -> None:
    provider = OpenAIProvider(client=_Client(_ParseResponses()))
    result = provider.generate_structured(prompt="Plan", model="gpt-5", schema=ProductSpec)
    assert result.title == "Maestro"


def test_openai_provider_generate_structured_falls_back_to_json_text() -> None:
    payload = (
        '{"title":"Maestro","summary":"Fallback","problem":"Need planning",'
        '"outcomes":["Plan"],"scope":["Code"],"acceptance_criteria":["Valid schema"]}'
    )
    provider = OpenAIProvider(client=_Client(_CreateOnlyResponses(payload)))
    result = provider.generate_structured(prompt="Plan", model="gpt-5", schema=ProductSpec)
    assert result.summary == "Fallback"


def test_openai_provider_requires_api_key_when_constructing_real_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIProvider()
    with pytest.raises(RuntimeError, match="Missing OpenAI API key"):
        provider.generate_text(prompt="x", model="gpt-5")


def test_openai_provider_normalize_error_marks_rate_limit_retryable() -> None:
    class RateLimitError(Exception):
        pass

    provider = OpenAIProvider(client=_Client(_CreateOnlyResponses("ok")))
    normalized = provider.normalize_error(RateLimitError("retry later"))
    assert normalized.retryable is True


def test_openai_provider_uses_custom_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAESTRO_OPENAI_KEY", "test-key")
    provider = OpenAIProvider(
        api_key_env="MAESTRO_OPENAI_KEY",
        client=_Client(_CreateOnlyResponses("ok")),
    )
    assert provider.api_key_env == "MAESTRO_OPENAI_KEY"
    assert os.environ["MAESTRO_OPENAI_KEY"] == "test-key"
