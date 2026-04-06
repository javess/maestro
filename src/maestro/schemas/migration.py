from __future__ import annotations

from pydantic import BaseModel, Field


class ValidationHook(BaseModel):
    name: str
    command: str
    required: bool = True


class MigrationPlan(BaseModel):
    summary: str
    required: bool = True
    changed_paths: list[str] = Field(default_factory=list)
    backward_compatibility_notes: list[str] = Field(default_factory=list)
    rollback_notes: list[str] = Field(default_factory=list)
    validation_hooks: list[ValidationHook] = Field(default_factory=list)
    impacted_surfaces: list[str] = Field(default_factory=list)
