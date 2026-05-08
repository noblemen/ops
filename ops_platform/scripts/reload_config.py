from __future__ import annotations


def reload_config_command(service: str) -> str:
    return f"systemctl reload {service} || systemctl restart {service}"
