from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ArchetypePack(BaseModel):
    name: str
    description: str
    architecture_defaults: dict[str, Any] = Field(default_factory=dict)
    policy_defaults: dict[str, Any] = Field(default_factory=dict)
    work_patterns: list[str] = Field(default_factory=list)
