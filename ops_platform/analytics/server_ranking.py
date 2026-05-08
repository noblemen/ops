from __future__ import annotations

from collections import Counter

from ..models import Alert


class ServerRankingAnalyzer:
    def build(self, alerts: list[Alert], limit: int = 5) -> list[dict[str, object]]:
        counter = Counter(alert.server_id for alert in alerts)
        return [{"server_id": server_id, "alerts": count} for server_id, count in counter.most_common(limit)]
