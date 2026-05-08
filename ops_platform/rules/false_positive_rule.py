from __future__ import annotations

from ..models import MetricSnapshot


class FalsePositiveRule:
    def is_false_positive(self, snapshot: MetricSnapshot, category: str) -> bool:
        if category == "cpu_spike" and snapshot.context.get("business_peak"):
            return False
        if category == "cpu_spike" and snapshot.context.get("planned_change"):
            return True
        if category == "service_down" and snapshot.context.get("deploy_window"):
            return True
        return False

    def explain(self, category: str) -> str:
        if category == "service_down":
            return "Deploy window explains transient service recycle."
        return "Planned change window explains transient metric noise."
