from __future__ import annotations

from datetime import datetime, timedelta
from random import Random

from .models import MetricSnapshot, Server


def build_server_inventory(total: int = 30) -> list[Server]:
    servers: list[Server] = []
    roles = ["gateway", "api", "scheduler", "database", "log-agent"]
    owners = ["ops", "middleware", "security"]
    os_families = ["centos", "kylin"]

    for index in range(total):
        servers.append(
            Server(
                id=f"srv-{index + 1:03d}",
                hostname=f"prod-node-{index + 1:02d}",
                os_family=os_families[index % len(os_families)],
                environment="production" if index < total - 4 else "staging",
                role=roles[index % len(roles)],
                ip_address=f"10.10.{index // 10}.{index % 10 + 10}",
                owner=owners[index % len(owners)],
            )
        )
    return servers


def build_metric_snapshots(
    servers: list[Server],
    cycle: int,
    rng: Random,
    start_time: datetime,
) -> list[MetricSnapshot]:
    snapshots: list[MetricSnapshot] = []
    timestamp = start_time + timedelta(minutes=cycle * 30)

    for index, server in enumerate(servers):
        cpu = round(rng.uniform(18, 62), 2)
        memory = round(rng.uniform(30, 75), 2)
        disk = round(rng.uniform(38, 78), 2)
        load = round(rng.uniform(0.3, 2.4), 2)
        log_keywords = ["healthy"]
        processes = [server.role, "sshd", "monitor-agent"]
        context = {"planned_change": False, "business_peak": False, "deploy_window": False}

        anomaly_seed = (cycle * len(servers) + index) % 10

        if server.environment == "staging" and cycle == 1 and index % 2 == 0:
            cpu = round(rng.uniform(82, 88), 2)
            if server.role in processes:
                processes.remove(server.role)
            log_keywords = ["deploy_start", "warming_up", "service_recycle"]
            context["planned_change"] = True
            context["deploy_window"] = True
            snapshots.append(
                MetricSnapshot(
                    server_id=server.id,
                    cpu_usage=cpu,
                    memory_usage=memory,
                    disk_usage=disk,
                    load_average=load,
                    log_keywords=log_keywords,
                    running_processes=processes,
                    timestamp=timestamp,
                    context=context,
                )
            )
            continue

        if anomaly_seed == 0:
            cpu = round(rng.uniform(87, 98), 2)
            load = round(rng.uniform(4.1, 7.9), 2)
            log_keywords = ["cpu_spike", "request_backlog"]
            context["business_peak"] = True
        elif anomaly_seed == 1:
            memory = round(rng.uniform(89, 97), 2)
            log_keywords = ["oom_warning", "cache_pressure"]
        elif anomaly_seed == 2:
            disk = round(rng.uniform(91, 98), 2)
            log_keywords = ["disk_full", "log_growth"]
        elif anomaly_seed == 3:
            processes.remove(server.role)
            log_keywords = ["service_exit", "heartbeat_missing"]
        elif anomaly_seed == 4 and server.environment == "staging":
            cpu = round(rng.uniform(82, 90), 2)
            if server.role in processes:
                processes.remove(server.role)
            log_keywords = ["deploy_start", "warming_up", "service_recycle"]
            context["planned_change"] = True
            context["deploy_window"] = True
        elif anomaly_seed == 5:
            disk = round(rng.uniform(85, 90), 2)
            memory = round(rng.uniform(82, 88), 2)
            log_keywords = ["rotation_delay", "iowait"]

        snapshots.append(
            MetricSnapshot(
                server_id=server.id,
                cpu_usage=cpu,
                memory_usage=memory,
                disk_usage=disk,
                load_average=load,
                log_keywords=log_keywords,
                running_processes=processes,
                timestamp=timestamp,
                context=context,
            )
        )

    return snapshots
