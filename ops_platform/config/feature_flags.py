from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FeatureFlags:
    notifications_enabled: bool = True
    timeline_enabled: bool = True
    compliance_enabled: bool = True
    capacity_planning_enabled: bool = True
    readiness_checks_enabled: bool = True
