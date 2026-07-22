"""FastAPI app exposing the correlation engine."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .engine import correlate_alerts
from .metrics import render_metrics
from .models import Alert, CorrelationReport, ServiceCatalogEntry

app = FastAPI(title="On-Call Alert Correlation Engine", version="0.1.0")
_last_report: CorrelationReport | None = None


class CorrelationRequest(BaseModel):
    alerts: list[Alert]
    services: dict[str, ServiceCatalogEntry]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/correlate", response_model=CorrelationReport)
def correlate(payload: CorrelationRequest) -> CorrelationReport:
    global _last_report
    _last_report = correlate_alerts(payload.alerts, payload.services)
    return _last_report


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    if _last_report is None:
        empty = CorrelationReport(
            reviewed_alerts=0,
            incident_count=0,
            page_worthy_incidents=0,
            incidents=[],
            suppressed_alert_ids=[],
            summary="No alert correlation run has completed yet.",
        )
        return render_metrics(empty)
    return render_metrics(_last_report)

