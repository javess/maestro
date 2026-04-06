from __future__ import annotations

from collections import deque
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock


@dataclass
class ScheduledRun:
    run_id: str
    state: str


class LocalRunScheduler:
    def __init__(self, max_workers: int = 2) -> None:
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = Lock()
        self.pending: deque[tuple[str, Callable[[], object]]] = deque()
        self.running: dict[str, Future[object]] = {}
        self.completed: dict[str, str] = {}

    def enqueue(self, run_id: str, task: Callable[[], object]) -> None:
        with self.lock:
            self.pending.append((run_id, task))
            self.completed[run_id] = "queued"
            self._dispatch()

    def list_runs(self) -> list[ScheduledRun]:
        with self.lock:
            rows = [ScheduledRun(run_id=run_id, state="running") for run_id in self.running]
            rows.extend(ScheduledRun(run_id=run_id, state="queued") for run_id, _ in self.pending)
            rows.extend(
                ScheduledRun(run_id=run_id, state=state)
                for run_id, state in self.completed.items()
                if run_id not in self.running
                and all(run_id != pending_id for pending_id, _ in self.pending)
            )
            return rows

    def cancel(self, run_id: str) -> bool:
        with self.lock:
            for index, item in enumerate(self.pending):
                pending_id, _task = item
                if pending_id == run_id:
                    del self.pending[index]
                    self.completed[run_id] = "cancelled"
                    return True
            future = self.running.get(run_id)
            if future is None:
                return False
            cancelled = future.cancel()
            if cancelled:
                self.running.pop(run_id, None)
                self.completed[run_id] = "cancelled"
            return cancelled

    def future_state(self, run_id: str) -> str:
        with self.lock:
            if run_id in self.running:
                return "running"
            for pending_id, _ in self.pending:
                if pending_id == run_id:
                    return "queued"
            return self.completed.get(run_id, "unknown")

    def _dispatch(self) -> None:
        while self.pending and len(self.running) < self.max_workers:
            run_id, task = self.pending.popleft()
            future = self.executor.submit(task)
            self.running[run_id] = future
            self.completed[run_id] = "running"
            future.add_done_callback(lambda _future, rid=run_id: self._finalize(rid))

    def _finalize(self, run_id: str) -> None:
        with self.lock:
            future = self.running.pop(run_id, None)
            if future is None:
                return
            self.completed[run_id] = "done" if not future.cancelled() else "cancelled"
            self._dispatch()
