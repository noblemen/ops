from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(slots=True)
class NotificationEvent:
    channel: str
    title: str
    body: str
    severity: str
    created_at: datetime


class Notifier(Protocol):
    channel_name: str

    def send(self, title: str, body: str, severity: str) -> NotificationEvent:
        ...
