from __future__ import annotations


class TokenMeter:
    def __init__(self, tokens_per_task: int) -> None:
        self.tokens_per_task = tokens_per_task

    def consume(self, automated_tasks: int) -> int:
        return automated_tasks * self.tokens_per_task
