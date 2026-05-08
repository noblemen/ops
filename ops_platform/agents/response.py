from __future__ import annotations

from datetime import datetime
from random import Random

from ..adapters.os_profiles import OSProfileAdapter
from ..models import Alert, IncidentResult, Server


class IncidentResponseAgent:
    def __init__(self, rng: Random) -> None:
        self.rng = rng
        self.os_adapter = OSProfileAdapter()

    def handle(self, server: Server, alert: Alert) -> IncidentResult:
        if alert.is_false_positive:
            return IncidentResult(
                alert_id=alert.id,
                server_id=server.id,
                action=None,
                status="suppressed",
                summary="Alert suppressed as false positive during reasoning stage.",
                executed_at=datetime.now(),
                execution_ms=0,
                requires_manual_followup=False,
            )

        action = self.os_adapter.build_action(server.os_family, alert.recommended_action, server.role)
        success = self._simulate_outcome(alert)
        summary = self._build_summary(server, alert, action.name, success)
        execution_ms = 800 + int(self.rng.uniform(0, 2200))

        return IncidentResult(
            alert_id=alert.id,
            server_id=server.id,
            action=action,
            status="resolved" if success else "manual_followup",
            summary=summary,
            executed_at=datetime.now(),
            execution_ms=execution_ms,
            requires_manual_followup=not success,
        )

    def _simulate_outcome(self, alert: Alert) -> bool:
        success_rate = {
            "service_down": 0.88,
            "disk_pressure": 0.8,
            "memory_pressure": 0.78,
            "cpu_spike": 0.81,
            "log_anomaly": 0.9,
        }[alert.category]
        penalty = 0.08 if alert.severity == "critical" else 0.0
        return self.rng.random() < max(success_rate - penalty, 0.45)

    def _build_summary(self, server: Server, alert: Alert, action_name: str, success: bool) -> str:
        if success:
            return (
                f"Executed {action_name} on {server.hostname} ({server.os_family}) and restored service health."
            )
        return (
            f"Executed {action_name} on {server.hostname} ({server.os_family}), but manual review is still required."
        )
