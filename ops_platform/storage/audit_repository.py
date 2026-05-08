from __future__ import annotations

from dataclasses import asdict

from ..models import AuditLog


class AuditRepository:
    def __init__(self) -> None:
        self.records: list[AuditLog] = []

    def add(self, record: AuditLog) -> None:
        self.records.append(record)

    def extend(self, records: list[AuditLog]) -> None:
        self.records.extend(records)

    def as_payload(self, limit: int | None = None) -> list[dict[str, object]]:
        items = self.records if limit is None else self.records[-limit:]
        return [asdict(item) for item in items]

    def clear(self) -> None:
        self.records.clear()
