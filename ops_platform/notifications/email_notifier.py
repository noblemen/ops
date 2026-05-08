from __future__ import annotations

from datetime import datetime

from .base import NotificationEvent


class EmailNotifier:
    channel_name = "email"

    def send(self, title: str, body: str, severity: str) -> NotificationEvent:
        return NotificationEvent(
            channel=self.channel_name,
            title=f"[Email] {title}",
            body=body,
            severity=severity,
            created_at=datetime.now(),
        )
