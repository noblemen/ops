from __future__ import annotations

from dataclasses import asdict

from ..models import IncidentResult


class IncidentRepository:
    def __init__(self) -> None:
        self.records: list[IncidentResult] = []

    def add(self, record: IncidentResult) -> None:
        self.records.append(record)

    def resolution_rate(self) -> float:
        actionable = [item for item in self.records if item.action is not None]
        if not actionable:
            return 0.0
        resolved = sum(1 for item in actionable if item.status == "resolved")
        return round((resolved / len(actionable)) * 100, 2)

    def as_payload(self, limit: int | None = None) -> list[dict[str, object]]:
        items = self.records if limit is None else self.records[-limit:]
        return [asdict(item) for item in items]

    def clear(self) -> None:
        self.records.clear()
