from __future__ import annotations


class SchedulerService:
    def build_daily_schedule(self, cycles: int) -> list[dict[str, object]]:
        return [
            {"cycle": index, "task": "monitoring-scan", "window": f"T+{index * 30}m"}
            for index in range(cycles)
        ]
