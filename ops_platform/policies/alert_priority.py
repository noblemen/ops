from __future__ import annotations


class AlertPriorityPolicy:
    def level(self, severity: str, signal_score: float) -> str:
        if severity == "critical" or signal_score >= 0.95:
            return "p1"
        if severity == "high" or signal_score >= 0.85:
            return "p2"
        return "p3"
