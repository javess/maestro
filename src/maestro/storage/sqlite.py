from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from maestro.schemas.contracts import ArtifactEntry, RunState
from maestro.schemas.storage import IndexedArtifactRecord, IndexedRunRecord


class SqliteRunIndex:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record_manifest(self, run_id: str, run_dir: Path) -> None:
        timestamp = self._timestamp()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs (
                    run_id,
                    repo_path,
                    status,
                    current_state,
                    run_dir,
                    created_at,
                    updated_at
                )
                VALUES (?, '', 'running', 'DISCOVER_REPO', ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    run_dir = excluded.run_dir,
                    updated_at = excluded.updated_at
                """,
                (run_id, str(run_dir), timestamp, timestamp),
            )

    def record_state(self, state: RunState, state_path: Path) -> None:
        timestamp = self._timestamp()
        run_dir = state_path.parent.parent / state.run_id
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs (
                    run_id,
                    repo_path,
                    brief_path,
                    status,
                    current_state,
                    current_ticket_id,
                    state_path,
                    run_dir,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    repo_path = excluded.repo_path,
                    brief_path = excluded.brief_path,
                    status = excluded.status,
                    current_state = excluded.current_state,
                    current_ticket_id = excluded.current_ticket_id,
                    state_path = excluded.state_path,
                    run_dir = excluded.run_dir,
                    updated_at = excluded.updated_at
                """,
                (
                    state.run_id,
                    str(state.repo_path),
                    str(state.brief_path) if state.brief_path is not None else None,
                    state.status,
                    state.current_state,
                    state.current_ticket_id,
                    str(state_path),
                    str(run_dir),
                    timestamp,
                    timestamp,
                ),
            )

    def record_artifact(self, run_id: str, artifact: ArtifactEntry) -> None:
        timestamp = self._timestamp()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO artifacts (run_id, name, kind, path, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, artifact.name, artifact.kind, artifact.path, timestamp),
            )

    def list_runs(self) -> list[IndexedRunRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    run_id,
                    repo_path,
                    brief_path,
                    status,
                    current_state,
                    current_ticket_id,
                    state_path,
                    run_dir,
                    created_at,
                    updated_at
                FROM runs
                ORDER BY updated_at DESC, run_id DESC
                """
            ).fetchall()
        return [
            IndexedRunRecord.model_validate(dict(row))
            for row in rows
        ]

    def load_run(self, run_id: str) -> IndexedRunRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    run_id,
                    repo_path,
                    brief_path,
                    status,
                    current_state,
                    current_ticket_id,
                    state_path,
                    run_dir,
                    created_at,
                    updated_at
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return IndexedRunRecord.model_validate(dict(row))

    def list_artifacts(self, run_id: str) -> list[IndexedArtifactRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT run_id, name, kind, path, created_at
                FROM artifacts
                WHERE run_id = ?
                ORDER BY created_at ASC, name ASC
                """,
                (run_id,),
            ).fetchall()
        return [IndexedArtifactRecord.model_validate(dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        self._ensure_schema(conn)
        return conn

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                repo_path TEXT NOT NULL,
                brief_path TEXT,
                status TEXT NOT NULL,
                current_state TEXT NOT NULL,
                current_ticket_id TEXT,
                state_path TEXT,
                run_dir TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS artifacts (
                run_id TEXT NOT NULL,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (run_id, name, path)
            )
            """
        )
        conn.commit()

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat()
