from __future__ import annotations


class OSCompatibilityMatrix:
    def __init__(self) -> None:
        self._matrix = {
            "centos": ["service_restart", "disk_cleanup", "config_update", "log_rotation"],
            "kylin": ["service_restart", "disk_cleanup", "config_update", "log_rotation"],
        }

    def supported_actions(self, os_family: str) -> list[str]:
        return list(self._matrix.get(os_family.lower(), []))

    def supports(self, os_family: str, action_name: str) -> bool:
        return action_name in self._matrix.get(os_family.lower(), [])
