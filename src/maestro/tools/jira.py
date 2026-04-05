from __future__ import annotations


class NoopJiraProvider:
    def create_ticket(self, payload: dict) -> dict:
        return {"status": "noop", "payload": payload}
