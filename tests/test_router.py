from maestro.core.structured import StructuredOutputRunner
from maestro.providers.fake import FakeProvider
from maestro.providers.router import ProviderRouter
from maestro.schemas.contracts import FallbackConfig, MaestroConfig, ProductSpec, RoleConfig


def test_router_uses_fallback_provider() -> None:
    primary = FakeProvider(
        resolver=lambda _prompt, _schema: (_ for _ in ()).throw(ValueError("primary failed"))
    )
    fallback = FakeProvider()
    config = MaestroConfig(
        providers={"fake": {"type": "fake"}, "fallback": {"type": "fake"}},
        llm={"product_designer": RoleConfig(provider="fake", model="m1")},
        fallbacks={"product_designer": [FallbackConfig(provider="fallback", model="m2")]},
        policy="default",
    )
    router = ProviderRouter(
        config=config,
        providers={"fake": primary, "fallback": fallback},
        runner=StructuredOutputRunner(),
    )
    result, route = router.generate_structured(
        role="product_designer",
        prompt="x",
        schema=ProductSpec,
    )
    assert result.title == "Maestro"
    assert route.provider_name == "fallback"
