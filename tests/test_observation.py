from maestro.core.observation import compile_observations
from maestro.schemas.observation import Observation


def test_compile_observations_produces_follow_up_tickets() -> None:
    compilation = compile_observations(
        [
            Observation(
                source="check",
                category="error",
                summary="pytest failed",
                detail="assertion error",
                severity="high",
            ),
            Observation(
                source="review",
                category="regression",
                summary="missing guard",
                detail="add regression coverage",
                path="src/app.py",
                severity="medium",
            ),
        ]
    )

    assert [item.id for item in compilation.follow_ups] == ["OBS-001", "OBS-002"]
    assert compilation.follow_ups[0].priority > compilation.follow_ups[1].priority
    assert "pytest failed" in compilation.follow_ups[0].title
