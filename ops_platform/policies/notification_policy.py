from __future__ import annotations

from ..models import IncidentResult


class NotificationPolicy:
    def should_notify(self, incident: IncidentResult) -> bool:
        return incident.status in {"manual_followup", "resolved"} and (
            incident.requires_manual_followup or incident.execution_ms >= 1800
        )
