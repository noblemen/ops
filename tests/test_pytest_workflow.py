from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from ops_platform.api_server import PlatformAPIHandler
from ops_platform.orchestrator import OpsAutomationPlatform


def test_seeded_simulation_matches_expected_summary() -> None:
    platform = OpsAutomationPlatform()

    result = platform.simulate_day(cycles=4)
    summary = result["summary"]

    assert {
        key: summary[key]
        for key in (
            "managed_servers",
            "total_alerts",
            "false_positives_filtered",
            "automated_tasks",
            "successful_automations",
            "manual_followups",
            "automation_rate",
            "tokens_consumed",
            "time_saved_hours",
            "estimated_cost",
        )
    } == {
        "managed_servers": 30,
        "total_alerts": 62,
        "false_positives_filtered": 2,
        "automated_tasks": 60,
        "successful_automations": 51,
        "manual_followups": 9,
        "automation_rate": 85.0,
        "tokens_consumed": 1500000,
        "time_saved_hours": 4.0,
        "estimated_cost": {"price_per_million": 8.0, "estimated_cost": 12.0},
    }
    assert len(summary["optimization_suggestions"]) == 8
    assert len(result["cycles"]) == 4
    assert len(result["timeline"]) == 12
    assert result["alert_trends"]
    assert result["notifications"]


def test_simulation_resets_history_between_runs() -> None:
    platform = OpsAutomationPlatform()

    first_result = platform.simulate_day(cycles=4)
    second_result = platform.simulate_day(cycles=4)

    assert second_result["summary"] == first_result["summary"]
    assert len(platform.alert_history) == first_result["summary"]["total_alerts"]
    assert len(platform.incident_history) == first_result["summary"]["automated_tasks"]
    assert len(platform.audit_logs) == first_result["summary"]["automated_tasks"]


def test_report_and_dashboard_exports_use_requested_paths(tmp_path) -> None:
    platform = OpsAutomationPlatform()
    platform.simulate_day(cycles=4)
    report_path = tmp_path / "audit_report.md"
    dashboard_path = tmp_path / "dashboard.json"

    written_report = platform.export_report(report_path)
    written_dashboard = platform.export_dashboard_json(dashboard_path)

    assert written_report == report_path
    assert written_dashboard == dashboard_path
    assert "# Multi-Agent O&M Audit Report" in report_path.read_text(encoding="utf-8")

    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    assert dashboard["summary"]["automation_rate"] == 85.0
    assert dashboard["health"]["status"] == "healthy"
    assert "Kylin" in dashboard["supported_os"]


def test_api_handler_serves_simulation_and_dashboard(tmp_path, monkeypatch) -> None:
    class TestAPIHandler(PlatformAPIHandler):
        platform = OpsAutomationPlatform()

    monkeypatch.setattr(
        TestAPIHandler.platform,
        "export_dashboard_json",
        lambda path="reports/dashboard.json": tmp_path / "dashboard.json",
    )

    server = ThreadingHTTPServer(("127.0.0.1", 0), TestAPIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"

        with urlopen(f"{base_url}/health", timeout=5) as response:
            assert response.status == 200
            health = json.loads(response.read().decode("utf-8"))
        assert health["system"]["managed_servers"] == 30
        assert health["readiness"]["ready"] is False

        with urlopen(f"{base_url}/simulate?cycles=1", data=b"", timeout=5) as response:
            assert response.status == 200
            simulated = json.loads(response.read().decode("utf-8"))
        assert simulated["summary"]["managed_servers"] == 30
        assert len(simulated["cycles"]) == 1

        with urlopen(f"{base_url}/dashboard", timeout=5) as response:
            assert response.status == 200
            dashboard = json.loads(response.read().decode("utf-8"))
        assert dashboard["readiness"]["ready"] is True
        assert dashboard["summary"]["total_alerts"] == simulated["summary"]["total_alerts"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
