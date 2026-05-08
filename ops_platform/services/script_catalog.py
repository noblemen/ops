from __future__ import annotations


class ScriptCatalog:
    def __init__(self) -> None:
        self._scripts = {
            "service_restart": "Restart service and verify health probe",
            "disk_cleanup": "Clean logs and rotate oversized files",
            "config_update": "Reload config and rebalance worker pool",
            "log_rotation": "Force rotation and compress cold logs",
        }

    def describe(self, action_name: str) -> str:
        return self._scripts.get(action_name, "Unknown remediation script")

    def list_actions(self) -> list[str]:
        return sorted(self._scripts)
