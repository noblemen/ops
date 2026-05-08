from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Server:
    id: str
    hostname: str
    os_family: str
    environment: str
    role: str
    ip_address: str
    owner: str


@dataclass(slots=True)
class MetricSnapshot:
    server_id: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    load_average: float
    log_keywords: list[str]
    running_processes: list[str]
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Alert:
    id: str
    server_id: str
    category: str
    severity: str
    title: str
    description: str
    probable_root_cause: str
    reasoning_steps: list[str]
    recommended_action: str
    is_false_positive: bool
    created_at: datetime
    signal_score: float


@dataclass(slots=True)
class RepairAction:
    name: str
    script_name: str
    command: str
    automation_level: str


@dataclass(slots=True)
class IncidentResult:
    alert_id: str
    server_id: str
    action: RepairAction | None
    status: str
    summary: str
    executed_at: datetime
    execution_ms: int
    requires_manual_followup: bool


@dataclass(slots=True)
class AuditLog:
    incident_id: str
    server_id: str
    os_family: str
    operator: str
    action_name: str
    status: str
    timestamp: datetime
    details: str


@dataclass(slots=True)
class OptimizationSuggestion:
    server_id: str
    priority: str
    title: str
    recommendation: str
    estimated_benefit: str


@dataclass(slots=True)
class DailySummary:
    managed_servers: int
    total_alerts: int
    false_positives_filtered: int
    automated_tasks: int
    successful_automations: int
    manual_followups: int
    automation_rate: float
    tokens_consumed: int
    time_saved_hours: float
    optimization_suggestions: list[OptimizationSuggestion]
