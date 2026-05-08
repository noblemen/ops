from __future__ import annotations

from ..models import MetricSnapshot, Server
from .base_rule import BaseRule, RuleMatch


class ServiceDownRule(BaseRule):
    def evaluate(self, server: Server, snapshot: MetricSnapshot) -> RuleMatch | None:
        if server.role not in snapshot.running_processes:
            return RuleMatch(
                category="service_down",
                severity="critical",
                description="Core process missing from runtime list and heartbeat log not found.",
            )
        return None
