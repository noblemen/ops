from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime

from ..models import AuditLog, IncidentResult, OptimizationSuggestion, Server


class AuditOptimizationAgent:
    def record(self, server: Server, incident: IncidentResult) -> AuditLog:
        action_name = incident.action.name if incident.action else "suppressed"
        return AuditLog(
            incident_id=incident.alert_id,
            server_id=server.id,
            os_family=server.os_family,
            operator="auto-agent",
            action_name=action_name,
            status=incident.status,
            timestamp=incident.executed_at,
            details=incident.summary,
        )

    def build_optimization_suggestions(
        self,
        servers: dict[str, Server],
        audit_logs: list[AuditLog],
    ) -> list[OptimizationSuggestion]:
        per_server = defaultdict(list)
        for log in audit_logs:
            per_server[log.server_id].append(log)

        suggestions: list[OptimizationSuggestion] = []
        for server_id, logs in per_server.items():
            counter = Counter(log.action_name for log in logs)
            server = servers[server_id]

            if counter["disk_cleanup"] >= 2:
                suggestions.append(
                    OptimizationSuggestion(
                        server_id=server_id,
                        priority="high",
                        title="Increase log retention controls",
                        recommendation=(
                            f"{server.hostname} repeatedly triggered disk cleanup. Add stricter rotation and split hot logs."
                        ),
                        estimated_benefit="Reduce disk alerts by 40 percent.",
                    )
                )
            if counter["config_update"] >= 2:
                suggestions.append(
                    OptimizationSuggestion(
                        server_id=server_id,
                        priority="medium",
                        title="Tune service memory and worker pool",
                        recommendation=(
                            f"{server.hostname} needs a tighter memory cap and worker concurrency review."
                        ),
                        estimated_benefit="Lower peak CPU and memory pressure during busy windows.",
                    )
                )
            if counter["service_restart"] >= 2:
                suggestions.append(
                    OptimizationSuggestion(
                        server_id=server_id,
                        priority="high",
                        title="Stabilize service startup path",
                        recommendation=(
                            f"{server.hostname} restarted multiple times. Add dependency checks and startup probes."
                        ),
                        estimated_benefit="Reduce crash-loop incidents and manual follow-up.",
                    )
                )

        return suggestions[:8]

    def generate_report(
        self,
        audit_logs: list[AuditLog],
        suggestions: list[OptimizationSuggestion],
        generated_at: datetime | None = None,
    ) -> str:
        timestamp = generated_at or datetime.now()
        total = len(audit_logs)
        resolved = sum(1 for log in audit_logs if log.status == "resolved")
        followups = sum(1 for log in audit_logs if log.status == "manual_followup")
        suppressed = sum(1 for log in audit_logs if log.status == "suppressed")

        lines = [
            "# Multi-Agent O&M Audit Report",
            "",
            f"Generated at: {timestamp.isoformat(timespec='seconds')}",
            f"Total operation records: {total}",
            f"Resolved automatically: {resolved}",
            f"Manual follow-ups: {followups}",
            f"Suppressed false positives: {suppressed}",
            "",
            "## Compliance Overview",
            "- All operations are attributed to the auto-agent execution identity.",
            "- Cross-OS scripts are selected through explicit CentOS and Kylin adapters.",
            "- Each incident preserves an execution summary for audit traceability.",
            "",
            "## Operation Highlights",
        ]

        for log in audit_logs[:10]:
            lines.append(
                f"- {log.timestamp.isoformat(timespec='seconds')} | {log.server_id} | {log.action_name} | {log.status}"
            )

        lines.extend(["", "## Optimization Suggestions"])
        if not suggestions:
            lines.append("- No immediate optimization suggestions were generated.")
        else:
            for suggestion in suggestions:
                lines.append(
                    f"- [{suggestion.priority}] {suggestion.server_id}: {suggestion.recommendation} ({suggestion.estimated_benefit})"
                )

        return "\n".join(lines)
