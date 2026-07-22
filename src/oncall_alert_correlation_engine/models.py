"""Pydantic models shared by the CLI, API, and tests."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "warning", "critical"]
IncidentSeverity = Literal["P4", "P3", "P2", "P1"]


class Alert(BaseModel):
    id: str
    service: str
    signal: str
    severity: Severity
    started_at: datetime
    summary: str
    runbook_url: str | None = None
    fingerprint: str | None = None


class ServiceCatalogEntry(BaseModel):
    owner: str | None = None
    tier: Literal["frontend", "backend", "data", "platform"] = "backend"
    escalation_policy: str | None = None
    dependencies: list[str] = Field(default_factory=list)


class Incident(BaseModel):
    key: str
    service: str
    severity: IncidentSeverity
    alert_count: int
    window_start: datetime
    window_end: datetime
    owner: str | None
    escalation_policy: str | None
    signals: list[str]
    contributing_alert_ids: list[str]
    recommended_action: str
    missing_readiness: list[str] = Field(default_factory=list)


class CorrelationReport(BaseModel):
    reviewed_alerts: int
    incident_count: int
    page_worthy_incidents: int
    incidents: list[Incident]
    suppressed_alert_ids: list[str]
    summary: str

