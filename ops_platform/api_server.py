from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .orchestrator import OpsAutomationPlatform


class PlatformAPIHandler(BaseHTTPRequestHandler):
    platform = OpsAutomationPlatform()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._write_json(self.platform.health_snapshot())
            return
        if parsed.path == "/readiness":
            self._write_json(self.platform.health_snapshot()["readiness"])
            return
        if parsed.path == "/servers":
            self._write_json({"servers": list(self.platform.servers.keys())})
            return
        if parsed.path == "/dashboard":
            self._write_json(self.platform.dashboard())
            return
        if parsed.path == "/kpis":
            self._write_json(self.platform.dashboard()["kpis"])
            return
        if parsed.path == "/timeline":
            self._write_json({"timeline": self.platform.timeline()})
            return
        if parsed.path == "/notifications":
            self._write_json({"notifications": self.platform.notifications()})
            return
        if parsed.path == "/report":
            self._write_text(self.platform.report_text())
            return

        self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/simulate":
            self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        params = parse_qs(parsed.query)
        cycles = int(params.get("cycles", [1])[0])
        payload = self.platform.simulate_day(cycles=cycles)
        self.platform.export_dashboard_json()
        self._write_json(payload)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_text(self, text: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), PlatformAPIHandler)
    print(f"Server running at http://{host}:{port}")
    server.serve_forever()
