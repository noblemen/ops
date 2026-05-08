from __future__ import annotations

from collections.abc import Iterable

from ..config.thresholds import MonitoringThresholds
from ..models import Alert, MetricSnapshot, Server
from ..rules.cpu_rule import CpuSpikeRule
from ..rules.disk_rule import DiskPressureRule
from ..rules.false_positive_rule import FalsePositiveRule
from ..rules.log_rule import LogAnomalyRule
from ..rules.memory_rule import MemoryPressureRule
from ..rules.service_rule import ServiceDownRule
from ..utils.id_utils import short_id


class MonitoringAlertAgent:
    def __init__(self, thresholds: MonitoringThresholds | None = None) -> None:
        self.thresholds = thresholds or MonitoringThresholds()
        self.rules = [
            ServiceDownRule(),
            DiskPressureRule(self.thresholds.disk_high),
            MemoryPressureRule(self.thresholds.memory_high),
            CpuSpikeRule(self.thresholds.cpu_high, self.thresholds.load_high),
            LogAnomalyRule(self.thresholds.disk_warning, self.thresholds.memory_warning),
        ]
        self.false_positive_rule = FalsePositiveRule()

    def analyze(self, servers: dict[str, Server], snapshots: Iterable[MetricSnapshot]) -> list[Alert]:
        alerts: list[Alert] = []

        for snapshot in snapshots:
            server = servers[snapshot.server_id]
            match = self._classify(server, snapshot)
            if match is None:
                continue

            false_positive = self.false_positive_rule.is_false_positive(snapshot, match.category)
            root_cause, reasoning_steps = self._reason(server, snapshot, match.category, false_positive)
            signal_score = self._signal_score(snapshot, match.category, false_positive)
            recommended_action = self._recommended_action(match.category)

            alerts.append(
                Alert(
                    id=short_id("alt"),
                    server_id=server.id,
                    category=match.category,
                    severity=match.severity,
                    title=f"{server.hostname} {match.category.replace('_', ' ')}",
                    description=match.description,
                    probable_root_cause=root_cause,
                    reasoning_steps=reasoning_steps,
                    recommended_action=recommended_action,
                    is_false_positive=false_positive,
                    created_at=snapshot.timestamp,
                    signal_score=signal_score,
                )
            )

        return alerts

    def _classify(self, server: Server, snapshot: MetricSnapshot):
        for rule in self.rules:
            match = rule.evaluate(server, snapshot)
            if match is not None:
                return match
        return None

    def _reason(
        self,
        server: Server,
        snapshot: MetricSnapshot,
        category: str,
        false_positive: bool,
    ) -> tuple[str, list[str]]:
        reasoning_steps = [
            f"Checked {server.hostname} baseline for role {server.role}.",
            f"Observed cpu={snapshot.cpu_usage}, mem={snapshot.memory_usage}, disk={snapshot.disk_usage}.",
            f"Parsed log keywords: {', '.join(snapshot.log_keywords)}.",
        ]

        if false_positive:
            reasoning_steps.append("Detected a planned change window, so the alert is downgraded.")
            reasoning_steps.append(self.false_positive_rule.explain(category))
            return "Scheduled release activity explains the transient anomaly.", reasoning_steps

        if category == "service_down":
            reasoning_steps.append("Missing process plus missing heartbeat strongly indicate service crash.")
            return "Application process exited unexpectedly after heartbeat loss.", reasoning_steps
        if category == "disk_pressure":
            reasoning_steps.append("Persistent log growth points to log cleanup backlog.")
            return "Accumulated logs consumed the free space threshold.", reasoning_steps
        if category == "memory_pressure":
            reasoning_steps.append("OOM warnings and cache pressure suggest memory leak or stale cache.")
            return "Application memory leak or cache expansion exhausted memory headroom.", reasoning_steps
        if category == "cpu_spike":
            reasoning_steps.append("High request backlog indicates a real load surge instead of a noisy sample.")
            return "Traffic surge pushed compute threads into sustained high load.", reasoning_steps

        reasoning_steps.append("Log rotation delay is the main cross-signal anomaly.")
        return "Log rotation stalled and amplified memory plus disk pressure.", reasoning_steps

    def _recommended_action(self, category: str) -> str:
        return {
            "service_down": "service_restart",
            "disk_pressure": "disk_cleanup",
            "memory_pressure": "config_update",
            "cpu_spike": "config_update",
            "log_anomaly": "log_rotation",
        }[category]

    def _signal_score(self, snapshot: MetricSnapshot, category: str, false_positive: bool) -> float:
        base_score = {
            "service_down": 0.99,
            "disk_pressure": 0.91,
            "memory_pressure": 0.9,
            "cpu_spike": 0.84,
            "log_anomaly": 0.79,
        }[category]
        if false_positive:
            base_score -= 0.32
        return round(max(base_score, 0.2), 2)
