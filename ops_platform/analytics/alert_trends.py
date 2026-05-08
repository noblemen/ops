from __future__ import annotations

from collections import Counter

from ..models import Alert


class AlertTrendAnalyzer:
    def build(self, alerts: list[Alert]) -> dict[str, int]:
        return dict(Counter(alert.category for alert in alerts))
