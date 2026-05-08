from __future__ import annotations

from dataclasses import asdict

from ..models import MetricSnapshot


class SnapshotRepository:
    def __init__(self) -> None:
        self.records: list[MetricSnapshot] = []

    def extend(self, records: list[MetricSnapshot]) -> None:
        self.records.extend(records)

    def latest_for_server(self, server_id: str) -> MetricSnapshot | None:
        for record in reversed(self.records):
            if record.server_id == server_id:
                return record
        return None

    def as_payload(self, limit: int | None = None) -> list[dict[str, object]]:
        items = self.records if limit is None else self.records[-limit:]
        return [asdict(item) for item in items]

    def clear(self) -> None:
        self.records.clear()
