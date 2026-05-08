from __future__ import annotations

import argparse
import json

from ops_platform.api_server import run_server
from ops_platform.orchestrator import OpsAutomationPlatform


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multi-agent enterprise O&M automation platform demo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate = subparsers.add_parser("simulate", help="Run the platform simulation")
    simulate.add_argument("--cycles", type=int, default=4, help="Number of monitoring cycles")
    simulate.add_argument(
        "--report-file",
        default="reports/audit_report.md",
        help="Where to write the generated audit report",
    )

    serve = subparsers.add_parser("serve", help="Start the local HTTP API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "simulate":
        platform = OpsAutomationPlatform()
        result = platform.simulate_day(cycles=args.cycles)
        report_path = platform.export_report(args.report_file)
        dashboard_path = platform.export_dashboard_json()
        print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
        print(f"Audit report written to {report_path}")
        print(f"Dashboard snapshot written to {dashboard_path}")
        return

    if args.command == "serve":
        run_server(host=args.host, port=args.port)
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
