from types import SimpleNamespace

from maestro.providers.gemini_adapter import GeminiProvider
from maestro.schemas.contracts import ProductSpec


class RecordingGeminiModels:
    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def test_gemini_generate_text_uses_models_api() -> None:
    models = RecordingGeminiModels([SimpleNamespace(text="hello")])
    provider = GeminiProvider(client=SimpleNamespace(models=models))

    text = provider.generate_text(prompt="hi", model="gemini-test")

    assert text == "hello"
    assert models.calls[0]["model"] == "gemini-test"
    assert models.calls[0]["contents"] == "hi"


def test_gemini_generate_structured_prefers_json_config() -> None:
    payload = ProductSpec(
        title="Spec",
        summary="Summary",
        problem="Problem",
        outcomes=["one"],
        scope=["scope"],
        acceptance_criteria=["done"],
    ).model_dump_json()
    models = RecordingGeminiModels([SimpleNamespace(text=payload)])
    provider = GeminiProvider(client=SimpleNamespace(models=models))

    result = provider.generate_structured(
        prompt="make spec",
        model="gemini-test",
        schema=ProductSpec,
    )

    assert result.title == "Spec"
    assert "config" in models.calls[0]


def test_gemini_generate_structured_falls_back_to_text_prompt() -> None:
    models = RecordingGeminiModels(
        [
            SimpleNamespace(text=None),
            SimpleNamespace(
                text=ProductSpec(
                    title="Fallback",
                    summary="Summary",
                    problem="Problem",
                    outcomes=["one"],
                    scope=["scope"],
                    acceptance_criteria=["done"],
                ).model_dump_json()
            ),
        ]
    )
    provider = GeminiProvider(client=SimpleNamespace(models=models))

    result = provider.generate_structured(
        prompt="make spec",
        model="gemini-test",
        schema=ProductSpec,
    )

    assert result.title == "Fallback"
    assert len(models.calls) == 2
