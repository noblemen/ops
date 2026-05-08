from __future__ import annotations

from ..models import DailySummary


class KPIReporter:
    def build(self, summary: DailySummary) -> dict[str, object]:
        return {
            "managed_servers": summary.managed_servers,
            "automation_rate": summary.automation_rate,
            "automated_tasks": summary.automated_tasks,
            "manual_followups": summary.manual_followups,
            "tokens_consumed": summary.tokens_consumed,
            "time_saved_hours": summary.time_saved_hours,
        }
