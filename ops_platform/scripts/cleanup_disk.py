from __future__ import annotations


def cleanup_disk_command() -> str:
    return "find /var/log -type f -name '*.log' -size +200M -delete"
