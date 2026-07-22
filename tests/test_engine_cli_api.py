from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from oncall_alert_correlation_engine.api import app
from oncall_alert_correlation_engine.cli import _load_alerts, _load_catalog
from oncall_alert_correlation_engine.engine import correlate_alerts

ROOT = Path(__file__).resolve().parents[1]


def test_correlates_noisy_alerts_into_page_worthy_incident() -> None:
    report = correlate_alerts(
        _load_alerts(ROOT / "examples/noisy_alerts.json"),
        _load_catalog(ROOT / "examples/service_catalog.json"),
    )

    assert report.reviewed_alerts == 5
    assert report.incident_count == 2
    assert report.page_worthy_incidents == 1
    checkout = next(incident for incident in report.incidents if incident.service == "checkout-api")
    assert checkout.severity == "P1"
    assert checkout.alert_count == 3
    assert checkout.missing_readiness == []
    assert "a-002" in report.suppressed_alert_ids


def test_clean_alerts_do_not_create_page() -> None:
    report = correlate_alerts(
        _load_alerts(ROOT / "examples/clean_alerts.json"),
        _load_catalog(ROOT / "examples/service_catalog.json"),
    )

    assert report.page_worthy_incidents == 0
    assert all(incident.severity not in {"P1", "P2"} for incident in report.incidents)


def test_cli_writes_reports_and_returns_page_exit_code(tmp_path: Path) -> None:
    json_out = tmp_path / "report.json"
    md_out = tmp_path / "report.md"
    metrics_out = tmp_path / "metrics.prom"
    command = [
        sys.executable,
        "-m",
        "oncall_alert_correlation_engine.cli",
        "correlate",
        str(ROOT / "examples/noisy_alerts.json"),
        "--catalog",
        str(ROOT / "examples/service_catalog.json"),
        "--json-out",
        str(json_out),
        "--markdown-out",
        str(md_out),
        "--metrics-out",
        str(metrics_out),
        "--fail-on-page",
    ]

    result = subprocess.run(command, cwd=ROOT, check=False, text=True, capture_output=True)

    assert result.returncode == 2
    assert "page-worthy incidents" in result.stdout
    assert json.loads(json_out.read_text())["page_worthy_incidents"] == 1
    assert "# On-Call Alert Correlation Report" in md_out.read_text()
    assert "oncall_correlation_page_worthy_incidents" in metrics_out.read_text()


def test_api_health_correlate_and_metrics() -> None:
    client = TestClient(app)
    payload = {
        "alerts": json.loads((ROOT / "examples/noisy_alerts.json").read_text())["alerts"],
        "services": json.loads((ROOT / "examples/service_catalog.json").read_text())["services"],
    }

    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/correlate", json=payload)
    assert response.status_code == 200
    assert response.json()["page_worthy_incidents"] == 1
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "oncall_correlation_alerts_reviewed_total" in metrics.text
