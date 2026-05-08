from __future__ import annotations

from datetime import datetime

from ..models import AuditLog, DailySummary, OptimizationSuggestion


class MarkdownReporter:
    def build(
        self,
        summary: DailySummary,
        audit_logs: list[AuditLog],
        suggestions: list[OptimizationSuggestion],
        compliance_lines: list[str],
        generated_at: datetime,
    ) -> str:
        lines = [
            "# Multi-Agent O&M Audit Report",
            "",
            f"Generated at: {generated_at.isoformat(timespec='seconds')}",
            f"Managed servers: {summary.managed_servers}",
            f"Total alerts: {summary.total_alerts}",
            f"False positives filtered: {summary.false_positives_filtered}",
            f"Automated tasks: {summary.automated_tasks}",
            f"Successful automations: {summary.successful_automations}",
            f"Automation rate: {summary.automation_rate}%",
            f"Tokens consumed: {summary.tokens_consumed}",
            f"Time saved hours: {summary.time_saved_hours}",
            "",
            "## Compliance Overview",
        ]
        for line in compliance_lines:
            lines.append(f"- {line}")
        lines.extend(["", "## Operation Highlights"])
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
