from __future__ import annotations

from ..models import MetricSnapshot, Server


class MaintenanceWindowService:
    def is_planned(self, server: Server, snapshot: MetricSnapshot) -> bool:
        return server.environment == "staging" and bool(snapshot.context.get("deploy_window"))
