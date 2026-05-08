from __future__ import annotations

from ..models import Alert, IncidentResult


class TimelineReporter:
    def build(self, alerts: list[Alert], incidents: list[IncidentResult], limit: int = 12) -> list[dict[str, object]]:
        timeline: list[dict[str, object]] = []
        for alert, incident in zip(alerts[-limit:], incidents[-limit:]):
            timeline.append(
                {
                    "server_id": alert.server_id,
                    "alert": alert.category,
                    "severity": alert.severity,
                    "action": incident.action.name if incident.action else "suppressed",
                    "status": incident.status,
                    "created_at": alert.created_at.isoformat(timespec="seconds"),
                }
            )
        return timeline
