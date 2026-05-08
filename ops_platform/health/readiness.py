from __future__ import annotations


class ReadinessService:
    def build(self, latest_snapshots: int, notifications_enabled: bool) -> dict[str, object]:
        ready = latest_snapshots > 0 and notifications_enabled
        return {
            "ready": ready,
            "latest_snapshots": latest_snapshots,
            "notifications_enabled": notifications_enabled,
        }
