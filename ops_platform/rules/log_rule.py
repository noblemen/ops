from __future__ import annotations

from ..models import MetricSnapshot, Server
from .base_rule import BaseRule, RuleMatch


class LogAnomalyRule(BaseRule):
    def __init__(self, disk_warning: float, memory_warning: float) -> None:
        self.disk_warning = disk_warning
        self.memory_warning = memory_warning

    def evaluate(self, server: Server, snapshot: MetricSnapshot) -> RuleMatch | None:
        if snapshot.disk_usage >= self.disk_warning and snapshot.memory_usage >= self.memory_warning:
            return RuleMatch(
                category="log_anomaly",
                severity="medium",
                description="Log rotation lag is increasing disk and memory pressure.",
            )
        return None
