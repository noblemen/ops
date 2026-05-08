from __future__ import annotations

from collections import Counter

from ..models import AuditLog


class CapacityPlanner:
    def build(self, audit_logs: list[AuditLog]) -> list[dict[str, object]]:
        counter = Counter(log.action_name for log in audit_logs)
        plans: list[dict[str, object]] = []
        if counter.get("config_update", 0) >= 2:
            plans.append({"focus": "compute", "recommendation": "Increase worker pool review cadence."})
        if counter.get("disk_cleanup", 0) >= 2:
            plans.append({"focus": "storage", "recommendation": "Expand hot log partition or tighten retention."})
        if counter.get("service_restart", 0) >= 2:
            plans.append({"focus": "resilience", "recommendation": "Add startup dependency checks and probe gating."})
        return plans
