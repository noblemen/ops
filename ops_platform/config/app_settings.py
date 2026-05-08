from __future__ import annotations

from dataclasses import dataclass, field

from .feature_flags import FeatureFlags
from .thresholds import MonitoringThresholds


@dataclass(slots=True)
class AppSettings:
    managed_servers_target: int = 30
    default_cycles: int = 4
    report_directory: str = "reports"
    report_file: str = "reports/audit_report.md"
    token_budget_per_task: int = 25000
    time_saved_per_60_tasks_hours: float = 4.0
    alert_channels: list[str] = field(default_factory=lambda: ["console", "email", "webhook"])
    feature_flags: FeatureFlags = field(default_factory=FeatureFlags)
    thresholds: MonitoringThresholds = field(default_factory=MonitoringThresholds)
