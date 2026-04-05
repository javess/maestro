from pydantic import BaseModel

from maestro.providers.fake import FakeProvider
from maestro.schemas.contracts import ProductSpec


class Dummy(BaseModel):
    value: str


def test_fake_provider_defaults() -> None:
    provider = FakeProvider()
    result = provider.generate_structured(prompt="x", model="fake", schema=ProductSpec)
    assert isinstance(result, ProductSpec)
    assert result.title == "Maestro"
    assert result.problem
    assert result.target_users
    assert result.assumption_log
    assert result.unresolved_questions


def test_fake_provider_resolver() -> None:
    provider = FakeProvider(resolver=lambda _prompt, schema: schema.model_validate({"value": "ok"}))
    result = provider.generate_structured(prompt="x", model="fake", schema=Dummy)
    assert isinstance(result, Dummy)
    assert result.value == "ok"
