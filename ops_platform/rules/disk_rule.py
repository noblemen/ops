from __future__ import annotations

from ..models import MetricSnapshot, Server
from .base_rule import BaseRule, RuleMatch


class DiskPressureRule(BaseRule):
    def __init__(self, disk_high: float) -> None:
        self.disk_high = disk_high

    def evaluate(self, server: Server, snapshot: MetricSnapshot) -> RuleMatch | None:
        if snapshot.disk_usage >= self.disk_high:
            return RuleMatch(
                category="disk_pressure",
                severity="high",
                description="Disk usage crossed 91 percent with log growth signs.",
            )
        return None
