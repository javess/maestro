from __future__ import annotations

from maestro.schemas.observation import Observation, ObservationCompilation, ObservationFollowUp


def compile_observations(observations: list[Observation]) -> ObservationCompilation:
    follow_ups: list[ObservationFollowUp] = []
    for index, observation in enumerate(observations, start=1):
        priority = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
        }[observation.severity]
        follow_ups.append(
            ObservationFollowUp(
                id=f"OBS-{index:03d}",
                title=_title_for_observation(observation),
                description=_description_for_observation(observation),
                priority=priority,
                acceptance_criteria=[
                    "Root cause is documented",
                    "A regression check exists or is justified",
                ],
                source_observation_ids=[f"OBS-{index:03d}"],
            )
        )
    return ObservationCompilation(observations=observations, follow_ups=follow_ups)


def _title_for_observation(observation: Observation) -> str:
    prefix = {
        "error": "Fix",
        "latency": "Improve",
        "feedback": "Address",
        "regression": "Prevent",
        "operational": "Stabilize",
    }[observation.category]
    return f"{prefix} {observation.summary}"


def _description_for_observation(observation: Observation) -> str:
    path = f" Affected path: {observation.path}." if observation.path else ""
    detail = f" {observation.detail}" if observation.detail else ""
    return f"Follow up on {observation.source} observation.{path}{detail}".strip()
