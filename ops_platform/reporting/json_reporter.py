from __future__ import annotations

from dataclasses import asdict

from ..models import DailySummary


class JsonReporter:
    def build(self, summary: DailySummary, extras: dict[str, object] | None = None) -> dict[str, object]:
        payload = asdict(summary)
        if extras:
            payload.update(extras)
        return payload
