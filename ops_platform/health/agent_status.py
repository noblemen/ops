from __future__ import annotations


class AgentStatusService:
    def build(self) -> list[dict[str, object]]:
        return [
            {"agent": "monitoring", "status": "running", "duty": "alert analysis"},
            {"agent": "response", "status": "running", "duty": "automated remediation"},
            {"agent": "audit", "status": "running", "duty": "audit and optimization"},
        ]
