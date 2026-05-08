from __future__ import annotations

from ..models import Alert


class RemediationPolicy:
    def requires_approval(self, alert: Alert) -> bool:
        return alert.category == "config_update" or alert.severity == "critical"
