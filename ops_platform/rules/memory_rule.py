from __future__ import annotations

from ..models import MetricSnapshot, Server
from .base_rule import BaseRule, RuleMatch


class MemoryPressureRule(BaseRule):
    def __init__(self, memory_high: float) -> None:
        self.memory_high = memory_high

    def evaluate(self, server: Server, snapshot: MetricSnapshot) -> RuleMatch | None:
        if snapshot.memory_usage >= self.memory_high:
            return RuleMatch(
                category="memory_pressure",
                severity="high",
                description="Memory usage remains above 89 percent with OOM warnings.",
            )
        return None
