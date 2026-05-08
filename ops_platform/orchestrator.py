from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from random import Random
from typing import Any

from .agents.audit import AuditOptimizationAgent
from .agents.monitoring import MonitoringAlertAgent
from .agents.response import IncidentResponseAgent
from .analytics.alert_trends import AlertTrendAnalyzer
from .analytics.cost_analysis import CostAnalyzer
from .analytics.server_ranking import ServerRankingAnalyzer
from .config import AppSettings, OSCompatibilityMatrix
from .health import AgentStatusService, ReadinessService, SystemHealthService
from .models import Alert, AuditLog, DailySummary, IncidentResult
from .notifications.console_notifier import ConsoleNotifier
from .notifications.email_notifier import EmailNotifier
from .notifications.manager import NotificationManager
from .notifications.slack_notifier import SlackNotifier
from .notifications.webhook_notifier import WebhookNotifier
from .policies.alert_priority import AlertPriorityPolicy
from .policies.notification_policy import NotificationPolicy
from .reporting.json_reporter import JsonReporter
from .reporting.kpi_reporter import KPIReporter
from .reporting.markdown_reporter import MarkdownReporter
from .reporting.timeline_reporter import TimelineReporter
from .sample_data import build_metric_snapshots, build_server_inventory
from .services.capacity_planner import CapacityPlanner
from .services.compliance_service import ComplianceService
from .services.maintenance_window import MaintenanceWindowService
from .services.scheduler_service import SchedulerService
from .services.script_catalog import ScriptCatalog
from .services.token_meter import TokenMeter
from .storage.audit_repository import AuditRepository
from .storage.incident_repository import IncidentRepository
from .storage.json_store import JsonStore
from .storage.snapshot_repository import SnapshotRepository


