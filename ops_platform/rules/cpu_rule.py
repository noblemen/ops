from __future__ import annotations

from ..models import MetricSnapshot, Server
from .base_rule import BaseRule, RuleMatch


class CpuSpikeRule(BaseRule):
    def __init__(self, cpu_high: float, load_high: float) -> None:
        self.cpu_high = cpu_high
        self.load_high = load_high

    def evaluate(self, server: Server, snapshot: MetricSnapshot) -> RuleMatch | None:
        if snapshot.cpu_usage >= self.cpu_high and snapshot.load_average >= self.load_high:
            return RuleMatch(
                category="cpu_spike",
                severity="medium",
                description="CPU and load average remain elevated beyond the baseline.",
            )
        return None
