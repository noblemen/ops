from __future__ import annotations

from ..models import RepairAction


class OSProfileAdapter:
    def __init__(self) -> None:
        self._profiles = {
            "centos": {
                "service_restart": ("restart_service.sh", "systemctl restart {service}"),
                "disk_cleanup": ("cleanup_disk.sh", "find /var/log -type f -name '*.log' -size +200M -delete"),
                "config_update": ("reload_config.sh", "systemctl reload {service}"),
                "log_rotation": ("rotate_logs.sh", "logrotate -f /etc/logrotate.conf"),
            },
            "kylin": {
                "service_restart": ("restart_service_kylin.sh", "systemctl restart {service}"),
                "disk_cleanup": ("cleanup_disk_kylin.sh", "journalctl --vacuum-size=1G && rm -rf /var/tmp/*"),
                "config_update": ("reload_config_kylin.sh", "systemctl daemon-reload && systemctl restart {service}"),
                "log_rotation": ("rotate_logs_kylin.sh", "logrotate -f /etc/logrotate.d/messages"),
            },
        }

    def build_action(self, os_family: str, action_name: str, service: str) -> RepairAction:
        profile = self._profiles.get(os_family.lower(), self._profiles["centos"])
        script_name, command_template = profile[action_name]
        command = command_template.format(service=service)
        automation_level = "full-auto" if action_name != "config_update" else "semi-auto"
        return RepairAction(
            name=action_name,
            script_name=script_name,
            command=command,
            automation_level=automation_level,
        )