class OpsAutomationPlatform:
    def __init__(self, seed: int = 20260508) -> None:
        self.seed = seed
        self.settings = AppSettings()
        self.rng = Random(seed)
        self.servers = {
            server.id: server
            for server in build_server_inventory(total=self.settings.managed_servers_target)
        }

        self.monitoring_agent = MonitoringAlertAgent(self.settings.thresholds)
        self.response_agent = IncidentResponseAgent(self.rng)
        self.audit_agent = AuditOptimizationAgent()

        self.snapshot_repository = SnapshotRepository()
        self.incident_repository = IncidentRepository()
        self.audit_repository = AuditRepository()
        self.json_store = JsonStore()

        self.script_catalog = ScriptCatalog()
        self.scheduler_service = SchedulerService()
        self.maintenance_window = MaintenanceWindowService()
        self.compliance_service = ComplianceService()
        self.capacity_planner = CapacityPlanner()
        self.token_meter = TokenMeter(self.settings.token_budget_per_task)

        self.markdown_reporter = MarkdownReporter()
        self.json_reporter = JsonReporter()
        self.kpi_reporter = KPIReporter()
        self.timeline_reporter = TimelineReporter()

        self.system_health_service = SystemHealthService()
        self.agent_status_service = AgentStatusService()
        self.readiness_service = ReadinessService()

        self.alert_trend_analyzer = AlertTrendAnalyzer()
        self.cost_analyzer = CostAnalyzer()
        self.server_ranking_analyzer = ServerRankingAnalyzer()
        self.alert_priority = AlertPriorityPolicy()
        self.notification_policy = NotificationPolicy()
        self.os_matrix = OSCompatibilityMatrix()
        self.notification_manager = NotificationManager(self._build_notifiers())

        self.alert_history: list[Alert] = []
        self.incident_history: list[IncidentResult] = []
        self.audit_logs: list[AuditLog] = []
        self.start_time = datetime(2026, 5, 8, 0, 0, 0)

    def run_cycle(self, cycle: int) -> dict[str, Any]:
        snapshots = build_metric_snapshots(list(self.servers.values()), cycle, self.rng, self.start_time)
        self.snapshot_repository.extend(snapshots)
        alerts = self.monitoring_agent.analyze(self.servers, snapshots)
        incidents: list[IncidentResult] = []
        planned_changes = 0

        for snapshot in snapshots:
            server = self.servers[snapshot.server_id]
            if self.maintenance_window.is_planned(server, snapshot):
                planned_changes += 1

        for alert in alerts:
            server = self.servers[alert.server_id]
            incident = self.response_agent.handle(server, alert)
            audit_log = self.audit_agent.record(server, incident)

            self.alert_history.append(alert)
            self.incident_history.append(incident)
            self.audit_logs.append(audit_log)

            self.incident_repository.add(incident)
            self.audit_repository.add(audit_log)
            incidents.append(incident)

            if self.settings.feature_flags.notifications_enabled and self.notification_policy.should_notify(incident):
                priority = self.alert_priority.level(alert.severity, alert.signal_score)
                action_name = incident.action.name if incident.action else "suppressed"
                script_help = self.script_catalog.describe(action_name)
                title = f"{priority.upper()} {server.hostname} {alert.category}"
                body = (
                    f"status={incident.status}; action={action_name}; script={script_help}; "
                    f"root_cause={alert.probable_root_cause}"
                )
                self.notification_manager.broadcast(title=title, body=body, severity=alert.severity)

        return {
            "cycle": cycle,
            "planned_changes": planned_changes,
            "alerts": [self._alert_to_payload(alert) for alert in alerts],
            "incidents": [self._incident_to_payload(incident) for incident in incidents],
            "notifications": self.notification_manager.recent_payloads(limit=6),
        }

    def simulate_day(self, cycles: int | None = None) -> dict[str, Any]:
        self._reset_history()
        total_cycles = cycles or self.settings.default_cycles
        cycle_results = [self.run_cycle(cycle) for cycle in range(total_cycles)]
        summary = self.build_daily_summary()
        report = self._build_report_text(summary)
        return {
            "summary": self._summary_to_payload(summary),
            "kpis": self.kpi_reporter.build(summary),
            "schedule": self.scheduler_service.build_daily_schedule(total_cycles),
            "cycles": cycle_results,
            "timeline": self.timeline_reporter.build(self.alert_history, self.incident_history),
            "alert_trends": self.alert_trend_analyzer.build(self.alert_history),
            "top_alerted_servers": self.server_ranking_analyzer.build(self.alert_history),
            "cost": self.cost_analyzer.estimate(summary.tokens_consumed),
            "capacity_plan": self.capacity_planner.build(self.audit_logs),
            "notifications": self.notification_manager.recent_payloads(limit=12),
            "report": report,
        }

    def build_daily_summary(self) -> DailySummary:
        false_positives = sum(1 for alert in self.alert_history if alert.is_false_positive)
        automated_tasks = sum(1 for incident in self.incident_history if incident.action is not None)
        successful = sum(1 for incident in self.incident_history if incident.status == "resolved")
        manual_followups = sum(1 for incident in self.incident_history if incident.requires_manual_followup)
        suggestions = self.audit_agent.build_optimization_suggestions(self.servers, self.audit_logs)
        tokens_consumed = self.token_meter.consume(automated_tasks)
        time_saved_hours = round(
            automated_tasks * self.settings.time_saved_per_60_tasks_hours / 60,
            1,
        ) if automated_tasks else 0.0
        automation_rate = round((successful / automated_tasks) * 100, 2) if automated_tasks else 0.0

        return DailySummary(
            managed_servers=len(self.servers),
            total_alerts=len(self.alert_history),
            false_positives_filtered=false_positives,
            automated_tasks=automated_tasks,
            successful_automations=successful,
            manual_followups=manual_followups,
            automation_rate=automation_rate,
            tokens_consumed=tokens_consumed,
            time_saved_hours=time_saved_hours,
            optimization_suggestions=suggestions,
        )

    def export_report(self, report_path: str | Path) -> Path:
        summary = self.build_daily_summary()
        report = self._build_report_text(summary)
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
        return path

    def export_dashboard_json(self, path: str | Path = "reports/dashboard.json") -> Path:
        return self.json_store.write(path, self.dashboard())

    def report_text(self) -> str:
        return self._build_report_text(self.build_daily_summary())

    def dashboard(self) -> dict[str, Any]:
        summary = self.build_daily_summary()
        latest_alerts = [self._alert_to_payload(alert) for alert in self.alert_history[-8:]]
        latest_logs = [asdict(log) for log in self.audit_logs[-8:]]
        kpis = self.kpi_reporter.build(summary)
        return {
            "summary": self._summary_to_payload(summary),
            "kpis": kpis,
            "health": self.system_health_service.build(
                managed_servers=len(self.servers),
                alert_count=len(self.alert_history),
                automation_rate=summary.automation_rate,
            ),
            "readiness": self.readiness_service.build(
                latest_snapshots=len(self.snapshot_repository.records),
                notifications_enabled=self.settings.feature_flags.notifications_enabled,
            ),
            "agent_status": self.agent_status_service.build(),
            "latest_alerts": latest_alerts,
            "latest_audit_logs": latest_logs,
            "alert_trends": self.alert_trend_analyzer.build(self.alert_history),
            "top_alerted_servers": self.server_ranking_analyzer.build(self.alert_history),
            "capacity_plan": self.capacity_planner.build(self.audit_logs),
            "notifications": self.notification_manager.recent_payloads(limit=8),
            "supported_os": {
                "CentOS": self.os_matrix.supported_actions("centos"),
                "Kylin": self.os_matrix.supported_actions("kylin"),
            },
        }

    def dump_state(self) -> str:
        payload = self.dashboard()
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    def health_snapshot(self) -> dict[str, Any]:
        summary = self.build_daily_summary()
        return {
            "system": self.system_health_service.build(
                managed_servers=len(self.servers),
                alert_count=len(self.alert_history),
                automation_rate=summary.automation_rate,
            ),
            "agents": self.agent_status_service.build(),
            "readiness": self.readiness_service.build(
                latest_snapshots=len(self.snapshot_repository.records),
                notifications_enabled=self.settings.feature_flags.notifications_enabled,
            ),
        }

    def timeline(self) -> list[dict[str, object]]:
        return self.timeline_reporter.build(self.alert_history, self.incident_history)

    def notifications(self) -> list[dict[str, object]]:
        return self.notification_manager.recent_payloads(limit=20)

    def _reset_history(self) -> None:
        self.rng = Random(self.seed)
        self.response_agent.rng = self.rng
        self.alert_history.clear()
        self.incident_history.clear()
        self.audit_logs.clear()
        self.snapshot_repository.clear()
        self.incident_repository.clear()
        self.audit_repository.clear()
        self.notification_manager.clear()

    def _build_notifiers(self) -> list[object]:
        registry = {
            "console": ConsoleNotifier(),
            "email": EmailNotifier(),
            "slack": SlackNotifier(),
            "webhook": WebhookNotifier(),
        }
        return [registry[name] for name in self.settings.alert_channels if name in registry]

    def _build_report_text(self, summary: DailySummary) -> str:
        return self.markdown_reporter.build(
            summary=summary,
            audit_logs=self.audit_logs,
            suggestions=summary.optimization_suggestions,
            compliance_lines=self.compliance_service.build(),
            generated_at=self.start_time,
        )

    def _alert_to_payload(self, alert: Alert) -> dict[str, Any]:
        return {
            "id": alert.id,
            "server_id": alert.server_id,
            "category": alert.category,
            "severity": alert.severity,
            "priority": self.alert_priority.level(alert.severity, alert.signal_score),
            "title": alert.title,
            "description": alert.description,
            "probable_root_cause": alert.probable_root_cause,
            "reasoning_steps": alert.reasoning_steps,
            "recommended_action": alert.recommended_action,
            "script_description": self.script_catalog.describe(alert.recommended_action),
            "is_false_positive": alert.is_false_positive,
            "created_at": alert.created_at.isoformat(timespec="seconds"),
            "signal_score": alert.signal_score,
        }

    def _incident_to_payload(self, incident: IncidentResult) -> dict[str, Any]:
        return {
            "alert_id": incident.alert_id,
            "server_id": incident.server_id,
            "status": incident.status,
            "summary": incident.summary,
            "action": asdict(incident.action) if incident.action else None,
            "executed_at": incident.executed_at.isoformat(timespec="seconds"),
            "execution_ms": incident.execution_ms,
            "requires_manual_followup": incident.requires_manual_followup,
        }

    def _summary_to_payload(self, summary: DailySummary) -> dict[str, Any]:
        extras = {
            "optimization_suggestions": [asdict(item) for item in summary.optimization_suggestions],
            "estimated_cost": self.cost_analyzer.estimate(summary.tokens_consumed),
        }
        return self.json_reporter.build(summary, extras=extras)
