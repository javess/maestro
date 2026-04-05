from __future__ import annotations

from pydantic import BaseModel, Field


class ImpactAnalysis(BaseModel):
    ticket_id: str
    likely_touched_modules: list[str] = Field(default_factory=list)
    nearby_tests: list[str] = Field(default_factory=list)
    hotspots: list[str] = Field(default_factory=list)
    coupled_interfaces: list[str] = Field(default_factory=list)
    context_slice: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
