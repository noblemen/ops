from __future__ import annotations


def restart_service_command(service: str) -> str:
    return f"systemctl restart {service} && systemctl is-active {service}"
