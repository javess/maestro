from __future__ import annotations

from pydantic import BaseModel


class IndexedRunRecord(BaseModel):
    run_id: str
    repo_path: str
    brief_path: str | None = None
    status: str
    current_state: str
    current_ticket_id: str | None = None
    state_path: str | None = None
    run_dir: str | None = None
    created_at: str
    updated_at: str


class IndexedArtifactRecord(BaseModel):
    run_id: str
    name: str
    kind: str
    path: str
    created_at: str
