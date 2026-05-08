from __future__ import annotations

from dataclasses import asdict

from .base import NotificationEvent, Notifier


class NotificationManager:
    def __init__(self, notifiers: list[Notifier]) -> None:
        self.notifiers = notifiers
        self.events: list[NotificationEvent] = []

    def broadcast(self, title: str, body: str, severity: str) -> list[NotificationEvent]:
        dispatched = [notifier.send(title, body, severity) for notifier in self.notifiers]
        self.events.extend(dispatched)
        return dispatched

    def recent_payloads(self, limit: int = 10) -> list[dict[str, object]]:
        return [asdict(event) for event in self.events[-limit:]]

    def clear(self) -> None:
        self.events.clear()
