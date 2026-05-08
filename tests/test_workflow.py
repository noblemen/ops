from pathlib import Path
import unittest

from ops_platform.orchestrator import OpsAutomationPlatform


class WorkflowTests(unittest.TestCase):
    def test_seeded_simulation_matches_demo_kpis(self) -> None:
        platform = OpsAutomationPlatform()
        result = platform.simulate_day(cycles=4)
        summary = result["summary"]

        self.assertEqual(summary["managed_servers"], 30)
        self.assertEqual(summary["automated_tasks"], 60)
        self.assertEqual(summary["successful_automations"], 51)
        self.assertEqual(summary["automation_rate"], 85.0)
        self.assertEqual(summary["tokens_consumed"], 1500000)
        self.assertEqual(summary["time_saved_hours"], 4.0)
        self.assertGreaterEqual(summary["false_positives_filtered"], 2)
        self.assertIn("timeline", result)
        self.assertIn("alert_trends", result)
        self.assertIn("notifications", result)

    def test_dashboard_exposes_extended_modules(self) -> None:
        platform = OpsAutomationPlatform()
        platform.simulate_day(cycles=4)
        dashboard = platform.dashboard()

        self.assertIn("health", dashboard)
        self.assertIn("readiness", dashboard)
        self.assertIn("agent_status", dashboard)
        self.assertIn("capacity_plan", dashboard)
        self.assertIn("notifications", dashboard)
        self.assertIn("Kylin", dashboard["supported_os"])

    def test_report_export_writes_expected_sections(self) -> None:
        platform = OpsAutomationPlatform()
        platform.simulate_day(cycles=4)
        target = Path("reports/test_audit_report.md")
        platform.export_report(target)
        content = target.read_text(encoding="utf-8")

        self.assertIn("# Multi-Agent O&M Audit Report", content)
        self.assertIn("## Compliance Overview", content)
        self.assertIn("## Optimization Suggestions", content)

    def test_repo_contains_at_least_30_python_files(self) -> None:
        py_files = list(Path("ops_platform").rglob("*.py"))
        self.assertGreaterEqual(len(py_files), 30)


if __name__ == "__main__":
    unittest.main()
