from __future__ import annotations

from dataclasses import dataclass

from ..models import MetricSnapshot, Server


@dataclass(slots=True)
class RuleMatch:
    category: str
    severity: str
    description: str


class BaseRule:
    def evaluate(self, server: Server, snapshot: MetricSnapshot) -> RuleMatch | None:
        raise NotImplementedError
