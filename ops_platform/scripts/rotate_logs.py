from __future__ import annotations


def rotate_logs_command() -> str:
    return "logrotate -f /etc/logrotate.conf"
