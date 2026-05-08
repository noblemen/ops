from __future__ import annotations


class SystemHealthService:
    def build(self, managed_servers: int, alert_count: int, automation_rate: float) -> dict[str, object]:
        return {
            "managed_servers": managed_servers,
            "alert_count": alert_count,
            "automation_rate": automation_rate,
            "status": "healthy" if automation_rate >= 80 else "watch",
        }
