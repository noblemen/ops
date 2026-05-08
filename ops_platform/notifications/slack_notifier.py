from __future__ import annotations

from datetime import datetime

from .base import NotificationEvent


class SlackNotifier:
    channel_name = "slack"

    def send(self, title: str, body: str, severity: str) -> NotificationEvent:
        return NotificationEvent(
            channel=self.channel_name,
            title=f"[Slack] {title}",
            body=body,
            severity=severity,
            created_at=datetime.now(),
        )
