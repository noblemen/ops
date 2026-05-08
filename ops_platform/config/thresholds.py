from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MonitoringThresholds:
    cpu_high: float = 87.0
    memory_high: float = 89.0
    disk_high: float = 91.0
    disk_warning: float = 85.0
    memory_warning: float = 82.0
    load_high: float = 4.0
