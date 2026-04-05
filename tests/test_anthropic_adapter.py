from types import SimpleNamespace

from maestro.providers.anthropic_adapter import AnthropicProvider
from maestro.schemas.contracts import ProductSpec


class RecordingAnthropicMessages:
    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def test_anthropic_generate_text_uses_messages_api() -> None:
    messages = RecordingAnthropicMessages(
        [SimpleNamespace(content=[SimpleNamespace(text="hello")])]
    )
    provider = AnthropicProvider(client=SimpleNamespace(messages=messages))

    text = provider.generate_text(prompt="hi", model="claude-test")

    assert text == "hello"
    assert messages.calls[0]["model"] == "claude-test"
    assert messages.calls[0]["messages"] == [{"role": "user", "content": "hi"}]


def test_anthropic_generate_structured_parses_json_payload() -> None:
    payload = ProductSpec(
        title="Spec",
        summary="Summary",
        problem="Problem",
        outcomes=["one"],
        scope=["scope"],
        acceptance_criteria=["done"],
    ).model_dump_json()
    messages = RecordingAnthropicMessages(
        [SimpleNamespace(content=[SimpleNamespace(text=payload)])]
    )
    provider = AnthropicProvider(client=SimpleNamespace(messages=messages))

    result = provider.generate_structured(
        prompt="make spec",
        model="claude-test",
        schema=ProductSpec,
    )

    assert result.title == "Spec"
